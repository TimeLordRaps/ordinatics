"""Check the dependency pin in a wheel and source distribution (sdist).

The packaged copies must retain the exact source-lock bytes and the exact
Hypermath repository, distribution, version, and commit identity. Archives are
read without extraction. This checks packaging integrity, not mathematical
proof status, and requires only Python's standard library.
"""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import io
import json
import re
import stat
import sys
import tarfile
import unicodedata
import zipfile
from pathlib import Path
from typing import NamedTuple

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_REPOSITORY = "https://github.com/TimeLordRaps/hypermath.git"
EXPECTED_DISTRIBUTION = "hypermath-foundations"
EXPECTED_VERSION = "0.1.0"
EXPECTED_FIELDS = {"schema_version", "repository", "commit", "distribution", "version"}
WHEEL_PIN = "ordinatics/_data/hypermath.json"
MAX_PIN_BYTES = 64 * 1024
MAX_RECORD_BYTES = 8 * 1024 * 1024
MAX_ARCHIVE_BYTES = 512 * 1024 * 1024
MAX_UNPACKED_BYTES = 512 * 1024 * 1024
MAX_MEMBERS = 20_000


class PackagedPinError(ValueError):
    """A built artifact does not retain the exact reviewed dependency pin."""


class DependencyIdentity(NamedTuple):
    """The exact external source and Python distribution coordinate."""

    repository: str
    distribution: str
    version: str
    commit: str


class CheckedArtifacts(NamedTuple):
    """The two checked artifacts and their retained dependency identity."""

    wheel: Path
    source_distribution: Path
    identity: DependencyIdentity


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise PackagedPinError(f"dependency pin contains a duplicate key: {key}")
        result[key] = value
    return result


def _pin_identity(contents: bytes, label: str) -> DependencyIdentity:
    try:
        data = json.loads(contents.decode("utf-8"), object_pairs_hook=_unique_object)
    except (UnicodeError, ValueError) as error:
        raise PackagedPinError(f"{label} is not unambiguous UTF-8 JSON: {error}") from error
    if not isinstance(data, dict) or set(data) != EXPECTED_FIELDS:
        raise PackagedPinError(f"{label} must contain exactly the versioned pin fields")
    if type(data["schema_version"]) is not int or data["schema_version"] != 1:
        raise PackagedPinError(f"{label} has an unsupported dependency-pin schema")
    repository = data["repository"]
    distribution = data["distribution"]
    version = data["version"]
    commit = data["commit"]
    if repository != EXPECTED_REPOSITORY:
        raise PackagedPinError(f"{label} does not name the canonical Hypermath repository")
    if distribution != EXPECTED_DISTRIBUTION or version != EXPECTED_VERSION:
        raise PackagedPinError(f"{label} does not name the required distribution and version")
    if not isinstance(commit, str) or re.fullmatch(r"[0-9a-f]{40}", commit) is None:
        raise PackagedPinError(f"{label} commit must be a full lowercase 40-digit Git SHA")
    return DependencyIdentity(repository, distribution, version, commit)


def _read_source_lock(path: Path) -> tuple[bytes, DependencyIdentity]:
    if path.is_symlink() or not path.is_file():
        raise PackagedPinError("source dependency lock must be a regular file")
    try:
        size = path.stat().st_size
        if size > MAX_PIN_BYTES:
            raise PackagedPinError("source dependency lock exceeds the bounded pin size")
        contents = path.read_bytes()
    except OSError as error:
        raise PackagedPinError(f"cannot read source dependency lock: {error}") from error
    if len(contents) != size or len(contents) > MAX_PIN_BYTES:
        raise PackagedPinError("source dependency lock changed or exceeded its size bound")
    return contents, _pin_identity(contents, "source dependency lock")


def _artifact_files(directory: Path) -> tuple[Path, Path]:
    if directory.is_symlink() or not directory.is_dir():
        raise PackagedPinError("distribution directory must be a regular directory")
    try:
        entries = list(directory.iterdir())
    except OSError as error:
        raise PackagedPinError(f"cannot inspect distribution directory: {error}") from error
    wheels = [path for path in entries if path.name.endswith(".whl")]
    source_distributions = [path for path in entries if path.name.endswith(".tar.gz")]
    if len(wheels) != 1:
        raise PackagedPinError("distribution directory must contain exactly one wheel")
    if len(source_distributions) != 1:
        raise PackagedPinError(
            "distribution directory must contain exactly one source distribution (.tar.gz)"
        )
    if set(entries) != {wheels[0], source_distributions[0]}:
        raise PackagedPinError("distribution directory contains an unexpected entry")
    for artifact in (*wheels, *source_distributions):
        if artifact.is_symlink() or not artifact.is_file():
            raise PackagedPinError("distribution artifacts must be regular files")
        try:
            if artifact.stat().st_size > MAX_ARCHIVE_BYTES:
                raise PackagedPinError("distribution artifact exceeds the bounded archive size")
        except OSError as error:
            raise PackagedPinError(f"cannot inspect distribution artifact: {error}") from error
    return wheels[0], source_distributions[0]


def _normalized_distribution(value: str) -> str:
    return re.sub(r"[-_.]+", "-", value).lower()


def _artifact_versions(wheel: Path, source_distribution: Path) -> tuple[str, str]:
    wheel_parts = wheel.name.removesuffix(".whl").split("-")
    if (
        len(wheel_parts) not in (5, 6)
        or _normalized_distribution(wheel_parts[0]) != "ordinatics"
        or not wheel_parts[1]
    ):
        raise PackagedPinError("wheel filename must identify an Ordinatics distribution")
    source_name = source_distribution.name.removesuffix(".tar.gz")
    prefix = "ordinatics-"
    if not source_name.startswith(prefix) or not source_name.removeprefix(prefix):
        raise PackagedPinError(
            "source-distribution filename must identify an Ordinatics distribution"
        )
    wheel_version = wheel_parts[1]
    source_version = source_name.removeprefix(prefix)
    if source_version != wheel_version:
        raise PackagedPinError("wheel and source-distribution versions do not match")
    return wheel_version, source_name


def _member_location(name: str, archive_label: str) -> str:
    location = name[:-1] if name.endswith("/") else name
    if (
        not location
        or "\\" in location
        or ":" in location
        or any(ord(character) < 32 or ord(character) == 127 for character in location)
        or any(part in ("", ".", "..") for part in location.split("/"))
    ):
        raise PackagedPinError(
            f"{archive_label} contains an unsafe or noncanonical member path"
        )
    return location


def _portable_member_key(location: str, archive_label: str) -> str:
    """Return a collision key for common case-folding and normalizing filesystems."""
    parts: list[str] = []
    for part in location.split("/"):
        normalized = unicodedata.normalize("NFC", part)
        if normalized.rstrip(" .") != normalized:
            raise PackagedPinError(
                f"{archive_label} contains a nonportable member path"
            )
        parts.append(normalized.casefold())
    return "/".join(parts)


def _check_packaged_contents(
    contents: bytes,
    source_contents: bytes,
    source_identity: DependencyIdentity,
    label: str,
) -> None:
    packaged_identity = _pin_identity(contents, label)
    if packaged_identity != source_identity:
        raise PackagedPinError(f"{label} does not retain the exact source identity")
    if contents != source_contents:
        raise PackagedPinError(f"{label} differs byte-for-byte from the source dependency lock")


def _read_zip_member(
    archive: zipfile.ZipFile,
    member: zipfile.ZipInfo,
    limit: int,
    label: str,
) -> bytes:
    if member.file_size > limit:
        raise PackagedPinError(f"{label} exceeds its bounded size")
    with archive.open(member) as stream:
        contents = stream.read(limit + 1)
    if len(contents) != member.file_size or len(contents) > limit:
        raise PackagedPinError(f"{label} is truncated or exceeds its size bound")
    return contents


def _validate_wheel_record(
    contents: bytes,
    archive_members: set[str],
    record_name: str,
    pin_contents: bytes,
) -> None:
    seen: set[str] = set()
    portable_seen: set[str] = set()
    pin_row: tuple[str, str] | None = None
    try:
        text = contents.decode("utf-8")
        for row in csv.reader(io.StringIO(text, newline=""), strict=True):
            if len(row) != 3:
                raise PackagedPinError("wheel RECORD rows must have exactly three fields")
            name, recorded_hash, recorded_size = row
            location = _member_location(name, "wheel RECORD")
            portable_key = _portable_member_key(location, "wheel RECORD")
            if name in seen:
                raise PackagedPinError("wheel RECORD contains a duplicate member reference")
            if portable_key in portable_seen:
                raise PackagedPinError(
                    "wheel RECORD contains portable-path-colliding member references"
                )
            if name not in archive_members:
                raise PackagedPinError("wheel RECORD refers to a missing archive member")
            seen.add(name)
            portable_seen.add(portable_key)
            if name == record_name:
                if recorded_hash or recorded_size:
                    raise PackagedPinError("wheel RECORD own row must omit hash and size")
            elif name == WHEEL_PIN:
                pin_row = recorded_hash, recorded_size
    except (UnicodeError, csv.Error) as error:
        raise PackagedPinError("wheel RECORD must be well-formed UTF-8 CSV") from error
    if seen != archive_members:
        raise PackagedPinError("wheel RECORD does not cover every archive member exactly once")
    if pin_row is None:
        raise PackagedPinError("wheel RECORD is missing the dependency-pin entry")
    digest = base64.urlsafe_b64encode(hashlib.sha256(pin_contents).digest())
    expected_hash = "sha256=" + digest.rstrip(b"=").decode("ascii")
    if pin_row[0] != expected_hash or pin_row[1] != str(len(pin_contents)):
        raise PackagedPinError("wheel RECORD does not bind the dependency-pin bytes")


def _wheel_pin(wheel: Path, version: str) -> bytes:
    seen: set[str] = set()
    portable_seen: set[str] = set()
    pin: zipfile.ZipInfo | None = None
    record: zipfile.ZipInfo | None = None
    total_size = 0
    expected_record = f"ordinatics-{version}.dist-info/RECORD"
    try:
        with zipfile.ZipFile(wheel) as archive:
            members = archive.infolist()
            if len(members) > MAX_MEMBERS:
                raise PackagedPinError("wheel contains too many archive members")
            for member in members:
                location = _member_location(member.orig_filename, "wheel")
                portable_key = _portable_member_key(location, "wheel")
                if location in seen:
                    raise PackagedPinError("wheel contains duplicate or conflicting member paths")
                if portable_key in portable_seen:
                    raise PackagedPinError(
                        "wheel contains portable-path-colliding member paths"
                    )
                seen.add(location)
                portable_seen.add(portable_key)
                mode = member.external_attr >> 16
                file_type = stat.S_IFMT(mode)
                if member.is_dir() or stat.S_ISDIR(mode):
                    raise PackagedPinError("wheel contains an explicit directory member")
                if stat.S_ISLNK(mode) or file_type not in (0, stat.S_IFREG):
                    raise PackagedPinError("wheel contains a non-regular archive member")
                if member.flag_bits & 0x1:
                    raise PackagedPinError("wheel contains an encrypted archive member")
                total_size += member.file_size
                if member.file_size < 0 or total_size > MAX_UNPACKED_BYTES:
                    raise PackagedPinError("wheel exceeds the bounded unpacked size")
                if location == WHEEL_PIN:
                    pin = member
                if location.endswith(".dist-info/RECORD"):
                    if location != expected_record or record is not None:
                        raise PackagedPinError(
                            "wheel contains an unexpected or duplicate RECORD manifest"
                        )
                    record = member
            if pin is None:
                raise PackagedPinError("wheel is missing its packaged dependency pin")
            if record is None:
                raise PackagedPinError("wheel is missing its expected RECORD manifest")
            pin_contents = _read_zip_member(
                archive, pin, MAX_PIN_BYTES, "wheel dependency pin"
            )
            record_contents = _read_zip_member(
                archive, record, MAX_RECORD_BYTES, "wheel RECORD manifest"
            )
    except PackagedPinError:
        raise
    except (OSError, EOFError, KeyError, RuntimeError, NotImplementedError, zipfile.BadZipFile) as error:
        raise PackagedPinError(f"cannot read wheel archive: {error}") from error
    _validate_wheel_record(record_contents, seen, expected_record, pin_contents)
    return pin_contents


def _source_distribution_pin(source_distribution: Path, root_name: str) -> bytes:
    target_name = f"{root_name}/verification/hypermath.json"
    seen: set[str] = set()
    portable_seen: set[str] = set()
    roots: set[str] = set()
    target: tarfile.TarInfo | None = None
    total_size = 0
    try:
        with tarfile.open(source_distribution, mode="r:gz") as archive:
            members = archive.getmembers()
            if len(members) > MAX_MEMBERS:
                raise PackagedPinError("source distribution contains too many archive members")
            for member in members:
                location = _member_location(member.name, "source distribution")
                portable_key = _portable_member_key(location, "source distribution")
                if location in seen:
                    raise PackagedPinError(
                        "source distribution contains duplicate or conflicting member paths"
                    )
                if portable_key in portable_seen:
                    raise PackagedPinError(
                        "source distribution contains portable-path-colliding member paths"
                    )
                seen.add(location)
                portable_seen.add(portable_key)
                roots.add(location.split("/", 1)[0])
                if not member.isfile() and not member.isdir():
                    raise PackagedPinError(
                        "source distribution contains a non-regular archive member"
                    )
                total_size += member.size
                if member.size < 0 or total_size > MAX_UNPACKED_BYTES:
                    raise PackagedPinError(
                        "source distribution exceeds the bounded unpacked size"
                    )
                if location == target_name:
                    if not member.isfile():
                        raise PackagedPinError(
                            "source-distribution dependency pin must be a regular file"
                        )
                    target = member
            if roots != {root_name}:
                raise PackagedPinError(
                    "source distribution must contain one filename-bound top-level directory"
                )
            if target is None:
                raise PackagedPinError(
                    "source distribution is missing its packaged dependency pin"
                )
            if target.size > MAX_PIN_BYTES:
                raise PackagedPinError(
                    "source-distribution dependency pin exceeds the bounded pin size"
                )
            stream = archive.extractfile(target)
            if stream is None:
                raise PackagedPinError("cannot read source-distribution dependency pin")
            with stream:
                contents = stream.read(MAX_PIN_BYTES + 1)
    except PackagedPinError:
        raise
    except (OSError, EOFError, KeyError, tarfile.TarError) as error:
        raise PackagedPinError(f"cannot read source-distribution archive: {error}") from error
    if len(contents) != target.size or len(contents) > MAX_PIN_BYTES:
        raise PackagedPinError(
            "source-distribution dependency pin is truncated or exceeds its size bound"
        )
    return contents


def check_packaged_pin(lock: Path, distribution_directory: Path) -> CheckedArtifacts:
    """Require both built artifacts to retain the validated source dependency lock."""
    source_contents, identity = _read_source_lock(lock)
    wheel, source_distribution = _artifact_files(distribution_directory)
    wheel_version, source_root = _artifact_versions(wheel, source_distribution)
    wheel_contents = _wheel_pin(wheel, wheel_version)
    source_distribution_contents = _source_distribution_pin(source_distribution, source_root)
    _check_packaged_contents(
        wheel_contents, source_contents, identity, "wheel dependency pin"
    )
    _check_packaged_contents(
        source_distribution_contents,
        source_contents,
        identity,
        "source-distribution dependency pin",
    )
    return CheckedArtifacts(wheel, source_distribution, identity)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--lock",
        type=Path,
        default=PROJECT_ROOT / "verification" / "hypermath.json",
    )
    parser.add_argument("--dist", type=Path, default=PROJECT_ROOT / "dist")
    arguments = parser.parse_args(argv)
    try:
        checked = check_packaged_pin(arguments.lock, arguments.dist)
    except PackagedPinError as error:
        print(f"Packaged dependency pin rejected: {error}", file=sys.stderr, flush=True)
        return 2
    identity = checked.identity
    print(
        "Packaged dependency pin retained: "
        f"repository={identity.repository} distribution={identity.distribution} "
        f"version={identity.version} commit={identity.commit}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

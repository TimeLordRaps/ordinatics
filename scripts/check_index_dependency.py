"""Compare an index wheel with the foundation wheel qualified in continuous integration.

Only a separately validated RECORD manifest and the nonsemantic WHEEL Generator
header may differ. ZIP compression and timestamps are container properties; every
named payload member is compared after decompression. Explicit archive directory
entries are unsupported. This checks artifact identity,
not mathematical proof status. The checker requires only Python's standard library.
"""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import io
import re
import stat
import sys
import zipfile
from email import policy
from email.parser import BytesParser
from pathlib import Path

DISTRIBUTION = "hypermath-foundations"
VERSION = "0.1.0"
DIST_INFO = "hypermath_foundations-0.1.0.dist-info"
MAX_MEMBER_BYTES = 32 * 1024 * 1024
MAX_WHEEL_BYTES = 128 * 1024 * 1024


class WheelQualificationError(ValueError):
    """The published artifact does not match the qualified dependency."""


def _one_wheel(directory: Path) -> Path:
    if not directory.is_dir():
        raise WheelQualificationError("wheel directory is missing")
    wheels = [path for path in directory.glob("*.whl") if path.is_file()]
    if len(wheels) != 1:
        raise WheelQualificationError("each directory must contain exactly one .whl file")
    wheel = wheels[0]
    if wheel.is_symlink():
        raise WheelQualificationError("wheel must be a regular file, not a symbolic link")
    parts = wheel.name.removesuffix(".whl").split("-")
    name = re.sub(r"[-_.]+", "-", parts[0]).lower()
    if len(parts) not in (5, 6) or name != DISTRIBUTION or parts[1] != VERSION:
        raise WheelQualificationError("wheel filename must identify hypermath-foundations 0.1.0")
    return wheel


def _safe_member_path(name: str) -> None:
    if (
        not name or "\\" in name or ":" in name
        or any(ord(character) < 32 for character in name)
        or any(part in ("", ".", "..") for part in name.removesuffix("/").split("/"))
    ):
        raise WheelQualificationError("wheel contains an unsafe or noncanonical member path")
    if name.endswith("/"):
        raise WheelQualificationError("explicit wheel directory entries are not supported")


def _member_name(member: zipfile.ZipInfo) -> str:
    name = member.orig_filename
    _safe_member_path(name)
    mode = member.external_attr >> 16
    if stat.S_ISLNK(mode):
        raise WheelQualificationError("wheel contains a symbolic-link payload")
    if stat.S_ISDIR(mode):
        raise WheelQualificationError("explicit wheel directory entries are not supported")
    return name


def _without_generator(contents: bytes) -> bytes:
    """Remove only Generator headers and their folded continuations, verbatim.

    Every other header, line ending, ordering choice and body byte is retained.
    A Generator-looking line in the body is not a header and is not removed.
    """
    output = []
    in_headers, skip = True, False
    for line in contents.splitlines(keepends=True):
        if in_headers and line in (b"\n", b"\r\n"):
            in_headers, skip = False, False
        if in_headers:
            if line.startswith((b" ", b"\t")):
                if skip:
                    continue
            else:
                skip = line.partition(b":")[0].lower() == b"generator"
                if skip:
                    continue
        output.append(line)
    return b"".join(output)


def _validate_record(payload: dict[str, bytes], record_name: str) -> None:
    """Validate ownership paths and original bytes before ignoring row ordering.

    Every archive member occurs exactly once. Only RECORD's own row has empty
    hash and size fields. Hashes use unpadded URL-safe SHA-256, and sizes are
    canonical decimal byte counts. WHEEL is hashed before Generator removal.
    """
    seen = set()
    try:
        text = payload[record_name].decode("utf-8")
        for row in csv.reader(io.StringIO(text, newline=""), strict=True):
            if len(row) != 3:
                raise WheelQualificationError("each RECORD row must have exactly three fields")
            name, recorded_hash, recorded_size = row
            _safe_member_path(name)
            if name in seen:
                raise WheelQualificationError("RECORD contains a duplicate member reference")
            seen.add(name)
            if name not in payload:
                raise WheelQualificationError("RECORD path is not an archive member")
            if name == record_name:
                if recorded_hash or recorded_size:
                    raise WheelQualificationError("only the own RECORD row must have empty hash and size")
                continue
            contents = payload[name]
            expected_hash = "sha256=" + base64.urlsafe_b64encode(
                hashlib.sha256(contents).digest(),
            ).rstrip(b"=").decode("ascii")
            if recorded_hash != expected_hash:
                raise WheelQualificationError("RECORD hash does not match its archive member")
            if recorded_size != str(len(contents)):
                raise WheelQualificationError("RECORD size does not match its archive member")
    except (UnicodeError, csv.Error) as error:
        raise WheelQualificationError("RECORD must be well-formed UTF-8 CSV") from error
    if seen != payload.keys():
        raise WheelQualificationError("RECORD is missing archive member entries")


def _payload(wheel: Path) -> dict[str, bytes]:
    payload: dict[str, bytes] = {}
    locations = set()
    total = 0
    try:
        with zipfile.ZipFile(wheel) as archive:
            members = archive.infolist()
            if len(members) > 10_000:
                raise WheelQualificationError("wheel has too many payload members")
            for member in members:
                name = _member_name(member)
                location = name.removesuffix("/")
                if location in locations:
                    raise WheelQualificationError("wheel contains duplicate or conflicting member paths")
                locations.add(location)
                if member.file_size > MAX_MEMBER_BYTES:
                    raise WheelQualificationError("wheel member exceeds the bounded comparison size")
                with archive.open(member) as stream:
                    contents = stream.read(MAX_MEMBER_BYTES + 1)
                total += len(contents)
                if len(contents) > MAX_MEMBER_BYTES or total > MAX_WHEEL_BYTES:
                    raise WheelQualificationError("wheel exceeds the bounded comparison size")
                payload[name] = contents
    except (OSError, zipfile.BadZipFile, RuntimeError, NotImplementedError) as error:
        raise WheelQualificationError(f"cannot read wheel payload: {error}") from error
    metadata_name = f"{DIST_INFO}/METADATA"
    wheel_name = f"{DIST_INFO}/WHEEL"
    record_name = f"{DIST_INFO}/RECORD"
    metadata_paths = [name for name in payload if name.endswith(".dist-info/METADATA")]
    if metadata_paths != [metadata_name] or wheel_name not in payload or record_name not in payload:
        raise WheelQualificationError("wheel must contain the single expected distribution metadata set")
    metadata = BytesParser(policy=policy.default).parsebytes(payload[metadata_name])
    if metadata.defects or len(metadata.get_all("Name", [])) != 1 or len(metadata.get_all("Version", [])) != 1:
        raise WheelQualificationError("wheel distribution metadata is malformed or ambiguous")
    name = re.sub(r"[-_.]+", "-", str(metadata["Name"])).lower()
    if name != DISTRIBUTION or str(metadata["Version"]) != VERSION:
        raise WheelQualificationError("wheel metadata must identify hypermath-foundations 0.1.0")
    _validate_record(payload, record_name)
    del payload[record_name]
    payload[wheel_name] = _without_generator(payload[wheel_name])
    return payload


def compare_wheels(qualified: Path, published: Path) -> tuple[Path, Path]:
    """Require one correctly identified wheel per directory and equal payloads."""
    reference, candidate = _one_wheel(qualified), _one_wheel(published)
    expected, actual = _payload(reference), _payload(candidate)
    if expected.keys() != actual.keys():
        raise WheelQualificationError("published wheel added or removed qualified payload members")
    changed = sorted(name for name in expected if expected[name] != actual[name])
    if changed:
        raise WheelQualificationError(f"published wheel changed qualified payload: {', '.join(changed[:5])}")
    return reference, candidate


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qualified", type=Path, required=True)
    parser.add_argument("--published", type=Path, required=True)
    arguments = parser.parse_args(argv)
    try:
        compare_wheels(arguments.qualified, arguments.published)
    except WheelQualificationError as error:
        print(f"Foundation wheel rejected: {error}", file=sys.stderr, flush=True)
        return 2
    print("Published foundation wheel payload matches the qualified artifact.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

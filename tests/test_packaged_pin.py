"""Built distributions must retain the exact reviewed Hypermath dependency pin."""

import base64
import csv
import hashlib
import importlib.util
import io
import json
import stat
import tarfile
import zipfile
from pathlib import Path

import pytest

CHECKER_PATH = Path(__file__).resolve().parents[1] / "scripts" / "check_packaged_pin.py"
SPEC = importlib.util.spec_from_file_location("packaged_pin_checker", CHECKER_PATH)
assert SPEC is not None and SPEC.loader is not None
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)

COMMIT = "6b050fc292ca2e9fc3169dce70388e3b79431bea"
PIN = {
    "schema_version": 1,
    "repository": "https://github.com/TimeLordRaps/hypermath.git",
    "commit": COMMIT,
    "distribution": "hypermath-foundations",
    "version": "0.1.0",
}
WHEEL_NAME = "ordinatics-0.2.0.dev0-py3-none-any.whl"
WHEEL_RECORD = "ordinatics-0.2.0.dev0.dist-info/RECORD"
SOURCE_NAME = "ordinatics-0.2.0.dev0.tar.gz"
SOURCE_ROOT = "ordinatics-0.2.0.dev0"


def encoded_pin(data=PIN):
    return (json.dumps(data, indent=2) + "\n").encode("utf-8")


def record_bytes(members):
    rows = []
    for name, contents in dict(members).items():
        digest = base64.urlsafe_b64encode(hashlib.sha256(contents).digest())
        rows.append([name, "sha256=" + digest.rstrip(b"=").decode("ascii"), str(len(contents))])
    rows.append([WHEEL_RECORD, "", ""])
    stream = io.StringIO(newline="")
    csv.writer(stream, lineterminator="\n").writerows(rows)
    return stream.getvalue().encode("utf-8")


def write_wheel(
    directory,
    pin_members=None,
    *,
    filename=WHEEL_NAME,
    extra_members=(),
    record_override=None,
):
    directory.mkdir(exist_ok=True)
    path = directory / filename
    pins = [encoded_pin()] if pin_members is None else pin_members
    members = [("ordinatics/__init__.py", b'__version__ = "0.2.0.dev0"\n')]
    members.extend(("ordinatics/_data/hypermath.json", contents) for contents in pins)
    members.extend(extra_members)
    record = record_bytes(members) if record_override is None else record_override
    with zipfile.ZipFile(path, "w") as archive:
        for name, contents in members:
            archive.writestr(name, contents)
        archive.writestr(WHEEL_RECORD, record)
    return path


def add_tar_member(archive, name, contents=b"", *, kind=tarfile.REGTYPE, linkname=""):
    member = tarfile.TarInfo(name)
    member.type = kind
    member.linkname = linkname
    if kind == tarfile.REGTYPE:
        member.size = len(contents)
        archive.addfile(member, io.BytesIO(contents))
    else:
        archive.addfile(member)


def write_source_distribution(
    directory,
    pin_members=None,
    *,
    filename=SOURCE_NAME,
    root=SOURCE_ROOT,
    extra_members=(),
):
    directory.mkdir(exist_ok=True)
    path = directory / filename
    pins = [encoded_pin()] if pin_members is None else pin_members
    with tarfile.open(path, "w:gz") as archive:
        add_tar_member(archive, f"{root}/PKG-INFO", b"Name: ordinatics\nVersion: 0.2.0.dev0\n")
        for contents in pins:
            add_tar_member(archive, f"{root}/verification/hypermath.json", contents)
        for name, contents, kind, linkname in extra_members:
            add_tar_member(archive, name, contents, kind=kind, linkname=linkname)
    return path


@pytest.fixture
def artifacts(tmp_path):
    lock = tmp_path / "verification" / "hypermath.json"
    lock.parent.mkdir()
    lock.write_bytes(encoded_pin())
    distribution_directory = tmp_path / "dist"
    wheel = write_wheel(distribution_directory)
    source_distribution = write_source_distribution(distribution_directory)
    return lock, distribution_directory, wheel, source_distribution


def replace_artifact_pin(kind, directory, contents):
    if kind == "wheel":
        return write_wheel(directory, [contents])
    return write_source_distribution(directory, [contents])


def test_matching_artifacts_retain_exact_pin_and_cli_reports_identity(artifacts, capsys):
    lock, distribution_directory, wheel, source_distribution = artifacts
    checked = checker.check_packaged_pin(lock, distribution_directory)
    assert checked.wheel == wheel
    assert checked.source_distribution == source_distribution
    assert checked.identity == checker.DependencyIdentity(
        PIN["repository"], PIN["distribution"], PIN["version"], PIN["commit"]
    )
    assert checker.main(["--lock", str(lock), "--dist", str(distribution_directory)]) == 0
    output = capsys.readouterr().out
    assert PIN["repository"] in output
    assert PIN["distribution"] in output
    assert PIN["version"] in output
    assert PIN["commit"] in output


@pytest.mark.parametrize("kind", ["wheel", "source_distribution"])
def test_semantically_equal_but_byte_different_pin_is_rejected(artifacts, kind):
    lock, distribution_directory, _, _ = artifacts
    replace_artifact_pin(kind, distribution_directory, json.dumps(PIN).encode("utf-8"))
    with pytest.raises(checker.PackagedPinError, match="byte-for-byte"):
        checker.check_packaged_pin(lock, distribution_directory)


def test_matching_stale_artifacts_do_not_validate_each_other(artifacts):
    lock, distribution_directory, _, _ = artifacts
    stale = dict(PIN)
    stale["commit"] = "a" * 40
    write_wheel(distribution_directory, [encoded_pin(stale)])
    write_source_distribution(distribution_directory, [encoded_pin(stale)])
    with pytest.raises(checker.PackagedPinError, match="exact source identity"):
        checker.check_packaged_pin(lock, distribution_directory)


@pytest.mark.parametrize("kind", ["wheel", "source_distribution"])
@pytest.mark.parametrize(
    "field,value",
    [
        ("repository", "https://github.com/unrelated/hypermath.git"),
        ("distribution", "hypermath"),
        ("version", "9.0.0"),
        ("commit", "a" * 40),
    ],
)
def test_each_identity_field_must_match_the_source(artifacts, kind, field, value):
    lock, distribution_directory, _, _ = artifacts
    changed = dict(PIN)
    changed[field] = value
    replace_artifact_pin(kind, distribution_directory, encoded_pin(changed))
    with pytest.raises(checker.PackagedPinError, match="canonical|required|exact source identity"):
        checker.check_packaged_pin(lock, distribution_directory)


@pytest.mark.parametrize(
    "kind,pin_members",
    [
        ("wheel", []),
        ("source_distribution", []),
        ("wheel", [encoded_pin(), encoded_pin()]),
        ("source_distribution", [encoded_pin(), encoded_pin()]),
    ],
)
def test_packaged_pin_must_exist_exactly_once(artifacts, kind, pin_members):
    lock, distribution_directory, _, _ = artifacts
    if kind == "wheel":
        if len(pin_members) == 2:
            with pytest.warns(UserWarning, match="Duplicate name"):
                write_wheel(distribution_directory, pin_members)
        else:
            write_wheel(distribution_directory, pin_members)
    else:
        write_source_distribution(distribution_directory, pin_members)
    with pytest.raises(checker.PackagedPinError, match="missing|duplicate"):
        checker.check_packaged_pin(lock, distribution_directory)


@pytest.mark.parametrize("kind", ["wheel", "source_distribution"])
def test_unsafe_archive_member_paths_are_rejected(artifacts, kind):
    lock, distribution_directory, _, _ = artifacts
    if kind == "wheel":
        write_wheel(distribution_directory, extra_members=[("../escape.py", b"unsafe\n")])
    else:
        write_source_distribution(
            distribution_directory,
            extra_members=[
                (f"{SOURCE_ROOT}/../escape.py", b"unsafe\n", tarfile.REGTYPE, ""),
            ],
        )
    with pytest.raises(checker.PackagedPinError, match="unsafe|noncanonical"):
        checker.check_packaged_pin(lock, distribution_directory)


@pytest.mark.parametrize(
    "kind,variant",
    [
        ("wheel", "ordinatics/_data/HYPERMATH.JSON"),
        ("wheel", "ordinatics/_data/hypermath.json."),
        ("source_distribution", f"{SOURCE_ROOT}/verification/HYPERMATH.JSON"),
        ("source_distribution", f"{SOURCE_ROOT}/verification/hypermath.json."),
    ],
)
def test_portable_dependency_pin_path_collisions_are_rejected(artifacts, kind, variant):
    lock, distribution_directory, _, _ = artifacts
    if kind == "wheel":
        write_wheel(distribution_directory, extra_members=[(variant, b"conflict\n")])
    else:
        write_source_distribution(
            distribution_directory,
            extra_members=[(variant, b"conflict\n", tarfile.REGTYPE, "")],
        )
    with pytest.raises(checker.PackagedPinError, match="portable|nonportable"):
        checker.check_packaged_pin(lock, distribution_directory)


@pytest.mark.parametrize("kind", ["wheel", "source_distribution"])
def test_unicode_normalization_path_collisions_are_rejected(artifacts, kind):
    lock, distribution_directory, _, _ = artifacts
    if kind == "wheel":
        write_wheel(
            distribution_directory,
            extra_members=[("ordinatics/caf\N{LATIN SMALL LETTER E WITH ACUTE}.txt", b"one")],
        )
        with zipfile.ZipFile(distribution_directory / WHEEL_NAME, "a") as archive:
            archive.writestr("ordinatics/cafe\N{COMBINING ACUTE ACCENT}.txt", b"two")
    else:
        write_source_distribution(
            distribution_directory,
            extra_members=[
                (
                    f"{SOURCE_ROOT}/caf\N{LATIN SMALL LETTER E WITH ACUTE}.txt",
                    b"one",
                    tarfile.REGTYPE,
                    "",
                ),
                (
                    f"{SOURCE_ROOT}/cafe\N{COMBINING ACUTE ACCENT}.txt",
                    b"two",
                    tarfile.REGTYPE,
                    "",
                ),
            ],
        )
    with pytest.raises(checker.PackagedPinError, match="portable-path-colliding"):
        checker.check_packaged_pin(lock, distribution_directory)


def test_wheel_symbolic_link_member_is_rejected(artifacts):
    lock, distribution_directory, wheel, _ = artifacts
    link = zipfile.ZipInfo("ordinatics/link")
    link.create_system = 3
    link.external_attr = (stat.S_IFLNK | 0o777) << 16
    with zipfile.ZipFile(wheel, "a") as archive:
        archive.writestr(link, "../outside")
    with pytest.raises(checker.PackagedPinError, match="non-regular"):
        checker.check_packaged_pin(lock, distribution_directory)


@pytest.mark.parametrize("link_kind", [tarfile.SYMTYPE, tarfile.LNKTYPE])
def test_source_distribution_link_member_is_rejected(artifacts, link_kind):
    lock, distribution_directory, _, _ = artifacts
    write_source_distribution(
        distribution_directory,
        extra_members=[
            (f"{SOURCE_ROOT}/link", b"", link_kind, f"{SOURCE_ROOT}/PKG-INFO"),
        ],
    )
    with pytest.raises(checker.PackagedPinError, match="non-regular"):
        checker.check_packaged_pin(lock, distribution_directory)


@pytest.mark.parametrize(
    "kind,duplicate",
    [("wheel", False), ("wheel", True), ("source", False), ("source", True)],
)
def test_exactly_one_artifact_of_each_kind_is_required(artifacts, kind, duplicate):
    lock, distribution_directory, wheel, source_distribution = artifacts
    target = wheel if kind == "wheel" else source_distribution
    if duplicate:
        if kind == "wheel":
            write_wheel(
                distribution_directory,
                filename="ordinatics-0.2.0.dev0-1-py3-none-any.whl",
            )
        else:
            write_source_distribution(
                distribution_directory,
                filename="ordinatics-9.0.0.tar.gz",
                root="ordinatics-9.0.0",
            )
    else:
        target.unlink()
    with pytest.raises(checker.PackagedPinError, match="exactly one"):
        checker.check_packaged_pin(lock, distribution_directory)


def test_unexpected_distribution_entry_is_rejected(artifacts):
    lock, distribution_directory, _, _ = artifacts
    (distribution_directory / "unexpected.txt").write_text("not qualified\n", encoding="utf-8")
    with pytest.raises(checker.PackagedPinError, match="unexpected entry"):
        checker.check_packaged_pin(lock, distribution_directory)


@pytest.mark.parametrize("kind", ["wheel", "source_distribution"])
def test_malformed_archives_are_rejected(artifacts, kind):
    lock, distribution_directory, wheel, source_distribution = artifacts
    target = wheel if kind == "wheel" else source_distribution
    target.write_bytes(b"not an archive")
    with pytest.raises(checker.PackagedPinError, match="cannot read"):
        checker.check_packaged_pin(lock, distribution_directory)


@pytest.mark.parametrize(
    "source_contents",
    [
        b"{",
        encoded_pin().replace(b"{\n", b'{\n  "schema_version": 1,\n', 1),
        encoded_pin({**PIN, "commit": "A" * 40}),
    ],
)
def test_source_lock_must_be_unambiguous_and_exact(artifacts, source_contents):
    lock, distribution_directory, _, _ = artifacts
    lock.write_bytes(source_contents)
    with pytest.raises(checker.PackagedPinError, match="unambiguous|duplicate|lowercase"):
        checker.check_packaged_pin(lock, distribution_directory)


@pytest.mark.parametrize(
    "kind,contents",
    [
        ("wheel", b"{"),
        (
            "source_distribution",
            encoded_pin().replace(b"{\n", b'{\n  "schema_version": 1,\n', 1),
        ),
    ],
)
def test_packaged_pin_must_be_unambiguous_json(artifacts, kind, contents):
    lock, distribution_directory, _, _ = artifacts
    replace_artifact_pin(kind, distribution_directory, contents)
    with pytest.raises(checker.PackagedPinError, match="unambiguous|duplicate"):
        checker.check_packaged_pin(lock, distribution_directory)


def test_wheel_record_must_bind_the_dependency_pin(artifacts):
    lock, distribution_directory, _, _ = artifacts
    members = [
        ("ordinatics/__init__.py", b'__version__ = "0.2.0.dev0"\n'),
        ("ordinatics/_data/hypermath.json", encoded_pin()),
    ]
    stale_record = record_bytes(members).replace(
        f",{len(encoded_pin())}\n".encode(), b",999\n"
    )
    write_wheel(distribution_directory, record_override=stale_record)
    with pytest.raises(checker.PackagedPinError, match="RECORD does not bind"):
        checker.check_packaged_pin(lock, distribution_directory)


def test_wheel_and_source_distribution_versions_must_match(artifacts):
    lock, distribution_directory, _, source_distribution = artifacts
    source_distribution.unlink()
    write_source_distribution(
        distribution_directory,
        filename="ordinatics-9.0.0.tar.gz",
        root="ordinatics-9.0.0",
    )
    with pytest.raises(checker.PackagedPinError, match="versions do not match"):
        checker.check_packaged_pin(lock, distribution_directory)


def test_cli_rejects_tampered_artifact_with_nonzero_result(artifacts, capsys):
    lock, distribution_directory, _, _ = artifacts
    changed = dict(PIN)
    changed["commit"] = "a" * 40
    write_wheel(distribution_directory, [encoded_pin(changed)])
    assert checker.main(["--lock", str(lock), "--dist", str(distribution_directory)]) == 2
    assert "rejected" in capsys.readouterr().err

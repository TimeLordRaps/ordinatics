"""Published dependency identity must match the qualified wheel's full payload."""

import base64
import csv
import hashlib
import importlib.util
import io
import zipfile
from pathlib import Path

import pytest

CHECKER_PATH = Path(__file__).resolve().parents[1] / "scripts" / "check_index_dependency.py"
SPEC = importlib.util.spec_from_file_location("index_dependency_checker", CHECKER_PATH)
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)

DIST_INFO = "hypermath_foundations-0.1.0.dist-info"
WHEEL_NAME = "hypermath_foundations-0.1.0-py3-none-any.whl"
RECORD_NAME = f"{DIST_INFO}/RECORD"


def payload():
    return {
        "hypermath_foundations/__init__.py": b"VERSION = '0.1.0'\n",
        "hypermath_foundations/_baseline.py": b"ALLOWED_AXIOMS = ('reviewed',)\n",
        f"{DIST_INFO}/METADATA": b"Metadata-Version: 2.4\nName: hypermath-foundations\nVersion: 0.1.0\n\nDescription\n",
        f"{DIST_INFO}/WHEEL": b"Wheel-Version: 1.0\nGenerator: original\nRoot-Is-Purelib: true\nTag: py3-none-any\n\n",
        f"{DIST_INFO}/entry_points.txt": b"[console_scripts]\nhypermath-foundations = hypermath_foundations.__main__:main\n",
        f"{DIST_INFO}/licenses/LICENSE": b"MIT license fixture\n",
        f"{DIST_INFO}/RECORD": b"record fixture\n",
    }


def record_bytes(members, *, reverse=False):
    rows = []
    for name, contents in members.items():
        if name != RECORD_NAME:
            digest = base64.urlsafe_b64encode(hashlib.sha256(contents).digest()).rstrip(b"=").decode("ascii")
            rows.append([name, f"sha256={digest}", str(len(contents))])
    rows.append([RECORD_NAME, "", ""])
    if reverse:
        rows.reverse()
    return rows_bytes(rows)


def rows_bytes(rows):
    stream = io.StringIO(newline="")
    csv.writer(stream, lineterminator="\n").writerows(rows)
    return stream.getvalue().encode("utf-8")


def write_wheel(directory, members, *, filename=WHEEL_NAME, compression=zipfile.ZIP_STORED, record=None):
    members = dict(members)
    members[RECORD_NAME] = record_bytes(members) if record is None else record
    directory.mkdir(exist_ok=True)
    path = directory / filename
    with zipfile.ZipFile(path, "w", compression=compression) as archive:
        for name, contents in members.items():
            if "\\" in name:
                # Bypass the writer's Windows path normalization so this test
                # models an archive that actually contains a raw backslash.
                member = zipfile.ZipInfo("raw-name")
                member.filename = member.orig_filename = name
                archive.writestr(member, contents, compress_type=compression)
            else:
                archive.writestr(name, contents)
    return path


@pytest.fixture
def pair(tmp_path):
    qualified, published = tmp_path / "qualified", tmp_path / "published"
    write_wheel(qualified, payload())
    write_wheel(published, payload())
    return qualified, published


def test_fresh_matching_wheels_pass_without_importing_foundation(pair):
    qualified, published = pair
    assert checker.compare_wheels(qualified, published) == (qualified / WHEEL_NAME, published / WHEEL_NAME)
    assert checker.main(["--qualified", str(qualified), "--published", str(published)]) == 0


def test_record_generator_and_zip_compression_may_differ(pair):
    qualified, published = pair
    members = payload()
    members[f"{DIST_INFO}/WHEEL"] = members[f"{DIST_INFO}/WHEEL"].replace(
        b"Generator: original\n", b"Generator: another builder\n continued version\n",
    )
    write_wheel(published, members, compression=zipfile.ZIP_DEFLATED,
                record=record_bytes(members, reverse=True))
    checker.compare_wheels(qualified, published)


def test_metadata_line_endings_may_differ_with_valid_raw_record(pair):
    qualified, published = pair
    members = payload()
    members[f"{DIST_INFO}/METADATA"] = members[f"{DIST_INFO}/METADATA"].replace(b"\n", b"\r\n")
    write_wheel(published, members)
    checker.compare_wheels(qualified, published)


def test_metadata_line_ending_normalization_cannot_hide_invalid_raw_record(pair):
    qualified, published = pair
    members = payload()
    stale_record = record_bytes(members)
    members[f"{DIST_INFO}/METADATA"] = members[f"{DIST_INFO}/METADATA"].replace(b"\n", b"\r\n")
    write_wheel(published, members, record=stale_record)
    with pytest.raises(checker.WheelQualificationError, match="RECORD hash"):
        checker.compare_wheels(qualified, published)


def test_semantic_metadata_change_is_rejected_after_line_ending_normalization(pair):
    qualified, published = pair
    members = payload()
    members[f"{DIST_INFO}/METADATA"] = members[f"{DIST_INFO}/METADATA"].replace(
        b"Description", b"Changed description",
    ).replace(b"\n", b"\r\n")
    write_wheel(published, members)
    with pytest.raises(checker.WheelQualificationError, match="METADATA"):
        checker.compare_wheels(qualified, published)


def test_source_line_endings_are_not_normalized(pair):
    qualified, published = pair
    members = payload()
    name = "hypermath_foundations/_baseline.py"
    members[name] = members[name].replace(b"\n", b"\r\n")
    write_wheel(published, members)
    with pytest.raises(checker.WheelQualificationError, match="_baseline.py"):
        checker.compare_wheels(qualified, published)


@pytest.mark.parametrize("name", [
    "hypermath_foundations/__init__.py", "hypermath_foundations/_baseline.py",
    f"{DIST_INFO}/METADATA", f"{DIST_INFO}/entry_points.txt", f"{DIST_INFO}/licenses/LICENSE",
])
def test_changed_code_policy_metadata_entrypoints_or_license_is_rejected(pair, name):
    qualified, published = pair
    members = payload()
    members[name] += b"changed payload\n"
    write_wheel(published, members)
    with pytest.raises(checker.WheelQualificationError, match="changed qualified payload"):
        checker.compare_wheels(qualified, published)


def test_semantic_wheel_header_change_is_rejected(pair):
    qualified, published = pair
    members = payload()
    members[f"{DIST_INFO}/WHEEL"] = members[f"{DIST_INFO}/WHEEL"].replace(b"Tag: py3-none-any", b"Tag: py2-none-any")
    write_wheel(published, members)
    with pytest.raises(checker.WheelQualificationError, match="WHEEL"):
        checker.compare_wheels(qualified, published)


def test_generator_text_in_wheel_body_is_not_ignored(pair):
    qualified, published = pair
    members = payload()
    members[f"{DIST_INFO}/WHEEL"] += b"Generator: body text is payload\n"
    write_wheel(published, members)
    with pytest.raises(checker.WheelQualificationError, match="WHEEL"):
        checker.compare_wheels(qualified, published)


@pytest.mark.parametrize("change", ["added", "removed"])
def test_added_or_removed_payload_is_rejected(pair, change):
    qualified, published = pair
    members = payload()
    if change == "added":
        members["hypermath_foundations/extra.py"] = b"unexpected code\n"
    else:
        del members[f"{DIST_INFO}/licenses/LICENSE"]
    write_wheel(published, members)
    with pytest.raises(checker.WheelQualificationError, match="added or removed"):
        checker.compare_wheels(qualified, published)


@pytest.mark.parametrize("field,replacement", [(b"Version: 0.1.0", b"Version: 9.0.0"), (b"Name: hypermath-foundations", b"Name: unrelated")])
def test_wrong_distribution_identity_is_rejected_even_when_both_wheels_match(pair, field, replacement):
    qualified, published = pair
    members = payload()
    members[f"{DIST_INFO}/METADATA"] = members[f"{DIST_INFO}/METADATA"].replace(field, replacement)
    write_wheel(qualified, members)
    write_wheel(published, members)
    with pytest.raises(checker.WheelQualificationError, match="metadata must identify"):
        checker.compare_wheels(qualified, published)


def test_duplicate_metadata_identity_is_rejected(pair):
    qualified, published = pair
    members = payload()
    members[f"{DIST_INFO}/METADATA"] = members[f"{DIST_INFO}/METADATA"].replace(b"Version: 0.1.0", b"Version: 0.1.0\nVersion: 9.0.0")
    write_wheel(published, members)
    with pytest.raises(checker.WheelQualificationError, match="ambiguous"):
        checker.compare_wheels(qualified, published)


def test_duplicate_archive_members_are_rejected(pair):
    qualified, published = pair
    with zipfile.ZipFile(published / WHEEL_NAME, "a") as archive:
        with pytest.warns(UserWarning, match="Duplicate name"):
            archive.writestr("hypermath_foundations/_baseline.py", b"second conflicting policy\n")
    with pytest.raises(checker.WheelQualificationError, match="duplicate"):
        checker.compare_wheels(qualified, published)


@pytest.mark.parametrize("path", ["../escape.py", "/absolute.py", "package/../escape.py", "C:/drive.py", "package\\alias.py", "package//alias.py"])
def test_unsafe_archive_member_paths_are_rejected(pair, path):
    qualified, published = pair
    members = payload()
    members[path] = b"unsafe path\n"
    write_wheel(published, members)
    with pytest.raises(checker.WheelQualificationError, match="unsafe|noncanonical"):
        checker.compare_wheels(qualified, published)


def test_exactly_one_wheel_per_directory_is_required(pair):
    qualified, published = pair
    write_wheel(published, payload(), filename="hypermath_foundations-0.1.0-1-py3-none-any.whl")
    with pytest.raises(checker.WheelQualificationError, match="exactly one"):
        checker.compare_wheels(qualified, published)


def test_mismatched_filename_and_metadata_version_is_rejected(tmp_path):
    qualified, published = tmp_path / "qualified", tmp_path / "published"
    for directory in (qualified, published):
        write_wheel(directory, payload(), filename="hypermath_foundations-9.0.0-py3-none-any.whl")
    with pytest.raises(checker.WheelQualificationError, match="filename must identify"):
        checker.compare_wheels(qualified, published)


def test_cli_rejects_tampered_wheel_with_nonzero_result(pair, capsys):
    qualified, published = pair
    members = payload()
    members["hypermath_foundations/_baseline.py"] = b"tampered policy\n"
    write_wheel(published, members)
    assert checker.main(["--qualified", str(qualified), "--published", str(published)]) == 2
    assert "rejected" in capsys.readouterr().err


@pytest.mark.parametrize("side", ["qualified", "published"])
def test_record_cannot_claim_ownership_outside_the_wheel(pair, side):
    qualified, published = pair
    directory = qualified if side == "qualified" else published
    members = payload()
    record = record_bytes(members) + b"../../../other-owned-file,,\n"
    write_wheel(directory, members, record=record)
    with pytest.raises(checker.WheelQualificationError, match="unsafe|noncanonical"):
        checker.compare_wheels(qualified, published)


@pytest.mark.parametrize("mutation,match", [
    ("duplicate", "duplicate"), ("missing", "missing"), ("extra", "not an archive member"),
    ("hash", "hash"), ("size", "size"), ("empty_hash", "hash"),
    ("empty_size", "size"), ("algorithm", "hash"), ("self_hash", "own RECORD"),
    ("self_size", "own RECORD"), ("columns", "three"),
])
def test_record_must_exactly_cover_members_with_valid_hashes_and_sizes(pair, mutation, match):
    qualified, published = pair
    members = payload()
    rows = list(csv.reader(io.StringIO(record_bytes(members).decode("utf-8"))))
    if mutation == "duplicate":
        rows.append(list(rows[0]))
    elif mutation == "missing":
        rows.pop(0)
    elif mutation == "extra":
        rows.append(["unowned.py", "", ""])
    elif mutation == "hash":
        rows[0][1] = "sha256=" + "a" * 43
    elif mutation == "size":
        rows[0][2] = str(int(rows[0][2]) + 1)
    elif mutation == "empty_hash":
        rows[0][1] = ""
    elif mutation == "empty_size":
        rows[0][2] = ""
    elif mutation == "algorithm":
        rows[0][1] = rows[0][1].replace("sha256=", "sha512=")
    elif mutation == "self_hash":
        rows[-1][1] = "sha256=" + "a" * 43
    elif mutation == "self_size":
        rows[-1][2] = "0"
    else:
        rows[0].append("unexpected column")
    write_wheel(published, members, record=rows_bytes(rows))
    with pytest.raises(checker.WheelQualificationError, match=match):
        checker.compare_wheels(qualified, published)


@pytest.mark.parametrize("record", [b'"unterminated', b"\xff\xfe"])
def test_record_requires_well_formed_utf8_csv(pair, record):
    qualified, published = pair
    write_wheel(published, payload(), record=record)
    with pytest.raises(checker.WheelQualificationError, match="RECORD"):
        checker.compare_wheels(qualified, published)


def test_explicit_archive_directory_entries_are_rejected(pair):
    qualified, published = pair
    members = payload()
    members["hypermath_foundations/empty/"] = b""
    write_wheel(published, members)
    with pytest.raises(checker.WheelQualificationError, match="directory"):
        checker.compare_wheels(qualified, published)

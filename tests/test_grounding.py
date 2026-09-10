"""Source-binding and evidence-boundary regressions; not completeness proofs."""

import hashlib
import importlib.util
import json
import subprocess
import sys
import types
import zipfile
from pathlib import Path

import pytest

from ordinatics import (
    GroundingEvidenceError,
    GroundingNotEstablishedError,
    verify_grounding,
)
from ordinatics import _foundation_source as source_checks
from ordinatics import grounding as g
from ordinatics._foundation_source import (
    DISTRIBUTION,
    REPOSITORY,
    VERSION,
    FoundationSourceError,
    read_pin,
    verify_checkout,
)


def git(root, *arguments):
    return subprocess.run(
        ["git", "-C", str(root), *arguments], check=True, capture_output=True,
        text=True, timeout=10,
    ).stdout.strip()


@pytest.fixture
def source(tmp_path):
    # Synthetic local Git history is confined to pytest's temporary directory.
    # These fixtures never commit to, reset, or mutate either working repository.
    root = tmp_path / "foundation"
    root.mkdir()
    package = root / "src" / "hypermath_foundations"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text('"""Fixture package."""\n', encoding="utf-8")
    git(root, "init")
    git(root, "add", ".")
    git(root, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
        "commit", "-m", "Synthetic foundation input")
    git(root, "remote", "add", "origin", REPOSITORY)
    lock = tmp_path / "hypermath.json"
    lock.write_text(json.dumps({
        "schema_version": 1, "repository": REPOSITORY, "commit": git(root, "rev-parse", "HEAD"),
        "distribution": DISTRIBUTION, "version": VERSION,
    }), encoding="utf-8")
    return root, lock


def report_for(lock, *, status="UNKNOWN"):
    pin = read_pin(lock)
    subject = {"repository": REPOSITORY.removesuffix(".git"), "revision": pin.commit, "dirty": False}
    relative = "src/hypermath_foundations/__init__.py"
    digest = hashlib.sha256((lock.parent / "foundation" / relative).read_bytes()).hexdigest()
    return {
        "format": "hypermath-audit-1",
        "subject": dict(subject), "subject_after": dict(subject),
        "inputs": {"before": {relative: digest}, "after": {relative: digest}, "stable": True},
        "target": {"name": "Hypermath.selfDerivation"},
        "claims": {"self_derivation": {"status": status, "reasons": ["fixture"]}},
    }


@pytest.fixture
def audit_boundary(source, monkeypatch):
    root, lock = source
    # These unit tests isolate the Ordinatics boundary from Lean execution.
    # Runtime-byte binding and actual Git behavior have separate tests below.
    monkeypatch.setattr(g, "_verify_runtime", lambda root, pin: None)
    monkeypatch.setattr(g.hypermath_foundations, "run_audit", lambda *a, **k: report_for(lock))
    monkeypatch.setattr(g.hypermath_foundations, "evaluate_gate", lambda *a, **k: False)
    return root, lock


def test_exact_clean_git_pin_is_accepted(source):
    root, lock = source
    pin = read_pin(lock)
    assert verify_checkout(root, pin) == root.resolve()
    assert pin.commit == git(root, "rev-parse", "HEAD")


@pytest.mark.parametrize("flag", ["--assume-unchanged", "--skip-worktree"])
def test_git_index_flags_cannot_hide_changed_foundation_source(source, flag):
    root, lock = source
    relative = "src/hypermath_foundations/__init__.py"
    git(root, "update-index", flag, relative)
    (root / relative).write_text("hidden source change\n", encoding="utf-8")
    assert git(root, "status", "--porcelain=v1") == ""
    with pytest.raises(FoundationSourceError, match="masked|content"):
        verify_checkout(root, read_pin(lock))


def test_actual_content_is_checked_when_git_status_reports_clean(source, monkeypatch):
    root, lock = source
    original = source_checks.git_output

    def cached_status(root, *arguments, **kwargs):
        if arguments[0] == "status":
            return ""
        return original(root, *arguments, **kwargs)

    (root / "src/hypermath_foundations/__init__.py").write_text("changed\n", encoding="utf-8")
    monkeypatch.setattr(source_checks, "git_output", cached_status)
    with pytest.raises(FoundationSourceError, match="tracked content"):
        verify_checkout(root, read_pin(lock))


@pytest.mark.parametrize("key,value", [
    ("commit", "main"), ("commit", "a" * 39), ("commit", "A" * 40),
    ("repository", "https://github.com/unrelated/hypermath.git"),
    ("distribution", "hypermath"), ("version", "9.0.0"), ("schema_version", True),
])
def test_malformed_or_substituted_pin_is_rejected_before_execution(source, key, value):
    _, lock = source
    data = json.loads(lock.read_text(encoding="utf-8"))
    data[key] = value
    lock.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(FoundationSourceError):
        read_pin(lock)


def test_duplicate_lock_fields_are_rejected(source):
    _, lock = source
    text = lock.read_text(encoding="utf-8")
    lock.write_text(text[:-1] + ', "commit": "' + "a" * 40 + '"}', encoding="utf-8")
    with pytest.raises(FoundationSourceError, match="duplicate"):
        read_pin(lock)


@pytest.mark.parametrize("mutation,match", [
    ("remote", "repository"), ("pin", "HEAD"), ("tracked", "dirty"),
    ("untracked", "dirty"), ("subdirectory", "repository root"), ("missing", "missing"),
])
def test_wrong_or_dirty_checkout_is_rejected_without_running_audit(source, monkeypatch, mutation, match):
    root, lock = source
    if mutation == "remote":
        git(root, "remote", "set-url", "origin", "https://github.com/unrelated/project.git")
    elif mutation == "pin":
        data = json.loads(lock.read_text(encoding="utf-8"))
        data["commit"] = "a" * 40
        lock.write_text(json.dumps(data), encoding="utf-8")
    elif mutation == "tracked":
        (root / "src/hypermath_foundations/__init__.py").write_text("changed\n", encoding="utf-8")
    elif mutation == "untracked":
        (root / "additional.lean").write_text("unreviewed\n", encoding="utf-8")
    elif mutation == "subdirectory":
        root = root / "src"
    else:
        root = root / "missing"
    monkeypatch.setattr(g.hypermath_foundations, "run_audit", lambda *a, **k: pytest.fail("audit must not run"))
    with pytest.raises(GroundingEvidenceError, match=match):
        verify_grounding(root, lock_path=lock)


def test_installed_same_version_with_different_python_bytes_is_rejected(source, monkeypatch, tmp_path):
    root, lock = source
    installed = tmp_path / "installed" / "hypermath_foundations"
    installed.mkdir(parents=True)
    module = installed / "__init__.py"
    module.write_text('"""Different same-version runner."""\n', encoding="utf-8")
    monkeypatch.setattr(g.metadata, "version", lambda name: VERSION)
    monkeypatch.setattr(g.hypermath_foundations, "__file__", str(module))
    with pytest.raises(GroundingEvidenceError, match="Python bytes differ"):
        verify_grounding(root, lock_path=lock)


def test_uninstalled_foundation_metadata_is_rejected(source, monkeypatch):
    root, lock = source

    def absent(name):
        raise g.metadata.PackageNotFoundError(name)

    monkeypatch.setattr(g.metadata, "version", absent)
    with pytest.raises(GroundingEvidenceError, match="not installed"):
        verify_grounding(root, lock_path=lock)


def test_source_mutation_during_audit_rejects_returned_pass(audit_boundary, monkeypatch):
    root, lock = audit_boundary

    def mutate(*args, **kwargs):
        (root / "src/hypermath_foundations/__init__.py").write_text("changed\n", encoding="utf-8")
        return report_for(lock, status="PASS")

    monkeypatch.setattr(g.hypermath_foundations, "run_audit", mutate)
    with pytest.raises(GroundingEvidenceError, match="dirty"):
        verify_grounding(root, lock_path=lock)


def test_ignored_audit_input_outside_commit_is_rejected(audit_boundary, monkeypatch):
    root, lock = audit_boundary
    (root / ".git/info/exclude").write_text("Ignored.lean\n", encoding="utf-8")
    (root / "Ignored.lean").write_text("uncommitted proof input\n", encoding="utf-8")
    assert git(root, "status", "--porcelain=v1") == ""
    report = report_for(lock)
    digest = hashlib.sha256((root / "Ignored.lean").read_bytes()).hexdigest()
    report["inputs"]["before"]["Ignored.lean"] = digest
    report["inputs"]["after"]["Ignored.lean"] = digest
    monkeypatch.setattr(g.hypermath_foundations, "run_audit", lambda *a, **k: report)
    with pytest.raises(GroundingEvidenceError, match="not part of the committed"):
        verify_grounding(root, lock_path=lock)


@pytest.mark.parametrize("bad_report", [None, {}, {"format": "unrelated", "status": "PASS"}])
def test_missing_or_unknown_dependency_report_is_rejected(audit_boundary, monkeypatch, bad_report):
    root, lock = audit_boundary
    monkeypatch.setattr(g.hypermath_foundations, "run_audit", lambda *a, **k: bad_report)
    with pytest.raises(GroundingEvidenceError, match="missing|unknown"):
        verify_grounding(root, lock_path=lock)


@pytest.mark.parametrize("mutation", ["revision", "repository", "dirty", "unstable", "inputs", "target", "claim"])
def test_forged_pass_cannot_override_source_binding(audit_boundary, monkeypatch, mutation):
    root, lock = audit_boundary
    report = report_for(lock, status="PASS")
    if mutation == "revision":
        report["subject"]["revision"] = "b" * 40
    elif mutation == "repository":
        report["subject_after"]["repository"] = "https://github.com/unrelated/hypermath"
    elif mutation == "dirty":
        report["subject_after"]["dirty"] = True
    elif mutation == "unstable":
        report["inputs"]["stable"] = False
    elif mutation == "inputs":
        report["inputs"]["after"] = {}
    elif mutation == "target":
        report["target"]["name"] = "Unrelated.trivial"
    else:
        del report["claims"]["self_derivation"]
    monkeypatch.setattr(g.hypermath_foundations, "run_audit", lambda *a, **k: report)
    monkeypatch.setattr(g.hypermath_foundations, "evaluate_gate", lambda *a, **k: True)
    with pytest.raises(GroundingEvidenceError):
        verify_grounding(root, lock_path=lock)


def test_reported_pass_cannot_override_negative_evidence_gate(audit_boundary, monkeypatch):
    root, lock = audit_boundary
    monkeypatch.setattr(g.hypermath_foundations, "run_audit", lambda *a, **k: report_for(lock, status="PASS"))
    result = verify_grounding(root, lock_path=lock)
    assert result.foundation_status == "UNKNOWN"
    assert result.completeness_status == "UNKNOWN"


def test_gate_cannot_promote_a_conflicting_unknown_claim(audit_boundary, monkeypatch):
    root, lock = audit_boundary
    monkeypatch.setattr(g.hypermath_foundations, "evaluate_gate", lambda *a, **k: True)
    with pytest.raises(GroundingEvidenceError, match="contradicts"):
        verify_grounding(root, lock_path=lock)


def test_each_requirement_runs_a_fresh_audit_and_retains_unknown(audit_boundary, monkeypatch):
    root, lock = audit_boundary
    calls = []

    def fresh(*args, **kwargs):
        calls.append(kwargs)
        return report_for(lock)

    monkeypatch.setattr(g.hypermath_foundations, "run_audit", fresh)
    first = verify_grounding(root, lock_path=lock, timeout=17)
    first.report["claims"]["self_derivation"]["status"] = "PASS"
    assert first.report["claims"]["self_derivation"]["status"] == "UNKNOWN"
    with pytest.raises(GroundingNotEstablishedError, match="UNKNOWN") as rejected:
        verify_grounding(root, lock_path=lock, require_grounding=True, timeout=17)
    assert rejected.value.result.foundation_status == "UNKNOWN"
    assert calls == [{"timeout": 17}, {"timeout": 17}]


def test_even_a_future_foundation_pass_does_not_supply_the_arithmetic_bridge(audit_boundary, monkeypatch):
    root, lock = audit_boundary
    monkeypatch.setattr(g.hypermath_foundations, "run_audit", lambda *a, **k: report_for(lock, status="PASS"))
    monkeypatch.setattr(g.hypermath_foundations, "evaluate_gate", lambda *a, **k: True)
    result = verify_grounding(root, lock_path=lock, require_grounding=True)
    assert result.foundation_status == "PASS"
    assert result.completeness_status == "UNKNOWN"
    with pytest.raises(GroundingNotEstablishedError, match="bridge") as rejected:
        verify_grounding(root, lock_path=lock, require_complete=True)
    assert rejected.value.result.to_dict()["bridge_status"] == "UNKNOWN"


def test_api_does_not_accept_precomputed_report(audit_boundary):
    root, lock = audit_boundary
    with pytest.raises(TypeError, match="report"):
        verify_grounding(root, lock_path=lock, report={"status": "PASS"})


def test_receipt_adapter_receives_pinned_root_for_fresh_replay(audit_boundary, monkeypatch, tmp_path):
    root, lock = audit_boundary
    calls = []
    adapter = types.ModuleType("hypermath_foundations.vstd")

    def receipt(report, directory, **kwargs):
        calls.append((report, directory, kwargs))
        directory.mkdir()
        path = directory / "receipt.json"
        path.write_text("{}", encoding="utf-8")
        return path

    adapter.write_verification_receipt = receipt
    monkeypatch.setitem(sys.modules, adapter.__name__, adapter)
    directory = tmp_path / "receipts"
    result = verify_grounding(root, lock_path=lock, receipt_directory=directory, timeout=19)
    assert result.receipt_path == directory / "receipt.json"
    assert result.to_dict()["receipt_path"] == "receipt.json"
    assert str(tmp_path) not in json.dumps(result.to_dict())
    assert calls[0][2] == {"foundation_root": root.resolve(), "timeout": 19}
    assert result.completeness_status == "UNKNOWN"


@pytest.fixture
def bootstrap():
    path = Path(__file__).resolve().parents[1] / "scripts" / "bootstrap_foundation.py"
    spec = importlib.util.spec_from_file_location("test_bootstrap_foundation", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_bootstrap_checkout_only_performs_no_build_or_install(source, bootstrap, monkeypatch):
    root, lock = source
    monkeypatch.setattr(bootstrap, "run", lambda *a, **k: pytest.fail("no mutation expected"))
    assert bootstrap.provision(lock, root, checkout_only=True, timeout=10) == root.resolve()


def test_bootstrap_rejects_dirty_existing_checkout_without_reset(source, bootstrap, monkeypatch):
    root, lock = source
    changed = root / "src/hypermath_foundations/__init__.py"
    changed.write_text("user change\n", encoding="utf-8")
    monkeypatch.setattr(bootstrap, "run", lambda *a, **k: pytest.fail("no mutation expected"))
    with pytest.raises(bootstrap._source.FoundationSourceError, match="dirty"):
        bootstrap.provision(lock, root, checkout_only=False, timeout=10)
    assert changed.read_text(encoding="utf-8") == "user change\n"


@pytest.mark.parametrize("mutation", ["version", "python_bytes", None])
def test_bootstrap_binds_wheel_metadata_and_bytes_before_index_free_install(source, bootstrap, monkeypatch, mutation):
    root, lock = source
    commands = []

    def wheel_or_install(command, **kwargs):
        commands.append(command)
        if "wheel" not in command:
            return
        directory = Path(command[command.index("--wheel-dir") + 1])
        wheel = directory / "hypermath_foundations-0.1.0-py3-none-any.whl"
        version = "9.0.0" if mutation == "version" else VERSION
        contents = (root / "src/hypermath_foundations/__init__.py").read_bytes()
        if mutation == "python_bytes":
            contents = b"changed\n"
        with zipfile.ZipFile(wheel, "w") as archive:
            archive.writestr("hypermath_foundations-0.1.0.dist-info/METADATA",
                             f"Name: {DISTRIBUTION}\nVersion: {version}\n")
            archive.writestr("hypermath_foundations/__init__.py", contents)

    monkeypatch.setattr(bootstrap, "run", wheel_or_install)
    if mutation:
        with pytest.raises(bootstrap._source.FoundationSourceError, match="wheel"):
            bootstrap.provision(lock, root, checkout_only=False, timeout=10)
        assert len(commands) == 1
    else:
        bootstrap.provision(lock, root, checkout_only=False, timeout=10)
        assert len(commands) == 2
        assert "--no-index" in commands[1] and "--no-deps" in commands[1]
        assert commands[1][-1].endswith(".whl")

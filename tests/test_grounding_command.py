"""Integrity command exit statuses; these fixtures are not proof evidence."""

import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest


@pytest.mark.parametrize("policy,strict,expected", [
    ({"status": "FAIL", "attempted": True}, False, 1),
    ({"status": "UNKNOWN", "attempted": True}, False, 1),
    (None, False, 1),
    ({"status": "PASS", "attempted": False}, False, 1),
    ({"status": "PASS", "attempted": True}, False, 0),
    ({"status": "PASS", "attempted": True}, True, 2),
])
def test_grounding_command_requires_policy_pass_but_preserves_unknown(
    tmp_path, monkeypatch, policy, strict, expected,
):
    root = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location(
        "grounding_integrity_command", root / "scripts/check_grounding.py",
    )
    command = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(command)
    report = {
        "toolchain": {"exit_code": 0},
        "execution": {"completed": True},
        "checks": {"proof_admissibility": {"status": "FAIL", "exit_code": None}},
    }
    if policy is not None:
        report["checks"]["assumption_policy"] = policy
    result = SimpleNamespace(
        foundation_status="UNKNOWN", completeness_status="UNKNOWN", report=report,
        to_dict=lambda: {"report": report},
    )
    monkeypatch.setattr(command, "verify_grounding", lambda *a, **k: result)
    output = tmp_path / "evidence"
    argv = ["check_grounding", "--output", str(output)]
    if strict:
        argv.append("--require-complete")
    monkeypatch.setattr(sys, "argv", argv)
    assert command.main() == expected
    assert json.loads((output / "grounding.json").read_text()) == {"report": report}

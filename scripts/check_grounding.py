"""Recompute the pinned foundation and retain evidence before enforcing its gates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ordinatics import verify_grounding


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--foundation-root", type=Path, default=Path(".dependencies/hypermath"))
    parser.add_argument("--output", type=Path, default=Path("build/verification"))
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--require-self-derivation", action="store_true")
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()
    if args.output.exists() and (not args.output.is_dir() or any(args.output.iterdir())):
        parser.error("output must be absent or empty; choose a fresh directory for each audit")
    result = verify_grounding(
        args.foundation_root, timeout=args.timeout,
        receipt_directory=args.output / "vstd",
    )
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "grounding.json").write_text(
        json.dumps(result.to_dict(), sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Hypermath self-derivation: {result.foundation_status}", flush=True)
    print(f"Ordinatics recursive arithmetic completeness: {result.completeness_status}", flush=True)
    report = result.report
    if report["toolchain"].get("exit_code") == 124 or any(
        item.get("exit_code") == 124 for item in report["checks"].values()
    ):
        return 124
    if report["execution"]["completed"] is not True:
        return 1
    if args.require_complete and result.completeness_status != "PASS":
        print("Publication gate is not satisfied: arithmetic bridge or completeness proof missing",
              flush=True)
        return 2
    if args.require_self_derivation and result.foundation_status != "PASS":
        print("Foundation gate is not satisfied: self-derivation remains unresolved", flush=True)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

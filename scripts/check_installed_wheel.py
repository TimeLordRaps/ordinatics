"""Check imports and representative calls from a clean, non-editable wheel install."""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
import venv
from pathlib import Path


def run(command: list[str], *, cwd: Path, timeout: int = 180) -> None:
    print(
        f"START installed-wheel check: {Path(command[0]).name} {' '.join(command[1:3])}",
        flush=True,
    )
    subprocess.run(command, cwd=cwd, check=True, timeout=timeout)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheel-dir", type=Path, default=Path("dist"))
    parser.add_argument(
        "--skip-symbolic",
        action="store_true",
        help="Skip phase 2 SymPy installation and interoperation test",
    )
    args = parser.parse_args()

    wheels = sorted(args.wheel_dir.resolve().glob("*.whl"))
    if len(wheels) != 1:
        raise SystemExit(f"Expected exactly one subject wheel in {args.wheel_dir}, found {len(wheels)}")

    wheel = str(wheels[0])

    with tempfile.TemporaryDirectory(prefix="installed-wheel-ord-") as temporary:
        root = Path(temporary)
        environment = root / "environment"
        venv.EnvBuilder(with_pip=True).create(environment)
        python = environment / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")

        # Phase 1: Pure stdlib --no-deps installation (verifying zero required runtime dependencies)
        run([str(python), "-m", "pip", "install", "--no-deps", wheel], cwd=root)
        run([str(python), "-m", "pip", "check"], cwd=root)

        stdlib_probe = (
            "import importlib, pathlib, sys; "
            "module = importlib.import_module('ordinatics'); "
            "assert pathlib.Path(module.__file__).resolve().is_relative_to("
            "pathlib.Path(sys.prefix).resolve()), 'import did not come from the isolated environment'; "
            "assert 'sympy' not in sys.modules, 'sympy was eagerly imported on pure stdlib path'; "
            "assert 'numpy' not in sys.modules, 'numpy was eagerly imported on pure stdlib path'; "
            "assert 'scipy' not in sys.modules, 'scipy was eagerly imported on pure stdlib path'; "
            "assert 1 + module.OMEGA == module.OMEGA, 'ordinal addition absorption failed'; "
            "assert module.OMEGA + 1 > module.OMEGA, 'ordinal addition ordering failed'; "
            "phi = module.Eq(module.Add(module.Nat(1), module.Nat(1)), module.Nat(2)); "
            "assert module.evaluate(phi) is True, 'semantics evaluation failed'; "
            "d = module.delta(lambda a: 2 * a, 0); "
            "assert d == 2, 'difference operator failed'; "
            "fp = module.find_fixed_point(lambda a: 1 + a, 0); "
            "assert fp == module.OMEGA, 'fixed point search failed'; "
            "print('PASS: zero-dependency installed wheel is importable and usable with pure stdlib')"
        )
        run([str(python), "-I", "-c", stdlib_probe], cwd=root, timeout=30)

        # Phase 2: Interoperability with optional symbolic extra (SymPy)
        if not args.skip_symbolic:
            run([str(python), "-m", "pip", "install", "sympy>=1.13.3,<2"], cwd=root)
            symbolic_probe = (
                "import ordinatics, sympy; "
                "from fractions import Fraction; "
                "assert ordinatics.wrap(ordinatics.X) == Fraction(-1, 2), 'wrap specialization failed'; "
                "p = (ordinatics.OMEGA**2 + 1).to_sympy(); "
                "assert ordinatics.Ordinal.from_sympy(p) == ordinatics.OMEGA**2 + 1; "
                "print('PASS: installed wheel interoperation with SymPy verified')"
            )
            run([str(python), "-I", "-c", symbolic_probe], cwd=root, timeout=30)


if __name__ == "__main__":
    main()

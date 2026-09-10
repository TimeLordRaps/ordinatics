"""Provision the exact reviewed Hypermath source before installing Ordinatics.

This bootstrap uses only Python's standard library and Git until the wheel
build. It never asks the package index to choose a Hypermath distribution.
"""

from __future__ import annotations

import argparse
import importlib.util
import subprocess
import sys
import tempfile
import zipfile
from email.parser import Parser
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
HELPER_PATH = PROJECT_ROOT / "src" / "ordinatics" / "_foundation_source.py"
_spec = importlib.util.spec_from_file_location("_ordinatics_foundation_source", HELPER_PATH)
if _spec is None or _spec.loader is None:
    raise RuntimeError("cannot load the repository's foundation source checker")
_source = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _source
_spec.loader.exec_module(_source)


def run(command: list[str], *, timeout: int) -> None:
    """Stream command output; terminate a hung command at the explicit bound."""
    print("Running:", " ".join(command), flush=True)
    try:
        subprocess.run(command, check=True, timeout=timeout)
    except (OSError, subprocess.SubprocessError) as error:
        raise _source.FoundationSourceError(f"foundation bootstrap command failed: {error}") from error


def provision(lock_path: Path, destination: Path, *, checkout_only: bool, timeout: int) -> Path:
    """Create a missing pinned checkout, or verify an existing one without reset."""
    _source.validate_timeout(timeout)
    pin = _source.read_pin(lock_path)
    destination = destination.resolve()
    if not destination.exists():
        destination.parent.mkdir(parents=True, exist_ok=True)
        run(["git", "init", str(destination)], timeout=timeout)
        run(["git", "-C", str(destination), "remote", "add", "origin", pin.repository], timeout=timeout)
        run(["git", "-C", str(destination), "fetch", "--depth=1", "origin", pin.commit], timeout=timeout)
        run(["git", "-C", str(destination), "checkout", "--detach", pin.commit], timeout=timeout)
    root = _source.verify_checkout(destination, pin, timeout=timeout)
    print(f"Checked clean foundation source: {pin.repository}@{pin.commit}", flush=True)
    if checkout_only:
        return root
    expected_sources = _source.python_sources(root / "src" / "hypermath_foundations")
    # The build directory is outside the checkout, preserving its clean state.
    with tempfile.TemporaryDirectory(prefix="ordinatics-foundation-wheel-") as temporary:
        wheel_directory = Path(temporary).resolve()
        run([
            sys.executable, "-m", "pip", "wheel", "--no-deps", "--wheel-dir",
            str(wheel_directory), str(root),
        ], timeout=timeout)
        _source.verify_checkout(root, pin, timeout=timeout)
        wheels = list(wheel_directory.glob("*.whl"))
        if len(wheels) != 1:
            raise _source.FoundationSourceError("the pinned source must build exactly one wheel")
        wheel = wheels[0]
        with zipfile.ZipFile(wheel) as archive:
            metadata_paths = [name for name in archive.namelist() if name.endswith(".dist-info/METADATA")]
            if len(metadata_paths) != 1:
                raise _source.FoundationSourceError("foundation wheel has ambiguous distribution metadata")
            metadata = Parser().parsestr(archive.read(metadata_paths[0]).decode("utf-8"))
            name = metadata.get("Name", "").replace("_", "-").lower()
            if name != pin.distribution or metadata.get("Version") != pin.version:
                raise _source.FoundationSourceError("built foundation wheel differs from the pinned package")
            prefix = "hypermath_foundations/"
            wheel_sources = {
                name.removeprefix(prefix): _source.hashlib.sha256(archive.read(name)).hexdigest()
                for name in archive.namelist() if name.startswith(prefix) and name.endswith(".py")
            }
            if wheel_sources != expected_sources:
                raise _source.FoundationSourceError("built foundation wheel changed the pinned Python bytes")
        # An explicit wheel path plus no-index prevents fallback to a similarly
        # named project. Base Hypermath uses the standard library; optional
        # verification dependencies are installed with Ordinatics' extras.
        run([
            sys.executable, "-m", "pip", "install", "--no-index", "--no-deps",
            "--force-reinstall", str(wheel),
        ], timeout=timeout)
    _source.verify_checkout(root, pin, timeout=timeout)
    print("Installed the pinned hypermath-foundations wheel; now install Ordinatics and its extras.", flush=True)
    return root


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lock", type=Path, default=PROJECT_ROOT / "verification" / "hypermath.json")
    parser.add_argument("--destination", type=Path, default=PROJECT_ROOT / ".dependencies" / "hypermath")
    parser.add_argument("--checkout-only", action="store_true", help="verify/provision source without building or installing")
    parser.add_argument("--timeout", type=int, default=120, help="timeout in seconds per subprocess")
    arguments = parser.parse_args(argv)
    try:
        provision(arguments.lock, arguments.destination, checkout_only=arguments.checkout_only, timeout=arguments.timeout)
    except _source.FoundationSourceError as error:
        print(f"Foundation bootstrap rejected: {error}", file=sys.stderr, flush=True)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

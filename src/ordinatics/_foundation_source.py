"""Standard-library source pin checks shared with the pre-install bootstrap.

This module must not import Ordinatics or Hypermath. A source coordinate is an
integrity boundary, not a proof of the claims attached to that source.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path

REPOSITORY = "https://github.com/TimeLordRaps/hypermath.git"
DISTRIBUTION = "hypermath-foundations"
VERSION = "0.1.0"


class FoundationSourceError(RuntimeError):
    """The requested dependency cannot be bound to the committed source pin."""


@dataclass(frozen=True)
class FoundationPin:
    """An exact Git dependency coordinate, with an independently named package."""

    repository: str
    commit: str
    distribution: str
    version: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def canonical_repository(value: object) -> str:
    """Accept only equivalent spellings of this project's canonical remote."""
    if value in (
        REPOSITORY,
        REPOSITORY.removesuffix(".git"),
        "git@github.com:TimeLordRaps/hypermath.git",
        "ssh://git@github.com/TimeLordRaps/hypermath.git",
    ):
        return REPOSITORY
    raise FoundationSourceError("foundation repository does not match the pinned Hypermath project")


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise FoundationSourceError(f"duplicate dependency lock key: {key}")
        result[key] = value
    return result


def read_pin(path: Path) -> FoundationPin:
    """Read the reviewed dependency lock, rejecting ambiguous or partial pins."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
    except (OSError, UnicodeError, ValueError) as error:
        raise FoundationSourceError(f"cannot read the foundation dependency lock: {error}") from error
    fields = {"schema_version", "repository", "commit", "distribution", "version"}
    if not isinstance(data, dict) or set(data) != fields:
        raise FoundationSourceError("foundation lock must contain exactly the versioned pin fields")
    if type(data["schema_version"]) is not int or data["schema_version"] != 1:
        raise FoundationSourceError("unsupported foundation dependency lock schema")
    if data["repository"] != REPOSITORY:
        raise FoundationSourceError("foundation lock must name the canonical Hypermath repository")
    commit = data["commit"]
    if not isinstance(commit, str) or re.fullmatch(r"[0-9a-f]{40}", commit) is None:
        raise FoundationSourceError("foundation commit must be a full lowercase 40-digit Git SHA")
    if data["distribution"] != DISTRIBUTION or data["version"] != VERSION:
        raise FoundationSourceError("foundation lock does not match the required distribution/version")
    return FoundationPin(REPOSITORY, commit, DISTRIBUTION, VERSION)


def validate_timeout(timeout: int) -> int:
    if type(timeout) is not int or timeout < 1:
        raise FoundationSourceError("timeout must be a positive integer number of seconds")
    return timeout


def git_output(root: Path, *arguments: str, timeout: int = 60, input_text: str | None = None) -> str:
    """Read a bounded Git result without executing a shell or repository hooks."""
    validate_timeout(timeout)
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *arguments], check=True, text=True,
            encoding="utf-8", errors="replace", capture_output=True, timeout=timeout,
            input=input_text,
        )
    except (OSError, subprocess.SubprocessError) as error:
        raise FoundationSourceError(f"cannot inspect foundation Git checkout: {error}") from error
    return result.stdout.strip()


def verify_checkout(root: Path, pin: FoundationPin, *, timeout: int = 60) -> Path:
    """Require the exact root, origin, commit and clean tracked/untracked inputs.

    Ignored build products are allowed; the audit checks its own input hashes.
    This does not sandbox Git, Lean, or hostile code inside a Python process.
    """
    root = root.resolve()
    if not root.is_dir():
        raise FoundationSourceError("foundation checkout is missing; run bootstrap_foundation.py")
    actual_root = Path(git_output(root, "rev-parse", "--show-toplevel", timeout=timeout)).resolve()
    if actual_root != root:
        raise FoundationSourceError("foundation path must be the repository root, not a subdirectory")
    canonical_repository(git_output(root, "remote", "get-url", "origin", timeout=timeout))
    if git_output(root, "rev-parse", "HEAD", timeout=timeout) != pin.commit:
        raise FoundationSourceError("foundation checkout HEAD differs from the committed dependency pin")
    if git_output(root, "status", "--porcelain=v1", "--untracked-files=all", timeout=timeout):
        raise FoundationSourceError("foundation checkout is dirty; committed clean inputs are required")
    flags = git_output(root, "ls-files", "-v", "-z", timeout=timeout)
    if any(record[0] == "S" or record[0].islower() for record in flags.split("\0") if record):
        raise FoundationSourceError("foundation source must not be masked by Git index flags")
    # Rehash actual files rather than trusting cached file metadata. Git applies
    # the committed text conversion rules, so normal LF/CRLF checkout differences
    # do not look like mathematical source changes. Custom Git filters/tooling
    # remain part of the explicitly trusted local execution environment.
    tree = git_output(root, "ls-tree", "-r", "-z", "HEAD", timeout=timeout)
    paths, expected = [], []
    for record in filter(None, tree.split("\0")):
        header, path = record.split("\t", 1)
        mode, kind, blob = header.split()
        if mode not in ("100644", "100755") or kind != "blob":
            raise FoundationSourceError("foundation source must contain regular files, not links/submodules")
        paths.append(path)
        expected.append(blob)
    if not paths:
        raise FoundationSourceError("foundation source pin contains no tracked files")
    actual = git_output(
        root, "hash-object", "--stdin-paths", timeout=timeout,
        input_text="".join(json.dumps(path, ensure_ascii=False) + "\n" for path in paths),
    ).splitlines()
    if actual != expected:
        raise FoundationSourceError("foundation tracked content differs from the committed dependency pin")
    return root


def python_sources(directory: Path) -> dict[str, str]:
    """Bind package Python bytes without treating cached bytecode as source."""
    if not directory.is_dir():
        raise FoundationSourceError("foundation Python package source is missing")
    result = {}
    for path in sorted(directory.rglob("*.py")):
        if path.is_symlink():
            raise FoundationSourceError("foundation package source must not contain symbolic links")
        result[path.relative_to(directory).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    if "__init__.py" not in result:
        raise FoundationSourceError("foundation package has no Python package initializer")
    return result


def verify_snapshot_paths(root: Path, snapshot: dict, *, timeout: int = 60) -> None:
    """Require audit inputs to belong to HEAD, including ignored source files.

    ``verify_checkout`` already checks committed contents. Installed runner
    entries correspond to the package source whose bytes are checked separately.
    """
    tracked = set(git_output(root, "ls-tree", "-r", "--name-only", "-z", "HEAD", timeout=timeout).split("\0"))
    for path in snapshot:
        if not isinstance(path, str):
            raise FoundationSourceError("foundation audit input paths must be strings")
        native = "src/" + path.removeprefix("runner/") if path.startswith("runner/hypermath_foundations/") else path
        if native not in tracked:
            raise FoundationSourceError("foundation audit input is not part of the committed dependency pin")

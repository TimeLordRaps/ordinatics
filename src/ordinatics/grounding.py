"""Fresh, source-bound verification of the Hypermath foundation dependency.

The dependency is an executable verification surface. Its presence does not
derive this library's arithmetic from the source ground. The source-to-library
bridge and recursively grounded arithmetic completeness remain unestablished.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from importlib import metadata
from pathlib import Path
from typing import Any

import hypermath_foundations

from ._foundation_source import (
    FoundationPin,
    FoundationSourceError,
    canonical_repository,
    python_sources,
    read_pin,
    validate_timeout,
    verify_checkout,
    verify_snapshot_paths,
)


class GroundingError(RuntimeError):
    """Grounding evidence could not be established or does not meet a requirement."""


class GroundingEvidenceError(GroundingError):
    """A fresh audit did not return evidence bound to the requested source."""


class GroundingNotEstablishedError(GroundingError):
    """The explicit foundation or completeness requirement remains unestablished."""

    def __init__(self, message: str, result: GroundingResult):
        super().__init__(message)
        self.result = result


@dataclass(frozen=True)
class GroundingResult:
    """A verification snapshot, not a certificate accepted by a future audit.

    ``report`` returns a defensive copy. Requirement checks occur only within
    ``verify_grounding`` immediately after a fresh audit, never on this object.
    """

    pin: FoundationPin
    foundation_status: str
    completeness_status: str
    receipt_path: Path | None
    _report_json: str

    @property
    def report(self) -> dict[str, Any]:
        return json.loads(self._report_json)

    def to_dict(self) -> dict[str, Any]:
        return {
            "format": "ordinatics-grounding-1",
            "pin": self.pin.to_dict(),
            "foundation_status": self.foundation_status,
            "completeness_status": self.completeness_status,
            "bridge_status": "UNKNOWN",
            # Portable artifact locator inside the caller's receipt directory;
            # the actual local Path remains available through the Python API.
            "receipt_path": self.receipt_path.name if self.receipt_path is not None else None,
            "report": self.report,
        }


def _default_lock() -> Path:
    # Hatch includes the reviewed root lock here in the built wheel. A source
    # checkout reads that same root file, rather than maintaining two copies.
    bundled = Path(__file__).parent / "_data" / "hypermath.json"
    if bundled.is_file():
        return bundled
    return Path(__file__).resolve().parents[2] / "verification" / "hypermath.json"


def _verify_runtime(root: Path, pin: FoundationPin) -> None:
    try:
        installed_version = metadata.version(pin.distribution)
    except metadata.PackageNotFoundError as error:
        raise GroundingEvidenceError("required Hypermath foundation distribution is not installed") from error
    if installed_version != pin.version:
        raise GroundingEvidenceError("installed foundation version differs from the dependency pin")
    module_file = getattr(hypermath_foundations, "__file__", None)
    if not isinstance(module_file, str):
        raise GroundingEvidenceError("installed foundation module has no inspectable Python source")
    installed = python_sources(Path(module_file).resolve().parent)
    committed = python_sources(root / "src" / "hypermath_foundations")
    if installed != committed:
        raise GroundingEvidenceError("installed foundation Python bytes differ from the pinned checkout")


def _validate_report(report: object, pin: FoundationPin, root: Path, timeout: int) -> dict[str, Any]:
    if not isinstance(report, dict) or report.get("format") != "hypermath-audit-1":
        raise GroundingEvidenceError("fresh foundation audit report is missing or has an unknown format")
    for key in ("subject", "subject_after"):
        subject = report.get(key)
        if not isinstance(subject, dict):
            raise GroundingEvidenceError(f"fresh foundation report is missing {key}")
        canonical_repository(subject.get("repository"))
        if subject.get("revision") != pin.commit or subject.get("dirty") is not False:
            raise GroundingEvidenceError("fresh foundation report is not bound to the clean pinned commit")
    inputs = report.get("inputs")
    if not isinstance(inputs, dict) or inputs.get("stable") is not True:
        raise GroundingEvidenceError("foundation audit inputs were absent or changed during checking")
    before, after = inputs.get("before"), inputs.get("after")
    if not isinstance(before, dict) or not before or before != after:
        raise GroundingEvidenceError("foundation audit lacks matching nonempty input snapshots")
    verify_snapshot_paths(root, before, timeout=timeout)
    claims = report.get("claims")
    claim = claims.get("self_derivation") if isinstance(claims, dict) else None
    if not isinstance(claim, dict) or claim.get("status") not in ("PASS", "FAIL", "UNKNOWN"):
        raise GroundingEvidenceError("foundation audit does not establish a typed self-derivation status")
    target = report.get("target")
    if not isinstance(target, dict) or target.get("name") != "Hypermath.selfDerivation":
        raise GroundingEvidenceError("foundation audit target is not Hypermath.selfDerivation")
    return report


def verify_grounding(
    foundation_root: str | Path,
    *,
    lock_path: str | Path | None = None,
    timeout: int = 60,
    receipt_directory: str | Path | None = None,
    require_grounding: bool = False,
    require_complete: bool = False,
) -> GroundingResult:
    """Audit a pinned checkout now and optionally require established grounding.

    No caller-supplied report, PASS flag, or earlier receipt is accepted. The
    installed runner's Python bytes must match the clean pinned checkout. Git
    identity and source cleanliness are checked before and after the audit.

    ``receipt_directory`` requests a Verifier Standard (VSTD) receipt using the
    dependency's verification extra and a further fresh replay. This is local
    evidence about named claims, not a publication or endorsement.

    ``require_grounding`` requires the dependency's self-derivation gate.
    ``require_complete`` always raises until a checked source-to-library bridge
    and recursively grounded arithmetic completeness theorem are implemented.
    The timeout bounds each subprocess, not total end-to-end execution time.
    """
    if type(require_grounding) is not bool or type(require_complete) is not bool:
        raise GroundingError("require_grounding and require_complete must be booleans")
    try:
        validate_timeout(timeout)
        pin = read_pin(Path(lock_path) if lock_path is not None else _default_lock())
        root = verify_checkout(Path(foundation_root), pin, timeout=timeout)
        _verify_runtime(root, pin)
        report = hypermath_foundations.run_audit(root, timeout=timeout)
        verify_checkout(root, pin, timeout=timeout)
        _verify_runtime(root, pin)
        report = _validate_report(report, pin, root, timeout)
        gate = hypermath_foundations.evaluate_gate(report, claim="self_derivation")
        if type(gate) is not bool:
            raise GroundingEvidenceError("foundation gate did not return a boolean decision")
        status = report["claims"]["self_derivation"]["status"]
        if gate and status != "PASS":
            raise GroundingEvidenceError("foundation gate contradicts the fresh report's claim status")
        if not gate and status == "PASS":
            # A reported PASS cannot override the checker revalidating evidence.
            status = "UNKNOWN"
        receipt_path = None
        if receipt_directory is not None:
            try:
                from hypermath_foundations.vstd import write_verification_receipt
            except ImportError as error:
                raise GroundingEvidenceError(
                    "receipt output requires Ordinatics' verification extra"
                ) from error
            receipt_path = Path(write_verification_receipt(
                report, Path(receipt_directory), foundation_root=root, timeout=timeout,
            ))
            verify_checkout(root, pin, timeout=timeout)
            _verify_runtime(root, pin)
        result = GroundingResult(
            pin, status, "UNKNOWN", receipt_path,
            json.dumps(report, sort_keys=True, allow_nan=False),
        )
    except FoundationSourceError as error:
        raise GroundingEvidenceError(str(error)) from error
    if require_complete:
        raise GroundingNotEstablishedError(
            "recursively grounded arithmetic completeness is UNKNOWN: "
            "the source-to-Ordinatics bridge and completeness proof are not established", result,
        )
    if require_grounding and result.foundation_status != "PASS":
        raise GroundingNotEstablishedError(
            f"Hypermath self-derivation grounding is {result.foundation_status}; "
            "the fresh proof gate did not pass", result,
        )
    return result

"""Exact ordinal arithmetic and explicitly bounded semantic tools.

Ordinary ordinal operations, commutative value operations, and bounded
satisfaction are distinct APIs. See the paper and docs for their contracts.
"""

from __future__ import annotations

from importlib import import_module
from typing import Any

__version__ = "0.3.0"

_LAZY_EXPORTS: dict[str, tuple[str, str]] = {
    # ordinals
    "OMEGA": ("ordinatics.ordinals", "OMEGA"),
    "ONE": ("ordinatics.ordinals", "ONE"),
    "ZERO": ("ordinatics.ordinals", "ZERO"),
    "Ordinal": ("ordinatics.ordinals", "Ordinal"),
    # algebra
    "X": ("ordinatics.algebra", "X"),
    "PoleError": ("ordinatics.algebra", "PoleError"),
    "complex_period": ("ordinatics.algebra", "complex_period"),
    "rational_function": ("ordinatics.algebra", "rational_function"),
    "rational_power_image": ("ordinatics.algebra", "rational_power_image"),
    "specialize": ("ordinatics.algebra", "specialize"),
    "wrap": ("ordinatics.algebra", "wrap"),
    # semantics
    "Add": ("ordinatics.semantics", "Add"),
    "And": ("ordinatics.semantics", "And"),
    "Eq": ("ordinatics.semantics", "Eq"),
    "EvaluationLimitError": ("ordinatics.semantics", "EvaluationLimitError"),
    "Exists": ("ordinatics.semantics", "Exists"),
    "ForAll": ("ordinatics.semantics", "ForAll"),
    "Formula": ("ordinatics.semantics", "Formula"),
    "FreeVariableError": ("ordinatics.semantics", "FreeVariableError"),
    "LanguageMembershipError": ("ordinatics.semantics", "LanguageMembershipError"),
    "Lt": ("ordinatics.semantics", "Lt"),
    "MalformedSyntaxError": ("ordinatics.semantics", "MalformedSyntaxError"),
    "Mul": ("ordinatics.semantics", "Mul"),
    "Nat": ("ordinatics.semantics", "Nat"),
    "Not": ("ordinatics.semantics", "Not"),
    "OrdinaticsSemanticsError": ("ordinatics.semantics", "OrdinaticsSemanticsError"),
    "Term": ("ordinatics.semantics", "Term"),
    "Truth": ("ordinatics.semantics", "Truth"),
    "Var": ("ordinatics.semantics", "Var"),
    "evaluate": ("ordinatics.semantics", "evaluate"),
    "free_variables": ("ordinatics.semantics", "free_variables"),
    "rank": ("ordinatics.semantics", "rank"),
    # calculus
    "Delta": ("ordinatics.calculus", "Delta"),
    "DifferenceOperator": ("ordinatics.calculus", "DifferenceOperator"),
    "DomainError": ("ordinatics.calculus", "DomainError"),
    "NormalFunction": ("ordinatics.calculus", "NormalFunction"),
    "OrdinalDerivative": ("ordinatics.calculus", "OrdinalDerivative"),
    "VeblenHierarchy": ("ordinatics.calculus", "VeblenHierarchy"),
    "VeblenTerm": ("ordinatics.calculus", "VeblenTerm"),
    "delta": ("ordinatics.calculus", "delta"),
    "derivative": ("ordinatics.calculus", "derivative"),
    "least_fixed_point": ("ordinatics.calculus", "least_fixed_point"),
    "ordinal_supremum": ("ordinatics.calculus", "ordinal_supremum"),
    "veblen": ("ordinatics.calculus", "veblen"),
    # dynamics
    "OrdinalAttractor": ("ordinatics.dynamics", "OrdinalAttractor"),
    "OrdinalDynamicalSystem": ("ordinatics.dynamics", "OrdinalDynamicalSystem"),
    "OrdinalOrbit": ("ordinatics.dynamics", "OrdinalOrbit"),
    "OrdinalTransformation": ("ordinatics.dynamics", "OrdinalTransformation"),
    "find_attractor": ("ordinatics.dynamics", "find_attractor"),
    "find_fixed_point": ("ordinatics.dynamics", "find_fixed_point"),
    "orbit": ("ordinatics.dynamics", "orbit"),
}

__all__ = list(_LAZY_EXPORTS)


def __getattr__(name: str) -> Any:
    target = _LAZY_EXPORTS.get(name)
    if target is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_name, attribute_name = target
    value = getattr(import_module(module_name), attribute_name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))


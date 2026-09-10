"""Exact ordinal arithmetic and explicitly bounded semantic tools.

Ordinary ordinal operations, commutative value operations, and bounded
satisfaction are distinct APIs. See the paper and docs for their contracts.
"""

from .algebra import (
    PoleError,
    X,
    complex_period,
    rational_function,
    rational_power_image,
    specialize,
    wrap,
)
from .grounding import (
    GroundingError,
    GroundingEvidenceError,
    GroundingNotEstablishedError,
    GroundingResult,
    verify_grounding,
)
from .ordinals import OMEGA, ONE, ZERO, Ordinal
from .semantics import (
    Add,
    And,
    Eq,
    EvaluationLimitError,
    Exists,
    ForAll,
    Formula,
    FreeVariableError,
    LanguageMembershipError,
    Lt,
    MalformedSyntaxError,
    Mul,
    Nat,
    Not,
    OrdinaticsSemanticsError,
    Term,
    Truth,
    Var,
    evaluate,
    free_variables,
    rank,
)

__version__ = "0.2.0.dev0"

__all__ = [
    "OMEGA", "ONE", "ZERO", "X", "Ordinal", "PoleError", "complex_period",
    "rational_function", "rational_power_image", "specialize", "wrap",
    "Add", "And", "Eq", "EvaluationLimitError", "Exists", "ForAll", "Formula",
    "FreeVariableError", "LanguageMembershipError", "Lt", "MalformedSyntaxError",
    "Mul", "Nat", "Not", "OrdinaticsSemanticsError", "Term", "Truth", "Var",
    "evaluate", "free_variables", "rank",
    "GroundingError", "GroundingEvidenceError", "GroundingNotEstablishedError",
    "GroundingResult", "verify_grounding",
]

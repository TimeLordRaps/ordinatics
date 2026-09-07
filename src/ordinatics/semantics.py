"""Explicit syntax and finite evaluation for an ordinal-indexed truth hierarchy.

Arithmetic terms denote natural numbers. Quantifiers range over ``0 <= n < bound``.
``Truth(beta, sentence)`` quotes a *closed syntax tree* belonging to stage beta;
the quotation itself has rank beta + 1. This is not an interpreter for numeric
sentence codes or for unbounded first-order arithmetic. Ill-typed trees raise an
exception before interpretation, rather than receiving a false truth value.

The evaluator is iterative and charges its budget for syntax inspection and
evaluation steps, including every quantifier iteration. The budget bounds these
steps, not the bit complexity of arbitrary-size integer arithmetic.
"""

from __future__ import annotations

import operator
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from .ordinals import ONE, ZERO, Ordinal

__all__ = [
    "Term", "Formula", "Nat", "Var", "Add", "Mul", "Eq", "Lt", "Not",
    "And", "Exists", "ForAll", "Truth", "rank", "free_variables", "evaluate",
    "OrdinaticsSemanticsError", "MalformedSyntaxError", "LanguageMembershipError",
    "FreeVariableError", "EvaluationLimitError",
]


class OrdinaticsSemanticsError(Exception):
    """Base exception for rejected syntax or an incomplete evaluation."""


class MalformedSyntaxError(OrdinaticsSemanticsError, ValueError):
    """The supplied object is outside the supported, typed syntax."""


class LanguageMembershipError(OrdinaticsSemanticsError, ValueError):
    """A formula or quotation exceeds its declared language stage."""


class FreeVariableError(OrdinaticsSemanticsError, ValueError):
    """A quotation is open, or evaluation lacks a variable assignment."""


class EvaluationLimitError(OrdinaticsSemanticsError, RuntimeError):
    """The step budget was exhausted; no truth value has been established."""


class Term:
    """Marker for the supported immutable natural-number term nodes."""

    __slots__ = ()


class Formula:
    """Marker for the supported immutable bounded-arithmetic formula nodes."""

    __slots__ = ()


def _natural(value: object, label: str) -> int:
    is_boolean = isinstance(value, bool) or (
        type(value).__module__ == "numpy" and type(value).__name__ in ("bool", "bool_")
    )
    if is_boolean:
        raise MalformedSyntaxError(f"{label} must be a nonnegative integer, excluding bool")
    if isinstance(value, float):
        raise MalformedSyntaxError(f"{label} must be an exact integer, excluding floats")
    try:
        natural = operator.index(value)
    except TypeError as error:
        raise MalformedSyntaxError(f"{label} must implement the exact integer protocol") from error
    if natural < 0:
        raise MalformedSyntaxError(f"{label} must be a nonnegative integer")
    return natural


def _variable(value: object) -> None:
    if type(value) is not str or not value.isidentifier():
        raise MalformedSyntaxError("a variable name must be a nonempty identifier string")


def _ordinal(value: object, label: str) -> None:
    if type(value) is not Ordinal:
        raise MalformedSyntaxError(f"{label} must be an Ordinal")
    # Recheck even frozen objects: callers can bypass dataclass construction.
    coefficients = getattr(value, "coefficients", None)
    if type(coefficients) is not tuple or any(
        type(coefficient) is not int or coefficient < 0 for coefficient in coefficients
    ) or (coefficients and coefficients[-1] == 0):
        raise MalformedSyntaxError(f"{label} has malformed ordinal coefficients")


def _term(value: object) -> None:
    if type(value) not in _TERM_TYPES:
        raise MalformedSyntaxError("expected a supported natural-number term")


def _formula(value: object) -> None:
    if type(value) not in _FORMULA_TYPES:
        raise MalformedSyntaxError("expected a supported bounded-arithmetic formula")


@dataclass(frozen=True, slots=True)
class Nat(Term):
    """An exact natural-number constant, canonicalized to a Python ``int``.

    The integer ``__index__`` protocol accepts NumPy and SymPy integers without
    accepting floats, strings, or booleans (including NumPy booleans).
    """

    value: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _natural(self.value, "Nat.value"))


@dataclass(frozen=True, slots=True)
class Var(Term):
    """A named natural-number variable."""

    name: str

    def __post_init__(self) -> None:
        _variable(self.name)


@dataclass(frozen=True, slots=True)
class Add(Term):
    """Addition of natural-number terms, not ordinal addition."""

    left: Term
    right: Term

    def __post_init__(self) -> None:
        _term(self.left)
        _term(self.right)


@dataclass(frozen=True, slots=True)
class Mul(Term):
    """Multiplication of natural-number terms, not ordinal multiplication."""

    left: Term
    right: Term

    def __post_init__(self) -> None:
        _term(self.left)
        _term(self.right)


@dataclass(frozen=True, slots=True)
class Eq(Formula):
    """Equality of natural-number terms."""

    left: Term
    right: Term

    def __post_init__(self) -> None:
        _term(self.left)
        _term(self.right)


@dataclass(frozen=True, slots=True)
class Lt(Formula):
    """Strict less-than comparison of natural-number terms."""

    left: Term
    right: Term

    def __post_init__(self) -> None:
        _term(self.left)
        _term(self.right)


@dataclass(frozen=True, slots=True)
class Not(Formula):
    """Logical negation."""

    body: Formula

    def __post_init__(self) -> None:
        _formula(self.body)


@dataclass(frozen=True, slots=True)
class And(Formula):
    """Logical conjunction, evaluated left to right with short-circuiting."""

    left: Formula
    right: Formula

    def __post_init__(self) -> None:
        _formula(self.left)
        _formula(self.right)


@dataclass(frozen=True, slots=True)
class Exists(Formula):
    """Existence of ``variable`` among natural numbers below ``bound``.

    The variable is bound in ``body`` only. Its occurrence in ``bound`` remains
    free (or belongs to an enclosing quantifier), as in standard bounded syntax.
    """

    variable: str
    bound: Term
    body: Formula

    def __post_init__(self) -> None:
        _variable(self.variable)
        _term(self.bound)
        _formula(self.body)


@dataclass(frozen=True, slots=True)
class ForAll(Formula):
    """Universality for natural numbers below an exclusive natural bound.

    The variable is bound in ``body`` only; see :class:`Exists`.
    """

    variable: str
    bound: Term
    body: Formula

    def __post_init__(self) -> None:
        _variable(self.variable)
        _term(self.bound)
        _formula(self.body)


@dataclass(frozen=True, slots=True)
class Truth(Formula):
    """A typed quotation of a closed formula of rank at most ``level``.

    The quotation has rank ``level + ONE``. Its closure and stage membership
    are checked by :func:`rank`, :func:`free_variables`, and :func:`evaluate`.
    A surrounding quantifier or assignment cannot bind names inside quotation.
    """

    level: Ordinal
    sentence: Formula

    def __post_init__(self) -> None:
        _ordinal(self.level, "Truth.level")
        _formula(self.sentence)


_TERM_TYPES = (Nat, Var, Add, Mul)
_FORMULA_TYPES = (Eq, Lt, Not, And, Exists, ForAll, Truth)


@dataclass(slots=True)
class _Budget:
    remaining: int

    def __post_init__(self) -> None:
        if type(self.remaining) is not int or self.remaining < 1:
            raise MalformedSyntaxError("max_steps must be a positive integer, excluding bool")

    def take(self) -> None:
        if self.remaining == 0:
            raise EvaluationLimitError("step budget exhausted; evaluation is incomplete")
        self.remaining -= 1


@dataclass(frozen=True, slots=True)
class _Info:
    rank: Ordinal
    free: frozenset[str]


def _children(node: object) -> tuple[Term | Formula, ...]:
    """Recheck local types on every analyzed tree, including altered objects."""
    kind = type(node)
    if kind is Nat:
        _natural(node.value, "Nat.value")
        if type(node.value) is not int:
            raise MalformedSyntaxError("Nat.value is not a canonical Python integer")
        return ()
    if kind is Var:
        _variable(node.name)
        return ()
    if kind in (Add, Mul, Eq, Lt):
        _term(node.left)
        _term(node.right)
        return (node.left, node.right)
    if kind is Not:
        _formula(node.body)
        return (node.body,)
    if kind is And:
        _formula(node.left)
        _formula(node.right)
        return (node.left, node.right)
    if kind in (Exists, ForAll):
        _variable(node.variable)
        _term(node.bound)
        _formula(node.body)
        return (node.bound, node.body)
    if kind is Truth:
        _ordinal(node.level, "Truth.level")
        _formula(node.sentence)
        return (node.sentence,)
    raise MalformedSyntaxError("unsupported syntax node")


def _analyze(formula: Formula, budget: _Budget) -> _Info:
    _formula(formula)
    pending: list[tuple[Term | Formula, bool]] = [(formula, False)]
    active: set[int] = set()
    complete: dict[int, _Info] = {}
    try:
        while pending:
            node, exiting = pending.pop()
            budget.take()
            key = id(node)
            if exiting:
                children = _children(node)
                infos = [complete[id(child)] for child in children]
                free = frozenset().union(*(info.free for info in infos))
                node_rank = max((info.rank for info in infos), default=ZERO)
                if type(node) is Var:
                    free = frozenset((node.name,))
                elif type(node) in (Exists, ForAll):
                    free = infos[0].free | (infos[1].free - {node.variable})
                elif type(node) is Truth:
                    if infos[0].free:
                        raise FreeVariableError("Truth requires a closed quoted sentence")
                    if infos[0].rank > node.level:
                        raise LanguageMembershipError(
                            "quoted sentence rank exceeds Truth.level"
                        )
                    node_rank = node.level + ONE
                complete[key] = _Info(node_rank, free)
                active.remove(key)
            else:
                if key in active:
                    raise MalformedSyntaxError("cyclic syntax is not a finite formula")
                if key in complete:
                    continue
                children = _children(node)
                active.add(key)
                pending.append((node, True))
                pending.extend((child, False) for child in reversed(children))
    except (AttributeError, RecursionError) as error:
        raise MalformedSyntaxError("malformed or recursively invalid syntax") from error
    return complete[id(formula)]


def rank(formula: Formula, *, max_steps: int = 10_000) -> Ordinal:
    """Validate syntax and return its least ordinal language stage.

    Arithmetic has rank zero; connectives/quantifiers take the maximum of their
    component ranks; ``Truth(beta, sentence)`` has rank beta + 1 and requires a
    closed sentence of rank at most beta. Malformed quotations raise errors.
    """
    return _analyze(formula, _Budget(max_steps)).rank


def free_variables(formula: Formula, *, max_steps: int = 10_000) -> frozenset[str]:
    """Validate syntax and return unbound variable names outside quotation."""
    return _analyze(formula, _Budget(max_steps)).free


def evaluate(
    formula: Formula,
    assignment: Mapping[str, int] | None = None,
    *,
    stage: Ordinal | None = None,
    max_steps: int = 10_000,
) -> bool:
    """Evaluate bounded syntax in the standard natural numbers.

    ``stage=None`` selects the formula's least valid language stage. An explicit
    stage must be an :class:`Ordinal` at least as large as :func:`rank`. All free
    variables need exact natural-number assignments; integer-protocol values
    are canonicalized to Python integers. Quotations must be closed even
    when an assignment is provided. No unbounded quantifiers are supported.

    The shared budget includes tree validation, assignment inspection, expression
    evaluation, and quantifier iterations. Exhaustion raises
    :class:`EvaluationLimitError`, never a false truth value.
    """
    budget = _Budget(max_steps)
    info = _analyze(formula, budget)
    if stage is not None:
        _ordinal(stage, "stage")
        if info.rank > stage:
            raise LanguageMembershipError("formula rank exceeds the requested stage")
    environment: dict[str, int] = {}
    if assignment is not None:
        if not isinstance(assignment, Mapping):
            raise MalformedSyntaxError("assignment must be a mapping of names to natural numbers")
        for name, value in assignment.items():
            budget.take()
            _variable(name)
            environment[name] = _natural(value, f"assignment[{name!r}]")
    missing = info.free - environment.keys()
    if missing:
        raise FreeVariableError(f"missing natural-number assignments for {', '.join(sorted(missing))}")

    pending: list[tuple[Any, ...]] = [("eval", formula, environment)]
    values: list[int | bool] = []
    while pending:
        budget.take()
        instruction = pending.pop()
        operation = instruction[0]
        if operation == "eval":
            _, node, env = instruction
            kind = type(node)
            if kind is Nat:
                values.append(node.value)
            elif kind is Var:
                values.append(env[node.name])
            elif kind in (Add, Mul, Eq, Lt):
                pending.append(("binary", kind))
                pending.append(("eval", node.right, env))
                pending.append(("eval", node.left, env))
            elif kind is Not:
                pending.append(("not",))
                pending.append(("eval", node.body, env))
            elif kind is And:
                pending.append(("and", node.right, env))
                pending.append(("eval", node.left, env))
            elif kind in (Exists, ForAll):
                pending.append(("quantifier_bound", node, env))
                pending.append(("eval", node.bound, env))
            elif kind is Truth:
                pending.append(("eval", node.sentence, {}))
        elif operation == "binary":
            right, left = values.pop(), values.pop()
            kind = instruction[1]
            if kind is Add:
                values.append(left + right)
            elif kind is Mul:
                values.append(left * right)
            elif kind is Eq:
                values.append(left == right)
            else:
                values.append(left < right)
        elif operation == "not":
            values.append(not values.pop())
        elif operation == "and":
            if values.pop():
                pending.append(("eval", instruction[1], instruction[2]))
            else:
                values.append(False)
        elif operation == "quantifier_bound":
            _, node, env = instruction
            bound = values.pop()
            pending.append(("quantifier_next", node, env, bound, 0))
        elif operation == "quantifier_next":
            _, node, env, bound, index = instruction
            if index >= bound:
                values.append(type(node) is ForAll)
            else:
                nested_env = {**env, node.variable: index}
                pending.append(("quantifier_result", node, env, bound, index))
                pending.append(("eval", node.body, nested_env))
        elif operation == "quantifier_result":
            _, node, env, bound, index = instruction
            result = values.pop()
            if (type(node) is Exists and result) or (type(node) is ForAll and not result):
                values.append(bool(result))
            else:
                pending.append(("quantifier_next", node, env, bound, index + 1))
    return bool(values.pop())

"""Finite examples and rejection boundaries; not proofs of arithmetic truth."""

from dataclasses import FrozenInstanceError

import pytest

from ordinatics.ordinals import OMEGA, ONE, ZERO, Ordinal
from ordinatics.semantics import (
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
    Truth,
    Var,
    evaluate,
    free_variables,
    rank,
)


def test_natural_arithmetic_and_connectives():
    statement = And(Eq(Add(Nat(2), Nat(3)), Nat(5)), Lt(Mul(Nat(2), Nat(3)), Nat(7)))
    assert rank(statement) == ZERO
    assert evaluate(statement, stage=ZERO) is True
    assert evaluate(Not(statement)) is False
    assert evaluate(Eq(Nat(0), Nat(1))) is False


def test_assignment_and_free_variables():
    statement = Eq(Add(Var("x"), Nat(1)), Var("y"))
    assert free_variables(statement) == frozenset({"x", "y"})
    assert evaluate(statement, {"x": 4, "y": 5}) is True
    with pytest.raises(FreeVariableError, match="y"):
        evaluate(statement, {"x": 4})


def test_empty_quantifier_ranges_and_exclusive_bound():
    assert evaluate(ForAll("n", Nat(0), Eq(Nat(0), Nat(1)))) is True
    assert evaluate(Exists("n", Nat(0), Eq(Nat(0), Nat(0)))) is False
    assert evaluate(Exists("n", Nat(3), Eq(Var("n"), Nat(3)))) is False
    assert evaluate(Exists("n", Nat(4), Eq(Var("n"), Nat(3)))) is True
    assert evaluate(ForAll("n", Nat(9), Lt(Var("n"), Nat(9)))) is True


def test_quantifier_bound_retains_outer_variable_and_does_not_mutate_assignment():
    statement = ForAll("n", Var("n"), Lt(Var("n"), Nat(3)))
    assert free_variables(statement) == frozenset({"n"})
    assignment = {"n": 3}
    assert evaluate(statement, assignment) is True
    assert assignment == {"n": 3}
    assert evaluate(statement, {"n": 4}) is False


def test_nested_quantifier_shadowing_restores_outer_binding():
    statement = ForAll(
        "n", Nat(3),
        And(Exists("n", Nat(4), Eq(Var("n"), Nat(3))), Lt(Var("n"), Nat(3))),
    )
    assert free_variables(statement) == frozenset()
    assert evaluate(statement) is True


def test_typed_truth_successor_rank_and_nested_truth():
    arithmetic = Eq(Add(Nat(2), Nat(2)), Nat(4))
    first = Truth(ZERO, arithmetic)
    second = Truth(ONE, first)
    assert rank(first) == ONE
    assert rank(second) == Ordinal((2,))
    assert evaluate(first, stage=ONE) is True
    assert evaluate(second, stage=Ordinal((2,))) is True
    assert evaluate(Truth(ZERO, Eq(Nat(0), Nat(1))), stage=ONE) is False


def test_explicit_stage_rejects_outer_rank_and_quote_rejects_inner_rank():
    first = Truth(ZERO, Eq(Nat(0), Nat(0)))
    with pytest.raises(LanguageMembershipError, match="requested stage"):
        evaluate(first, stage=ZERO)
    malformed_quote = Truth(ZERO, first)
    with pytest.raises(LanguageMembershipError, match="Truth.level"):
        rank(malformed_quote)
    with pytest.raises(LanguageMembershipError):
        evaluate(malformed_quote)


def test_limit_stage_and_successor_ordinal_ordering():
    at_limit = Truth(OMEGA, Truth(ZERO, Eq(Nat(0), Nat(0))))
    assert rank(at_limit) == OMEGA + ONE
    with pytest.raises(LanguageMembershipError):
        evaluate(at_limit, stage=OMEGA)
    assert evaluate(at_limit, stage=OMEGA + ONE) is True
    assert rank(And(Eq(Nat(0), Nat(0)), at_limit)) == OMEGA + ONE


def test_quotation_is_closed_and_cannot_capture_an_outer_binder_or_assignment():
    quote = Truth(ZERO, Eq(Var("n"), Var("n")))
    with pytest.raises(FreeVariableError, match="closed"):
        evaluate(quote, {"n": 0})
    with pytest.raises(FreeVariableError, match="closed"):
        evaluate(ForAll("n", Nat(3), quote))
    closed_quote = Truth(ZERO, ForAll("n", Nat(4), Lt(Var("n"), Nat(4))))
    assert evaluate(closed_quote, stage=ONE) is True


@pytest.mark.parametrize("value", [True, False, -1, 1.5, "1"])
def test_natural_literals_and_assignments_reject_non_naturals(value):
    with pytest.raises(MalformedSyntaxError):
        Nat(value)
    with pytest.raises(MalformedSyntaxError):
        evaluate(Eq(Var("n"), Nat(0)), {"n": value})


@pytest.mark.parametrize("value", [True, 0, -1, 1.5, "n"])
def test_ordinal_stage_and_truth_level_require_ordinals(value):
    with pytest.raises(MalformedSyntaxError):
        Truth(value, Eq(Nat(0), Nat(0)))
    with pytest.raises(MalformedSyntaxError):
        evaluate(Eq(Nat(0), Nat(0)), stage=value)


@pytest.mark.parametrize("value", [True, 0, -1, 1.5])
def test_step_budget_requires_positive_integer(value):
    with pytest.raises(MalformedSyntaxError, match="max_steps"):
        evaluate(Eq(Nat(0), Nat(0)), max_steps=value)


def test_malformed_and_unsupported_syntax_is_an_error_not_false():
    with pytest.raises(MalformedSyntaxError):
        Eq(Nat(0), True)
    with pytest.raises(MalformedSyntaxError):
        evaluate(Nat(0))
    with pytest.raises(MalformedSyntaxError):
        evaluate(Formula())
    with pytest.raises(MalformedSyntaxError):
        evaluate(12345)
    with pytest.raises(MalformedSyntaxError):
        evaluate(Eq(Nat(0), Nat(0)), assignment=[("n", 1)])


def test_malformed_branch_rejected_even_if_short_circuited():
    malformed = Eq(Nat(0), Nat(0))
    object.__setattr__(malformed, "left", True)
    with pytest.raises(MalformedSyntaxError):
        evaluate(And(Eq(Nat(0), Nat(1)), malformed))


def test_frozen_syntax_and_cyclic_or_uninitialized_object_rejection():
    statement = Not(Eq(Nat(0), Nat(0)))
    with pytest.raises(FrozenInstanceError):
        statement.body = Eq(Nat(0), Nat(1))
    object.__setattr__(statement, "body", statement)
    with pytest.raises(MalformedSyntaxError, match="cyclic"):
        evaluate(statement)
    with pytest.raises(MalformedSyntaxError, match="malformed"):
        evaluate(object.__new__(Eq))


def test_shared_subtrees_and_deep_syntax_do_not_require_python_recursion():
    shared = Eq(Nat(0), Nat(0))
    assert evaluate(And(shared, shared)) is True
    deep = shared
    for _ in range(1500):
        deep = Not(deep)
    assert evaluate(deep, max_steps=20_000) is True
    with pytest.raises(EvaluationLimitError):
        rank(deep, max_steps=100)


def test_quantifier_exhaustion_raises_instead_of_returning_false():
    statement = ForAll("n", Nat(10**12), Eq(Var("n"), Var("n")))
    with pytest.raises(EvaluationLimitError):
        evaluate(statement, max_steps=100)
    assert evaluate(Exists("n", Nat(10**12), Eq(Var("n"), Nat(0))), max_steps=100) is True


def test_truth_evaluation_spends_shared_budget():
    sentence = ForAll("n", Nat(40), Lt(Var("n"), Nat(40)))
    quote = Truth(ONE, Truth(ZERO, sentence))
    with pytest.raises(EvaluationLimitError):
        evaluate(quote, max_steps=100)
    assert evaluate(quote, max_steps=1000) is True


def test_sympy_integer_literals_and_assignments_use_exact_python_arithmetic():
    import sympy

    natural = Nat(sympy.Integer(10**50))
    assert type(natural.value) is int
    assert natural.value == 10**50
    statement = Eq(Add(Var("n"), Nat(sympy.Integer(1))), Nat(10**50 + 1))
    assert evaluate(statement, {"n": sympy.Integer(10**50)}) is True
    with pytest.raises(MalformedSyntaxError):
        Nat(sympy.Rational(3, 2))
    with pytest.raises(MalformedSyntaxError):
        Nat(sympy.Float(3))


def test_numpy_integer_inputs_canonicalize_before_arithmetic_to_avoid_overflow():
    numpy = pytest.importorskip("numpy")
    maximum = numpy.int64(2**63 - 1)
    natural = Nat(maximum)
    assert type(natural.value) is int
    assert evaluate(Eq(Add(natural, Nat(1)), Nat(2**63))) is True
    assert evaluate(Eq(Add(Var("n"), Nat(1)), Nat(2**63)), {"n": maximum}) is True
    for boolean in (numpy.bool_(False), numpy.bool_(True)):
        with pytest.raises(MalformedSyntaxError):
            Nat(boolean)
        with pytest.raises(MalformedSyntaxError):
            evaluate(Eq(Var("n"), Nat(0)), {"n": boolean})
    with pytest.raises(MalformedSyntaxError):
        Nat(numpy.float64(3))


def test_float_subclass_cannot_supply_integer_protocol_to_bypass_rejection():
    class IndexFloat(float):
        def __index__(self):
            return int(self)

    value = IndexFloat(3.5)
    with pytest.raises(MalformedSyntaxError):
        Nat(value)
    with pytest.raises(MalformedSyntaxError):
        evaluate(Eq(Var("n"), Nat(3)), {"n": value})

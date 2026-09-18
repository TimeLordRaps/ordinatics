"""Differential and adversarial tests for the claims in ``ordinatics.semantics``.

This module found no defect. That is the result, and these tests are what makes
it a result rather than an impression: the evaluator is checked against an
independent recursive interpreter written from the module's own documentation,
over randomly generated syntax, and every documented guarantee is exercised with
an input that could have broken it.

There is therefore no negative control in the usual sense -- nothing was fixed,
so there is no unfixed source to run against. In its place, each section was
validated by mutation: a plausible defect was injected into a copy of
``semantics.py`` and the suite was required to fail. Every mutation tried is
recorded with its outcome in ``tests/MUTATIONS.md``.

The first mutation run reported three survivors and only one of them was a gap
in this file: ``_Budget.take`` could be shifted by one step without any test
noticing, because every budget used here sat far from the boundary. That is now
pinned by ``test_the_budget_boundary_is_exact``, which counts ten steps by hand,
and by ``test_one_step_below_the_minimum_always_refuses``, which finds the least
viable budget for six shapes and requires one less to raise. Of the other two,
one was a mutation too weak to implement the defect it was named after, and one
is an equivalent mutant that no test can kill -- quotations are required to be
closed, so the environment passed into one is never read. It is listed in
MUTATIONS.md as required to survive.
"""

from __future__ import annotations

import itertools
import random

import pytest

from ordinatics.ordinals import OMEGA, ONE, ZERO, Ordinal
from ordinatics.semantics import (
    Add,
    And,
    Eq,
    EvaluationLimitError,
    Exists,
    ForAll,
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

BIG = 2_000_000


# ==========================================================================
# An independent interpreter, written from the documentation
# ==========================================================================
# The shipped evaluator is an explicit instruction stack over a value stack.
# This is plain recursion over the tree. They share no code, so agreement
# between them is evidence rather than a tautology.


def ref_value(node: object, env: dict[str, int]) -> int:
    kind = type(node)
    if kind is Nat:
        return node.value
    if kind is Var:
        return env[node.name]
    if kind is Add:
        return ref_value(node.left, env) + ref_value(node.right, env)
    if kind is Mul:
        return ref_value(node.left, env) * ref_value(node.right, env)
    raise AssertionError(kind)


def ref_truth(node: object, env: dict[str, int]) -> bool:
    kind = type(node)
    if kind is Eq:
        return ref_value(node.left, env) == ref_value(node.right, env)
    if kind is Lt:
        return ref_value(node.left, env) < ref_value(node.right, env)
    if kind is Not:
        return not ref_truth(node.body, env)
    if kind is And:
        return ref_truth(node.left, env) and ref_truth(node.right, env)
    if kind is Exists:
        return any(
            ref_truth(node.body, {**env, node.variable: i})
            for i in range(ref_value(node.bound, env))
        )
    if kind is ForAll:
        return all(
            ref_truth(node.body, {**env, node.variable: i})
            for i in range(ref_value(node.bound, env))
        )
    if kind is Truth:
        # The stratified T-schema: True_beta(<S>) holds exactly when S holds.
        return ref_truth(node.sentence, {})
    raise AssertionError(kind)


def ref_free(node: object) -> frozenset[str]:
    kind = type(node)
    if kind is Nat:
        return frozenset()
    if kind is Var:
        return frozenset({node.name})
    if kind in (Add, Mul, Eq, Lt, And):
        return ref_free(node.left) | ref_free(node.right)
    if kind is Not:
        return ref_free(node.body)
    if kind in (Exists, ForAll):
        return ref_free(node.bound) | (ref_free(node.body) - {node.variable})
    if kind is Truth:
        return ref_free(node.sentence)
    raise AssertionError(kind)


def ref_rank(node: object) -> Ordinal:
    kind = type(node)
    if kind in (Nat, Var):
        return ZERO
    if kind in (Add, Mul, Eq, Lt, And):
        return max(ref_rank(node.left), ref_rank(node.right))
    if kind is Not:
        return ref_rank(node.body)
    if kind in (Exists, ForAll):
        return max(ref_rank(node.bound), ref_rank(node.body))
    if kind is Truth:
        return node.level + ONE
    raise AssertionError(kind)


def rand_term(rng: random.Random, names: list[str], depth: int) -> object:
    if depth <= 0 or rng.random() < 0.4:
        if not names or rng.random() < 0.5:
            return Nat(rng.randrange(4))
        return Var(rng.choice(names))
    return rng.choice([Add, Mul])(
        rand_term(rng, names, depth - 1), rand_term(rng, names, depth - 1)
    )


def rand_formula(rng: random.Random, names: list[str], depth: int) -> object:
    if depth <= 0:
        return rng.choice([Eq, Lt])(rand_term(rng, names, 1), rand_term(rng, names, 1))
    choice = rng.randrange(6)
    if choice == 0:
        return Eq(rand_term(rng, names, 2), rand_term(rng, names, 2))
    if choice == 1:
        return Lt(rand_term(rng, names, 2), rand_term(rng, names, 2))
    if choice == 2:
        return Not(rand_formula(rng, names, depth - 1))
    if choice == 3:
        return And(rand_formula(rng, names, depth - 1), rand_formula(rng, names, depth - 1))
    var = f"q{depth}"
    return rng.choice([Exists, ForAll])(
        var, Nat(rng.randrange(4)), rand_formula(rng, names + [var], depth - 1)
    )


# ==========================================================================
# 1. evaluate agrees with the reference
# ==========================================================================


@pytest.mark.parametrize("seed", [1, 2, 3, 5, 8])
def test_evaluate_agrees_with_an_independent_interpreter(seed: int) -> None:
    rng = random.Random(seed)
    names = ["a", "b"]
    compared = 0
    for _ in range(60):
        formula = rand_formula(rng, names, 3)
        free = ref_free(formula)
        for va, vb in itertools.product(range(3), repeat=2):
            env = {"a": va, "b": vb}
            assignment = {k: v for k, v in env.items() if k in free}
            assert evaluate(formula, assignment, max_steps=BIG) == ref_truth(formula, env)
            compared += 1
    assert compared >= 500


@pytest.mark.parametrize("seed", [11, 13, 17])
def test_free_variables_agrees_with_the_reference(seed: int) -> None:
    rng = random.Random(seed)
    for _ in range(80):
        formula = rand_formula(rng, ["a", "b"], 3)
        assert free_variables(formula, max_steps=BIG) == ref_free(formula)


@pytest.mark.parametrize("seed", [19, 23, 29])
def test_rank_agrees_with_the_reference(seed: int) -> None:
    rng = random.Random(seed)
    for _ in range(80):
        formula = rand_formula(rng, ["a", "b"], 3)
        assert rank(formula, max_steps=BIG) == ref_rank(formula)


# ==========================================================================
# 2. The budget bounds quantifier iterations, not just syntax nodes
# ==========================================================================

# Five syntax nodes, five thousand iterations. If the budget only charged for
# syntax this would finish inside a budget of ten.
WIDE = ForAll("i", Nat(5000), Lt(Var("i"), Nat(5000)))


@pytest.mark.parametrize("steps", [10, 100, 1000, 10_000])
def test_a_wide_quantifier_is_refused_under_a_small_budget(steps: int) -> None:
    with pytest.raises(EvaluationLimitError):
        evaluate(WIDE, max_steps=steps)


def test_and_answers_under_a_large_one() -> None:
    assert evaluate(WIDE, max_steps=100_000) is True


def test_the_refusal_is_not_a_truth_value() -> None:
    """The documented guarantee: exhaustion raises, never returns False."""
    with pytest.raises(EvaluationLimitError, match="incomplete"):
        evaluate(ForAll("i", Nat(100), Eq(Var("i"), Var("i"))), max_steps=20)


@pytest.mark.parametrize("bad", [0, -1, -100])
def test_a_nonpositive_budget_is_refused(bad: int) -> None:
    with pytest.raises(MalformedSyntaxError, match="positive integer"):
        evaluate(Eq(Nat(0), Nat(0)), max_steps=bad)


def test_a_boolean_budget_is_refused() -> None:
    with pytest.raises(MalformedSyntaxError, match="positive integer"):
        evaluate(Eq(Nat(0), Nat(0)), max_steps=True)


def minimum_budget(formula: object, assignment: object = None, high: int = 1 << 22) -> int:
    """The least max_steps for which evaluation completes."""
    low = 1
    while low < high:
        mid = (low + high) // 2
        try:
            evaluate(formula, assignment, max_steps=mid)
            high = mid
        except EvaluationLimitError:
            low = mid + 1
    return low


def test_the_budget_boundary_is_exact() -> None:
    """The smallest formula there is, counted by hand.

    Analysis pops six instructions: enter and exit for the Eq and for each of
    its two Nat children. Evaluation pops four: the Eq, both Nats, and the
    binary combine. Ten. An off-by-one in ``_Budget.take`` is invisible to every
    other test in this file, because they all sit far from the boundary.
    """
    formula = Eq(Nat(0), Nat(0))
    assert minimum_budget(formula) == 10
    with pytest.raises(EvaluationLimitError):
        evaluate(formula, max_steps=9)
    assert evaluate(formula, max_steps=10) is True


@pytest.mark.parametrize(
    "formula",
    [
        Eq(Nat(0), Nat(0)),
        Not(Eq(Nat(0), Nat(1))),
        And(Eq(Nat(1), Nat(1)), Lt(Nat(0), Nat(1))),
        ForAll("i", Nat(4), Lt(Var("i"), Nat(4))),
        Exists("i", Nat(4), Eq(Var("i"), Nat(3))),
        Truth(ZERO, Eq(Nat(1), Nat(1))),
    ],
)
def test_one_step_below_the_minimum_always_refuses(formula: object) -> None:
    """The boundary property, without needing the exact count for each shape."""
    least = minimum_budget(formula)
    with pytest.raises(EvaluationLimitError):
        evaluate(formula, max_steps=least - 1)
    assert isinstance(evaluate(formula, max_steps=least), bool)


def test_a_wider_quantifier_costs_strictly_more() -> None:
    """Each additional iteration is charged, so the minimum budget must rise."""
    budgets = [
        minimum_budget(ForAll("i", Nat(n), Lt(Var("i"), Nat(n))))
        for n in (1, 2, 4, 8, 16)
    ]
    assert budgets == sorted(budgets) and len(set(budgets)) == 5
    steps_per_iteration = (budgets[-1] - budgets[0]) / (16 - 1)
    assert steps_per_iteration >= 1


def test_the_assignment_is_charged_too() -> None:
    """Documented: the shared budget includes assignment inspection."""
    formula = Eq(Var("a"), Var("a"))
    big_assignment = {f"v{i}": 0 for i in range(500)} | {"a": 1}
    with pytest.raises(EvaluationLimitError):
        evaluate(formula, big_assignment, max_steps=50)


# ==========================================================================
# 3. Truth: stratification, closure, opacity
# ==========================================================================

CLOSED = Eq(Nat(1), Nat(1))


def test_arithmetic_has_rank_zero() -> None:
    assert rank(CLOSED) == ZERO


@pytest.mark.parametrize("level,expected", [(ZERO, 1), (ONE, 2)])
def test_a_quotation_has_rank_level_plus_one(level: Ordinal, expected: int) -> None:
    assert rank(Truth(level, CLOSED)) == Ordinal.from_int(expected)


def test_quotations_stack() -> None:
    assert rank(Truth(ONE, Truth(ZERO, CLOSED))) == Ordinal.from_int(2)


def test_a_quotation_cannot_quote_its_own_stage() -> None:
    """Truth(0, Truth(0, .)) is the shape a liar needs. It is refused."""
    with pytest.raises(LanguageMembershipError, match="exceeds"):
        rank(Truth(ZERO, Truth(ZERO, CLOSED)))


def test_a_quotation_cannot_quote_a_higher_stage() -> None:
    with pytest.raises(LanguageMembershipError, match="exceeds"):
        rank(Truth(ONE, Truth(ONE, Truth(ZERO, CLOSED))))


def test_an_open_quotation_is_refused() -> None:
    with pytest.raises(FreeVariableError, match="closed"):
        rank(Truth(ZERO, Eq(Var("x"), Nat(0))))


def test_an_open_quotation_is_refused_even_with_an_assignment() -> None:
    """Documented: quotations must be closed even when an assignment is given."""
    with pytest.raises(FreeVariableError, match="closed"):
        evaluate(Truth(ZERO, Eq(Var("x"), Nat(0))), {"x": 0})


def test_a_quantifier_cannot_bind_inside_a_quotation() -> None:
    """Opacity. The x below is not the quotation's x, and there isn't one."""
    inner = Truth(ZERO, Eq(Nat(1), Nat(1)))
    formula = ForAll("x", Nat(3), inner)
    assert free_variables(formula) == frozenset()
    assert evaluate(formula) is True


def test_quotation_is_transparent_to_truth() -> None:
    """The stratified T-schema, both ways round."""
    assert evaluate(Truth(ZERO, Eq(Nat(1), Nat(1)))) is True
    assert evaluate(Truth(ZERO, Eq(Nat(1), Nat(2)))) is False


@pytest.mark.parametrize("level", [ZERO, ONE, OMEGA, OMEGA * 2, OMEGA**2])
def test_transfinite_levels_are_accepted(level: Ordinal) -> None:
    quoted = Truth(level, CLOSED)
    assert rank(quoted) == level + ONE
    assert evaluate(quoted) is True


def test_a_transfinite_rank_is_not_a_finite_one() -> None:
    assert rank(Truth(OMEGA, CLOSED)) > Ordinal.from_int(10**6)


@pytest.mark.parametrize("level", [0, 1, "0", None, 1.0])
def test_a_non_ordinal_level_is_refused(level: object) -> None:
    with pytest.raises(MalformedSyntaxError, match="Ordinal"):
        Truth(level, CLOSED)


# ==========================================================================
# 4. stage
# ==========================================================================


def test_an_explicit_stage_below_the_rank_is_refused() -> None:
    with pytest.raises(LanguageMembershipError, match="exceeds the requested stage"):
        evaluate(Truth(ONE, CLOSED), stage=ONE)


def test_an_explicit_stage_at_the_rank_is_accepted() -> None:
    assert evaluate(Truth(ZERO, CLOSED), stage=ONE) is True


def test_a_larger_stage_is_accepted() -> None:
    assert evaluate(Truth(ZERO, CLOSED), stage=OMEGA) is True


def test_stage_none_selects_the_least_valid_one() -> None:
    formula = Truth(ONE, CLOSED)
    assert evaluate(formula) == evaluate(formula, stage=rank(formula))


# ==========================================================================
# 5. Syntax is rechecked, not trusted
# ==========================================================================


def test_cyclic_syntax_is_a_typed_refusal_not_a_stack_overflow() -> None:
    node = Not(Eq(Nat(0), Nat(0)))
    object.__setattr__(node, "body", node)
    with pytest.raises(MalformedSyntaxError, match="cyclic"):
        rank(node, max_steps=1000)


def test_a_longer_cycle_is_also_caught() -> None:
    inner = Not(Eq(Nat(0), Nat(0)))
    outer = Not(inner)
    object.__setattr__(inner, "body", outer)
    with pytest.raises(MalformedSyntaxError, match="cyclic"):
        rank(outer, max_steps=1000)


def test_a_child_replaced_with_a_raw_value_is_refused() -> None:
    node = Eq(Nat(0), Nat(0))
    object.__setattr__(node, "left", 3)
    with pytest.raises(MalformedSyntaxError):
        rank(node, max_steps=1000)


def test_a_nat_mutated_to_hold_a_bool_is_refused() -> None:
    node = Nat(0)
    object.__setattr__(node, "value", True)
    with pytest.raises(MalformedSyntaxError, match="bool"):
        rank(Eq(node, Nat(1)), max_steps=1000)


def test_a_nat_mutated_to_hold_a_negative_is_refused() -> None:
    node = Nat(0)
    object.__setattr__(node, "value", -1)
    with pytest.raises(MalformedSyntaxError, match="nonnegative"):
        rank(Eq(node, Nat(1)), max_steps=1000)


@pytest.mark.parametrize("bad", [True, False, 1.0, "3", None, -1])
def test_nat_refuses_what_is_not_a_natural(bad: object) -> None:
    with pytest.raises(MalformedSyntaxError):
        Nat(bad)


@pytest.mark.parametrize("bad", ["", "1abc", "a b", "a-b", 3, None, b"x"])
def test_var_refuses_what_is_not_an_identifier(bad: object) -> None:
    with pytest.raises(MalformedSyntaxError):
        Var(bad)


@pytest.mark.parametrize("name", ["class", "lambda", "True", "_", "x1"])
def test_var_accepts_any_identifier_including_python_keywords(name: str) -> None:
    """``str.isidentifier`` is the stated rule, and keywords satisfy it. These
    are variable names in the object language, not Python names."""
    assert Var(name).name == name


def test_a_str_subclass_is_not_a_variable_name() -> None:
    """The check is ``type(value) is not str``, deliberately exact."""

    class Name(str):
        pass

    with pytest.raises(MalformedSyntaxError):
        Var(Name("x"))


def test_a_formula_where_a_term_belongs_is_refused() -> None:
    with pytest.raises(MalformedSyntaxError, match="natural-number term"):
        Add(Eq(Nat(0), Nat(0)), Nat(1))


def test_a_term_where_a_formula_belongs_is_refused() -> None:
    with pytest.raises(MalformedSyntaxError, match="formula"):
        Not(Nat(0))


def test_a_bare_term_cannot_be_evaluated() -> None:
    with pytest.raises(MalformedSyntaxError, match="formula"):
        evaluate(Nat(1))


# ==========================================================================
# 6. Assignments
# ==========================================================================


def test_a_missing_assignment_is_refused() -> None:
    with pytest.raises(FreeVariableError, match="missing"):
        evaluate(Eq(Var("x"), Nat(0)))


def test_the_message_names_every_missing_variable() -> None:
    with pytest.raises(FreeVariableError, match="x, y"):
        evaluate(Eq(Var("x"), Var("y")))


def test_a_float_assignment_is_refused() -> None:
    with pytest.raises(MalformedSyntaxError, match="floats"):
        evaluate(Eq(Var("x"), Nat(0)), {"x": 0.0})


def test_a_boolean_assignment_is_refused() -> None:
    with pytest.raises(MalformedSyntaxError, match="bool"):
        evaluate(Eq(Var("x"), Nat(1)), {"x": True})


def test_a_non_mapping_assignment_is_refused() -> None:
    with pytest.raises(MalformedSyntaxError, match="mapping"):
        evaluate(Eq(Var("x"), Nat(0)), [("x", 0)])


def test_an_extra_assignment_is_harmless() -> None:
    assert evaluate(Eq(Nat(0), Nat(0)), {"unused": 5}) is True


def test_a_quantifier_shadows_an_assignment() -> None:
    """ForAll i<2. i<2 is true whatever the caller says i is."""
    formula = ForAll("i", Nat(2), Lt(Var("i"), Nat(2)))
    assert evaluate(formula, {"i": 99}) is True


def test_the_bound_is_read_outside_the_quantifier() -> None:
    """Documented: the variable's occurrence in `bound` stays free."""
    formula = Exists("i", Var("i"), Eq(Var("i"), Nat(0)))
    assert free_variables(formula) == frozenset({"i"})
    assert evaluate(formula, {"i": 3}) is True
    assert evaluate(formula, {"i": 0}) is False


# ==========================================================================
# 7. Structure sharing and depth
# ==========================================================================


def test_a_shared_subterm_is_not_a_cycle() -> None:
    shared = ForAll("i", Nat(3), Lt(Var("i"), Nat(3)))
    assert evaluate(And(shared, shared)) is True


def test_rank_is_linear_in_distinct_nodes_even_when_evaluation_is_not() -> None:
    """`_analyze` memoizes by identity, so a DAG costs its node count. The
    evaluator does not memoize, so the same object costs its expansion. Both
    are honest; they are just different numbers, and the budget is shared."""
    deep = ForAll("i", Nat(2), Lt(Var("i"), Nat(2)))
    for _ in range(12):
        deep = And(deep, deep)
    assert rank(deep, max_steps=10_000) == ZERO
    with pytest.raises(EvaluationLimitError):
        evaluate(deep, max_steps=10_000)


def test_deep_nesting_does_not_recurse() -> None:
    """5000 levels is far past Python's recursion limit. Both passes are
    iterative, so this must simply answer."""
    deep = Eq(Nat(0), Nat(0))
    for _ in range(5000):
        deep = Not(deep)
    assert rank(deep, max_steps=200_000) == ZERO
    assert evaluate(deep, max_steps=200_000) is True


def test_deep_terms_do_not_recurse() -> None:
    term = Nat(1)
    for _ in range(5000):
        term = Add(term, Nat(1))
    assert evaluate(Eq(term, Nat(5001)), max_steps=200_000) is True


# ==========================================================================
# 8. The disclosed gap between step count and bit length
# ==========================================================================


@pytest.mark.parametrize("k,bits", [(4, 16), (6, 64), (8, 256), (10, 1024)])
def test_making_a_big_integer_costs_proportionally_many_steps(k: int, bits: int) -> None:
    """The module discloses that the budget bounds steps, not bit complexity.

    Measured, the gap is narrow: repeated squaring through a shared subterm
    doubles the bit count and doubles the step count together, because the
    evaluator does not memoize. So a budget of N buys roughly N bits, and the
    disclaimer is more cautious than it needs to be.
    """
    term = Nat(2)
    for _ in range(k):
        term = Mul(term, term)
    formula = Eq(term, Nat(0))
    with pytest.raises(EvaluationLimitError):
        evaluate(formula, max_steps=bits)
    assert evaluate(formula, max_steps=bits * 8) is False


def test_a_linear_chain_is_also_paid_for() -> None:
    term = Nat(10**6)
    for _ in range(100):
        term = Mul(term, Nat(10**6))
    with pytest.raises(EvaluationLimitError):
        evaluate(Eq(term, Nat(0)), max_steps=100)
    assert evaluate(Eq(term, Nat(0)), max_steps=1000) is False


def test_one_literal_is_unbounded_but_it_is_the_callers_own_number() -> None:
    """No amplification: the caller wrote the integer out."""
    big = Nat(10**5000)
    assert evaluate(Eq(big, big), max_steps=10) is True


# ==========================================================================
# 9. Error taxonomy
# ==========================================================================


@pytest.mark.parametrize(
    "error,base",
    [
        (MalformedSyntaxError, ValueError),
        (LanguageMembershipError, ValueError),
        (FreeVariableError, ValueError),
        (EvaluationLimitError, RuntimeError),
    ],
)
def test_the_error_classes_keep_their_builtin_bases(error: type, base: type) -> None:
    """Callers catch ValueError or RuntimeError; these must stay compatible."""
    assert issubclass(error, base)

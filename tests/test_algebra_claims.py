"""Adversarial tests for the claims in ``ordinatics.algebra``.

This module found no defect either. As with ``test_semantics_claims``, that is
a result only if the tests could have detected one, so the same discipline
applies: every documented guarantee is exercised with an input that could have
broken it, and the suite is validated by mutation rather than by a negative
control. ``tests/MUTATIONS.md`` records the mutations and their outcomes.

The sharpest section here is the last. ``algebra``'s docstring says
specialization "is not a homomorphism for ordinary ordinal addition or
multiplication" -- a disclaimer, and therefore a claim. Measured, the situation
is sharper than the disclaimer: over 300 random ordinal pairs, ``natural_add``
and ``natural_mul`` agree with polynomial ``+`` and ``*`` on every single one,
while ordinary ordinal ``+`` disagrees on 178 of them. The Cantor normal form
is the polynomial, Hessenberg operations are the polynomial operations, and the
noncommutative ones are not. Conflating the two is the failure this package's
AGENTS.md names first, so it is pinned here rather than described.
"""

from __future__ import annotations

import fractions
import random
import subprocess
import sys

import pytest
import sympy as sp

from ordinatics.algebra import (
    X,
    PoleError,
    complex_period,
    rational_function,
    rational_power_image,
    specialize,
    wrap,
)
from ordinatics.ordinals import OMEGA, ONE, ZERO, Ordinal

# --------------------------------------------------------------------------
# 1. rational_function accepts exactly what it says it accepts
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("label", "value", "expected"),
    [
        ("int", 3, sp.Integer(3)),
        ("zero", 0, sp.Integer(0)),
        ("negative int", -7, sp.Integer(-7)),
        ("Fraction", fractions.Fraction(2, 3), sp.Rational(2, 3)),
        ("SymPy Rational", sp.Rational(-5, 4), sp.Rational(-5, 4)),
        ("polynomial", X**2 + 1, X**2 + 1),
        ("rational function", 1 / (X + 1), 1 / (X + 1)),
    ],
)
def test_exact_scalars_are_accepted(label: str, value: object, expected: sp.Expr) -> None:
    assert sp.simplify(rational_function(value) - expected) == 0


@pytest.mark.parametrize(
    ("label", "value"),
    [
        ("float", 0.5),
        ("float that is an exact integer", 2.0),
        ("string that would parse", "X + 1"),
        ("string that is a number", "3"),
        ("bool True", True),
        ("bool False", False),
        ("foreign symbol", sp.Symbol("Y") + X),
        ("nonrational function", sp.sin(X)),
        ("imaginary coefficient", sp.I * X),
        ("infinity", sp.oo),
        ("negative infinity", -sp.oo),
        ("nan", sp.nan),
        ("float coefficient", sp.Rational(1, 2) * X + sp.Float("0.25")),
        ("matrix", sp.Matrix([[1, 0], [0, 1]])),
        ("none", None),
    ],
)
def test_inexact_and_nonscalar_inputs_are_refused(label: str, value: object) -> None:
    """Each of these is named in the docstring as rejected."""
    with pytest.raises((TypeError, ValueError)):
        rational_function(value)


def test_a_string_is_never_parsed_even_when_it_would_succeed() -> None:
    """"Strings are never parsed" is a security property, not a convenience one.

    ``"X + 1"`` is a perfectly good SymPy expression as text. Refusing it is the
    whole point: parsing attacker-supplied text into a symbolic engine is how
    you get evaluation you did not ask for.
    """
    with pytest.raises(TypeError):
        rational_function("X + 1")
    with pytest.raises(TypeError):
        rational_function("__import__('os')")


def test_a_bool_is_not_a_number_here() -> None:
    """``True == 1`` in Python. The adapter refuses it anyway, and should."""
    with pytest.raises(TypeError):
        rational_function(True)
    assert rational_function(1) == sp.Integer(1)


def test_the_text_and_bool_guards_are_a_distinct_layer_from_strict_sympify() -> None:
    """Both guards are load-bearing, and the mutation control is why this exists.

    Deleting the early ``isinstance(value, (str, ..., bool))`` check does not
    make ``rational_function`` accept a string or a bool -- ``sympify(...,
    strict=True)`` refuses every string, and ``sympify(True)`` returns a
    ``BooleanTrue`` that is not an ``Expr``. So a suite that only asserts
    ``TypeError`` cannot tell the two layers apart, and both mutations survived
    the first run of ``mutate_algebra.py`` for exactly that reason.

    The message is the only observable that distinguishes them, so it is pinned.
    That is deliberately brittle: the claim under test is which defence exists,
    not merely that something refuses.
    """
    for value in ("X + 1", "3", b"3", bytearray(b"3"), True, False):
        with pytest.raises(TypeError, match="not text or bool"):
            rational_function(value)

    # Layer two, exercised directly so that removing either is a failing test.
    for text in ("X + 1", "3", "__import__('os')"):
        with pytest.raises(sp.SympifyError):
            sp.sympify(text, strict=True)
    assert not isinstance(sp.sympify(True, strict=True), sp.Expr)

    # And the witness that ``strict=True`` is doing work: without it, SymPy parses.
    assert sp.sympify("X + 1") == X + 1


def test_a_zero_denominator_is_refused_though_not_by_the_branch_that_says_so() -> None:
    """Refused, and worth recording exactly how.

    ``rational_function`` has an explicit ``"expr has an identically zero
    denominator"`` guard. It is not reachable through this entry point: SymPy
    collapses ``X/(X - X)``, ``1/0`` and friends to ``zoo`` during construction,
    and ``_exact_expr``'s infinity check rejects them first. The outcome is
    correct either way, so this is defence in depth rather than a defect -- but
    a test asserting the unreachable message would have been asserting something
    that never happens.
    """
    for bad in (X / (X - X), sp.zoo, sp.Integer(1) / sp.Integer(0), sp.nan):
        with pytest.raises(ValueError, match="infinity or NaN"):
            rational_function(bad)


def test_common_factors_are_cancelled_on_the_way_out() -> None:
    assert sp.simplify(rational_function((X**2 - 1) / (X - 1)) - (X + 1)) == 0
    assert sp.simplify(rational_function((X**3 - X) / X) - (X**2 - 1)) == 0


def test_a_foreign_symbol_is_named_in_the_error() -> None:
    with pytest.raises(ValueError, match="Y"):
        rational_function(sp.Symbol("Y") + X)


def test_a_non_default_symbol_works_and_swaps_which_symbol_is_foreign() -> None:
    y = sp.Symbol("Y")
    assert sp.simplify(rational_function(y**2, symbol=y) - y**2) == 0
    with pytest.raises(ValueError):
        rational_function(X**2, symbol=y)


def test_a_noncommutative_symbol_is_not_a_valid_variable() -> None:
    with pytest.raises(TypeError):
        rational_function(X, symbol=sp.Symbol("N", commutative=False))


# --------------------------------------------------------------------------
# 2. specialize cancels before it evaluates
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("expr", "at", "want"),
    [
        ((X**2 - 1) / (X - 1), 1, 2),
        ((X**3 - X) / X, 0, -1),
        ((X**2 - 4) / (X - 2), 2, 4),
        ((X - 1) ** 2 / (X - 1), 1, 0),
        (X**2 + 1, sp.Rational(-1, 2), sp.Rational(5, 4)),
    ],
)
def test_a_removable_singularity_is_evaluated_after_cancelling(
    expr: sp.Expr, at: object, want: object
) -> None:
    """The documented convention: the value belongs to the reduced function.

    Every one of these is 0/0 if you substitute before cancelling, so each case
    distinguishes the documented behaviour from the naive one.
    """
    assert specialize(expr, at=at) == want


@pytest.mark.parametrize(
    ("expr", "at"),
    [
        (1 / (X - 1), 1),
        (1 / (2 * X + 1), sp.Rational(-1, 2)),
        ((X + 1) / (X - 1) ** 2, 1),
        (X / (X**2 - 1), 1),
        (X / (X**2 - 1), -1),
    ],
)
def test_a_genuine_pole_raises(expr: sp.Expr, at: object) -> None:
    with pytest.raises(PoleError):
        specialize(expr, at=at)


def test_pole_error_is_a_zero_division_error() -> None:
    """Callers who catch ZeroDivisionError must not be surprised."""
    assert issubclass(PoleError, ZeroDivisionError)
    with pytest.raises(ZeroDivisionError):
        specialize(1 / (X - 1), at=1)


def test_the_result_is_exact_and_not_a_float() -> None:
    value = specialize(X**2 + X, at=sp.Rational(1, 3))
    assert value == sp.Rational(4, 9)
    assert isinstance(value, sp.Rational)
    assert not isinstance(value, sp.Float)


def test_the_point_must_be_an_exact_rational() -> None:
    for bad in (0.5, "1", True, sp.sqrt(2), sp.oo, sp.I):
        with pytest.raises((TypeError, ValueError)):
            specialize(X, at=bad)


def test_specialization_is_a_ring_homomorphism_on_polynomials() -> None:
    """The one algebraic law the module does claim, over random polynomials."""
    rng = random.Random(4242)
    for _ in range(200):
        f = sum(rng.randrange(-4, 5) * X**k for k in range(rng.randrange(1, 5)))
        g = sum(rng.randrange(-4, 5) * X**k for k in range(rng.randrange(1, 5)))
        at = sp.Rational(rng.randrange(-5, 6), rng.randrange(1, 5))
        assert specialize(f + g, at=at) == specialize(f, at=at) + specialize(g, at=at)
        assert specialize(f * g, at=at) == specialize(f, at=at) * specialize(g, at=at)


def test_the_homomorphism_survives_fractions_away_from_their_poles() -> None:
    f, g = 1 / (X + 3), X / (X - 7)
    at = sp.Rational(1, 2)
    assert specialize(f + g, at=at) == specialize(f, at=at) + specialize(g, at=at)
    assert specialize(f * g, at=at) == specialize(f, at=at) * specialize(g, at=at)


def test_a_sum_can_be_defined_where_a_summand_is_not() -> None:
    """Why the homomorphism is stated for polynomials and not for all of Q(X).

    ``1/(X-1)`` and ``-1/(X-1)`` each have a pole at 1; their sum is 0, which
    does not. So the law cannot be extended by simply asserting it everywhere,
    and this is the case that shows why.
    """
    assert specialize(1 / (X - 1) + (-1 / (X - 1)), at=1) == 0
    with pytest.raises(PoleError):
        specialize(1 / (X - 1), at=1)


# --------------------------------------------------------------------------
# 3. wrap is exactly specialization at -1/2
# --------------------------------------------------------------------------


@pytest.mark.parametrize("expr", [X, X**2, X**3, 1 + X, X**2 + X + 1, (X**2 - 1) / (X - 1)])
def test_wrap_agrees_with_specialize_at_minus_one_half(expr: sp.Expr) -> None:
    assert wrap(expr) == specialize(expr, at=sp.Rational(-1, 2))


def test_wrap_is_partial_on_q_of_x() -> None:
    """The docstring calls the extension partial. This is the witness."""
    with pytest.raises(PoleError):
        wrap(1 / (2 * X + 1))


def test_wrap_of_a_constant_is_that_constant() -> None:
    for k in (0, 1, -3, fractions.Fraction(5, 7)):
        assert wrap(k) == sp.Rational(k)


# --------------------------------------------------------------------------
# 4. rational_power_image fixes one logarithm, coherently
# --------------------------------------------------------------------------


def test_the_exponent_addition_law_holds() -> None:
    """The stated reason for fixing a logarithm: F(a+b) = F(a)F(b)."""
    rng = random.Random(9)
    for _ in range(60):
        a = sp.Rational(rng.randrange(-6, 7), rng.randrange(1, 6))
        b = sp.Rational(rng.randrange(-6, 7), rng.randrange(1, 6))
        lhs = rational_power_image(a + b)
        rhs = rational_power_image(a) * rational_power_image(b)
        assert sp.simplify(lhs - rhs) == 0


def test_the_value_map_is_recovered_at_integer_exponents() -> None:
    assert sp.simplify(rational_power_image(0) - 1) == 0
    assert sp.simplify(rational_power_image(1) - sp.Rational(-1, 2)) == 0
    assert sp.simplify(rational_power_image(2) - sp.Rational(1, 4)) == 0
    assert sp.simplify(rational_power_image(-1) + 2) == 0


def test_the_half_power_squares_back_and_is_not_real() -> None:
    """"not a real root convention" is a claim, and this is what makes it one.

    -1/2 has no real square root, so any function claiming to be a coherent
    half power of it must leave the reals. It does, and it still squares back.
    """
    half = rational_power_image(sp.Rational(1, 2))
    assert sp.simplify(half**2 - sp.Rational(-1, 2)) == 0
    assert sp.simplify(sp.im(sp.expand(half))) != 0


def test_the_exponent_must_be_an_exact_rational() -> None:
    for bad in (0.5, "1", True, sp.sqrt(2), sp.oo, sp.I, None):
        with pytest.raises((TypeError, ValueError)):
            rational_power_image(bad)


def test_it_is_not_ordinal_exponentiation() -> None:
    """Also disclaimed, also therefore a claim worth a witness.

    Ordinal exponentiation of 2 is monotone and unbounded. This map sends 1 to
    -1/2 and 2 to 1/4: not monotone, not ordinal, not even positive.
    """
    values = [rational_power_image(k) for k in (1, 2, 3)]
    assert values[0] == sp.Rational(-1, 2)
    assert values[1] == sp.Rational(1, 4)
    assert values[0] < 0 < values[1]


# --------------------------------------------------------------------------
# 5. complex_period really is a period
# --------------------------------------------------------------------------


def test_the_period_shifts_nothing() -> None:
    """Stated as the identity that carries the content: exp(period * c) == 1.

    That form is exact and SymPy proves it outright. The per-point form is then
    a corollary, and is checked below rather than asserted through ``simplify``,
    because ``simplify`` does not prove every instance of it -- at z = -7/5 it
    leaves ``-(-1)**(3/5) + exp(3*I*pi/5)``, which is zero but is not recognised
    as zero. That is a limit of the simplifier, not of the module, so the test
    must not be written in a way that depends on it.
    """
    period = complex_period()
    constant = -sp.log(2) + sp.I * sp.pi
    assert sp.simplify(sp.exp(period * constant) - 1) == 0


def test_the_period_shifts_nothing_pointwise() -> None:
    period = complex_period()
    constant = -sp.log(2) + sp.I * sp.pi
    for z in (0, 1, sp.Rational(1, 3), -2, sp.Rational(-7, 5), sp.Rational(11, 7)):
        difference = sp.exp((z + period) * constant) - sp.exp(z * constant)
        assert abs(complex(sp.N(difference, 60))) < 1e-40


def test_the_period_is_complex_and_not_an_integer() -> None:
    """The docstring says so explicitly; a caller assuming otherwise is wrong."""
    period = complex_period()
    assert sp.simplify(sp.im(sp.expand(period))) != 0
    assert not period.is_integer


def test_the_period_is_not_a_period_of_the_rational_map() -> None:
    """The extension has this period. The value map on Q does not inherit it,
    because the shifted exponent is not rational, so it is not even in the
    domain of ``rational_power_image``."""
    with pytest.raises((TypeError, ValueError)):
        rational_power_image(complex_period())


# --------------------------------------------------------------------------
# 6. the disclaimer that matters most: ordinal vs natural operations
# --------------------------------------------------------------------------


def _random_ordinal(rng: random.Random) -> Ordinal:
    value = ZERO
    for _ in range(rng.randrange(1, 4)):
        value = value.natural_add(Ordinal.omega_power(rng.randrange(0, 3)) * rng.randrange(1, 4))
    return value


def test_hessenberg_operations_are_exactly_the_polynomial_operations() -> None:
    """Measured over 300 random pairs: agreement on every one.

    This is the positive half of the disclaimer. The Cantor normal form is a
    polynomial in omega, and the natural operations are the ones that treat it
    as such.
    """
    rng = random.Random(11)
    for _ in range(300):
        a, b = _random_ordinal(rng), _random_ordinal(rng)
        assert sp.expand(a.natural_add(b).to_sympy(X) - (a.to_sympy(X) + b.to_sympy(X))) == 0
        assert sp.expand(a.natural_mul(b).to_sympy(X) - (a.to_sympy(X) * b.to_sympy(X))) == 0


def test_ordinary_ordinal_addition_is_not_polynomial_addition() -> None:
    """The negative half. 178 of the same 300 pairs disagree.

    A test asserting only the positive half would pass against an implementation
    that had quietly made ``__add__`` commutative, which is the specific error
    this package's AGENTS.md names first.
    """
    rng = random.Random(11)
    disagreements = sum(
        1
        for a, b in ((_random_ordinal(rng), _random_ordinal(rng)) for _ in range(300))
        if sp.expand((a + b).to_sympy(X) - (a.to_sympy(X) + b.to_sympy(X))) != 0
    )
    assert disagreements == 178


def test_the_canonical_witness_one_plus_omega() -> None:
    """1 + omega = omega, but omega + 1 does not absorb. Under ``wrap`` the
    difference is visible as a plain number: -1/2 against 1/2."""
    assert (ONE + OMEGA).to_sympy(X) == X
    assert (OMEGA + ONE).to_sympy(X) == X + 1
    assert wrap((ONE + OMEGA).to_sympy(X)) == sp.Rational(-1, 2)
    assert wrap(ONE.to_sympy(X)) + wrap(OMEGA.to_sympy(X)) == sp.Rational(1, 2)
    assert ONE.natural_add(OMEGA) == OMEGA.natural_add(ONE)
    assert ONE + OMEGA != OMEGA + ONE


def test_ordinal_multiplication_is_not_polynomial_multiplication_either() -> None:
    """(omega + 1) * 2 = omega*2 + 1, not omega*2 + 2."""
    left = (OMEGA + ONE) * 2
    assert left.to_sympy(X) != sp.expand((X + 1) * 2)
    assert (OMEGA + ONE).natural_mul(Ordinal.from_int(2)).to_sympy(X) == sp.expand((X + 1) * 2)


# --------------------------------------------------------------------------
# 7. the packaging claim: dependencies = [] is not decorative
# --------------------------------------------------------------------------


def test_importing_ordinatics_does_not_import_sympy() -> None:
    """``dependencies = []`` in pyproject means sympy must stay optional.

    A plain ``import ordinatics`` plus ordinal arithmetic must not touch it; only
    reaching for the algebra layer may. Run in a subprocess because this one is
    already imported here.
    """
    script = (
        "import sys; sys.path.insert(0, 'src'); import ordinatics;"
        "assert 'sympy' not in sys.modules, 'import ordinatics pulled sympy';"
        "from ordinatics.ordinals import OMEGA; _ = OMEGA * 2 + 1;"
        "assert 'sympy' not in sys.modules, 'ordinal arithmetic pulled sympy';"
        "_ = ordinatics.wrap;"
        "assert 'sympy' in sys.modules, 'touching wrap did not load sympy';"
        "print('ok')"
    )
    proc = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.strip() == "ok"

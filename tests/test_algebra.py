"""Concrete checks for the exact value layer and its numerical boundary."""

from fractions import Fraction

import pytest
import sympy as sp

from ordinatics.algebra import (
    PoleError,
    X,
    complex_period,
    rational_function,
    rational_power_image,
    specialize,
    wrap,
)


def test_exact_rational_inputs_and_polynomial_value():
    assert rational_function(4) == sp.Integer(4)
    assert rational_function(Fraction(2, 3)) == sp.Rational(2, 3)
    assert rational_function(sp.Rational(2, 3)) == sp.Rational(2, 3)
    assert wrap(X**2 + 3 * X + 2) == sp.Rational(3, 4)
    assert specialize(X / (1 + X), at=Fraction(1, 2)) == sp.Rational(1, 3)


def test_cancellation_is_distinct_from_a_pole():
    quotient = (X**2 - 1) / (X - 1)
    assert rational_function(quotient) == X + 1
    assert specialize(quotient, at=1) == 2
    assert wrap((4 * X**2 - 1) / (2 * X + 1)) == -2
    with pytest.raises(PoleError, match="pole"):
        specialize(1 / (X - 1), at=1)
    with pytest.raises(PoleError, match="pole"):
        wrap(1 / (2 * X + 1))
    assert issubclass(PoleError, ZeroDivisionError)


def test_custom_symbol_and_wrong_symbol_are_distinct():
    t = sp.Symbol("t")
    assert rational_function((t**2 - 1) / (t - 1), symbol=t) == t + 1
    assert specialize(t / (t + 2), symbol=t, at=2) == sp.Rational(1, 2)
    assert wrap(t + 1, symbol=t) == sp.Rational(1, 2)
    with pytest.raises(ValueError, match="other than"):
        rational_function(t + X, symbol=t)
    with pytest.raises(ValueError, match="other than"):
        rational_function(X, symbol=t)
    with pytest.raises(ValueError, match="other than"):
        rational_function(sp.Symbol("X", positive=True))


@pytest.mark.parametrize("symbol", ["X", 1, X + 1, sp.Symbol("N", commutative=False)])
def test_invalid_symbol_is_rejected(symbol):
    with pytest.raises(TypeError, match="Symbol"):
        rational_function(1, symbol=symbol)


@pytest.mark.parametrize("value", ["X + 1", b"1", True, 0.5, sp.Float("0.5"), X + sp.Float("0.25"), [1, 2], sp.Matrix([1, 2]), sp.MatrixSymbol("A", 2, 2)])
def test_inexact_text_or_nonscalar_inputs_are_rejected(value):
    with pytest.raises(TypeError):
        rational_function(value)


def test_object_string_representation_is_never_parsed():
    class LooksLikeAnExpression:
        def __str__(self):
            return "X + 1"

    with pytest.raises(TypeError):
        rational_function(LooksLikeAnExpression())


@pytest.mark.parametrize("value", [sp.sqrt(2), sp.pi, sp.E, sp.I, sp.sqrt(X), sp.sin(X), sp.exp(X), X**sp.Rational(1, 3)])
def test_nonrational_functions_and_coefficients_are_rejected(value):
    with pytest.raises(ValueError, match="rational"):
        rational_function(value)


@pytest.mark.parametrize("value", [sp.nan, sp.oo, -sp.oo, sp.zoo])
def test_nonfinite_expressions_are_rejected(value):
    with pytest.raises(ValueError, match="infinity or NaN"):
        rational_function(value)


@pytest.mark.parametrize("point", ["1/2", 0.5, sp.sqrt(2), X, True])
def test_specialization_requires_an_exact_rational_point(point):
    with pytest.raises((TypeError, ValueError)):
        specialize(X, at=point)


def test_wrap_preserves_polynomial_ring_operations():
    p = X**3 + 2 * X + 7
    q = 3 * X**2 - X - 2
    assert wrap(p + q) == wrap(p) + wrap(q)
    assert wrap(p * q) == wrap(p) * wrap(q)


def test_root_branch_has_explicit_nonreal_value_and_exact_powers():
    image = rational_power_image(Fraction(1, 2))
    assert image == sp.I / sp.sqrt(2)
    assert sp.simplify(image**2) == sp.Rational(-1, 2)
    assert rational_power_image(0) == 1
    assert rational_power_image(1) == sp.Rational(-1, 2)
    assert rational_power_image(-2) == 4
    # A real cube root is not the branch selected by the documented logarithm.
    assert complex(rational_power_image(Fraction(1, 3)).evalf()).imag > 0


@pytest.mark.parametrize("r,s", [(Fraction(1, 2), Fraction(1, 2)), (Fraction(1, 3), Fraction(2, 3)), (Fraction(-2, 3), Fraction(1, 4))])
def test_one_branch_preserves_exponent_addition(r, s):
    actual = rational_power_image(r + s)
    composed = rational_power_image(r) * rational_power_image(s)
    assert abs(complex((actual - composed).evalf(30))) < 1e-25


@pytest.mark.parametrize("exponent", ["1/2", 0.5, sp.sqrt(2), X, sp.oo, True])
def test_power_image_rejects_nonrational_or_inexact_exponents(exponent):
    with pytest.raises((TypeError, ValueError)):
        rational_power_image(exponent)


def test_complex_period_is_bound_to_the_selected_logarithm():
    logarithm = -sp.log(2) + sp.I * sp.pi
    period = complex_period()
    assert sp.simplify(period * logarithm) == 2 * sp.pi * sp.I
    assert sp.exp(sp.simplify(period * logarithm)) == 1
    z = sp.Rational(2, 3) + sp.I / 7
    residual = sp.exp((z + period) * logarithm) - sp.exp(z * logarithm)
    assert abs(complex(residual.evalf(30))) < 1e-25


def test_numpy_scalar_adapter_and_lambdify_boundary():
    np = pytest.importorskip("numpy")
    assert rational_function(np.int64(7)) == 7
    assert specialize(X + 1, at=np.int64(3)) == 4
    with pytest.raises(TypeError):
        rational_function(np.float64(0.5))
    with pytest.raises(TypeError):
        rational_function(np.array([1, 2]))
    polynomial = rational_function(X**2 + 1)
    evaluate = sp.lambdify(X, polynomial, modules="numpy")
    np.testing.assert_allclose(evaluate(np.array([0.0, 1.0, 2.0])), [1.0, 2.0, 5.0])

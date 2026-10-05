"""Exact checks of ``rational_power_image`` on the exponent axis.

``rational_power_image(r) = exp(r * (-log(2) + I*pi))`` fixes one logarithm of
-1/2 for every exponent. This module checks, exactly with SymPy, what that
implies on the rational exponent axis and what it does not:

1. composable: exponents add and values multiply;
2. the modulus is ``2**(-r)``, strictly decreasing in ``r``, so the map is
   injective on exponents (order survives, reversed, in the modulus);
3. phase classes by the multiplicative order of ``exp(I*pi*r)``: integer ``r``
   on the real axis (order 1 or 2), half-odd ``r`` on the imaginary axis
   (order 4), other rationals of finite order ``2q / gcd(2q, |p|)``;
4. the image is one-dimensional: modulus and phase are both functions of the
   single parameter ``r`` (a logarithmic spiral).

The statements are properties of this one map on rational exponents. They do not
say that the map is an ordinal homomorphism, and they say nothing about
irrational, surreal or complex exponents.

Skip rationale: the whole module is skipped when SymPy is absent
(``OPTIONAL_DEPENDENCY_ABSENT``; install the ``scientific`` extra).

Mutation check: ``check_value_map`` is parameterised by the map, and the last
tests require it to reject maps that drop the imaginary branch or reverse the
sign of the logarithm. A checker that accepted those would test nothing.
"""

from __future__ import annotations

import cmath
import math
from fractions import Fraction
from typing import Callable

import pytest

sp = pytest.importorskip("sympy")

from ordinatics.algebra import rational_power_image  # noqa: E402

GRID = sorted({Fraction(p, q) for q in range(1, 7) for p in range(-12, 13)})


def _rat(r: Fraction):
    return sp.Rational(r.numerator, r.denominator)


def _phase_order(r: Fraction) -> int:
    """Order of exp(I*pi*r) = exp(2*pi*I * p / (2q)) in the circle group."""
    p, q = r.numerator, r.denominator
    return 2 * q // math.gcd(2 * q, abs(p)) if p else 1


def check_value_map(image: Callable[[object], object]) -> None:
    """Assert every claim above for ``image``; raise AssertionError on the first violation."""
    # 1. composability, exactly
    for a in GRID[::7]:
        for b in GRID[::11]:
            assert sp.simplify(image(_rat(a + b)) - image(_rat(a)) * image(_rat(b))) == 0, (a, b)
    # 2. exact modulus 2**(-r), strictly decreasing in r (hence injective)
    for r in GRID:
        assert sp.simplify(sp.Abs(image(_rat(r))) - sp.Integer(2) ** (-_rat(r))) == 0, r
    moduli = [sp.Integer(2) ** (-_rat(r)) for r in GRID]
    assert all(bool(m1 > m2) for m1, m2 in zip(moduli, moduli[1:]))
    # 3. phase classes, exactly: unit phase = value / modulus must be exp(I*pi*r)
    for r in GRID:
        unit = sp.simplify(image(_rat(r)) * sp.Integer(2) ** _rat(r))
        assert sp.simplify(unit - sp.exp(sp.I * sp.pi * _rat(r))) == 0, r
        order = _phase_order(r)
        assert sp.simplify(unit**order - 1) == 0
        assert all(sp.simplify(unit**k - 1) != 0 for k in range(1, order))
        if r.denominator == 1:
            assert order in (1, 2) and sp.im(unit) == 0  # real axis
        elif r.denominator == 2:
            assert order == 4 and sp.re(unit) == 0  # imaginary axis
        else:
            assert order not in (1, 2, 4)  # other rationals: finite order, off both axes
            assert sp.im(unit) != 0 and sp.re(unit) != 0
    # 4. one parameter only: numeric phase check, tolerance 1e-12 / 1e-9
    for r in GRID[::9]:
        z = complex(sp.N(image(_rat(r)), 30))
        assert abs(abs(z) - 2.0 ** float(-r)) < 1e-12
        d = (cmath.phase(z) - math.pi * float(r)) / (2 * math.pi)
        assert abs(d - round(d)) < 1e-9, (r, d)


def test_rational_power_image_satisfies_every_exponent_axis_claim() -> None:
    check_value_map(rational_power_image)


def test_exponents_add_and_values_multiply() -> None:
    for a in GRID[::7]:
        for b in GRID[::11]:
            lhs = rational_power_image(_rat(a + b))
            rhs = rational_power_image(_rat(a)) * rational_power_image(_rat(b))
            assert sp.simplify(lhs - rhs) == 0


def test_modulus_is_strictly_decreasing_so_the_map_is_injective_on_exponents() -> None:
    values = [sp.Abs(rational_power_image(_rat(r))) for r in GRID]
    assert [sp.simplify(v - sp.Integer(2) ** (-_rat(r))) for v, r in zip(values, GRID)] == [
        0
    ] * len(GRID)
    assert len(set(sp.Integer(2) ** (-_rat(r)) for r in GRID)) == len(GRID)
    assert all(bool(a > b) for a, b in zip(values, values[1:]))


def test_phase_order_classes() -> None:
    integers = [r for r in GRID if r.denominator == 1]
    halves = [r for r in GRID if r.denominator == 2]
    others = [r for r in GRID if r.denominator > 2]
    assert integers and halves and others
    for r in integers:
        z = rational_power_image(_rat(r)) * sp.Integer(2) ** _rat(r)
        assert sp.simplify(z - (-1) ** int(r)) == 0  # real axis: phase +1 or -1
    for r in halves:
        z = rational_power_image(_rat(r)) * sp.Integer(2) ** _rat(r)
        assert sp.simplify(sp.re(z)) == 0 and sp.simplify(sp.im(z)) in (1, -1)  # imaginary axis
    for r in others:
        n = _phase_order(r)
        z = rational_power_image(_rat(r)) * sp.Integer(2) ** _rat(r)
        assert sp.simplify(z**n - 1) == 0  # finite order: periodic under repeated multiplication


def test_image_is_one_dimensional() -> None:
    # Modulus and phase are both read off the same r: the phase is pi*r mod 2*pi
    # wherever the modulus is 2**(-r). Two exponents with equal modulus are equal.
    for r in GRID[::5]:
        z = complex(sp.N(rational_power_image(_rat(r)), 30))
        assert abs(abs(z) - 2.0 ** float(-r)) < 1e-12
        turns = (cmath.phase(z) - math.pi * float(r)) / (2 * math.pi)
        assert abs(turns - round(turns)) < 1e-9


# --------------------------------------------------------------------------
# Mutation checks: the checker must reject maps without the imaginary branch.
# --------------------------------------------------------------------------


def _without_imaginary_branch(exponent):
    return sp.exp(exponent * -sp.log(2))


def _wrong_modulus_direction(exponent):
    return sp.exp(exponent * (sp.log(2) + sp.I * sp.pi))


def test_map_without_the_imaginary_branch_is_rejected() -> None:
    with pytest.raises(AssertionError):
        check_value_map(_without_imaginary_branch)


def test_map_with_increasing_modulus_is_rejected() -> None:
    with pytest.raises(AssertionError):
        check_value_map(_wrong_modulus_direction)

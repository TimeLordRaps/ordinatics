"""Checks of bounded ordinal laws, asymmetric witnesses and exact conversions."""

from dataclasses import FrozenInstanceError
from itertools import product

import pytest

from ordinatics.ordinals import OMEGA, ONE, ZERO, Ordinal


class IndexInteger:
    def __init__(self, value):
        self.value = value

    def __index__(self):
        return self.value


class IndexFloat(float):
    def __index__(self):
        return int(self)


def test_canonical_immutable_representation_and_integer_hashing():
    value = Ordinal([3, 2, 0, 0])
    assert value.coefficients == (3, 2)
    assert repr(value) == "Ordinal(coefficients=(3, 2))"
    assert str(value) == "ω*2 + 3"
    assert str(Ordinal((1, 0, 3))) == "ω^2*3 + 1"
    assert Ordinal((0, 0)) == ZERO
    assert str(ZERO) == "0"
    assert len({Ordinal((3, 2)), value}) == 1
    assert len({3, Ordinal.from_int(3)}) == 1
    assert not ZERO and ONE and OMEGA
    with pytest.raises(FrozenInstanceError):
        value.coefficients = (9,)


def test_ordinary_addition_absorption_and_order():
    assert 1 + OMEGA == OMEGA
    assert OMEGA + 1 == Ordinal((1, 1))
    assert OMEGA + 1 != 1 + OMEGA
    assert Ordinal((5, 4, 3)) + Ordinal((7, 2)) == Ordinal((7, 6, 3))
    assert Ordinal((5, 4)) + Ordinal((7, 2, 1)) == Ordinal((7, 2, 1))
    assert OMEGA + ZERO == ZERO + OMEGA == OMEGA


def test_ordinary_multiplication_order_and_lower_term_absorption():
    assert 2 * OMEGA == OMEGA
    assert OMEGA * 2 == Ordinal((0, 2))
    assert (OMEGA + 1) * 2 == Ordinal((1, 2))
    assert 2 * (OMEGA + 1) == Ordinal((2, 1))
    assert (OMEGA + 1) * OMEGA == Ordinal.omega_power(2)
    assert Ordinal((5, 4, 3)) * Ordinal((2, 0, 7)) == Ordinal((5, 4, 6, 0, 7))
    assert OMEGA * ZERO == ZERO * OMEGA == ZERO


def test_ordinary_associativity_and_distribution_over_right_sum_samples():
    samples = [ZERO, ONE, Ordinal.from_int(3), OMEGA, OMEGA + 2, Ordinal((1, 2, 1))]
    for a, b, c in product(samples, repeat=3):
        assert (a + b) + c == a + (b + c), (a, b, c)
        assert (a * b) * c == a * (b * c), (a, b, c)
        assert a * (b + c) == a * b + a * c, (a, b, c)


def test_ordinary_multiplication_does_not_distribute_over_left_sum():
    # (1 + 1)*omega = omega, whereas 1*omega + 1*omega = omega*2.
    assert (ONE + ONE) * OMEGA == OMEGA
    assert ONE * OMEGA + ONE * OMEGA == OMEGA * 2
    assert (ONE + ONE) * OMEGA != ONE * OMEGA + ONE * OMEGA


def test_finite_arithmetic_and_power_agree_with_natural_numbers():
    for a, b in product(range(7), repeat=2):
        oa, ob = Ordinal.from_int(a), Ordinal.from_int(b)
        assert (oa + ob).to_int() == a + b
        assert (oa * ob).to_int() == a * b
        assert (oa**b).to_int() == a**b
        assert (oa < ob) == (a < b)
    assert ZERO**0 == ONE
    assert (OMEGA + 1) ** 3 == Ordinal((1, 1, 1, 1))
    assert OMEGA**4 == Ordinal.omega_power(4)
    assert OMEGA**0 == ONE


def test_order_compares_highest_exponent_before_coefficients():
    ordered = [ZERO, ONE, Ordinal.from_int(10**100), OMEGA, OMEGA + 1, OMEGA * 2,
               Ordinal((100, 100)), Ordinal.omega_power(2)]
    assert sorted(reversed(ordered)) == ordered
    assert all(a < b for a, b in zip(ordered, ordered[1:]))
    assert OMEGA >= 0 and 0 <= OMEGA
    assert 1 <= ONE <= 1
    assert ONE != -1
    assert ONE != True  # noqa: E712 - Explicitly check boolean non-coercion.
    assert ONE != 1.0


def test_natural_operations_are_commutative_and_distributive_samples():
    assert OMEGA.natural_add(1) == 1 + OMEGA + 1
    assert (OMEGA + 1).natural_mul(OMEGA + 1) == Ordinal((1, 2, 1))
    samples = [ZERO, ONE, Ordinal.from_int(3), OMEGA + 1, Ordinal((2, 0, 3))]
    for a, b, c in product(samples, repeat=3):
        assert a.natural_add(b) == b.natural_add(a)
        assert a.natural_mul(b) == b.natural_mul(a)
        assert a.natural_add(b).natural_add(c) == a.natural_add(b.natural_add(c))
        assert a.natural_mul(b).natural_mul(c) == a.natural_mul(b.natural_mul(c))
        assert a.natural_mul(b.natural_add(c)) == a.natural_mul(b).natural_add(a.natural_mul(c))


def test_exact_index_protocol_is_supported():
    assert Ordinal((IndexInteger(2), IndexInteger(1))) == OMEGA + 2
    assert Ordinal.from_int(IndexInteger(3)) == 3
    assert Ordinal.omega_power(IndexInteger(2)) == OMEGA**2
    assert OMEGA + IndexInteger(2) == OMEGA + 2
    assert IndexInteger(2) + OMEGA == OMEGA
    assert OMEGA * IndexInteger(2) == OMEGA * 2
    assert IndexInteger(2) * OMEGA == OMEGA
    assert (ONE + ONE) ** IndexInteger(3) == 8


def test_finite_right_product_matches_repeated_ordinal_addition():
    for value in [ZERO, ONE, OMEGA + 1, Ordinal((5, 4, 3))]:
        total = ZERO
        for count in range(8):
            assert value * count == total
            total = total + value


@pytest.mark.parametrize("invalid", [True, False, 1.0, IndexFloat(1), float("inf"), "3", None])
def test_inexact_and_boolean_inputs_are_rejected(invalid):
    with pytest.raises(TypeError):
        Ordinal((invalid,))
    with pytest.raises(TypeError):
        Ordinal.from_int(invalid)
    with pytest.raises(TypeError):
        Ordinal.omega_power(invalid)
    with pytest.raises(TypeError):
        OMEGA + invalid
    with pytest.raises(TypeError):
        OMEGA * invalid
    with pytest.raises(TypeError):
        OMEGA**invalid
    with pytest.raises(TypeError):
        OMEGA.natural_add(invalid)
    with pytest.raises(TypeError):
        OMEGA.natural_mul(invalid)


def test_negative_values_and_out_of_scope_operations_are_rejected():
    for constructor in [lambda: Ordinal((-1,)), lambda: Ordinal.from_int(-1),
                        lambda: Ordinal.omega_power(-1), lambda: OMEGA + -1,
                        lambda: OMEGA * -1, lambda: OMEGA**-1]:
        with pytest.raises(ValueError):
            constructor()
    with pytest.raises(ValueError, match="infinite ordinal"):
        OMEGA.to_int()
    with pytest.raises(TypeError):
        OMEGA**OMEGA
    with pytest.raises(TypeError, match="modular"):
        pow(OMEGA, 2, 3)


def test_sympy_roundtrip_and_natural_operation_correspondence():
    sp = pytest.importorskip("sympy")
    x = sp.Symbol("X")
    a, b = Ordinal((3, 2, 1)), Ordinal((1, 1))
    assert a.to_sympy() == x**2 + 2*x + 3
    assert Ordinal.from_sympy(a.to_sympy()) == a
    assert Ordinal.from_sympy(ZERO.to_sympy()) == ZERO
    assert Ordinal.from_sympy(sp.Integer(3)) == 3
    assert Ordinal.from_sympy(sp.Poly(x**2 + 2*x, x)) == Ordinal((0, 2, 1))
    y = sp.Symbol("Y")
    assert Ordinal.from_sympy(a.to_sympy(y), y) == a
    assert sp.expand(a.to_sympy() + b.to_sympy()) == a.natural_add(b).to_sympy()
    assert sp.expand(a.to_sympy() * b.to_sympy()) == a.natural_mul(b).to_sympy()
    assert (1 + OMEGA).to_sympy() != 1 + OMEGA.to_sympy()
    assert (2 * OMEGA).to_sympy() != 2 * OMEGA.to_sympy()


def test_sympy_rejects_nonexact_nonpolynomial_and_wrong_symbol_inputs():
    sp = pytest.importorskip("sympy")
    x, y = sp.symbols("X Y")
    for invalid in [sp.Float(1), x + sp.Float(1), x/2, -x, x - 1, 1/x,
                    sp.sqrt(x), sp.sin(x), x+y, y, sp.oo, sp.sqrt(2), sp.nan]:
        with pytest.raises(ValueError):
            Ordinal.from_sympy(invalid)
    for invalid in [True, 1.0, "X + 1", b"X", None]:
        with pytest.raises(TypeError):
            Ordinal.from_sympy(invalid)
    with pytest.raises(TypeError, match="Symbol"):
        ONE.to_sympy(x + 1)
    with pytest.raises(TypeError, match="Symbol"):
        Ordinal.from_sympy(1, "X")


@pytest.mark.parametrize("direction", ["to_sympy", "from_sympy"])
def test_sympy_adapters_reject_noncommutative_symbols(direction):
    sp = pytest.importorskip("sympy")
    symbol = sp.Symbol("A", commutative=False)
    with pytest.raises(TypeError, match="commutative SymPy Symbol"):
        if direction == "to_sympy":
            Ordinal((1, 2, 1)).to_sympy(symbol)
        else:
            Ordinal.from_sympy(symbol**2 + 2*symbol + 1, symbol)


def test_numpy_exact_integer_interoperation_and_boolean_rejection():
    np = pytest.importorskip("numpy")
    assert Ordinal.from_int(np.int64(4)) == 4
    assert Ordinal((np.int64(2), np.int64(1))) == OMEGA + 2
    assert OMEGA * np.int64(2) == OMEGA * 2
    with pytest.raises(TypeError):
        Ordinal.from_int(np.bool_(True))
    with pytest.raises(TypeError):
        Ordinal.from_int(np.float64(2))

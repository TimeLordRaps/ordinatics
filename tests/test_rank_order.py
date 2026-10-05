"""Exhaustive bounded-grid check of the rank order of the omegas below ``omega ** omega``.

The statements below are the ones proved in Lean (``RankOrder.lean``, kernel-checked)
in the hypermath lean4 directory on branch ``claude/translator-and-ladder``. Ordinatics
contains no Lean, so this suite re-checks them on the repo's own ``Ordinal`` type, over
finite grids of coefficient tuples:

* ``<`` is a strict total order (irreflexive, transitive, trichotomous);
* ``omega**j < omega**j'`` for ``j < j'``;
* banding: ``x < omega**k`` exactly when no coefficient at rank ``k`` or above is
  nonzero, so each nonzero ``x`` lies in exactly one band
  ``[omega**k, omega**(k+1))`` (zero is the sole element below ``omega**0``);
* cofinality: every ``x`` is below some ``omega**j``, so no element of the domain
  bounds the omegas, which is why ``omega**omega`` is outside ``Ordinal``.

A finite grid is evidence for the grid, not a proof for all ordinals; the general
argument is lexicographic order on the Cantor-normal-form coefficients.
Not covered: anything about ``omega**omega`` itself (it is not an ``Ordinal``).
"""

from __future__ import annotations

from itertools import product
from typing import Callable

import pytest

from ordinatics.ordinals import Ordinal

Less = Callable[[Ordinal, Ordinal], bool]


def _grid(max_len: int, max_coeff: int) -> list[Ordinal]:
    seen: dict[tuple[int, ...], Ordinal] = {}
    for coefficients in product(range(max_coeff + 1), repeat=max_len):
        value = Ordinal(coefficients)
        seen[value.coefficients] = value
    return list(seen.values())


SMALL = _grid(4, 2)  # 81 distinct ordinals below omega**4: triples are exhaustive
WIDE = _grid(4, 3)  # 256 distinct ordinals: pairs are exhaustive
POWERS = [Ordinal.omega_power(j) for j in range(0, 12)]


def check_strict_total_order(less: Less, elements: list[Ordinal], triples: list[Ordinal]) -> None:
    for x in elements:
        assert not less(x, x), x  # irreflexive
    for x, y in product(elements, repeat=2):
        outcomes = [less(x, y), x == y, less(y, x)]
        assert sum(outcomes) == 1, (x, y)  # trichotomy: exactly one
    for x, y, z in product(triples, repeat=3):
        if less(x, y) and less(y, z):
            assert less(x, z), (x, y, z)  # transitive


def test_strict_total_order_on_the_grid() -> None:
    check_strict_total_order(lambda a, b: a < b, WIDE, SMALL)


def test_order_is_lexicographic_on_leading_rank_first_coefficients() -> None:
    """Independent model: the Lean ``lt`` on towers, leading rank first, padded."""

    def lean_lt(x: Ordinal, y: Ordinal) -> bool:
        k = max(len(x.coefficients), len(y.coefficients))
        a = tuple(reversed(x.coefficients + (0,) * (k - len(x.coefficients))))
        b = tuple(reversed(y.coefficients + (0,) * (k - len(y.coefficients))))
        for p, q in zip(a, b):
            if p != q:
                return p < q
        return False

    for x, y in product(WIDE, repeat=2):
        assert (x < y) == lean_lt(x, y), (x, y)


def test_a_weakened_order_is_rejected() -> None:
    # Mirrors the Lean check that a non-strict order is not accepted.
    with pytest.raises(AssertionError):
        check_strict_total_order(lambda a, b: a <= b, SMALL[:10], SMALL[:3])


def test_a_non_transitive_relation_is_rejected() -> None:
    def rock_paper_scissors(a: Ordinal, b: Ordinal) -> bool:
        return (len(a.coefficients) - len(b.coefficients)) % 3 == 1

    with pytest.raises(AssertionError):
        check_strict_total_order(rock_paper_scissors, SMALL[:30], SMALL[:30])


def test_omega_powers_are_strictly_monotone_in_the_exponent() -> None:
    for j, j2 in product(range(len(POWERS)), repeat=2):
        assert (POWERS[j] < POWERS[j2]) == (j < j2)
        assert (POWERS[j] == POWERS[j2]) == (j == j2)


def test_every_nonzero_element_lies_in_exactly_one_band() -> None:
    for x in WIDE:
        if not x:
            assert x < POWERS[0]  # zero is the only element below omega**0
            continue
        bands = [k for k in range(0, 8) if POWERS[k] <= x < POWERS[k + 1]]
        assert bands == [len(x.coefficients) - 1], (x, bands)


def test_below_an_omega_power_iff_high_coefficients_vanish() -> None:
    for x in WIDE:
        for k in range(0, 8):
            high_zero = all(c == 0 for c in x.coefficients[k:])
            assert (x < POWERS[k]) == high_zero, (x, k)
            # lower bound of the band: positive leading coefficient at rank k means not below
            if len(x.coefficients) > k and x.coefficients[k] > 0:
                assert not x < POWERS[k]


def test_the_omegas_are_cofinal_in_the_domain() -> None:
    for x in WIDE:
        j = len(x.coefficients)
        assert x < Ordinal.omega_power(j)
        assert not Ordinal.omega_power(j) <= x
    # No element of the domain bounds all the omega powers, so the supremum is outside it.
    for x in WIDE:
        assert any(x < p for p in POWERS)


def test_omega_powers_have_no_largest_element() -> None:
    for j in range(0, 20):
        assert Ordinal.omega_power(j) < Ordinal.omega_power(j + 1)

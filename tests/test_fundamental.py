"""Tests for ``ordinatics.fundamental``: fundamental sequences and the Hardy hierarchy.

Evidence layers, weakest to strongest:

* verified closed forms ``H_omega(n) = 2n``, ``H_{omega*c}(n) = 2**c * n``,
  ``H_{omega**2}(n) = n * 2**n``, ``H_{omega**3}(2) = 2048``;
* the structural recurrences ``H_0(n) = n`` and ``H_{b+1}(n) = H_b(n + 1)``;
* a differential test against an independent implementation (``_incubator_*``
  below), transcribed from the incubator script ``fundamental.py`` in the
  hyperstratum repository. It deliberately uses the incubator's own
  representation (``[(exponent, coefficient), ...]``, leading rank first) and
  its own control flow, and shares no code with the module under test;
* the budget contract: exhaustion raises ``HardyBudgetError`` and never returns
  a value.
"""

from __future__ import annotations

import subprocess
import sys

import pytest

from ordinatics.fundamental import (
    HardyBudgetError,
    HardyDescent,
    hardy,
    hardy_descent,
    hardy_fundamental,
    hardy_omega_omega,
    omega_omega_fundamental,
)
from ordinatics.ordinals import OMEGA, ONE, ZERO, Ordinal

# --------------------------------------------------------------------------
# Independent reference implementation (incubator representation).
# --------------------------------------------------------------------------


def _to_leading_first(a: Ordinal) -> list[tuple[int, int]]:
    """Ordinatics coefficients are constant-term first; the incubator is leading rank first."""
    return [(e, c) for e, c in reversed(list(enumerate(a.coefficients))) if c]


def _inc_norm(a):
    return [(e, c) for e, c in a if c]


def _inc_is_limit(a):
    return bool(a) and a[-1][0] >= 1


def _inc_pred(a):
    assert a and a[-1][0] == 0
    return _inc_norm(a[:-1] + [(0, a[-1][1] - 1)])


def _inc_fund(a, n):
    e, c = a[-1]
    return _inc_norm(a[:-1] + [(e, c - 1)] + [(e - 1, n)])


def _inc_descend(a, n, limit):
    """Incubator Hardy descent: (H_a(n), steps, limit_steps); raises past ``limit``."""
    steps = limits = 0
    while a:
        if steps > limit:
            raise RuntimeError("step budget exceeded")
        if _inc_is_limit(a):
            a = _inc_fund(a, n)
            limits += 1
        else:
            a = _inc_pred(a)
            n += 1
        steps += 1
    return n, steps, limits


def _omega_pow(k: int, c: int = 1) -> Ordinal:
    return Ordinal((0,) * k + (c,))


# --------------------------------------------------------------------------
# Closed forms.
# --------------------------------------------------------------------------


@pytest.mark.parametrize("n", range(0, 10))
def test_closed_forms_for_omega_multiples_and_omega_squared(n: int) -> None:
    assert hardy(OMEGA, n) == 2 * n
    assert hardy(OMEGA * 2, n) == 4 * n
    assert hardy(Ordinal((0, 3)), n) == 8 * n
    assert hardy(_omega_pow(2), n) == n * 2**n


def test_omega_cubed_at_two_is_2048() -> None:
    assert hardy(_omega_pow(3), 2) == 2048


def test_omega_fourth_at_two_exceeds_ten_million_steps() -> None:
    # Termination is guaranteed, but the length is beyond 10**7: a budget of 10**7
    # must be reported as exhausted, not answered.
    with pytest.raises(HardyBudgetError) as info:
        hardy(_omega_pow(4), 2, max_steps=10**7)
    assert info.value.steps == 10**7
    assert info.value.budget == 10**7


def test_structural_recurrences() -> None:
    for n in range(6):
        assert hardy(ZERO, n) == n
        for coefficients in [(1,), (4,), (2, 1), (0, 1), (3, 0, 1), (1, 2)]:
            beta = Ordinal(coefficients)
            assert hardy(beta + ONE, n) == hardy(beta, n + 1)


def test_limit_ordinal_unfolds_through_its_fundamental_sequence() -> None:
    for coefficients in [(0, 1), (0, 2), (0, 0, 1), (0, 0, 2), (0, 1, 1)]:
        alpha = Ordinal(coefficients)
        assert alpha.is_limit
        for n in range(1, 3):  # n = 3 is beyond the budget for omega**2 * 2
            assert hardy(alpha, n, max_steps=10**6) == hardy(
                hardy_fundamental(alpha, n), n, max_steps=10**6
            )


def test_descent_reports_steps_and_limit_unfoldings() -> None:
    # omega at n: one limit unfolding to n, then n successor steps.
    result = hardy_descent(OMEGA, 5)
    assert result == HardyDescent(value=10, steps=6, limit_steps=1)


# --------------------------------------------------------------------------
# Fundamental sequences.
# --------------------------------------------------------------------------


def test_hardy_fundamental_examples_and_index_convention() -> None:
    assert hardy_fundamental(OMEGA, 7) == Ordinal.from_int(7)
    assert hardy_fundamental(_omega_pow(2), 3) == OMEGA * 3
    assert hardy_fundamental(_omega_pow(3), 4) == _omega_pow(2) * 4
    # omega**2*2 [3] = omega**2 + omega*3 (the lowest term, omega**2*2, loses one copy)
    assert hardy_fundamental(Ordinal((0, 0, 2)), 3) == Ordinal((0, 3, 1))
    for coefficients in [(0, 1), (0, 0, 1), (0, 0, 2), (0, 2, 1), (0, 0, 0, 1)]:
        alpha = Ordinal(coefficients)
        for n in range(1, 6):
            assert hardy_fundamental(alpha, n) == alpha.fundamental_sequence(n - 1)


def test_hardy_fundamental_is_strictly_below_and_increasing() -> None:
    for coefficients in [(0, 1), (0, 0, 1), (0, 0, 2), (0, 3, 1)]:
        alpha = Ordinal(coefficients)
        values = [hardy_fundamental(alpha, n) for n in range(0, 6)]
        assert all(v < alpha for v in values)
        assert all(a < b for a, b in zip(values, values[1:]))


@pytest.mark.parametrize("bad", [ZERO, ONE, Ordinal((3,)), Ordinal((2, 1))])
def test_hardy_fundamental_rejects_zero_and_successors(bad: Ordinal) -> None:
    with pytest.raises(ValueError):
        hardy_fundamental(bad, 1)


def test_omega_omega_fundamental_is_omega_to_the_n() -> None:
    for n in range(6):
        assert omega_omega_fundamental(n) == Ordinal.omega_power(n)
    # omega**omega[n] is a limit (n >= 1), strictly increasing, never omega**omega itself.
    assert all(omega_omega_fundamental(n) < omega_omega_fundamental(n + 1) for n in range(6))


def test_hardy_omega_omega_is_hardy_of_omega_to_the_n() -> None:
    for n in (0, 1, 2):
        assert hardy_omega_omega(n).value == hardy(Ordinal.omega_power(n), n)
    assert hardy_omega_omega(2).value == hardy(_omega_pow(2), 2) == 8
    with pytest.raises(HardyBudgetError):
        hardy_omega_omega(3, max_steps=10**5)
    with pytest.raises(HardyBudgetError):
        hardy_omega_omega(4, max_steps=10**5)


# --------------------------------------------------------------------------
# Differential test against the independent incubator implementation.
# --------------------------------------------------------------------------

BUDGET = 5_000


def _grid():
    for c3 in range(3):
        for c2 in range(3):
            for c1 in range(3):
                for c0 in range(3):
                    yield Ordinal((c0, c1, c2, c3))


def test_differential_against_the_incubator_implementation() -> None:
    compared = exhausted = 0
    for alpha in _grid():
        reference = _to_leading_first(alpha)
        for n in range(0, 5):
            try:
                value, steps, limits = _inc_descend(reference, n, limit=BUDGET - 1)
            except RuntimeError:
                with pytest.raises(HardyBudgetError):
                    hardy(alpha, n, max_steps=BUDGET)
                exhausted += 1
                continue
            got = hardy_descent(alpha, n, max_steps=BUDGET)
            assert (got.value, got.steps, got.limit_steps) == (value, steps, limits), (alpha, n)
            compared += 1
    # Both regimes must really be exercised, or the test proves nothing.
    assert compared > 100
    assert exhausted > 20


def test_differential_fundamental_sequences() -> None:
    for alpha in _grid():
        if not alpha.is_limit:
            continue
        reference = _to_leading_first(alpha)
        for n in range(0, 5):
            expected = _inc_fund(reference, n)
            assert _to_leading_first(hardy_fundamental(alpha, n)) == expected


# --------------------------------------------------------------------------
# Budget contract and input validation.
# --------------------------------------------------------------------------


def test_budget_is_exact_never_partial() -> None:
    # H_omega(n) takes exactly n + 1 steps.
    for n in range(0, 8):
        assert hardy_descent(OMEGA, n, max_steps=n + 1).steps == n + 1
        with pytest.raises(HardyBudgetError):
            hardy(OMEGA, n, max_steps=n)


def test_zero_budget_still_answers_zero_without_a_step() -> None:
    assert hardy(ZERO, 5, max_steps=0) == 5
    with pytest.raises(HardyBudgetError):
        hardy(ONE, 5, max_steps=0)


def test_budget_error_is_specific_and_not_a_value_error() -> None:
    assert issubclass(HardyBudgetError, RuntimeError)
    assert not issubclass(HardyBudgetError, ValueError)
    with pytest.raises(HardyBudgetError) as info:
        hardy(_omega_pow(3), 3, max_steps=1000)
    assert info.value.steps == 1000 and info.value.budget == 1000


@pytest.mark.parametrize("bad", [True, False, 1.0, 2.5, "3", None, -1])
def test_inputs_are_not_silently_coerced(bad: object) -> None:
    expected = ValueError if isinstance(bad, int) and not isinstance(bad, bool) else TypeError
    with pytest.raises(expected):
        hardy(OMEGA, bad)
    with pytest.raises(expected):
        hardy(OMEGA, 1, max_steps=bad)
    with pytest.raises(expected):
        hardy(bad, 1)


def test_exact_integers_are_accepted_as_finite_ordinals() -> None:
    assert hardy(3, 4) == 7


# --------------------------------------------------------------------------
# Packaging contract: lazy export, zero dependencies.
# --------------------------------------------------------------------------


def test_exports_are_lazy_and_dependency_free() -> None:
    script = (
        "import sys; sys.path.insert(0, 'src'); import ordinatics;"
        "assert 'ordinatics.fundamental' not in sys.modules, 'eager import';"
        "assert 'sympy' not in sys.modules;"
        "from ordinatics import Ordinal, hardy, HardyBudgetError;"
        "assert 'ordinatics.fundamental' in sys.modules;"
        "assert hardy(Ordinal((0, 1)), 3) == 6;"
        "assert 'sympy' not in sys.modules, 'hardy pulled sympy';"
        "assert callable(ordinatics.hardy_fundamental) and 'hardy' in ordinatics.__all__;"
        "print('ok')"
    )
    proc = subprocess.run([sys.executable, "-S", "-c", script], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.strip() == "ok"

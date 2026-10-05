"""Fundamental sequences and the Hardy hierarchy below ``omega ** omega``.

This module works backwards from a limit ordinal into the natural numbers. For
``alpha`` below ``omega**omega`` in Cantor normal form whose lowest nonzero term
is ``omega**k * c`` with ``k >= 1``, the *Hardy-indexed* fundamental sequence is

    alpha[n] = (alpha with that term replaced by omega**k * (c - 1)) + omega**(k-1) * n

so ``omega**k[n] = omega**(k-1) * n`` and ``omega[n] = n``. The Hardy hierarchy is

    H_0(n) = n,   H_{beta+1}(n) = H_beta(n + 1),   H_lambda(n) = H_{lambda[n]}(n).

Index convention. :meth:`ordinatics.ordinals.Ordinal.fundamental_sequence` uses
the shifted index ``n + 1`` (its sequence starts at ``n = 0`` with a nonzero
step). Here the index is the Hardy argument itself, so for ``n >= 1``
``hardy_fundamental(a, n) == a.fundamental_sequence(n - 1)``. Both are exact and
tested against each other.

Every descent terminates (this is transfinite induction below ``omega**omega``)
but its length is not bounded by any function of the finite data that the
ordinal's coefficients display: ``H_omega(n) = 2n``, ``H_{omega^2}(n) = n*2^n``,
``H_{omega^3}(2) = 2048`` and ``H_{omega^4}(2)`` takes more than ``10**7`` steps.
Every entry point therefore takes an explicit step budget. When the budget is
exhausted :class:`HardyBudgetError` is raised; a value is returned only for a
completed descent, never a partial or truncated one.

``omega**omega`` itself is not an :class:`~ordinatics.ordinals.Ordinal`. Its
fundamental sequence ``omega**omega[n] = omega**n`` is exposed separately by
:func:`omega_omega_fundamental` and :func:`hardy_omega_omega`.

Pure standard library; the only import is the ordinal type.
"""

from __future__ import annotations

from dataclasses import dataclass

from .ordinals import Ordinal, _nonnegative_index

DEFAULT_MAX_STEPS = 1_000_000


class HardyBudgetError(RuntimeError):
    """The step budget ran out before the descent reached zero.

    No value of the Hardy function has been established. ``steps`` is the number
    of descent steps taken and ``budget`` the limit that was supplied.
    """

    def __init__(self, steps: int, budget: int) -> None:
        super().__init__(
            f"Hardy descent not finished within the step budget ({budget}); "
            f"{steps} steps taken, no value established"
        )
        self.steps = steps
        self.budget = budget


@dataclass(frozen=True, slots=True)
class HardyDescent:
    """A completed Hardy descent: ``value = H_alpha(n)`` after ``steps`` steps.

    ``limit_steps`` counts the steps that unfolded a limit ordinal; the rest were
    predecessor steps.
    """

    value: int
    steps: int
    limit_steps: int


def _as_ordinal(value: object, name: str) -> Ordinal:
    if isinstance(value, Ordinal):
        return value
    converted = Ordinal._operand(value)
    if converted is NotImplemented:
        raise TypeError(f"{name} must be an Ordinal or an exact nonnegative integer")
    return converted


def _budget(max_steps: object) -> int:
    return _nonnegative_index(max_steps, "max_steps")


def hardy_fundamental(alpha: object, n: object) -> Ordinal:
    """Return ``alpha[n]``, the Hardy-indexed fundamental sequence of a limit ordinal.

    Raises ``ValueError`` if ``alpha`` is zero or a successor.
    """
    a = _as_ordinal(alpha, "alpha")
    index = _nonnegative_index(n, "n")
    if not a.is_limit:
        raise ValueError("fundamental sequence is only defined for limit ordinals")
    values = list(a.coefficients)
    k = next(i for i, c in enumerate(values) if i > 0 and c > 0)
    values[k] -= 1
    values[k - 1] = index
    return Ordinal(tuple(values))


def omega_omega_fundamental(n: object) -> Ordinal:
    """Return ``omega**omega[n] = omega**n`` (``omega**omega`` is outside ``Ordinal``)."""
    return Ordinal.omega_power(_nonnegative_index(n, "n"))


def hardy_descent(
    alpha: object, n: object, *, max_steps: object = DEFAULT_MAX_STEPS
) -> HardyDescent:
    """Run the Hardy descent from ``alpha`` at argument ``n`` within a step budget.

    Each predecessor step or limit unfolding is one step. Raises
    :class:`HardyBudgetError` if more than ``max_steps`` steps are required.
    """
    a = _as_ordinal(alpha, "alpha")
    value = _nonnegative_index(n, "n")
    budget = _budget(max_steps)
    # Mutable ascending coefficient list, mirroring Ordinal.coefficients.
    coeffs = list(a.coefficients)
    steps = limit_steps = 0
    while coeffs:
        if steps >= budget:
            raise HardyBudgetError(steps, budget)
        if coeffs[0] > 0:
            coeffs[0] -= 1
            value += 1
        else:
            k = next(i for i, c in enumerate(coeffs) if c > 0)
            coeffs[k] -= 1
            coeffs[k - 1] = value
            limit_steps += 1
        while coeffs and coeffs[-1] == 0:
            coeffs.pop()
        steps += 1
    return HardyDescent(value, steps, limit_steps)


def hardy(alpha: object, n: object, *, max_steps: object = DEFAULT_MAX_STEPS) -> int:
    """Return ``H_alpha(n)`` or raise :class:`HardyBudgetError`; see :func:`hardy_descent`."""
    return hardy_descent(alpha, n, max_steps=max_steps).value


def hardy_omega_omega(
    n: object, *, max_steps: object = DEFAULT_MAX_STEPS
) -> HardyDescent:
    """Return the descent for ``H_{omega**omega}(n) = H_{omega**n}(n)``.

    This is the first step ``omega**omega[n] = omega**n`` followed by an ordinary
    bounded descent, so the budget applies to the ``omega**n`` descent and the
    unfolding of ``omega**omega`` itself is not charged as a step. Already
    ``n = 4`` exceeds ``10**7`` steps, hence the budget error for most inputs.
    """
    index = _nonnegative_index(n, "n")
    return hardy_descent(omega_omega_fundamental(index), index, max_steps=max_steps)


__all__ = [
    "DEFAULT_MAX_STEPS",
    "HardyBudgetError",
    "HardyDescent",
    "hardy",
    "hardy_descent",
    "hardy_fundamental",
    "hardy_omega_omega",
    "omega_omega_fundamental",
]

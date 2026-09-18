"""Invariant tests for ordinal dynamical systems.

dynamics.py carried no test module of its own; it was exercised only incidentally
through test_ordinal_calculus.py. These tests pin the properties the module has
to hold rather than the outputs it happens to produce:

- An orbit agrees with direct iteration at every stage it answers for.
- A declared attractor is a real one: fixed points are fixed, and the states of
  a periodic cycle close under the transformation with the declared period.
- T**n is n-fold application, and composition is associative.
- find_fixed_point either returns an actual fixed point or refuses.
- The orbit is monotone in its own bound: raising max_stage never removes a
  stage, and never changes the value at a stage that was already answered.
"""

from __future__ import annotations

import pytest

from ordinatics.dynamics import (
    OrdinalDynamicalSystem,
    OrdinalTransformation,
    find_fixed_point,
    orbit,
)
from ordinatics.ordinals import OMEGA, ONE, ZERO, Ordinal


def _o(n: int) -> Ordinal:
    return Ordinal.from_int(n)


# A carrier small enough that cycles, tails and collapses are all reachable.
CASES: dict[str, object] = {
    "identity": lambda x: x,
    "successor": lambda x: x + ONE,
    "mod5_successor": lambda x: _o((x.to_int() + 1) % 5) if x.is_finite else x,
    "two_cycle_at_zero": lambda x: _o(1) if x == ZERO else (ZERO if x == _o(1) else x),
    "tail_then_two_cycle": lambda x: _o({0: 1, 1: 2, 2: 3, 3: 2}.get(x.to_int(), 2))
    if x.is_finite
    else x,
    "collapse_to_three": lambda x: _o(3) if x.is_finite and x.to_int() != 3 else x,
    "halve": lambda x: _o(x.to_int() // 2) if x.is_finite else x,
    "omega_plus": lambda x: OMEGA + x,
    "constant_omega": lambda _x: OMEGA,
}

START_STATES = [0, 1, 2, 4]


@pytest.mark.parametrize("name", sorted(CASES))
@pytest.mark.parametrize("start", START_STATES)
def test_orbit_agrees_with_direct_iteration(name: str, start: int) -> None:
    # The orbit is a cache of iterated application. Any stage it answers for
    # must carry the same value that iterating by hand produces; a stage it
    # declines to answer for is allowed, a stage it answers wrongly is not.
    transform = OrdinalTransformation(CASES[name], name=name)
    orb = orbit(transform, start, max_stage=12)

    direct = [_o(start)]
    for _ in range(12):
        direct.append(transform.step(direct[-1]))

    for stage in range(13):
        try:
            observed = orb[stage]
        except KeyError:
            continue
        assert observed == direct[stage], f"stage {stage}"

    for index, value in enumerate(orb.trajectory):
        assert value == direct[index], f"trajectory index {index}"


@pytest.mark.parametrize("name", sorted(CASES))
@pytest.mark.parametrize("start", START_STATES)
def test_declared_attractors_are_real(name: str, start: int) -> None:
    transform = OrdinalTransformation(CASES[name], name=name)
    attractor = orbit(transform, start, max_stage=12).attractor
    if attractor is None:
        return

    if attractor.is_fixed_point:
        state = attractor.states[0]
        assert transform.step(state) == state
        assert attractor.period == 1

    if attractor.is_periodic:
        states = attractor.states
        assert len(states) == attractor.period
        # A cycle must close, and must not be a fixed point wearing a cycle's label.
        for index, state in enumerate(states):
            assert transform.step(state) == states[(index + 1) % len(states)]
        assert len(set(states)) == len(states)


@pytest.mark.parametrize("name", sorted(CASES))
def test_transformation_power_is_n_fold_application(name: str) -> None:
    transform = OrdinalTransformation(CASES[name], name=name)
    for power in range(5):
        composed = transform**power
        for start in (0, 1, 3):
            expected = _o(start)
            for _ in range(power):
                expected = transform.step(expected)
            assert composed.step(start) == expected


def test_composition_is_associative() -> None:
    names = sorted(CASES)[:5]
    for first in names:
        for second in names:
            for third in names:
                a, b, c = (OrdinalTransformation(CASES[n], name=n) for n in (first, second, third))
                for start in (0, 2):
                    assert ((a * b) * c).step(start) == (a * (b * c)).step(start)


@pytest.mark.parametrize("name", sorted(CASES))
@pytest.mark.parametrize("start", START_STATES)
def test_find_fixed_point_returns_a_fixed_point_or_refuses(name: str, start: int) -> None:
    transform = OrdinalTransformation(CASES[name], name=name)
    try:
        point = find_fixed_point(transform, start, max_steps=30)
    except ValueError:
        return  # An honest refusal is a permitted outcome; a wrong answer is not.
    assert transform.step(point) == point


# ============================================================================
# Regression: the orbit must be monotone in its own bound
# ============================================================================

# The count of successor stages evaluated past omega was read off the finite
# part of max_stage. omega * 2 has finite part 0, so it evaluated no stage past
# omega at all, while the strictly smaller bound omega + 3 evaluated three:
# asking for a longer orbit returned a shorter one. The same line left stage
# omega * 2 to be inferred from a one-element trajectory, which reported omega.


def _successor_system() -> OrdinalDynamicalSystem:
    return OrdinalDynamicalSystem(lambda x: x + ONE, name="successor")


def test_raising_max_stage_never_removes_an_evaluated_stage() -> None:
    bounds = [OMEGA, OMEGA + 1, OMEGA + 3, OMEGA + 7, OMEGA * 2, OMEGA * 2 + 4, OMEGA * 3]
    system = _successor_system()
    previous_keys: set[Ordinal] = set()
    previous_bound = None
    for bound in bounds:
        keys = set(system.orbit(0, max_stage=bound).stages)
        assert previous_keys <= keys, (
            f"bound {bound} dropped stages that {previous_bound} had evaluated: "
            f"{sorted(str(k) for k in previous_keys - keys)}"
        )
        previous_keys, previous_bound = keys, bound


def test_stage_below_the_bound_is_evaluated_rather_than_missing() -> None:
    # omega + 1 < omega * 2, so the bound omega * 2 must answer for it.
    orb = _successor_system().orbit(0, max_stage=OMEGA * 2)
    assert orb[OMEGA] == OMEGA
    assert orb[OMEGA + 1] == OMEGA + 1
    assert orb[OMEGA + 2] == OMEGA + 2


def test_limit_stage_value_is_not_inferred_from_a_single_sample() -> None:
    # Iterating the successor from 0 reaches omega at stage omega, and omega * 2
    # at stage omega * 2. Inferring the second limit from the one-element
    # trajectory [omega] returned omega, which is the value at the stage before.
    orb = _successor_system().orbit(0, max_stage=OMEGA * 2)
    assert orb[OMEGA * 2] == OMEGA * 2


def test_bound_below_omega_times_two_still_honours_its_finite_part() -> None:
    # The fix must not over-evaluate: omega + 3 asks for exactly three stages
    # past omega, and omega + 4 is beyond that bound.
    orb = _successor_system().orbit(0, max_stage=OMEGA + 3)
    assert orb[OMEGA + 3] == OMEGA + 3
    with pytest.raises(KeyError):
        _ = orb[OMEGA + 4]


def test_every_evaluated_stage_stays_within_the_requested_bound() -> None:
    for bound in (OMEGA, OMEGA + 3, OMEGA * 2, OMEGA * 3):
        orb = _successor_system().orbit(0, max_stage=bound)
        for stage in orb.stages:
            assert stage <= bound, f"stage {stage} exceeds bound {bound}"


def test_transfinite_fixed_point_is_reached_and_is_genuinely_fixed() -> None:
    # alpha -> omega + alpha has least fixed point omega ** 2, reached at the
    # limit stage omega.
    system = OrdinalDynamicalSystem(lambda x: OMEGA + x, name="omega_plus")
    orb = system.orbit(0, max_stage=OMEGA * 2)
    assert orb[OMEGA] == OMEGA**2
    assert system.step(orb[OMEGA]) == orb[OMEGA]
    assert orb.attractor is not None
    assert orb.attractor.is_fixed_point
    assert orb.attractor.stage == OMEGA


# ============================================================================
# Orbit container surface
# ============================================================================


def test_orbit_membership_and_iteration() -> None:
    orb = orbit(OrdinalTransformation(lambda x: x + ONE), 0, max_stage=5)
    assert len(orb) == 6
    assert [s.to_int() for s in orb] == [0, 1, 2, 3, 4, 5]
    assert 3 in orb
    assert 99 not in orb
    # Non-ordinal and negative stages are absences, not crashes.
    assert "x" not in orb
    assert -1 not in orb


def test_is_monotone_distinguishes_monotone_from_decreasing() -> None:
    assert OrdinalTransformation(lambda x: x + ONE).is_monotone(range(6))
    reversing = OrdinalTransformation(
        lambda x: _o(5 - x.to_int()) if x.is_finite else x, name="reversing"
    )
    assert reversing.is_monotone(range(6)) is False


def test_fixed_initial_state_is_detected_at_stage_zero() -> None:
    orb = orbit(OrdinalTransformation(lambda x: x), 7, max_stage=5)
    assert orb.attractor is not None
    assert orb.attractor.is_fixed_point
    assert orb.attractor.stage == ZERO
    assert orb.attractor.states == (_o(7),)


def test_strictly_increasing_system_has_no_finite_fixed_point() -> None:
    system = OrdinalDynamicalSystem(lambda x: x + 1)
    with pytest.raises(ValueError, match="No attractor detected"):
        system.find_fixed_point(0, max_steps=20)

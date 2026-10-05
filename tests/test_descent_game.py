"""A rewrite game whose termination needs omega**2, not a single natural-number measure.

State (a, b) stands for omega*a + b. A step either lowers b by one, or, when b is already 0, lowers a by one and lets an
adversary refill b with any natural number m. Every run from an infinite position is a finite descent ending at (0, 0),
yet the run length is not bounded by any function of (a, b) alone: it is bounded only by the ordinal. The checks use
ordinatics' own exact `Ordinal` comparison (coefficients constant-term first, so (a, b) is Ordinal((b, a))).
"""
import random

from ordinatics import OMEGA, Ordinal


def as_ordinal(state):
    a, b = state
    return Ordinal((b, a))


def step(state, m):
    a, b = state
    if a > 0 and b == 0:
        return (a - 1, m)
    if b > 0:
        return (a, b - 1)
    return state


def run_length(state, adversary):
    n = 0
    while state != (0, 0):
        state = step(state, adversary(n))
        n += 1
    return n


def test_the_encoding_is_omega_times_a_plus_b():
    assert as_ordinal((1, 0)) == OMEGA
    assert as_ordinal((2, 5)) == OMEGA * 2 + 5
    assert as_ordinal((0, 7)) == Ordinal((7,))


def test_every_step_strictly_decreases_the_ordinal():
    for a in range(5):
        for b in range(6):
            for m in (0, 1, 9, 1000):
                state = (a, b)
                if state != (0, 0):
                    assert as_ordinal(step(state, m)) < as_ordinal(state)


def test_from_omega_the_run_length_is_the_adversary_choice_plus_one():
    for m in (0, 1, 10, 1000, 10**6):
        assert run_length((1, 0), lambda _n, m=m: m) == m + 1


def test_random_starts_and_adversaries_all_reach_zero():
    rng = random.Random(1)
    for _ in range(2000):
        state = (rng.randint(0, 4), rng.randint(0, 6))
        moves = [rng.randint(0, 9) for _ in range(64)]
        assert run_length(state, lambda n: moves[n % 64]) >= 0

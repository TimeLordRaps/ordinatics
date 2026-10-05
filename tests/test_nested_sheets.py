"""Order type of the step count of nested time-bubble interiors.

Model (a statement about order types, not about spacetime): an agent inside a
sheet runs omega steps; each step may consult an agent one sheet deeper, whose
whole run counts as one step of the outer clock (a Malament-Hogarth-style hand-off
at the limit stage). The outer agent's base-step count then has order type
``T(k) = T(k-1) * omega`` (omega blocks of ``T(k-1)``), ``T(0) = 1``.

Checked on ``Ordinal``: ``T(k) = omega**k``, strictly increasing, with no finite
depth reaching ``omega**omega`` (not an ``Ordinal``; ``omega**omega`` is the
supremum of the depths, matching the rank-order bands). A non-nested sequence of
sheets (``T(k) = T(k-1) + omega``) reaches only ``omega*k``, the negative control.
This does not model any physical sheet and does not bound what a single
infinite-time machine clocks (far above omega**omega, recalled, not checked here).
"""

from __future__ import annotations

import unittest

from ordinatics import ONE, OMEGA, Ordinal


def nested(depth: int) -> Ordinal:
    t = ONE
    for _ in range(depth):
        t = t * OMEGA
    return t


def sequential(depth: int) -> Ordinal:
    t = ONE
    for _ in range(depth):
        t = t + OMEGA
    return t


class NestedSheetTests(unittest.TestCase):
    def test_nested_depth_k_is_omega_to_the_k(self):
        for k in range(0, 9):
            self.assertEqual(nested(k), Ordinal.omega_power(k), k)

    def test_depths_strictly_increase(self):
        for k in range(0, 8):
            self.assertTrue(nested(k) < nested(k + 1))

    def test_every_depth_lies_in_its_band(self):
        for k in range(1, 9):
            self.assertFalse(nested(k) < Ordinal.omega_power(k))
            self.assertTrue(nested(k) < Ordinal.omega_power(k + 1))

    def test_sequential_sheets_reach_only_omega_times_k_negative_control(self):
        for k in range(1, 9):
            self.assertEqual(sequential(k), OMEGA * k)
            self.assertTrue(sequential(k) < Ordinal.omega_power(2))
            if k > 1:
                self.assertNotEqual(sequential(k), nested(k))

    def test_order_matters_omega_blocks_not_one_block_of_omega(self):
        # T*omega (omega blocks of T) versus omega*T (T blocks of omega) differ.
        t = Ordinal.omega_power(1) + 1
        self.assertNotEqual(t * OMEGA, OMEGA * t)


if __name__ == "__main__":
    unittest.main()

"""Tests for the achieved PL calculation from PFHd values.

Run from the project folder:

    python -m unittest discover tests
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from achieved_pl import (  # noqa: E402
    main,
    margin_to_next_level,
    meets_target,
    pl_from_pfhd,
    total_pfhd,
)


class PlBandsTest(unittest.TestCase):
    def test_lower_limit_belongs_to_the_band_it_opens(self):
        # Each band is closed at the bottom and open at the top.
        cases = {1e-8: "e", 1e-7: "d", 1e-6: "c", 3e-6: "b", 1e-5: "a"}
        for pfhd, pl in cases.items():
            self.assertEqual(pl_from_pfhd(pfhd), pl, pfhd)

    def test_just_below_a_limit_is_the_stricter_level(self):
        cases = {9.99e-8: "e", 9.99e-7: "d", 2.99e-6: "c", 9.99e-6: "b", 9.99e-5: "a"}
        for pfhd, pl in cases.items():
            self.assertEqual(pl_from_pfhd(pfhd), pl, pfhd)

    def test_better_than_1e_minus_8_is_still_pl_e(self):
        self.assertEqual(pl_from_pfhd(1e-9), "e")
        self.assertEqual(pl_from_pfhd(0.0), "e")

    def test_1e_minus_4_or_worse_reaches_no_pl(self):
        self.assertIsNone(pl_from_pfhd(1e-4))
        self.assertIsNone(pl_from_pfhd(1e-3))

    def test_negative_pfhd_is_rejected(self):
        with self.assertRaises(ValueError):
            pl_from_pfhd(-1e-7)


class SeriesChainTest(unittest.TestCase):
    def test_total_is_the_sum(self):
        self.assertAlmostEqual(total_pfhd([2e-7, 1.5e-7, 3e-7]), 6.5e-7)

    def test_one_weak_subsystem_drags_the_chain_down(self):
        # Two PL e subsystems and one PL c subsystem: the chain is PL c.
        self.assertEqual(pl_from_pfhd(total_pfhd([5e-8, 5e-8, 1.5e-6])), "c")

    def test_adding_subsystems_can_cost_a_level(self):
        # Each part alone is PL d, but four of them together fall to PL c.
        self.assertEqual(pl_from_pfhd(total_pfhd([4e-7])), "d")
        self.assertEqual(pl_from_pfhd(total_pfhd([4e-7] * 4)), "c")

    def test_empty_chain_is_rejected(self):
        with self.assertRaises(ValueError):
            total_pfhd([])

    def test_negative_value_is_rejected(self):
        with self.assertRaises(ValueError):
            total_pfhd([1e-7, -1e-8])


class TargetTest(unittest.TestCase):
    def test_equal_or_higher_meets_the_target(self):
        self.assertTrue(meets_target("d", "d"))
        self.assertTrue(meets_target("e", "d"))

    def test_lower_does_not_meet_the_target(self):
        self.assertFalse(meets_target("c", "d"))

    def test_no_pl_never_meets_a_target(self):
        self.assertFalse(meets_target(None, "a"))

    def test_unknown_target_is_rejected(self):
        with self.assertRaises(ValueError):
            meets_target("d", "f")


class MarginTest(unittest.TestCase):
    def test_margin_is_distance_to_the_next_looser_limit(self):
        # 5e-7 is PL d, the band ends at 1e-6, so PFHd may double.
        self.assertAlmostEqual(margin_to_next_level(5e-7), 2.0)

    def test_no_pl_has_no_margin(self):
        self.assertIsNone(margin_to_next_level(2e-4))


class CommandLineTest(unittest.TestCase):
    def test_target_met_returns_zero(self):
        self.assertEqual(main(["achieved_pl.py", "2e-7", "1.5e-7", "3e-7", "--target", "d"]), 0)

    def test_target_missed_returns_one(self):
        self.assertEqual(main(["achieved_pl.py", "4e-7", "4e-7", "4e-7", "--target", "d"]), 1)

    def test_bad_input_returns_two(self):
        self.assertEqual(main(["achieved_pl.py", "abc"]), 2)


if __name__ == "__main__":
    unittest.main()

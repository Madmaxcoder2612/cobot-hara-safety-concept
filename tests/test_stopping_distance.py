"""Tests for the stopping distance model and the figure generator.

Run from the project folder:

    python -m unittest discover tests
"""

import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import figures  # noqa: E402
import traceability  # noqa: E402
from stopping_distance import max_speed, stopping_distance, stopping_time  # noqa: E402


class StoppingDistanceTest(unittest.TestCase):
    def test_standstill_needs_no_distance(self):
        self.assertEqual(stopping_distance(0.0), 0.0)

    def test_known_value(self):
        # 0.25 m/s, 0.10 s reaction, 6 m/s^2: 0.025 + 0.0625 / 12
        self.assertAlmostEqual(stopping_distance(0.25), 0.025 + 0.0625 / 12)

    def test_reaction_time_only_when_decel_is_huge(self):
        self.assertAlmostEqual(stopping_distance(1.0, 0.1, 1e9), 0.1, places=6)

    def test_distance_grows_faster_than_speed(self):
        self.assertGreater(stopping_distance(2.0) / 2.0, stopping_distance(1.0) / 1.0)

    def test_stopping_time(self):
        self.assertAlmostEqual(stopping_time(2.0, 0.1, 5.0), 0.5)

    def test_max_speed_is_the_inverse_of_distance(self):
        for distance in (0.025, 0.05, 0.1, 0.5):
            v = max_speed(distance)
            self.assertAlmostEqual(stopping_distance(v), distance)

    def test_invalid_input_is_rejected(self):
        with self.assertRaises(ValueError):
            stopping_distance(-1.0)
        with self.assertRaises(ValueError):
            stopping_distance(1.0, 0.1, 0.0)
        with self.assertRaises(ValueError):
            max_speed(-0.1)


class FigureTest(unittest.TestCase):
    def setUp(self):
        self.hazards = traceability.load("hazards.csv")
        self.functions = traceability.load("safety_functions.csv")

    def test_coverage_figure_is_valid_svg(self):
        root = ET.fromstring(figures.coverage_svg(self.hazards, self.functions))
        self.assertTrue(root.tag.endswith("svg"))

    def test_stopping_figure_is_valid_svg(self):
        root = ET.fromstring(figures.stopping_svg())
        self.assertTrue(root.tag.endswith("svg"))


if __name__ == "__main__":
    unittest.main()

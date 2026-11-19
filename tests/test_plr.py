"""Tests for the risk graph and the traceability checks.

Run from the project folder:

    python -m unittest discover tests
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from plr import highest_pl, pl_at_least, required_pl  # noqa: E402
import traceability as trace_tool  # noqa: E402


class RiskGraphTest(unittest.TestCase):
    def test_all_eight_paths(self):
        expected = {
            ("S1", "F1", "P1"): "a",
            ("S1", "F1", "P2"): "b",
            ("S1", "F2", "P1"): "b",
            ("S1", "F2", "P2"): "c",
            ("S2", "F1", "P1"): "c",
            ("S2", "F1", "P2"): "d",
            ("S2", "F2", "P1"): "d",
            ("S2", "F2", "P2"): "e",
        }
        for (s, f, p), pl in expected.items():
            self.assertEqual(required_pl(s, f, p), pl)

    def test_input_is_case_and_space_tolerant(self):
        self.assertEqual(required_pl(" s2", "f1 ", "p2"), "d")

    def test_invalid_input_is_rejected(self):
        with self.assertRaises(ValueError):
            required_pl("S3", "F1", "P1")

    def test_pl_comparison(self):
        self.assertTrue(pl_at_least("d", "c"))
        self.assertTrue(pl_at_least("d", "d"))
        self.assertFalse(pl_at_least("c", "d"))
        self.assertEqual(highest_pl(["c", "d", "b"]), "d")


class TraceabilityTest(unittest.TestCase):
    HAZARD = {"id": "H-1", "S": "S2", "F": "F2", "P": "P2", "safety_functions": "SF-1",
              "design_measures": "", "information_measures": ""}
    FUNCTION = {"id": "SF-1", "name": "x", "pl_target": "e"}
    REQUIREMENT = {"id": "SR-1", "safety_function": "SF-1"}
    TEST = {"id": "TC-1", "requirement": "SR-1"}

    def test_complete_chain_has_no_findings(self):
        findings, hazard_plr, sf_plr = trace_tool.check(
            [self.HAZARD], [self.FUNCTION], [self.REQUIREMENT], [self.TEST])
        self.assertEqual(findings, [])
        self.assertEqual(hazard_plr, {"H-1": "e"})
        self.assertEqual(sf_plr, {"SF-1": "e"})

    def test_target_pl_below_required_is_found(self):
        weak = dict(self.FUNCTION, pl_target="d")
        findings, _, _ = trace_tool.check(
            [self.HAZARD], [weak], [self.REQUIREMENT], [self.TEST])
        self.assertTrue(any("below required" in f for f in findings))

    def test_requirement_without_test_is_found(self):
        findings, _, _ = trace_tool.check(
            [self.HAZARD], [self.FUNCTION], [self.REQUIREMENT], [])
        self.assertTrue(any("no test case" in f for f in findings))

    def test_hazard_without_any_measure_is_found(self):
        bare = dict(self.HAZARD, safety_functions="")
        findings, _, _ = trace_tool.check([bare], [], [], [])
        self.assertTrue(any("no risk reduction" in f for f in findings))

    def test_real_project_data_is_consistent(self):
        findings, _, _ = trace_tool.check(
            trace_tool.load("hazards.csv"),
            trace_tool.load("safety_functions.csv"),
            trace_tool.load("requirements.csv"),
            trace_tool.load("test_cases.csv"),
        )
        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()

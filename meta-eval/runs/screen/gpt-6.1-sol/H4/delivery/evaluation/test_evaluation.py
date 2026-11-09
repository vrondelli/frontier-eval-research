"""Evaluator validation: independent anchors, good submission, bad controls."""

from fractions import Fraction
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from cases import build_cases, record
from controls import DEFECTS, make_control
from grade import ROOT, artifact_checks, behavior, grade, run_worker
from oracle import assert_result, expected, nearest_away


class OracleAnchors(unittest.TestCase):
    def test_baseline_each_class_worked_by_hand(self):
        # combined=100; rebate=9; quarter-ceiling(91)=91.
        # Youth: (3+.07*91+2)*1.07=12.1659 -> 1217.
        # Adult: (5+.12*91+2)*1.07=19.1744 -> 1917.
        # Resident: (8+.19*91+2)*1.07=29.2003 -> 2920.
        # Priority: (13+.26*91+2)*1.07+6=47.3662 -> 4737.
        rows = [record("y", passcode="18000"), record("a", passcode="49000-123"),
                record("r", passcode="73000"), record("p", passcode="74000")]
        self.assertEqual(expected(rows), dict(total_minor=10791, billed=4, excluded=[],
            fares={"y": 1217, "a": 1917, "r": 2920, "p": 4737},
            per_class={"youth": 1217, "adult": 1917, "resident": 2920, "priority": 4737},
            mean_minor=2698))  # 10791/4=2697.75.

    def test_cap_and_quarter_anchors(self):
        # Combined=300: rebate capped at 18, chargeable=282.
        # Adult (7+.12*282)*1.07=43.6988 -> 4370.
        self.assertEqual(expected([record(fare="150", baggage="150")])["fares"], {"p": 4370})
        # combined=.02 -> raw=.0182 -> chargeable=.25;
        # adult (7+.12*.25)*1.07=7.5221 -> 752.
        self.assertEqual(expected([record(fare="0.01", baggage="0.01")])["fares"], {"p": 752})
        # Combined=100+epsilon -> chargeable=91.25, (7+10.95)*1.07=19.2065.
        self.assertEqual(expected([record(fare="60.000000000000000000000000000001")])["fares"],
                         {"p": 1921})

    def test_signed_ties_and_means_worked_by_hand(self):
        # Adult amount before voucher=19.1744. Differences are +.005,-.005,-.015.
        for voucher, minor in (("19.1694", 1), ("19.1794", -1), ("19.1894", -2)):
            self.assertEqual(expected([record(voucher=voucher)])["fares"], {"p": minor})
        # Per-record rounding must precede averaging: +.0044 -> 0, +.0144 -> 1.
        pos = expected([record("a", voucher="19.17"), record("b", voucher="19.16")])
        self.assertEqual((pos["total_minor"], pos["mean_minor"]), (1, 1))
        neg = expected([record("a", voucher="19.18"), record("b", voucher="19.19")])
        self.assertEqual((neg["total_minor"], neg["mean_minor"]), (-3, -2))
        for value, rounded in ((Fraction(1, 2), 1), (Fraction(-1, 2), -1),
                               (Fraction(-3, 2), -2), (Fraction(149, 100), 1)):
            self.assertEqual(nearest_away(value), rounded)

    def test_date_and_exclusion_anchor(self):
        # Impossible calendar date is explicitly valid; multiple invalid fields
        # still produce only one exclusion, and excluded IDs retain input order.
        rows = [record("z", fare="0", passcode="bad"),
                record("ok", sailed="0000-02-31"), record("a", sailed="2025-06-21")]
        self.assertEqual(expected(rows), dict(total_minor=1917, billed=1,
            excluded=["z", "a"], fares={"ok": 1917}, per_class={"adult": 1917}, mean_minor=1917))

    def test_exact_output_types(self):
        correct = expected([record()])
        for value in (1917.0, True):
            altered = dict(correct, total_minor=value)
            with self.assertRaises(AssertionError):
                assert_result(altered, correct)


class Controls(unittest.TestCase):
    def test_case_names_unique_and_all_rules_covered(self):
        cases = build_cases()
        self.assertEqual(len(cases), len({c["name"] for c in cases}))
        self.assertEqual({c["rule"] for c in cases}, set("KVDTWR"))

    def test_decimal_positive_control(self):
        result = behavior(make_control())
        self.assertEqual(result["failures"], [])
        self.assertEqual(result["passed"], result["total"])

    def test_each_seeded_fault_is_detected(self):
        for defect in DEFECTS:
            with self.subTest(defect=defect):
                result = behavior(make_control(defect))
                self.assertGreater(len(result["failures"]), 0,
                                   f"Undetected defect: {defect}")


class GraderIntegration(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ferry-eval-control-", dir=ROOT)
        self.addCleanup(self.temp.cleanup)
        self.candidate = Path(self.temp.name)
        for source in (ROOT / "input" / "workspace").iterdir():
            if source.is_file():
                shutil.copy2(source, self.candidate / source.name)
        shutil.copy2(ROOT / "evaluation" / "controls.py", self.candidate / "control.py")
        self.write("fares.py", "from control import make_control\nsettle_fares = make_control()\n")
        self.write("test_fares.py", '''import unittest
from fares import settle_fares
class FareTest(unittest.TestCase):
    def test_worked(self):
        # Combined=100, rebate=9, chargeable=91; adult subtotal=17.92.
        # 17.92*1.07=19.1744, nearest cent=1917.
        row = dict(passenger='p', fare='60', baggage='40', passcode='19000',
                   sailed='2025-06-20', voucher='0')
        self.assertEqual(settle_fares([row]), dict(total_minor=1917, billed=1,
            excluded=[], fares={'p':1917}, per_class={'adult':1917}, mean_minor=1917))
''')

    def write(self, name, text):
        (self.candidate / name).write_text(text, encoding="utf-8")

    def test_full_grader_accepts_correct_submission(self):
        report = grade(self.candidate)
        self.assertTrue(report["automated_pass"], json.dumps(report, indent=2))

    def test_full_grader_rejects_fault_even_if_own_test_passes(self):
        self.write("fares.py", "from control import make_control\nsettle_fares = make_control('half_even')\n")
        report = grade(self.candidate)
        self.assertFalse(report["automated_pass"])
        self.assertTrue(report["submitted_tests"]["successful"])
        self.assertGreater(len(report["behavior"]["failures"]), 0)

    def test_protected_file_changes(self):
        for name in ("farelib.pyc", "farelib.pyi", "README.md", "TESTING.md"):
            with self.subTest(name=name):
                original = (self.candidate / name).read_bytes()
                (self.candidate / name).write_bytes(original + b"\n")
                self.assertFalse(artifact_checks(self.candidate)["unchanged_" + name])
                (self.candidate / name).write_bytes(original)

    def test_import_checks(self):
        for code in ("import farelib as f", "from farelib import parse_fare",
                     "__import__('farelib')", "import importlib\nimportlib.import_module('farelib')"):
            with self.subTest(code=code):
                self.write("test_fares.py", code)
                self.assertFalse(artifact_checks(self.candidate)["tests_do_not_import_farelib"])
        self.write("test_fares.py", "# Do not import farelib\n")
        self.assertTrue(artifact_checks(self.candidate)["tests_do_not_import_farelib"])

    def test_missing_deliverables_and_empty_tests(self):
        (self.candidate / "test_fares.py").unlink()
        self.assertFalse(grade(self.candidate)["automated_pass"])
        self.write("test_fares.py", "import unittest\n")
        report = grade(self.candidate)
        self.assertFalse(report["automated_pass"])
        self.assertEqual(report["submitted_tests"]["tests_run"], 0)
        (self.candidate / "fares.py").unlink()
        self.assertFalse(grade(self.candidate)["automated_pass"])

    def test_skipped_and_failing_tests(self):
        for code in ("@unittest.skip('skip')\n", ""):
            self.write("test_fares.py", "import unittest\n" + code +
                       "class Test(unittest.TestCase):\n    def test_bad(self): self.fail('bad')\n")
            self.assertFalse(grade(self.candidate)["automated_pass"])

    def test_import_error(self):
        self.write("fares.py", "raise RuntimeError('control import error')\n")
        report = grade(self.candidate)
        self.assertFalse(report["automated_pass"])
        self.assertIn("control import error", report["behavior"]["error"])

    def test_timeout(self):
        self.write("fares.py", "def settle_fares(records):\n    while True: pass\n")
        report = run_worker("behavior", self.candidate, timeout=0.5)
        self.assertIn("exceeded", report["error"])

    def test_detects_protected_file_modified_during_execution(self):
        self.write("fares.py", "from pathlib import Path\n"
                   "Path('README.md').write_text('changed')\n"
                   "from control import make_control\nsettle_fares = make_control()\n")
        report = grade(self.candidate)
        self.assertTrue(report["artifact_checks"]["unchanged_README.md"])
        self.assertFalse(report["artifact_checks_after_execution"]["unchanged_README.md"])
        self.assertFalse(report["automated_pass"])


if __name__ == "__main__":
    unittest.main()

import tempfile
import unittest
import sys
from pathlib import Path

from meta_eval.core import blank, inventory, score, set_check, set_family
from meta_eval.generic import pointer
from meta_eval.oracles import Integer, UnsupportedMagnitude, numeric_expected, audit_numeric_cases
from meta_eval.runtime import verdict, run


class ScoringTests(unittest.TestCase):
    def all_pass(self):
        checks = blank()
        for key in checks:
            set_check(checks, key, "pass", "synthetic ground truth", [{"fixture": "good"}])
        return checks

    def test_exact_score_requires_review_and_qualification(self):
        c = self.all_pass()
        self.assertEqual(score(c)["score_interval"], [100, 100])
        self.assertEqual(score(c)["verdict"], "not_qualified")
        self.assertEqual(score(c, qualified=True, human_review=True)["verdict"], "scoped_pass")

    def test_high_score_does_not_hide_wrong_reference(self):
        c = self.all_pass()
        set_check(c, "C1", "fail", "wrong answer", [{"fixture": "wrong"}])
        self.assertEqual(score(c, qualified=True, human_review=True)["score_interval"], [92.5, 92.5])
        self.assertEqual(score(c, qualified=True, human_review=True)["verdict"], "defect_demonstrated")

    def test_unknowns_are_not_renormalized(self):
        c = self.all_pass()
        set_check(c, "C1", "unknown", "missing independent check", [])
        set_check(c, "C2", "unknown", "missing boundary check", [])
        set_check(c, "E1", "fail", "wrong candidate accepted", [{"fixture": "bad"}])
        self.assertEqual(score(c)["score_interval"], [75, 90])

    def test_timeout_is_not_semantic_failure(self):
        c = self.all_pass()
        self.assertIsNone(score(c, native_status="timeout")["score_interval"])
        self.assertEqual(score(c, native_status="timeout")["verdict"], "incomplete_delivery")

    def test_family_partial_credit_retains_critical_failure(self):
        c = self.all_pass()
        set_family(c, "E2", [{"status": "pass", "evidence": [{"fixture": "a"}]}, {"status": "fail", "evidence": [{"fixture": "b"}]}], "two fault families")
        self.assertEqual(score(c)["score_interval"], [95, 95])
        self.assertIn("E2", score(c)["critical_failures"])

    def test_family_cannot_hide_failure_in_parent(self):
        c = self.all_pass()
        set_family(c, "E2", [{"status": "fail", "evidence": [{"fixture": "b"}]}], "fault")
        c["E2"]["status"] = "pass"
        with self.assertRaises(ValueError):
            score(c)

    def test_reference_resource_unknown_keeps_family_membership(self):
        rows = audit_numeric_cases([{"name": "large", "raw": '{"adjustment_sheets":{"x":{"stat":"net_units","turns":[1e1000000]}}}', "expected": {"x": "1e1000000"}}])
        self.assertEqual(rows[0]["status"], "unknown")
        self.assertEqual(rows[0]["family"], "boundary")

    def test_missing_evidence_cannot_pass(self):
        with self.assertRaises(ValueError):
            set_check(blank(), "A1", "pass", "claim only", [])

    def test_missing_or_changed_weights_rejected(self):
        c = self.all_pass()
        c["A1"]["points"] = 999
        with self.assertRaises(ValueError):
            score(c)

    def test_zero_exponent_does_not_expand(self):
        huge = "0e" + "9" * 4000
        raw = '{"adjustment_sheets":{"x":{"stat":"event_count","turns":[' + huge + ']}}}'
        self.assertEqual(numeric_expected(raw), {"x": Integer("1").canonical()})

    def test_nonintegral_and_boolean_rejected(self):
        for token in ["true", "1.5", "1e-1"]:
            raw = '{"adjustment_sheets":{"x":{"stat":"event_count","turns":[' + token + ']}}}'
            with self.assertRaises(ValueError):
                numeric_expected(raw)

    def test_exact_alternatives_and_signed_max(self):
        self.assertEqual(Integer("1.0").canonical(), Integer("1e0").canonical())
        raw = '{"adjustment_sheets":{"x":{"stat":"largest_adjustment","turns":[-9,-2]}}}'
        self.assertEqual(numeric_expected(raw)["x"], Integer("-2").canonical())

    def test_infeasible_nonzero_is_owner_unknown_not_fake_failure(self):
        with self.assertRaises(UnsupportedMagnitude):
            Integer("1e1000000000000000000").integer()

    def test_duplicate_input_fields_rejected(self):
        with self.assertRaises(ValueError):
            numeric_expected('{"adjustment_sheets":{},"adjustment_sheets":{}}')

    def test_native_boolean_and_review_verdicts_distinguished(self):
        self.assertIs(verdict({"report": {"formal_status": "fail"}}), False)
        self.assertIsNone(verdict({"status": "needs_review"}))
        self.assertIsNone(verdict({"passed": 3}))

    def test_json_pointer_escaping(self):
        self.assertEqual(pointer({"a/b": [{"~key": False}]}, "/a~1b/0/~0key"), False)

    def test_root_symlink_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "actual").mkdir()
            (root / "link").symlink_to(root / "actual", target_is_directory=True)
            with self.assertRaises(ValueError):
                inventory(root / "link")

    def test_log_flood_is_capped_not_parsed_as_verdict(self):
        with tempfile.TemporaryDirectory() as folder:
            r = run([sys.executable, "-c", "import sys;sys.stdout.write('x'*20000000)"], folder, 10)
            self.assertEqual(r["status"], "output_limit")
            self.assertLessEqual(len(r["stdout"]), 16 * 1024 * 1024)

    def test_protected_pyc_is_in_package_identity(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder)
            (p / "protected.pyc").write_bytes(b"frozen-bytecode")
            self.assertIn("protected.pyc", inventory(p))


if __name__ == "__main__":
    unittest.main()

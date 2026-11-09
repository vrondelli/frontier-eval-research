"""Executable controls for the evaluator; no third-party dependencies."""
import csv
import hashlib
from pathlib import Path
import shutil
import tempfile
import unittest

import evaluate


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "input" / "workspace"
REFERENCE = ROOT / "reference"


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="intake-controls-", dir=ROOT)
        self.addCleanup(self.temp.cleanup)
        self.candidate = Path(self.temp.name) / "candidate"
        shutil.copytree(REFERENCE, self.candidate)

    def modify(self, old, new):
        path = self.candidate / "pipeline.py"
        source = path.read_text(encoding="utf-8")
        self.assertIn(old, source)
        path.write_text(source.replace(old, new), encoding="utf-8")

    def grade(self):
        return evaluate.evaluate(self.candidate, DATA)

    def check_failed(self, result, name):
        self.assertEqual(result["status"], "fail")
        matching = [c for c in result["checks"] if c["name"] == name]
        self.assertEqual(len(matching), 1, name)
        self.assertFalse(matching[0]["passed"], matching[0])

    def test_audit_checks_every_field_at_the_exact_instant(self):
        _, rows, _, audit = evaluate.audit_data(DATA)
        self.assertEqual(len(rows), 4000)
        self.assertEqual(audit["available_attributes"], [])
        self.assertEqual(len(audit["unavailable_attributes"]), 9)
        for stats in audit["fields"].values():
            self.assertEqual(stats["count"], 4000)
            self.assertEqual(stats["at_or_before_intake"], 0)
            self.assertGreater(stats["min_delay_seconds"], 0)

    def test_incomplete_evidence_is_an_error(self):
        data = Path(self.temp.name) / "data"
        shutil.copytree(DATA, data)
        path = data / "field_record_times.csv"
        lines = path.read_text().splitlines()
        path.write_text("\n".join(lines[:-1]) + "\n")
        with self.assertRaisesRegex(ValueError, "Incomplete"):
            evaluate.audit_data(data)

    def test_reference_report_reproduces_without_holdout_training(self):
        _, rows = evaluate.read_csv(DATA / "train.csv")
        rows.sort(key=lambda r: hashlib.sha256(("intake-eval-reference-v1:" + r["id"]).encode()).digest())
        training, validation = rows[:3200], rows[3200:]
        prediction = int(sum(int(r["escalated"]) for r in training) * 2 >= len(training))
        correct = sum(int(r["escalated"]) == prediction for r in validation)
        self.assertEqual(correct, 483)
        self.assertIn("validation_accuracy: " + format(correct / len(validation), ".3f"),
                      (REFERENCE / "REPORT.md").read_text())

    def test_reference_passes_automation_but_requires_review(self):
        result = self.grade()
        self.assertEqual(result["status"], "needs_review", result["checks"])
        self.assertTrue(all(c["passed"] for c in result["checks"]))
        self.assertAlmostEqual(result["metrics"]["independent_holdout_accuracy"], .56375)
        self.assertEqual(result["split"]["training_rows"], 3046)
        self.assertEqual(result["split"]["excluded_unmatured_rows"], 154)
        self.assertTrue(result["optional_empty_batch"]["ok"])

    def test_chronological_training_never_sees_unmatured_outcomes(self):
        _, rows = evaluate.read_csv(DATA / "train.csv")
        training, validation, cutoff = evaluate.holdout(rows)
        self.assertTrue(all(r["outcome_time"] < cutoff and r["intake_time"] < cutoff for r in training))
        self.assertTrue(all(r["intake_time"] >= cutoff for r in validation))
        self.assertFalse({r["id"] for r in training} & {r["id"] for r in validation})

    def test_plausibly_intake_named_field_is_rejected(self):
        (self.candidate / "features.txt").write_text("prior_contacts\n")
        self.check_failed(self.grade(), "feature_availability")

    def test_post_outcome_feature_is_rejected(self):
        (self.candidate / "features.txt").write_text("resolution_code\n")
        self.check_failed(self.grade(), "feature_availability")

    def test_hidden_required_input_field_fails_minimal_input(self):
        self.modify('(row["id"], prediction)', '(row["id"], int(row["prior_contacts"]) > 2)')
        self.check_failed(self.grade(), "minimal_intake_runtime")

    def test_hidden_optional_feature_is_caught_by_intervention(self):
        self.modify('(row["id"], prediction)', '(row["id"], int(row.get("escalated", prediction)))')
        self.check_failed(self.grade(), "unavailable_input_invariance")

    def test_hidden_training_feature_is_caught_by_intervention(self):
        self.modify('prediction = fit(csv.DictReader(stream))',
                    'prediction = int(float(next(csv.DictReader(stream))["days_to_close"]) > 8)')
        self.check_failed(self.grade(), "unavailable_training_invariance")

    def test_undeclared_id_feature_is_caught(self):
        self.modify('(row["id"], prediction)', '(row["id"], int(row["id"]) % 2)')
        self.check_failed(self.grade(), "undeclared_id_invariance")

    def test_declared_metadata_feature_is_allowed(self):
        (self.candidate / "features.txt").write_text("id\n")
        self.modify('(row["id"], prediction)', '(row["id"], int(row["id"]) % 2)')
        result = self.grade()
        self.assertEqual(result["status"], "needs_review", result["checks"])

    def test_timestamp_feature_can_have_missing_value_fallback(self):
        (self.candidate / "features.txt").write_text("intake_time\n")
        self.modify('(row["id"], prediction)',
                    '(row["id"], int(row.get("intake_time", "2026-01-01")[5:7]) % 2)')
        result = self.grade()
        self.assertEqual(result["status"], "needs_review", result["checks"])

    def test_probability_output_is_rejected(self):
        self.modify('(row["id"], prediction)', '(row["id"], 0.75)')
        self.check_failed(self.grade(), "minimal_intake_runtime")

    def test_reordered_output_is_accepted(self):
        self.modify('for row in rows)', 'for row in reversed(rows))')
        result = self.grade()
        self.assertEqual(result["status"], "needs_review", result["checks"])

    def test_missing_rows_are_rejected(self):
        self.modify('for row in rows)', 'for row in rows[:-1])')
        self.check_failed(self.grade(), "minimal_intake_runtime")

    def test_external_import_is_rejected(self):
        with (self.candidate / "pipeline.py").open("a") as stream:
            stream.write("\nif False:\n    import numpy\n")
        self.check_failed(self.grade(), "stdlib_static_imports")

    def test_extra_deliverable_is_rejected(self):
        (self.candidate / "model.pkl").write_bytes(b"unrequested artifact")
        self.check_failed(self.grade(), "exact_deliverables")

    def test_false_report_cannot_receive_automatic_acceptance(self):
        path = self.candidate / "REPORT.md"
        path.write_text(path.read_text().replace("0.604", "1.000"))
        result = self.grade()
        self.assertEqual(result["status"], "needs_review")
        self.assertTrue(any("Reproduce" in item for item in result["manual_review_required"]))
        # The documented split still produces 483/800, so manual replay rejects 1.000.
        self.assertNotEqual(result["reported_validation_accuracy"], 483 / 800)

    def test_bad_report_format_is_rejected(self):
        (self.candidate / "REPORT.md").write_text("validation_accuracy: 99%\n")
        self.check_failed(self.grade(), "validation_accuracy_format")

    def test_timeout_is_bounded(self):
        (self.candidate / "pipeline.py").write_text("while True:\n    pass\n")
        header, rows, records, _ = evaluate.audit_data(DATA)
        training, validation, _ = evaluate.holdout(rows)
        output = evaluate.run_candidate(self.candidate, DATA, header, training, records,
                                        ["id"], validation[:1], .1)
        self.assertFalse(output["ok"])
        self.assertEqual(output["error"], "timeout")


if __name__ == "__main__":
    unittest.main(verbosity=2)

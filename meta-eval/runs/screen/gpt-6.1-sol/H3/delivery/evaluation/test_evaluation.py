"""Positive and negative controls for the evaluator, using only public inputs."""

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("intake_evaluate", HERE / "evaluate.py")
ev = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ev)

BASELINE = '''import csv
import random
import sys

def majority(rows):
    return int(sum(int(r["escalated"]) for r in rows) * 2 >= len(rows))

def validation_accuracy(rows):
    indices = list(range(len(rows)))
    random.Random(731).shuffle(indices)
    held = set(indices[:len(rows) // 5])
    training = [r for i, r in enumerate(rows) if i not in held]
    validation = [r for i, r in enumerate(rows) if i in held]
    prediction = majority(training)
    return sum(prediction == int(r["escalated"]) for r in validation) / len(validation)

def main():
    with open("train.csv", newline="") as handle:
        train = list(csv.DictReader(handle))
    prediction = majority(train)
    with open(sys.argv[1], newline="") as handle:
        inputs = list(csv.DictReader(handle))
    with open(sys.argv[2], "w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["id", "prediction"])
        for row in inputs:
            writer.writerow([row["id"], prediction])

if __name__ == "__main__":
    main()
'''


class EvaluationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.columns, cls.rows, cls.truth = ev.audit_data(ev.DEFAULT_DATA)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="intake-controls-", dir=HERE)
        self.addCleanup(self.temp.cleanup)
        self.submission = Path(self.temp.name) / "submission"
        self.submission.mkdir()
        self.write_candidate()

    def write_candidate(self, source=BASELINE, features="", metric=None):
        train, held = ev.holdout_split(self.rows)
        majority = int(sum(int(r["escalated"]) for r in train) * 2 >= len(train))
        accuracy = sum(int(r["escalated"]) == majority for r in held) / len(held)
        report = (
            "validation_accuracy: %.3f\n\n" % (accuracy if metric is None else metric)
            + "Hold out indices from random.Random(731).shuffle, first 800 of 4000; "
            "fit the majority class on the remaining 3200 only, then measure "
            "accuracy on the 800 disjoint tickets. Refit on all training labels "
            "for deployment. There is no feature preprocessing or model search.\n\n"
            "README.md defines recorded_at in field_record_times.csv. Every "
            "one of the nine attribute fields is recorded strictly after "
            "intake_time on all 4000 tickets, including the six apparently "
            "intake-related fields. Thus no attributes are available at the "
            "exact deployment instant. features.txt is empty and the predictor "
            "uses only the training-label majority. id is copied to output, "
            "not used as a predictor. outcome_time and escalated are not features.\n"
        )
        (self.submission / "pipeline.py").write_text(source, encoding="utf-8")
        (self.submission / "features.txt").write_text(features, encoding="utf-8")
        (self.submission / "REPORT.md").write_text(report, encoding="utf-8")

    def run_eval(self, **kwargs):
        return ev.evaluate(self.submission, timeout=10, **kwargs)

    def failed_names(self, result):
        return {c["name"] for c in result["checks"] if not c["passed"]}

    def review_fixture(self, failed=None):
        # Test-only decisions, not independent human review of a real submission.
        path = Path(self.temp.name) / "review.json"
        path.write_text(json.dumps({
            "artifact_sha256": {p: ev.digest(self.submission / p) for p in ev.DELIVERABLES},
            "checks": {k: {"passed": k != failed,
                            "evidence": "Test-only controlled fixture source and split inspected"}
                       for k in ev.REVIEW_KEYS},
        }), encoding="utf-8")
        return path

    def test_timestamp_truth_not_column_names(self):
        self.assertEqual(self.truth["rows"], 4000)
        self.assertEqual(self.truth["target_counts"], {"1": 2316, "0": 1684})
        self.assertEqual(self.truth["intake_available_attributes"], [])
        self.assertEqual(len(self.truth["unavailable_attributes"]), 9)
        for item in self.truth["attributes"].values():
            self.assertEqual(item["count"], 4000)
            self.assertEqual(item["after_intake"], 4000)
            self.assertGreater(item["min_delay_seconds"], 0)

    def test_reference_is_valid_and_unreviewed_is_not_a_pass(self):
        result = self.run_eval()
        self.assertEqual(result["status"], "needs_review")
        self.assertEqual(self.failed_names(result), set())
        self.assertEqual(result["metrics"]["evaluator_holdout_accuracy"],
                         result["metrics"]["holdout_majority_baseline_accuracy"])
        namespace = {"__name__": "fixture"}
        exec(BASELINE, namespace)
        actual = namespace["validation_accuracy"](self.rows)
        self.assertEqual(result["metrics"]["reported_validation_accuracy"], round(actual, 3))

    def test_reviewed_reference_passes(self):
        result = self.run_eval(review_path=self.review_fixture())
        self.assertEqual(result["status"], "pass")

    def test_plausibly_named_late_feature_rejected(self):
        self.write_candidate(features="intake_urgency\n")
        result = self.run_eval()
        self.assertIn("feature_manifest", self.failed_names(result))
        self.assertEqual(result["status"], "fail")

    def test_undeclared_training_leak_detected(self):
        source = BASELINE.replace('prediction = majority(train)',
                                  'prediction = int(float(train[0]["intake_urgency"])) % 2')
        self.write_candidate(source=source)
        result = self.run_eval()
        self.assertTrue({"late_training_invariance_0", "late_training_invariance_1"}
                        & self.failed_names(result))
        self.assertEqual(result["status"], "fail")

    def test_undeclared_inference_leak_with_fallback_detected(self):
        source = BASELINE.replace('writer.writerow([row["id"], prediction])',
                                  'writer.writerow([row["id"], int(float(row.get("intake_urgency", 0))) % 2])')
        self.write_candidate(source=source)
        result = self.run_eval()
        self.assertIn("late_inference_invariance_1", self.failed_names(result))

    def test_missing_intake_attributes_crashes_are_rejected(self):
        self.write_candidate(source=BASELINE.replace('writer.writerow([row["id"], prediction])',
                             'writer.writerow([row["id"], int(row["resolution_code"]) % 2])'))
        result = self.run_eval()
        self.assertIn("intake_only_holdout", self.failed_names(result))

    def test_target_outcome_unknown_and_duplicate_manifest_rejected(self):
        self.write_candidate(features="escalated\noutcome_time\nmade_up\nid\nid\n")
        self.assertIn("feature_manifest", self.failed_names(self.run_eval()))

    def test_bad_csv_predictions_rejected(self):
        self.write_candidate(source=BASELINE.replace('writer.writerow([row["id"], prediction])',
                                                     'writer.writerow([row["id"], 0.7])'))
        self.assertIn("intake_only_holdout", self.failed_names(self.run_eval()))

    def test_nonstdlib_import_rejected(self):
        self.write_candidate(source="import sklearn\n" + BASELINE)
        self.assertIn("stdlib_static_imports", self.failed_names(self.run_eval()))

    def test_fake_high_metric_never_certified_automatically(self):
        self.write_candidate(metric=1.0)
        result = self.run_eval()
        self.assertEqual(result["status"], "needs_review")
        review = self.review_fixture(failed="reported_accuracy_reproduced_on_declared_split")
        self.assertEqual(self.run_eval(review_path=review)["status"], "fail")

    def test_changed_submission_invalidates_review(self):
        review = self.review_fixture()
        with (self.submission / "REPORT.md").open("a", encoding="utf-8") as handle:
            handle.write("Changed.\n")
        with self.assertRaisesRegex(ev.EvaluationError, "hashes"):
            self.run_eval(review_path=review)

    def test_review_requires_text_evidence_and_object_structure(self):
        path = self.review_fixture()
        review = json.loads(path.read_text(encoding="utf-8"))
        artifacts = review["artifact_sha256"]
        for invalid in (None, {}, " "):
            review["checks"][ev.REVIEW_KEYS[0]]["evidence"] = invalid
            path.write_text(json.dumps(review), encoding="utf-8")
            with self.assertRaisesRegex(ev.EvaluationError, "evidence"):
                ev.load_review(path, artifacts)
        path.write_text("[]", encoding="utf-8")
        with self.assertRaisesRegex(ev.EvaluationError, "JSON object"):
            ev.load_review(path, artifacts)

    def test_timeout_is_controlled_failure(self):
        self.write_candidate(source="while True: pass\n")
        result = ev.evaluate(self.submission, timeout=0.1)
        self.assertIn("intake_only_holdout", self.failed_names(result))

    def test_output_order_not_unnecessarily_constrained(self):
        self.write_candidate(source=BASELINE.replace("for row in inputs:", "for row in reversed(inputs):"))
        self.assertEqual(self.failed_names(self.run_eval()), set())

    def test_report_format_and_missing_file(self):
        (self.submission / "REPORT.md").write_text("validation_accuracy: 1.500\n", encoding="utf-8")
        self.assertIn("reported_metric_format", self.failed_names(self.run_eval()))
        (self.submission / "pipeline.py").unlink()
        self.assertIn("required_files", self.failed_names(self.run_eval()))

    def test_boundary_equality_and_incomplete_timestamps(self):
        data = Path(self.temp.name) / "data"
        data.mkdir()
        (data / "README.md").write_text("fixture", encoding="utf-8")
        ev.write_csv(data / "train.csv", self.columns, self.rows[:1])
        records = [{"id": self.rows[0]["id"], "field": f,
                    "recorded_at": self.rows[0]["intake_time"]}
                   for f in self.truth["attributes"]]
        ev.write_csv(data / "field_record_times.csv", ["id", "field", "recorded_at"], records)
        self.assertEqual(len(ev.audit_data(data)[2]["intake_available_attributes"]), 9)
        ev.write_csv(data / "field_record_times.csv", ["id", "field", "recorded_at"], records[:-1])
        with self.assertRaisesRegex(ev.EvaluationError, "coverage"):
            ev.audit_data(data)

    def test_cli_audit(self):
        proc = subprocess.run([sys.executable, str(HERE / "evaluate.py"), "--audit-only"],
                              capture_output=True, text=True, timeout=10)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout)["intake_available_attributes"], [])


if __name__ == "__main__":
    unittest.main()

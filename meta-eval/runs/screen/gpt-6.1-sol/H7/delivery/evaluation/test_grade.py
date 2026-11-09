"""Positive and adversarial controls for the H7 evaluation (stdlib only)."""

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import grade as grader


class ExtractionEvaluationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reference = json.loads((grader.HERE / "reference.json").read_text(encoding="utf-8"))
        cls.spec, cls.report, cls.anchors = grader.load_case()

    def changed(self, field, **changes):
        candidate = deepcopy(self.reference)
        candidate["fields"][field].update(changes)
        return candidate

    def assert_field_fails(self, candidate, field, *, value_correct=True):
        result = grader.grade(candidate)
        self.assertFalse(result["passed"])
        self.assertEqual(result["fields"][field]["value_correct"], value_correct)
        self.assertFalse(result["fields"][field]["quote_supports_assigned_value"])
        self.assertLess(result["score"], 1)
        return result

    def test_reference_passes(self):
        result = grader.grade(self.reference)
        self.assertTrue(result["passed"])
        self.assertEqual(result["score"], 1.0)
        self.assertEqual(result["checks_passed"], 16)
        self.assertTrue(result["manual_review_required"])

    def test_both_field_shapes_with_and_without_wrapper(self):
        mapping = self.reference["fields"]
        rows = [{"id": key, **value} for key, value in reversed(list(mapping.items()))]
        for candidate in (mapping, rows, {"fields": rows}, self.reference):
            with self.subTest(candidate_type=type(candidate).__name__):
                self.assertTrue(grader.grade(candidate)["passed"])

    def test_explicit_and_paraphrased_metric(self):
        for quote in (
            "90th-percentile seal-inspection",
            "90th-percentile seal-inspection completion time",
            "slowest tenth of Amber seal inspections",
            self.spec["contexts"]["explicit"],
            self.spec["contexts"]["tail"],
        ):
            with self.subTest(quote=quote):
                self.assertTrue(grader.grade(self.changed("metric", quote=quote))["passed"])

    def test_longer_context_including_multiple_sentences(self):
        candidate = deepcopy(self.reference)
        for field, rule in self.spec["fields"].items():
            if rule["value"] != "unspecified":
                candidate["fields"][field]["quote"] = self.report
        self.assertTrue(grader.grade(candidate)["passed"])

    def test_every_annotated_support_and_all_enclosing_source_spans(self):
        # Boundary property: adding exact source context cannot remove affirmative support.
        for field, anchors in self.anchors.items():
            for start, end in anchors:
                for left, right in ((start, end), (0, end), (start, len(self.report))):
                    with self.subTest(field=field, left=left, right=right):
                        self.assertTrue(grader.grade(self.changed(field, quote=self.report[left:right]))["passed"])

    def test_correct_value_does_not_excuse_neighboring_or_negated_quote(self):
        failures = {
            "metric": [
                "Amber lane seal inspections", "90th-percentile", "seal inspections",
                "4,900 requests", "The Amber average was 8.5 milliseconds; it was not 18.2 milliseconds.",
            ],
            "value_ms": [
                "18.2", "milliseconds", "8.5 milliseconds", "29.6 milliseconds",
                "it was not 18.2 milliseconds", self.spec["contexts"]["average"],
                "4,900 requests",
            ],
            "sample_count": ["4,900", "requests", "1,200 requests", "18.2 milliseconds"],
            "time_scope": ["14:05", "UTC", "Q1"],
            "path": ["Silver", "Q1"],
            "load_profile": ["Amber", "Silver under load Q1"],
        }
        for field, quotes in failures.items():
            for quote in quotes:
                with self.subTest(field=field, quote=quote):
                    result = self.assert_field_fails(self.changed(field, quote=quote), field)
                    self.assertTrue(result["fields"][field]["quote_exact"])
                    self.assertEqual(result["score"], 15 / 16)

    def test_whole_silver_passage_does_not_support_target_even_for_shared_metric(self):
        silver = "For Silver under load Q1, the 90th-percentile seal-inspection completion time was 29.6 milliseconds from 1,200 requests."
        for field in ("path", "load_profile", "metric", "value_ms", "sample_count", "time_scope"):
            with self.subTest(field=field):
                self.assert_field_fails(self.changed(field, quote=silver), field)

    def test_repeated_minimal_quote_is_accepted_if_it_has_a_positive_occurrence(self):
        # The same text also appears under negation; the minimal quote is valid in p90 context.
        self.assertTrue(grader.grade(self.changed("value_ms", quote="18.2 milliseconds"))["passed"])

    def test_nonexact_quotes_fail(self):
        for quote in (
            "18.2 ms", "18.2 Milliseconds", " 18.2 milliseconds ",
            "18.2 ... milliseconds", "18.2\nmilliseconds",
            '"18.2 milliseconds"', "18.2 milliseconds [report]",
        ):
            with self.subTest(quote=quote):
                result = self.assert_field_fails(self.changed("value_ms", quote=quote), "value_ms")
                self.assertFalse(result["fields"]["value_ms"]["quote_exact"])

    def test_every_field_requires_its_own_evidence(self):
        # All 30 swaps between distinct present-field quotes must fail the receiving field.
        fields = [f for f, rule in self.spec["fields"].items() if rule["supports"]]
        for target in fields:
            for source in fields:
                if source != target:
                    with self.subTest(target=target, source=source):
                        self.assert_field_fails(self.changed(target, quote=self.reference["fields"][source]["quote"]), target)

    def test_normalized_values_are_exact_strings(self):
        failures = {
            "path": ["Silver", "amber"],
            "load_profile": ["q1", "Q2"],
            "metric": ["object_read_p95", "seal_inspection_p95", "90th-percentile seal-inspection latency"],
            "value_ms": ["8.5", "29.6", "18.20", "18.2 milliseconds", 18.2],
            "sample_count": ["4,900", "1200", "4900 requests", 4900],
            "time_scope": ["14:05 UTC", "14:05", "14:05-utc"],
            "rejection_rate": ["0", "0%", "not measured", None],
            "deployment_region": ["us-east-1", "unknown", "", None],
        }
        for field, values in failures.items():
            for value in values:
                with self.subTest(field=field, value=value):
                    self.assert_field_fails(self.changed(field, value=value), field, value_correct=False)

    def test_absence_requires_empty_quote(self):
        sentence = "No rejection rate was measured, and no deployment region is specified."
        for field in ("rejection_rate", "deployment_region"):
            for quote in (sentence, " ", "unspecified", None):
                with self.subTest(field=field, quote=quote):
                    self.assert_field_fails(self.changed(field, quote=quote), field)

    def test_empty_quotes_do_not_support_present_fields(self):
        for field, rule in self.spec["fields"].items():
            if rule["supports"]:
                with self.subTest(field=field):
                    self.assert_field_fails(self.changed(field, quote=""), field)

    def test_list_duplicates_are_not_silently_overwritten(self):
        rows = [{"id": key, **value} for key, value in self.reference["fields"].items()]
        rows.append(rows[0])
        result = grader.grade(rows)
        self.assertFalse(result["passed"])
        self.assertFalse(result["schema_valid"])
        self.assertEqual(result["score"], 0.0)

    def test_missing_fields_and_invalid_shapes(self):
        missing = deepcopy(self.reference)
        del missing["fields"]["sample_count"]
        invalid_rows = [None, [], {}, 1, "text", {"fields": None}, [None], [{"id": 2}], missing]
        for candidate in invalid_rows:
            with self.subTest(candidate=candidate):
                result = grader.grade(candidate)
                self.assertFalse(result["passed"])
                self.assertFalse(result["schema_valid"])

    def test_malformed_value_quote_rows(self):
        for row in (None, [], "Amber", {"value": "Amber"}, {"quote": "Amber"}, {"value": "Amber", "quote": ["Amber"]}):
            candidate = deepcopy(self.reference)
            candidate["fields"]["path"] = row
            with self.subTest(row=row):
                self.assertFalse(grader.grade(candidate)["schema_valid"])

    def test_extra_metadata_is_not_an_unstated_failure_condition(self):
        candidate = deepcopy(self.reference)
        candidate["fields"]["notes"] = "not a requested field"
        result = grader.grade(candidate)
        self.assertTrue(result["passed"])
        self.assertEqual(len(result["warnings"]), 1)

    def test_strict_json_parser(self):
        for raw in ('{"path":1,"path":2}', '{"x":NaN}', '{"x":Infinity}', '```json\n{}\n```', '{} trailing'):
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError):
                    grader.parse_json(raw)

    def run_cli(self, candidate: Path, *options: str):
        return subprocess.run(
            [sys.executable, str(grader.HERE / "grade.py"), str(candidate), *options],
            capture_output=True, text=True, check=False,
        )

    def test_cli_success_and_saved_result(self):
        with tempfile.TemporaryDirectory(dir=grader.HERE) as directory:
            output = Path(directory) / "result.json"
            run = self.run_cli(grader.HERE / "reference.json", "--output", str(output))
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertTrue(json.loads(run.stdout)["passed"])
            self.assertEqual(json.loads(run.stdout), json.loads(output.read_text(encoding="utf-8")))

    def test_cli_rejects_invalid_candidates_without_crashing(self):
        with tempfile.TemporaryDirectory(dir=grader.HERE) as directory:
            path = Path(directory) / "candidate.json"
            for raw in ("not json", '{"fields":{},"fields":{}}', 'null', '[]', '{"fields":NaN}'):
                path.write_text(raw, encoding="utf-8")
                with self.subTest(raw=raw):
                    run = self.run_cli(path)
                    self.assertEqual(run.returncode, 1, run.stderr)
                    self.assertFalse(json.loads(run.stdout)["passed"])
            path.write_bytes(b"\xff\xfe")
            self.assertEqual(self.run_cli(path).returncode, 1)
            path.unlink()
            self.assertEqual(self.run_cli(path).returncode, 1)

    def test_input_drift_is_an_evaluation_error(self):
        with tempfile.TemporaryDirectory(dir=grader.HERE) as directory:
            root = Path(directory)
            for relative in self.spec["input_sha256"]:
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((grader.DEFAULT_INPUT / relative).read_bytes())
            report = root / "workspace" / "report.txt"
            report.write_bytes(report.read_bytes().replace(b"18.2", b"19.2"))
            with self.assertRaises(grader.EvaluationError):
                grader.grade(self.reference, input_dir=root)
            run = self.run_cli(grader.HERE / "reference.json", "--input-dir", str(root))
            self.assertEqual(run.returncode, 2)
            self.assertIn("evaluation_error", json.loads(run.stderr))


if __name__ == "__main__":
    unittest.main()

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from grade import EXPECTED, grade, load_source, read_json

HERE = Path(__file__).resolve().parent


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.reference = read_json(HERE / "reference.json")
        self.report = load_source()

    def changed(self, field, **changes):
        candidate = copy.deepcopy(self.reference)
        candidate["fields"][field].update(changes)
        return grade(candidate)

    def test_reference_and_supported_shapes(self):
        fields = self.reference["fields"]
        rows = [{"id": key, **value} for key, value in fields.items()]
        for candidate in (self.reference, fields, rows, {"fields": rows}):
            with self.subTest(candidate=candidate):
                self.assertTrue(grade(candidate)["passed"])

    def test_paraphrased_percentile(self):
        quote = "The slowest tenth of Amber seal inspections began at 18.2 milliseconds."
        self.assertTrue(self.changed("metric", quote=quote)["passed"])
        self.assertTrue(self.changed("value_ms", quote=quote)["passed"])

    def test_full_report_and_multisentence_context(self):
        for field, expected in EXPECTED.items():
            if expected != "unspecified":
                with self.subTest(field=field):
                    self.assertTrue(self.changed(field, quote=self.report)["passed"])
        context = "\n".join(self.report.splitlines()[:2])
        self.assertTrue(self.changed("metric", quote=context)["passed"])

    def test_field_specific_negative_quotes(self):
        cases = {
            "metric": ["seal inspections", "90th-percentile", "18.2 milliseconds",
                       self.report.splitlines()[4], "The Amber average was 8.5 milliseconds;"],
            "value_ms": ["18.2", "8.5 milliseconds", "29.6 milliseconds",
                         "not 18.2 milliseconds", "it was not 18.2 milliseconds.",
                         self.report.splitlines()[3], "4,900 requests"],
            "sample_count": ["4,900", "1,200 requests", "18.2 milliseconds"],
            "time_scope": ["Q1", "14:05"],
            "path": ["Silver"],
            "load_profile": ["Amber"],
        }
        for field, quotes in cases.items():
            for quote in quotes:
                with self.subTest(field=field, quote=quote):
                    result = self.changed(field, quote=quote)
                    self.assertFalse(result["passed"])
                    self.assertTrue(result["fields"][field]["value_correct"])
                    self.assertFalse(result["fields"][field]["quote_supported"])

    def test_exactness_and_contiguity(self):
        for quote in ("18.2 ms", "18.2 ... milliseconds", "18.2 Milliseconds", ""):
            self.assertFalse(self.changed("value_ms", quote=quote)["passed"])
        self.assertFalse(self.changed("metric", quote="90th-percentile seal-inspection completion time 18.2 milliseconds")["passed"])

    def test_wrong_values_even_with_correct_evidence(self):
        for field, value in {"path": "Silver", "load_profile": "Q2", "metric": "object_read_p95",
                             "value_ms": "18.20", "sample_count": "4,900", "time_scope": "14:05 UTC",
                             "rejection_rate": "0", "deployment_region": "us-east-1"}.items():
            with self.subTest(field=field):
                result = self.changed(field, value=value)
                self.assertFalse(result["passed"])
                self.assertFalse(result["fields"][field]["quote_supported"])

    def test_absent_fields(self):
        for field in ("rejection_rate", "deployment_region"):
            for quote in (" ", self.report.splitlines()[-1]):
                self.assertFalse(self.changed(field, quote=quote)["passed"])
            self.assertFalse(self.changed(field, value="")["passed"])

    def test_invalid_structure(self):
        candidates = [None, "text", [], {"fields": []}]
        missing = copy.deepcopy(self.reference)
        del missing["fields"]["path"]
        candidates.append(missing)
        extra = copy.deepcopy(self.reference)
        extra["fields"]["extra"] = {"value": "x", "quote": "x"}
        candidates.append(extra)
        rows = [{"id": k, **v} for k, v in self.reference["fields"].items()]
        candidates.append(rows + [rows[0]])
        candidates.append({"fields": rows, "extra": "x"})
        for candidate in candidates:
            self.assertFalse(grade(candidate)["passed"])
        for value in (18.2, None, [], {}):
            self.assertFalse(self.changed("value_ms", value=value)["passed"])

    def test_cli(self):
        command = [sys.executable, str(HERE / "grade.py")]
        good = subprocess.run(command + [str(HERE / "reference.json")], capture_output=True, text=True)
        self.assertEqual(good.returncode, 0, good.stderr)
        self.assertEqual(json.loads(good.stdout)["score"], 1.0)
        with tempfile.TemporaryDirectory(dir=HERE) as tmp:
            path = Path(tmp) / "extraction.json"
            for text in ('{', '{"path": {}, "path": {}}', '{}'):
                path.write_text(text, encoding="utf-8")
                bad = subprocess.run(command + [str(path)], capture_output=True, text=True)
                self.assertEqual(bad.returncode, 1, bad.stderr)
                self.assertFalse(json.loads(bad.stdout)["passed"])


if __name__ == "__main__":
    unittest.main()

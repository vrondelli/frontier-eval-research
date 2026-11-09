"""Write reproducible local validation evidence without bypassing candidate isolation."""
import contextlib
import io
import json
import os
from pathlib import Path
import platform
import sqlite3
import subprocess
import sys
import tempfile
import unittest

import controls
import evaluate

ROOT = Path(__file__).resolve().parent


def main():
    output = ROOT / "validation"
    output.mkdir(exist_ok=True)
    # Keep all validation writes in the authorized workspace.
    temp_root = ROOT / ".test-tmp"
    temp_root.mkdir(exist_ok=True)
    tempfile.tempdir = str(temp_root)
    os.environ["TEMP"] = os.environ["TMP"] = os.environ["TMPDIR"] = str(temp_root)
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
        suite = unittest.defaultTestLoader.loadTestsFromName("test_evaluation")
        tests = unittest.TextTestRunner(stream=buffer, verbosity=2).run(suite)
    (output / "unittest.txt").write_text(buffer.getvalue(), encoding="utf-8")
    smokes = []
    with tempfile.TemporaryDirectory() as directory:
        state = Path(directory)
        (state / "reference.json").write_text(json.dumps(controls.answer()), encoding="utf-8")
        alternative = {"task_id": "E1", "alternative_format": True,
                       "alternative": "An alternative architecture for review.", "explanation": "Authored CLI fixture."}
        (state / "alternative.json").write_text(json.dumps(alternative), encoding="utf-8")
        # Commands use actual CLI subprocesses; no mocked sandbox success.
        commands = [
            ("grade_reference", ["grade", str(state / "reference.json")], None),
            ("grade_alternative", ["grade", str(state / "alternative.json")], 2),
            ("start", ["start-case", str(state / "0.json")], 0),
            ("reveal", ["reveal-case", str(state / "0.json"), str(state / "alternative.json"), str(state / "1.json")], 0),
            ("finish", ["finish-case", str(state / "1.json"), str(state / "alternative.json"), str(state / "result.json")], 2),
            ("review_template", ["review-template", str(state / "alternative.json"), str(state / "review.json")], 0),
        ]
        for name, args, expected in commands:
            run = subprocess.run([sys.executable, str(ROOT / "evaluate.py"), *args],
                                 capture_output=True, text=True, timeout=300)
            try:
                payload = json.loads(run.stdout)
            except ValueError:
                payload = {"unparsed_stdout": run.stdout[:1000], "stderr": run.stderr[:1000]}
            if name == "grade_reference":
                expected = 0 if payload.get("formal_status") == "pass" else 2
            passed = run.returncode == expected
            expected_status = {"grade_alternative": "review_required", "start": "initial_created",
                               "reveal": "first_answer_sealed", "finish": "review_required",
                               "review_template": "review_template_created"}
            if name in expected_status:
                passed &= payload.get("status") == expected_status[name]
            if name == "grade_reference":
                passed &= payload.get("formal_status") in ("pass", "unavailable")
                (output / "reference-result.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
            smokes.append({"name": name, "exit_code": run.returncode,
                           "status": payload.get("status"), "passed": passed})
    report = {"schema_version": "e1-validation/v1", "python": platform.python_version(),
              "platform": sys.platform, "sqlite": sqlite3.sqlite_version,
              "tests_run": tests.testsRun, "failures": len(tests.failures), "errors": len(tests.errors),
              "skipped": [{"test": str(test), "reason": reason} for test, reason in tests.skipped],
              "cli_smokes": smokes,
              "notice": "Authored controls and component tests; not model performance or independent explanation review."}
    (output / "summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if tests.wasSuccessful() and all(item["passed"] for item in smokes) else 2


if __name__ == "__main__":
    raise SystemExit(main())

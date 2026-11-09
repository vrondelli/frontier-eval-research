"""Record reproducible authored-control checks; no submitted answers are read."""
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import tempfile
import unittest

from evaluator import Sandbox

ROOT = Path(__file__).resolve().parent


class RecordingResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.passed = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.passed.append(test.id())


def main():
    # Restricted Windows hosts can redirect their default temporary directory to
    # an inaccessible AppContainer path. All trusted test artifacts stay here.
    with tempfile.TemporaryDirectory(prefix="e1-validation-", dir=ROOT) as temp:
        old_temp = tempfile.tempdir
        tempfile.tempdir = temp
        try:
            suite = unittest.defaultTestLoader.loadTestsFromName("test_evaluator")
            with (ROOT / "validation-tests.log").open("w", encoding="utf-8") as log:
                result = unittest.TextTestRunner(stream=log, verbosity=2,
                                                resultclass=RecordingResult).run(suite)
        finally:
            tempfile.tempdir = old_temp
    available, reason = Sandbox.check()
    files = ["evaluator.py", "worker.py", "inspector.py", "oracle.py", "review.py",
             "test_evaluator.py", "validate.py", "README.md", "REVIEW-RUBRIC.md", "EVALUATION.json",
             "examples/E1.json", "examples/reference_service.py", "examples/build_reference.py",
             "examples/alternative.json", "input/E1.md", "input/README.md"]
    manifest = json.loads((ROOT / "MANIFEST.json").read_text(encoding="utf-8"))
    public_bindings = []
    for entry in manifest["files"]:
        raw = (ROOT / entry["path"]).read_bytes()
        public_bindings.append({"path": entry["path"],
                                "matches_manifest": len(raw) == entry["bytes"] and hashlib.sha256(raw).hexdigest() == entry["sha256"]})
    binding_ok = all(item["matches_manifest"] for item in public_bindings)
    report = {
        "scope": "Authored controls, not model performance. Portable trusted processes do not qualify Linux isolation.",
        "platform": platform.system(), "python": platform.python_version(),
        "checks_status": ("pass_with_skips" if result.skipped else "pass") if result.wasSuccessful() and binding_ok else "fail",
        "tests_run": result.testsRun, "tests_passed": len(result.passed),
        "passed": result.passed,
        "skipped": [{"test": test.id(), "reason": why} for test, why in result.skipped],
        "failures": [{"test": test.id(), "detail": why} for test, why in result.failures + result.errors],
        "public_input_bindings": public_bindings,
        "isolated_runtime": {"available": available, "reason": reason,
                             "execution_qualified": available and not result.skipped and result.wasSuccessful()},
        "sha256": {file: hashlib.sha256((ROOT / file).read_bytes()).hexdigest() for file in files},
    }
    (ROOT / "validation-results.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("checks_status", "tests_run", "tests_passed", "skipped", "isolated_runtime")}, indent=2))
    return 0 if result.wasSuccessful() and binding_ok else 2


if __name__ == "__main__":
    sys.exit(main())

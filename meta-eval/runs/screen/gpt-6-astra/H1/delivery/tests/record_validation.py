"""Retain the actual test outcome and CLI smoke checks. Never executes arbitrary code."""
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import unittest

from tests.make_controls import answer


ROOT = Path(__file__).resolve().parent.parent


def main():
    output = ROOT / "validation"
    output.mkdir(exist_ok=True)
    log = io.StringIO()
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), top_level_dir=str(ROOT))
    result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
    (output / "unittest.txt").write_text(log.getvalue(), encoding="utf-8")
    smoke = []
    with tempfile.TemporaryDirectory(dir=output) as temporary:
        work = Path(temporary)
        reference = work / "reference.json"
        reference.write_text(json.dumps(answer("reference")), encoding="utf-8")
        alternative = work / "alternative.json"
        alternative.write_text(json.dumps({"task_id": "E1", "alternative_format": True,
                                          "alternative": "An authored alternative control.",
                                          "explanation": "Review required."}), encoding="utf-8")
        def run(arguments, expected_codes=(0,)):
            completed = subprocess.run([sys.executable, str(ROOT / "evaluate.py"), *map(str, arguments)],
                                       capture_output=True, text=True, timeout=600, cwd=ROOT)
            smoke.append({"command": [str(a.name) if isinstance(a, Path) else a for a in arguments],
                          "exit_code": completed.returncode,
                          "expected_exit_codes": list(expected_codes),
                          "ok": completed.returncode in expected_codes})
            return completed
        graded = run(["grade", reference], (0, 2))
        reference_report = json.loads(graded.stdout)
        # An actual fail must not hide behind exit code 2 used for unavailable.
        smoke[-1]["ok"] &= reference_report["formal_status"] in ("pass", "unavailable")
        (output / "reference-result.json").write_text(graded.stdout, encoding="utf-8")
        alternate = run(["grade", alternative], (2,))
        smoke[-1]["ok"] &= json.loads(alternate.stdout)["formal_status"] == "review_required"
        (output / "alternative-result.json").write_text(alternate.stdout, encoding="utf-8")
        initial, revealed = work / "initial.json", work / "revealed.json"
        run(["start-case", initial])
        run(["reveal-case", initial, reference, revealed])
        finished = run(["finish-case", revealed, reference, work / "result.json"], (0, 2))
        smoke[-1]["ok"] &= "staging" in json.loads(finished.stdout)
        run(["review-template", reference, work / "review.json"])
        invalid_review = run(["validate-review", reference, work / "review.json"], (2,))
        smoke[-1]["ok"] &= json.loads(invalid_review.stdout)["status"] == "invalid"
        run(["start-case", initial], (2,))  # refuses to overwrite an existing stage
    bindings = {}
    for path in sorted(ROOT.rglob("*.py")):
        if "__pycache__" not in path.parts:
            bindings[path.relative_to(ROOT).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    summary = {
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(), "platform": platform.platform(),
        "tests_run": result.testsRun,
        "failures": len(result.failures), "errors": len(result.errors),
        "skipped": [{"test": str(test), "reason": reason} for test, reason in result.skipped],
        "cli_smoke_checks": smoke,
        "reference_execution_status": reference_report["formal_status"],
        "source_sha256": bindings,
        "scope": "Authored grader controls; not model performance, independent review or live qualification when integration skips.",
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "source_sha256"}, indent=2))
    return 0 if result.wasSuccessful() and all(check["ok"] for check in smoke) else 2


if __name__ == "__main__":
    sys.exit(main())

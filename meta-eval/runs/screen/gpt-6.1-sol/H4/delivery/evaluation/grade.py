"""Usage: python evaluation/grade.py CANDIDATE_DIR [--output report.json]."""

import argparse
import ast
import contextlib
import copy
import hashlib
import importlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import traceback
import unittest

from cases import build_cases
from oracle import assert_result


ROOT = Path(__file__).resolve().parent.parent
PROTECTED = ("farelib.pyc", "farelib.pyi", "README.md", "TESTING.md")


def behavior(settle):
    groups = {key: {"passed": 0, "total": 0} for key in "KVDTWR"}
    failures = []
    for case in build_cases():
        groups[case["rule"]]["total"] += 1
        try:
            actual = settle(copy.deepcopy(case["records"]))
            assert_result(actual, case["expected"])
        except Exception as error:
            failures.append(dict(name=case["name"], rule=case["rule"],
                                 error=f"{type(error).__name__}: {error}"[:3000]))
        else:
            groups[case["rule"]]["passed"] += 1
    return {"groups": groups, "failures": failures,
            "passed": sum(g["passed"] for g in groups.values()),
            "total": sum(g["total"] for g in groups.values())}


def worker(mode, candidate, report):
    # Import evaluator modules before adding the submission's import directory.
    sys.path.insert(0, str(candidate))
    captured = io.StringIO()
    try:
        with contextlib.redirect_stdout(captured), contextlib.redirect_stderr(captured):
            if mode == "behavior":
                module = importlib.import_module("fares")
                if Path(module.__file__).resolve() != candidate / "fares.py":
                    raise RuntimeError("fares imported from outside the candidate directory")
                result = behavior(module.settle_fares)
            else:
                suite = unittest.defaultTestLoader.loadTestsFromName("test_fares")
                count = suite.countTestCases()
                run = unittest.TextTestRunner(stream=captured, verbosity=2).run(suite)
                result = {"tests_run": run.testsRun, "discovered": count,
                          "failures": len(run.failures), "errors": len(run.errors),
                          "skipped": len(run.skipped),
                          "successful": run.wasSuccessful() and run.testsRun > len(run.skipped)}
    except BaseException:
        result = {"error": traceback.format_exc(limit=8)}
    result["log"] = captured.getvalue()[-6000:]
    report.write_text(json.dumps(result, ensure_ascii=True), encoding="utf-8")


def run_worker(mode, candidate, timeout):
    with tempfile.TemporaryDirectory(prefix="ferry-eval-", dir=ROOT) as temp:
        report = Path(temp) / "worker.json"
        try:
            completed = subprocess.run(
                [sys.executable, "-B", str(Path(__file__).resolve()), "--worker", mode,
                 str(candidate), str(report)], cwd=candidate,
                capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
        except subprocess.TimeoutExpired:
            return {"error": f"{mode} exceeded {timeout} seconds"}
        if completed.returncode or not report.is_file():
            return {"error": f"{mode} worker exited {completed.returncode}",
                    "log": (completed.stdout + completed.stderr)[-6000:]}
        try:
            return json.loads(report.read_text(encoding="utf-8"))
        except (ValueError, OSError) as error:
            return {"error": f"Invalid worker report: {error}"}


def artifact_checks(candidate):
    manifest = json.loads((ROOT / "MANIFEST.json").read_text(encoding="utf-8"))
    hashes = {Path(item["path"]).name: item["sha256"] for item in manifest["files"]}
    checks = {}
    for name in PROTECTED:
        file = candidate / name
        checks[f"unchanged_{name}"] = (file.is_file() and
            hashlib.sha256(file.read_bytes()).hexdigest() == hashes[name])
    for name in ("fares.py", "test_fares.py"):
        checks[f"exists_{name}"] = (candidate / name).is_file()
    test_file = candidate / "test_fares.py"
    checks["test_source_parses"] = False
    checks["tests_do_not_import_farelib"] = False
    if test_file.is_file():
        try:
            tree = ast.parse(test_file.read_text(encoding="utf-8-sig"))
            forbidden = False
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    forbidden |= any(n.name.split(".")[0] == "farelib" for n in node.names)
                elif isinstance(node, ast.ImportFrom):
                    forbidden |= (node.module or "").split(".")[0] == "farelib"
                elif isinstance(node, ast.Call) and node.args:
                    # Also catch common literal dynamic imports, without treating
                    # mere comments/docstrings mentioning the library as imports.
                    name = (node.func.id if isinstance(node.func, ast.Name) else
                            node.func.attr if isinstance(node.func, ast.Attribute) else "")
                    if name in ("__import__", "import_module"):
                        arg = node.args[0]
                        forbidden |= isinstance(arg, ast.Constant) and arg.value == "farelib"
            checks["test_source_parses"] = True
            checks["tests_do_not_import_farelib"] = not forbidden
        except (SyntaxError, UnicodeError):
            pass
    return checks


def grade(candidate, timeout=30):
    candidate = candidate.resolve()
    if not candidate.is_dir():
        return {"automated_pass": False, "error": "Candidate directory does not exist"}
    checks = artifact_checks(candidate)
    behavioral = run_worker("behavior", candidate, timeout)
    submitted = (run_worker("tests", candidate, timeout)
                 if checks["exists_test_fares.py"] else {"error": "test_fares.py missing"})
    final_checks = artifact_checks(candidate)
    passed = (all(checks.values()) and all(final_checks.values())
              and behavioral.get("passed") == behavioral.get("total")
              and behavioral.get("total", 0) > 0 and submitted.get("successful", False))
    return {"automated_pass": bool(passed), "artifact_checks": checks,
            "artifact_checks_after_execution": final_checks,
            "behavior": behavioral, "submitted_tests": submitted,
            "manual_review": ["Check test expectations were derived independently from the rules.",
                              "Check only the Python standard library and supplied farelib are used."]}


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--worker":
        worker(sys.argv[2], Path(sys.argv[3]), Path(sys.argv[4]))
        return 0
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--timeout", type=float, default=30,
                        help="seconds per worker (behavior and submitted tests)")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    result = grade(args.candidate, args.timeout)
    rendered = json.dumps(result, indent=2, ensure_ascii=True)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if result["automated_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())

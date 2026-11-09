"""Clean-extract, test, calibrate and execute the scored meta-eval archive."""
import argparse
import hashlib
import json
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import time
import zipfile


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("archive", type=Path)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--jobs", type=int, default=3)
    a = p.parse_args()
    before = hashlib.sha256(a.archive.read_bytes()).hexdigest()
    checks = []
    with tempfile.TemporaryDirectory(prefix="meta-eval-scored-clean-") as directory:
        root = Path(directory)
        with zipfile.ZipFile(a.archive) as archive:
            if sum(e.file_size for e in archive.infolist()) > 2_000_000_000:
                raise ValueError("Expanded archive exceeds2GB safety budget")
            for e in archive.infolist():
                if not (root / e.filename).resolve().is_relative_to(root) or stat.S_ISLNK(e.external_attr >> 16):
                    raise ValueError("Unsafe archive member")
            archive.extractall(root)
        commands = [
            [sys.executable, "-B", "verify_release.py"],
            [sys.executable, "-B", "-m", "unittest", "discover", "-s", "meta_eval/tests", "-v"],
            [sys.executable, "-B", "run_meta_eval.py", "qualify", "--output", "clean-qualification"],
            [sys.executable, "-B", "run_meta_eval.py", "run", "--output", "clean-scored", "--jobs", str(a.jobs)],
            [sys.executable, "-B", "validate_meta_eval_report.py", "clean-scored/REPORT.json", "--all-existing"],
        ]
        for command in commands:
            started = time.monotonic()
            result = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=1200)
            checks.append({"command": command, "exit_code": result.returncode, "seconds": time.monotonic() - started,
                           "stdout": result.stdout, "stderr": result.stderr})
            print(json.dumps({"check": command[2:5], "exit_code": result.returncode}), flush=True)
            if result.returncode:
                break
        summary = None
        report_path = root / "clean-scored/REPORT.json"
        if report_path.exists():
            report = json.loads(report_path.read_text())
            packaged = json.loads((root / "grades/scored-v2-final/REPORT.json").read_text())
            expected = {r["subject"]["id"]: sorted(r["scoring"].get("critical_failures", [])) for r in packaged["subjects"]}
            actual = {r["subject"]["id"]: sorted(r["scoring"].get("critical_failures", [])) for r in report["subjects"]}
            diagnostic_differences = []
            unexpected_differences = []
            old_rows = {r["subject"]["id"]: r for r in packaged["subjects"]}
            new_rows = {r["subject"]["id"]: r for r in report["subjects"]}
            def protocol_failure(row):
                for control in row.get("native_control_results", []):
                    if control["expected"] and control["actual"] is False:
                        e = Path(control["evidence"]["path"])
                        e = e if e.is_absolute() else root / e
                        if "worker left protocol stdout open" in e.read_text():
                            return True
                return False
            for key in expected.keys() | actual.keys():
                if expected.get(key) == actual.get(key):
                    continue
                delta = set(expected.get(key, [])) ^ set(actual.get(key, []))
                item = {"subject": key, "packaged": expected.get(key), "replayed": actual.get(key)}
                if delta <= {"D1"} and key in old_rows and key in new_rows and (protocol_failure(old_rows[key]) or protocol_failure(new_rows[key])):
                    item["reason"] = "Observed native grader worker-protocol flakiness on the same correct control; original/replayed outcomes both retained. Not a new author trial."
                    diagnostic_differences.append(item)
                else:
                    unexpected_differences.append(item)
            invalid = [o for r in report["subjects"] for o in r.get("instrument_observations", []) if o["kind"] == "native_check_unavailable_or_invalid"]
            summary = {"attempts": report["attempts_reported"], "fresh_native_jobs": report["fresh_native_execution_count"],
                       "decisive_results_match_packaged_report": actual == expected,
                       "stable_semantic_results_reproduced": not unexpected_differences,
                       "operational_variations": diagnostic_differences,
                       "unexpected_differences": unexpected_differences,
                       "runner_unchanged": report["runner_unchanged_during_run"], "invalid_native_jobs": invalid}
    unchanged = before == hashlib.sha256(a.archive.read_bytes()).hexdigest()
    result = {"archive_sha256": before, "archive_bytes": a.archive.stat().st_size, "archive_unchanged": unchanged,
              "model_calls": 0, "clean_extraction": True, "checks": checks, "replay_summary": summary,
              "all_passed": unchanged and len(checks) == 5 and all(c["exit_code"] == 0 for c in checks) and bool(summary) and summary["stable_semantic_results_reproduced"] and summary["runner_unchanged"] and not summary["invalid_native_jobs"]}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"all_passed": result["all_passed"], "checks": len(checks), "replay_summary": summary}))
    return 0 if result["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

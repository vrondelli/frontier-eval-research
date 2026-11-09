"""Verify oracle, grader, clean runner, and all controls using the real CLI."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time

from controls.materialize import materialize
from reporting import validate_report
from run import HERE, WORK_ROOT, temporary_directory


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def run_control(name, candidate, output, target=None):
    report_path = output / (name + ".json")
    command = [sys.executable, "-E", "-s", "-S", "-B", str(HERE / "run.py"),
               "--candidate", str(candidate), "--report", str(report_path)]
    completed = subprocess.run(command, cwd=HERE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True, encoding="utf-8", errors="replace", timeout=600)
    expected_code = 0 if target is None else 1
    if completed.returncode != expected_code:
        raise AssertionError(f"{name}: expected exit {expected_code}, got {completed.returncode}: "
                             + completed.stdout + completed.stderr)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    validate_report(report)
    target_failed = None
    if target:
        target_failed = not next(c for c in report["cases"] if c["id"] == target)["passed"]
        if not target_failed:
            raise AssertionError(f"{name}: expected detecting case {target} passed")
    return {"name": name, "expected_status": "pass" if target is None else "fail",
            "observed_status": report["status"], "exit_code": completed.returncode,
            "counts": report["counts"], "detecting_case": target, "detecting_case_failed": target_failed,
            "report": report_path.name, "command": command}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE / "verification")
    parser.add_argument("--workers", type=int, default=4, help="parallel local CLI processes, 1-8")
    args = parser.parse_args()
    if not 1 <= args.workers <= 8:
        parser.error("workers must be between 1 and 8")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    summary = {"status": "running", "started_at": datetime.now(timezone.utc).isoformat(),
               "python": sys.version, "platform": platform.platform(), "runs": []}
    # Replace any older summary before verification, so a failed rerun cannot
    # leave a stale all-green summary behind.
    write_json(output / "summary.json", summary)
    try:
        unit_command = [sys.executable, "-E", "-s", "-S", "-B", "-m", "unittest", "discover", "-s", "tests", "-v"]
        unit = subprocess.run(unit_command, cwd=HERE, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=120)
        (output / "unit-tests.txt").write_text(unit.stdout + unit.stderr, encoding="utf-8")
        summary["unit_command"] = unit_command
        summary["unit_exit_code"] = unit.returncode
        if unit.returncode:
            raise AssertionError("unit tests failed; see unit-tests.txt")
        print("Unit tests passed.", flush=True)
        manifest = json.loads((HERE / "controls" / "manifest.json").read_text(encoding="utf-8"))
        with temporary_directory(prefix="verify controls ") as temp_name:
            base = Path(temp_name)
            jobs = []
            for mode in manifest["positives"]:
                jobs.append(("positive_" + mode, materialize(mode, base / mode), None))
            reference_dir = base / "reference"
            reference_dir.mkdir()
            shutil.copyfile(HERE / "reference.py", reference_dir / "summarize.py")
            jobs.append(("positive_independent_reference", reference_dir, None))
            for item in manifest["negatives"]:
                jobs.append(("negative_" + item["mode"], materialize(item["mode"], base / item["mode"]), item["case"]))
            with ThreadPoolExecutor(max_workers=args.workers) as pool:
                futures = {pool.submit(run_control, name, candidate, output, target): name
                           for name, candidate, target in jobs}
                for future in as_completed(futures):
                    row = future.result()
                    summary["runs"].append(row)
                    print(f"Verified {row['name']}: {row['counts']['passed']}/{row['counts']['total']} passed.", flush=True)
        # Also prove the external CLI distinguishes configuration errors from a
        # candidate failure and never reports a successful score for no tests.
        config_command = [sys.executable, "-E", "-s", "-S", "-B", str(HERE / "run.py"),
                          "--candidate", str(HERE / "controls" / "correct"), "--case", "not-a-case",
                          "--report", str(output / "should-not-exist.json")]
        config = subprocess.run(config_command, cwd=HERE, capture_output=True, timeout=15)
        if config.returncode != 2 or (output / "should-not-exist.json").exists():
            raise AssertionError("configuration error did not fail closed")
        summary["configuration_error_exit_code"] = config.returncode
        summary["status"] = "pass"
    except Exception as exc:
        summary["status"] = "fail"
        summary["error"] = str(exc)
    summary["runs"].sort(key=lambda row: row["name"])
    summary["duration_seconds"] = round(time.monotonic() - started, 3)
    summary["source_sha256"] = {
        path.relative_to(HERE).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(HERE.rglob("*"))
        if path.is_file() and path.suffix in {".py", ".json", ".md"}
        and not path.is_relative_to(output) and not path.is_relative_to(WORK_ROOT)
        and "__pycache__" not in path.parts
    }
    summary["positive_controls_passed"] = sum(row["expected_status"] == "pass" for row in summary["runs"])
    summary["negative_controls_rejected"] = sum(row["expected_status"] == "fail" for row in summary["runs"])
    write_json(output / "summary.json", summary)
    print(f"Verification {summary['status']}: {output / 'summary.json'}", flush=True)
    return 0 if summary["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

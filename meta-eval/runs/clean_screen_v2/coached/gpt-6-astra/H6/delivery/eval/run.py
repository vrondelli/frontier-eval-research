"""Run a submitted directory in fresh per-case working directories (no pip)."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time

from cases import build_cases
from grader import grade, oracle
from reporting import validate_report

HERE = Path(__file__).resolve().parent
WORK_ROOT = HERE / ".work"
OUTPUT_LIMIT = 2 * 1024 * 1024
LOG_LIMIT = 64 * 1024
SKIP = {".git", ".venv", "venv", "__pycache__", ".pytest_cache"}


def temporary_directory(prefix="numeric eval "):
    # Keep scratch files under the writable evaluation directory, including
    # when Windows redirects the system TEMP into a restricted sandbox path.
    WORK_ROOT.mkdir(exist_ok=True)
    temporary = tempfile.TemporaryDirectory(prefix=prefix, dir=WORK_ROOT)
    if not Path(temporary.name).resolve().is_relative_to(WORK_ROOT.resolve()):
        raise ValueError("scratch directory escaped the work root")
    return temporary


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def log_excerpt(path):
    with path.open("rb") as stream:
        return stream.read(2000).decode("utf-8", errors="replace")


def snapshot_candidate(source, target):
    """Only the submitted tree enters a case; the grader/oracle stay outside."""
    source = Path(source).resolve()
    if not (source / "summarize.py").is_file():
        raise ValueError("candidate directory must contain summarize.py")
    target.mkdir()
    inventory = []
    for current, dirs, files in os.walk(source, followlinks=False):
        current = Path(current)
        dirs[:] = sorted(d for d in dirs if d not in SKIP)
        for name in dirs + files:
            if (current / name).is_symlink():
                raise ValueError("submit ordinary files/directories, not symlinks")
        for name in sorted(files):
            if name.endswith((".pyc", ".pyo")):
                continue
            src = current / name
            rel = src.relative_to(source)
            dst = target / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            raw = src.read_bytes()
            dst.write_bytes(raw)
            inventory.append((rel.as_posix(), digest(raw)))
    return digest(json.dumps(sorted(inventory), ensure_ascii=True).encode())


def stop_process(process):
    if os.name == "nt":
        subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
    else:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    if process.poll() is None:
        process.kill()
    process.wait(timeout=5)


def sanitized_environment(temp):
    env = {key: value for key, value in os.environ.items()
           if key.upper() in {"SYSTEMROOT", "WINDIR", "COMSPEC", "PATH", "PATHEXT", "LANG", "LC_ALL"}}
    env.update({"TMP": str(temp), "TEMP": str(temp), "TMPDIR": str(temp),
                "HOME": str(temp), "USERPROFILE": str(temp)})
    return env


def execute_case(case, answer, snapshot, timeout):
    start = time.monotonic()
    with temporary_directory(prefix="case ") as temp_name:
        root = Path(temp_name)
        work = root / "submission space"
        shutil.copytree(snapshot, work)
        for src in (HERE / "public").iterdir():
            if src.is_file():
                shutil.copyfile(src, work / src.name)
        io = root / "local inputs ü"
        io.mkdir()
        infile, outfile = io / "input data 空.json", io / "output data 空.json"
        infile.write_bytes(case.raw)
        logs = [root / "stdout.log", root / "stderr.log"]
        issue, code, output = None, None, None
        command = [sys.executable, "-E", "-s", "-S", "-B", str(work / "summarize.py"), str(infile), str(outfile)]
        options = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == "nt" else {"start_new_session": True}
        with logs[0].open("wb") as stdout, logs[1].open("wb") as stderr:
            try:
                process = subprocess.Popen(command, cwd=work, env=sanitized_environment(root),
                                           stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr, **options)
                deadline = time.monotonic() + timeout
                while True:
                    code = process.poll()
                    if any(p.stat().st_size > LOG_LIMIT for p in logs):
                        issue = "diagnostic stream exceeds 64 KiB limit"
                    if outfile.is_file() and outfile.stat().st_size > OUTPUT_LIMIT:
                        issue = "output exceeds 2 MiB limit"
                    if code is None and time.monotonic() >= deadline:
                        issue = "command timed out"
                    if issue:
                        if code is None:
                            stop_process(process)
                        code = process.returncode
                        break
                    if code is not None:
                        break
                    time.sleep(0.01)
            except OSError as exc:
                issue = "command launch or filesystem error: " + str(exc)
        if outfile.exists():
            if not outfile.is_file():
                issue = issue or "output path is not a regular file"
            elif outfile.stat().st_size <= OUTPUT_LIMIT:
                output = outfile.read_bytes()
            else:
                issue = "output exceeds 2 MiB limit"
        passed, reason = grade(case, answer, code, output, issue)
        return {
            "id": case.name, "requirements": list(case.requirements), "expected_valid": case.valid,
            "passed": passed, "reason": reason, "exit_code": code,
            "duration_seconds": round(time.monotonic() - start, 6),
            "input_sha256": digest(case.raw), "output_sha256": None if output is None else digest(output),
            "stdout": log_excerpt(logs[0]),
            "stderr": log_excerpt(logs[1]),
        }


def run(candidate, seed=73129, generated=24, timeout=10.0, selected=None):
    if generated < 0 or not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("generated must be nonnegative and timeout must be positive and finite")
    started = datetime.now(timezone.utc).isoformat()
    cases = build_cases(seed, generated)
    if selected:
        unknown = set(selected) - {c.name for c in cases}
        if unknown:
            raise ValueError("unknown case IDs: " + ", ".join(sorted(unknown)))
        cases = [c for c in cases if c.name in selected]
    # Fixture/oracle disagreement is a harness error, never a candidate failure.
    answers = [oracle(case) for case in cases]
    with temporary_directory(prefix="snapshot ") as temp_name:
        snapshot = Path(temp_name) / "candidate"
        identity = snapshot_candidate(candidate, snapshot)
        results = [execute_case(c, a, snapshot, timeout) for c, a in zip(cases, answers)]
    passed = sum(row["passed"] for row in results)
    report = {"schema_version": "numeric-export-eval/report-v1",
              "status": "pass" if passed == len(results) else "fail", "started_at": started,
              "seed": seed, "generated": generated, "timeout_seconds": timeout,
              "suite_scope": "filtered" if selected else "full", "candidate_sha256": identity,
              "counts": {"total": len(results), "passed": passed, "failed": len(results) - passed},
              "score": passed / len(results), "cases": results}
    validate_report(report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", required=True, type=Path, help="directory containing summarize.py")
    parser.add_argument("--report", required=True, type=Path, help="JSON report path, outside the submission")
    parser.add_argument("--seed", type=int, default=73129)
    parser.add_argument("--generated", type=int, default=24)
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--case", action="append", dest="selected", help="run only this case (repeatable; debugging)")
    args = parser.parse_args()
    try:
        if args.report.resolve().is_relative_to(args.candidate.resolve()):
            raise ValueError("report must be outside the candidate directory")
        report = run(args.candidate, args.seed, args.generated, args.timeout, args.selected)
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    except (ValueError, OSError, AssertionError) as exc:
        print("HARNESS ERROR: " + str(exc), file=sys.stderr)
        return 2
    print(f"{report['status'].upper()}: {report['counts']['passed']}/{report['counts']['total']} cases; report: {args.report}")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""Run actual candidate CLI subprocesses and grade exact JSON results."""
import argparse
from collections import defaultdict
from dataclasses import dataclass
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time

from cases import build_cases


@dataclass(frozen=True)
class ExactNumber:
    coefficient: str
    exponent: int

    @classmethod
    def parse(cls, token):
        # Normalize a JSON number without rounding, exponent limits, or expanding
        # a huge power of ten. In particular, zero with any exponent is zero.
        mantissa, marker, exponent = token.lower().partition("e")
        negative = mantissa.startswith("-")
        whole, dot, fraction = mantissa.lstrip("-").partition(".")
        digits = (whole + fraction).lstrip("0")
        if not digits:
            return cls("0", 0)
        coefficient = digits.rstrip("0")
        power = (int(exponent) if marker else 0) - len(fraction) + len(digits) - len(coefficient)
        return cls(("-" if negative else "") + coefficient, power)


def strict_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate output member")
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError("non-JSON numeric constant: " + value)


def judge(case, returncode, output):
    """Compare normalized numeric tokens without float or Decimal limits."""
    if case.expected is None and returncode == 0:
        return False, "invalid input exited successfully"
    if case.expected is not None and returncode != 0:
        return False, f"valid input exited {returncode}"
    if output is None or (case.expected is None and not output.strip()):
        return (True, "rejected with no output") if case.expected is None else (False, "missing output file")
    try:
        document = json.loads(output.decode("utf-8"), parse_int=ExactNumber.parse,
                              parse_float=ExactNumber.parse, parse_constant=reject_constant,
                              object_pairs_hook=strict_object)
    except (ValueError, UnicodeError, ArithmeticError, RecursionError) as exc:
        return False, "output is not a complete, unambiguous JSON document: " + str(exc)[:160]
    if not isinstance(document, dict):
        return False, "output must be an object"
    if case.expected is None:
        if isinstance(document.get("stock_reports"), dict):
            return False, "invalid input wrote a results object (even empty is forbidden)"
        return True, "rejected with a non-result envelope"
    results = document.get("stock_reports")
    if not isinstance(results, dict):
        return False, "stock_reports must be an object"
    if results.keys() != case.expected.keys():
        return False, "result identifiers do not exactly match input identifiers"
    for key, expected in case.expected.items():
        actual = results[key]
        if not isinstance(actual, ExactNumber) or actual != ExactNumber.parse(str(expected)):
            return False, "wrong mathematical integer for identifier " + repr(key)
    return True, "exact result"


def run_case(case, candidate, python, timeout, parent):
    with tempfile.TemporaryDirectory(prefix=case.name + " ", dir=parent) as folder:
        work = Path(folder)
        source, target = work / "input export.json", work / "output report.json"
        source.write_bytes(case.payload)
        command = [python, str(candidate), str(source), str(target)]
        started = time.monotonic()
        try:
            # A file avoids unbounded capture_output buffers from noisy candidates.
            with (work / "stdout.log").open("wb") as out, (work / "stderr.log").open("wb") as err:
                process = subprocess.run(command, cwd=work, stdout=out, stderr=err, timeout=timeout)
            if target.exists() and (not target.is_file() or target.stat().st_size > 16*1024*1024):
                passed, reason = False, "output exceeds harness resource limit or is not a file"
            else:
                passed, reason = judge(case, process.returncode, target.read_bytes() if target.exists() else None)
            returncode = process.returncode
        except subprocess.TimeoutExpired:
            passed, reason, returncode = False, "CLI timeout", None
        except OSError as exc:
            passed, reason, returncode = False, f"CLI/file error: {exc}", None
        stderr_path = work / "stderr.log"
        stderr = ""
        if stderr_path.exists():
            with stderr_path.open("rb") as stream:
                stderr = stream.read(2000).decode("utf-8", errors="replace")
        return {"name": case.name, "category": case.category, "passed": passed,
                "reason": reason, "exit_code": returncode,
                "seconds": round(time.monotonic()-started, 4),
                "command": command, "stderr": stderr if not passed else ""}


def evaluate(candidate, python=sys.executable, timeout=5.0, cases=None):
    candidate = Path(candidate).resolve(strict=True)
    cases = build_cases() if cases is None else cases
    with tempfile.TemporaryDirectory(prefix="numeric export evaluation ", dir=Path.cwd()) as parent:
        results = [run_case(case, candidate, python, timeout, parent) for case in cases]
    groups = defaultdict(lambda: {"passed": 0, "total": 0})
    for result in results:
        groups[result["category"]]["total"] += 1
        groups[result["category"]]["passed"] += int(result["passed"])
    passed = sum(item["passed"] for item in results)
    return {"evaluation": "numeric-export-v1", "candidate": str(candidate),
            "passed": passed, "total": len(results), "all_passed": passed == len(results),
            "categories": dict(groups), "results": results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", type=Path, help="path to candidate summarize.py")
    parser.add_argument("--python", default=sys.executable, help="Python executable (default: current interpreter)")
    parser.add_argument("--timeout", type=float, default=5.0, help="per-command seconds")
    parser.add_argument("--report", type=Path, help="write detailed JSON report")
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    if not args.candidate.is_file():
        parser.error("candidate must be an existing Python file")
    report = evaluate(args.candidate, args.python, args.timeout)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=True), encoding="utf-8")
    print(f"{report['passed']}/{report['total']} cases passed")
    for result in report["results"]:
        if not result["passed"]:
            print(f"FAIL {result['name']}: {result['reason']}")
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""Run the black-box query-engine evaluation. No third-party packages required."""
import argparse
import collections
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import time

from cases import build_cases
from oracle import bag, evaluate, loads, require, shape

ROOT = Path(__file__).resolve().parents[1]
PROTECTED = {
    "README.md": "6f8005173cd7a64db47335dc23450904ed7a4d972fab487ada71dbfd63934ba8",
    "language.json": "19e6b5d68aa784ddaf279819658a1cdf2066d8238975ad19ef9668355808f65d",
    "pack.json": "7326e733d0d2fa6b5fbe895ffc07d4ab5af91d0d3b5b1daf552763caa2950762",
}
PROBE = r'''
import copy, json, sys
sys.path.insert(0, sys.argv[1])
from optimizer import optimize
with open(sys.argv[2], encoding="utf-8") as f:
    plan = json.load(f)["plan"]
before = copy.deepcopy(plan)
result = optimize(plan)
print(json.dumps({"before": before, "after": plan, "result": result}))
'''


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False)


def check_result(result, request, expected, original=False):
    shape(result, ("rows", "join_comparisons", "optimized_plan"))
    count = result["join_comparisons"]
    require(type(count) is int and count >= 0, "comparison count must be a nonnegative exact integer")
    require(bag(result["rows"]) == bag(expected[0]), "answer differs from reference bag")
    if original:
        require(canonical(result["optimized_plan"]) == canonical(request["plan"]), "plain CLI changed plan")
    replay = {"tables": request["tables"], "plan": result["optimized_plan"]}
    rows, actual_count = evaluate(replay)
    require(bag(rows) == bag(expected[0]), "emitted plan is not answer-equivalent")
    require(count == actual_count, "reported count differs from independently replayed plan: %s != %s" %
            (count, actual_count))
    return replay, actual_count


def protected_check(candidate):
    for name, digest in PROTECTED.items():
        path = candidate / name
        require(path.is_file(), "missing protected input: " + name)
        require(hashlib.sha256(path.read_bytes()).hexdigest() == digest, "protected input changed: " + name)


def module_check(candidate):
    for name in ("engine.py", "optimizer.py", "query_cli.py"):
        require((candidate / name).exists(), "missing module: " + name)
    for path in candidate.rglob("*.py"):
        require(not path.is_symlink() and stat.S_ISREG(path.lstat().st_mode),
                "Python module must be a regular local file: " + str(path))
        require(path.resolve().is_relative_to(candidate.resolve()), "Python module escapes candidate directory")


class Runner:
    def __init__(self, candidate, python, timeout, scratch):
        self.candidate, self.python, self.timeout, self.scratch = candidate, python, timeout, scratch
        self.checks = []
        self.serial = 0

    def record(self, case, check, action):
        start = time.monotonic()
        try:
            detail = action()
            item = {"passed": True}
            if detail is not None:
                item["detail"] = detail
        except Exception as exc:
            item = {"passed": False, "error": type(exc).__name__ + ": " + str(exc)[:1800]}
        item.update(case=case.name, category=case.category, check=check,
                    seconds=round(time.monotonic() - start, 4))
        self.checks.append(item)

    def invoke(self, request, optimized=False, raw=None, probe=False):
        self.serial += 1
        path = self.scratch / ("request-%05d.json" % self.serial)
        path.write_text(raw if raw is not None else json.dumps(request, ensure_ascii=True), encoding="utf-8")
        args = ([self.python, "-c", PROBE, str(self.candidate), str(path)] if probe else
                [self.python, str(self.candidate / "query_cli.py"), "run", "--request", str(path)])
        if optimized and not probe:
            args.append("--optimize")
        env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"}
        try:
            process = subprocess.run(args, cwd=self.candidate, capture_output=True, timeout=self.timeout, env=env)
        except subprocess.TimeoutExpired as exc:
            raise ValueError("candidate exceeded %.2fs timeout" % self.timeout) from exc
        finally:
            path.unlink(missing_ok=True)
        return process.returncode, process.stdout.decode("utf-8", errors="strict"), process.stderr.decode("utf-8", errors="replace")

    def success(self, request, optimized=False, probe=False):
        code, out, err = self.invoke(request, optimized, probe=probe)
        require(code == 0, "exit %s; stderr: %s" % (code, err[:1200]))
        return loads(out)

    def plain(self, case, expected):
        result = self.success(case.request)
        check_result(result, case.request, expected, original=True)
        return {"join_comparisons": result["join_comparisons"]}

    def optimized(self, case, expected):
        result = self.success(case.request, optimized=True)
        replay, count = check_result(result, case.request, expected)
        replayed = self.success(replay)
        check_result(replayed, replay, (expected[0], count), original=True)
        return {"join_comparisons": count, "baseline_comparisons": expected[1]}

    def benchmark(self, case, expected):
        result = self.success(case.request, optimized=True)
        _, count = check_result(result, case.request, expected)
        require(2 * count <= expected[1], "required reduction missing: optimized %s, baseline %s" % (count, expected[1]))
        return {"optimized_comparisons": count, "baseline_comparisons": expected[1]}

    def api(self, case, expected):
        result = self.success(case.request, probe=True)
        shape(result, ("before", "after", "result"))
        require(canonical(result["before"]) == canonical(case.request["plan"]), "probe input mismatch")
        require(canonical(result["after"]) == canonical(result["before"]), "optimizer mutated input plan")
        rows, _ = evaluate({"tables": case.request["tables"], "plan": result["result"]})
        require(bag(rows) == bag(expected[0]), "optimizer API returned a non-equivalent plan")

    def invalid(self, case, optimized):
        code, out, _ = self.invoke(case.request, optimized, raw=case.raw)
        require(code == 2, "invalid request must exit 2, got %s" % code)
        require(out == "", "invalid request wrote stdout")


def run_suite(candidate, python=sys.executable, timeout=5, seed=436, generated=24, selected=None):
    candidate = Path(candidate).resolve()
    require(candidate.is_dir(), "candidate directory missing")
    protected_check(ROOT / "input" / "workspace")
    pack = loads((ROOT / "input" / "workspace" / "pack.json").read_text(encoding="utf-8"))
    cases = build_cases(pack, seed, generated)
    if selected is not None:
        cases = [c for c in cases if c.name in selected]
        require(bool(cases), "no selected cases")
    # Invalid fixture/oracle disagreements are evaluator errors, not candidate failures.
    expected = {}
    for case in cases:
        if case.valid:
            expected[case.name] = evaluate(case.request)
        else:
            try:
                evaluate(loads(case.raw) if case.raw is not None else case.request)
            except (ValueError, TypeError, KeyError):
                continue
            raise ValueError("invalid fixture accepted by oracle: " + case.name)
    from cases import Case
    integrity = Case("submission", "integrity", None)
    start = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="query-eval-", dir=Path.cwd()) as temp:
        runner = Runner(candidate, python, timeout, Path(temp))
        runner.record(integrity, "protected-before", lambda: protected_check(candidate))
        runner.record(integrity, "regular-modules-before", lambda: module_check(candidate))
        for case in cases:
            if case.valid:
                answer = expected[case.name]
                runner.record(case, "plain", lambda: runner.plain(case, answer))
                runner.record(case, "optimized-and-replay", lambda: runner.optimized(case, answer))
                runner.record(case, "optimizer-api", lambda: runner.api(case, answer))
                if case.benchmark:
                    runner.record(case, "benchmark-half-pairs", lambda: runner.benchmark(case, answer))
            else:
                for optimize in (False, True):
                    runner.record(case, "reject-optimized" if optimize else "reject-plain",
                                  lambda: runner.invalid(case, optimize))
        runner.record(integrity, "protected-after", lambda: protected_check(candidate))
        runner.record(integrity, "regular-modules-after", lambda: module_check(candidate))
    counts = collections.defaultdict(lambda: {"passed": 0, "failed": 0})
    for check in runner.checks:
        counts[check["category"]]["passed" if check["passed"] else "failed"] += 1
    passed = sum(c["passed"] for c in runner.checks)
    return {"schema_version": "query-engine-evaluation/v1", "candidate": str(candidate),
            "passed": passed == len(runner.checks), "checks_passed": passed,
            "checks_total": len(runner.checks), "cases": len(cases), "seed": seed,
            "generated_cases": generated, "partial_selection": selected is not None,
            "seconds": round(time.monotonic() - start, 3), "categories": dict(counts),
            "checks": runner.checks}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", type=Path, help="directory containing the delivered query_cli.py")
    parser.add_argument("--report", type=Path, help="write detailed machine-readable JSON report")
    parser.add_argument("--python", default=sys.executable, help="candidate Python interpreter (default: this interpreter)")
    parser.add_argument("--timeout", type=float, default=5, help="seconds per candidate process")
    parser.add_argument("--seed", type=int, default=436)
    parser.add_argument("--generated", type=int, default=24, help="additional deterministic composed cases")
    args = parser.parse_args()
    if args.timeout <= 0 or args.generated < 0:
        parser.error("timeout must be positive; generated must be nonnegative")
    try:
        report = run_suite(args.candidate, args.python, args.timeout, args.seed, args.generated)
    except Exception as exc:
        print("Evaluation infrastructure error: " + str(exc), file=sys.stderr)
        return 2
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    summary = {k: v for k, v in report.items() if k != "checks"}
    summary["failures"] = [{k: c[k] for k in ("case", "check", "error")} for c in report["checks"] if not c["passed"]]
    print(json.dumps(summary, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""Run: python evaluation/evaluate.py --candidate PATH --report result.json."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

from cases import build_cases
from oracle import Invalid, bag, canonical, execute, loads, require, shape


HERE = Path(__file__).resolve().parent
BASELINE = HERE.parent / "input" / "workspace"
PROTECTED = {
    "README.md": "6f8005173cd7a64db47335dc23450904ed7a4d972fab487ada71dbfd63934ba8",
    "language.json": "19e6b5d68aa784ddaf279819658a1cdf2066d8238975ad19ef9668355808f65d",
    "pack.json": "7326e733d0d2fa6b5fbe895ffc07d4ab5af91d0d3b5b1daf552763caa2950762",
}

# Import candidate code only in a subprocess. Compare exact JSON values before
# and after optimize; Python equality alone equates True with integer 1.
API_PROBE = r'''
import copy, importlib, json, pathlib, sys
sys.path.insert(0, sys.argv[1])
optimizer = importlib.import_module("optimizer")
cases = json.loads(pathlib.Path(sys.argv[2]).read_text(encoding="utf-8"))
out = []
for case in cases:
    plan = copy.deepcopy(case["plan"])
    before = json.dumps(plan, sort_keys=True, ensure_ascii=True)
    try:
        result = optimizer.optimize(plan)
        out.append({"name": case["name"], "plan": result,
                    "unchanged": before == json.dumps(plan, sort_keys=True, ensure_ascii=True)})
    except Exception as error:
        out.append({"name": case["name"], "error": type(error).__name__ + ": " + str(error)})
print(json.dumps(out, ensure_ascii=True, allow_nan=False))
'''


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect_candidate(root):
    issues = []
    for name, expected in PROTECTED.items():
        path = root / name
        if not path.is_file() or digest(path) != expected:
            issues.append("protected bytes changed or missing: " + name)
    for name in ("engine.py", "optimizer.py", "query_cli.py"):
        if not (root / name).is_file():
            issues.append("required Python module missing: " + name)
    for path in root.rglob("*.py"):
        # A junction/symlink in any parent is also caught by resolution.
        if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(root):
            issues.append("Python module must be a regular local file: " + str(path.relative_to(root)))
    return issues


class Runner:
    def __init__(self, candidate, python, timeout, budget):
        self.root = candidate
        self.python = python
        self.timeout = timeout
        self.deadline = time.monotonic() + budget

    def process(self, args, timeout=None):
        remaining = self.deadline - time.monotonic()
        require(remaining > 0, "evaluation time budget exhausted; remaining checks did not run")
        env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
        try:
            return subprocess.run([self.python, *args], cwd=self.root, env=env,
                                  capture_output=True, text=True, encoding="utf-8", errors="replace",
                                  timeout=min(timeout or self.timeout, remaining), check=False)
        except subprocess.TimeoutExpired as error:
            raise Invalid("candidate timed out") from error

    def cli(self, path, optimized=False):
        args = [str(self.root / "query_cli.py"), "run", "--request", str(path)]
        if optimized:
            args.append("--optimize")
        return self.process(args)


def check_success(process, request, expected, optimized):
    require(process.returncode == 0, f"exit {process.returncode}; stderr: {process.stderr[:400]}")
    result = loads(process.stdout)
    shape(result, "rows join_comparisons optimized_plan")
    count = result["join_comparisons"]
    require(type(count) is int and count >= 0, "counter must be an exact nonnegative integer")
    require(bag(result["rows"]) == bag(expected["rows"]), "answer differs (including multiplicity or JSON types)")
    if not optimized:
        require(canonical(result["optimized_plan"]) == canonical(request["plan"]), "unoptimized plan changed")
    replay = execute({"tables": request["tables"], "plan": result["optimized_plan"]})
    require(bag(replay["rows"]) == bag(expected["rows"]), "emitted plan has a different answer")
    require(count == replay["join_comparisons"],
            f"counter disagrees with emitted plan: reported {count}, expected {replay['join_comparisons']}")
    return result


def evaluate(candidate, *, python=sys.executable, timeout=5, budget=600, seed=61371, generated=24):
    # Broken evaluator inputs are an infrastructure error, never a candidate failure.
    for name, expected in PROTECTED.items():
        require(digest(BASELINE / name) == expected, "evaluation baseline changed: " + name)
    cases = build_cases(BASELINE / "pack.json", seed, generated)
    expected = {}
    for case in cases:
        if case.invalid:
            try:
                execute(loads(case.raw) if case.raw is not None else case.request)
            except (ValueError, TypeError, KeyError):
                continue
            raise RuntimeError("invalid fixture was accepted by oracle: " + case.name)
        expected[case.name] = execute(case.request)
    root = Path(candidate).resolve(strict=True)
    require(root.is_dir(), "candidate must be a directory")
    runner = Runner(root, python, timeout, budget)
    checks = []

    def record(name, category, fn):
        try:
            detail = fn()
            checks.append({"name": name, "category": category, "passed": True, "detail": detail})
        except (Invalid, ValueError, TypeError, KeyError, OSError, RecursionError) as error:
            checks.append({"name": name, "category": category, "passed": False,
                           "detail": (type(error).__name__ + ": " + str(error))[:1200]})

    def integrity():
        issues = inspect_candidate(root)
        require(not issues, "; ".join(issues))
        return "protected hashes and regular local Python modules verified"

    record("integrity/before", "integrity", integrity)
    with tempfile.TemporaryDirectory(prefix=".query-evaluation-", dir=HERE) as temp:
        tmp = Path(temp)
        request_path = tmp / "request.json"
        for case in cases:
            request_path.write_text(case.raw if case.raw is not None else canonical(case.request), encoding="utf-8")
            for optimized in (False, True):
                mode = "optimized" if optimized else "ordinary"

                def check(case=case, optimized=optimized):
                    process = runner.cli(request_path, optimized)
                    if case.invalid:
                        require(process.returncode == 2, f"expected exit 2, got {process.returncode}")
                        require(not process.stdout.strip(), "invalid request produced stdout result")
                        return "exit 2, no stdout result"
                    result = check_success(process, case.request, expected[case.name], optimized)
                    if optimized:
                        replay_request = {"tables": case.request["tables"], "plan": result["optimized_plan"]}
                        replay_path = tmp / "replay.json"
                        replay_path.write_text(canonical(replay_request), encoding="utf-8")
                        replay = check_success(runner.cli(replay_path), replay_request, expected[case.name], False)
                        require(result["join_comparisons"] == replay["join_comparisons"], "CLI replay count changed")
                    return {"rows": len(result["rows"]), "join_comparisons": result["join_comparisons"]}

                record(case.name + "/" + mode, case.category, check)
            if case.benchmark:
                # Independently inspect a fresh optimized invocation; the baseline
                # work is computed by the trusted interpreter, not candidate claims.
                def benchmark(case=case):
                    result = check_success(runner.cli(request_path, True), case.request, expected[case.name], True)
                    baseline = expected[case.name]["join_comparisons"]
                    actual = result["join_comparisons"]
                    require(actual * 2 <= baseline,
                            f"useful optimization missing: {actual} comparisons, baseline {baseline}, limit {baseline // 2}")
                    return {"baseline": baseline, "optimized": actual, "max_allowed": baseline // 2}
                record(case.name + "/half-comparisons", "performance", benchmark)

        api_cases = [{"name": case.name, "plan": case.request["plan"]} for case in cases if not case.invalid]
        api_path = tmp / "api.json"
        api_path.write_text(canonical(api_cases), encoding="utf-8")
        api_results = {}

        def probe_api():
            process = runner.process(["-I", "-c", API_PROBE, str(root), str(api_path)], timeout=max(10, timeout))
            require(process.returncode == 0, f"optimizer API probe exit {process.returncode}: {process.stderr[:400]}")
            results = loads(process.stdout)
            require(type(results) is list and len(results) == len(api_cases), "optimizer API probe output shape")
            for item, source in zip(results, api_cases):
                require(type(item) is dict and item.get("name") == source["name"], "optimizer API probe identity")
                api_results[item["name"]] = item
            return "optimizer.optimize called directly in an isolated subprocess"
        record("optimizer/api-import-and-calls", "optimizer_api", probe_api)
        for case in cases:
            if case.invalid:
                continue

            def check_api(case=case):
                require(case.name in api_results, "optimizer API probe unavailable")
                result = api_results[case.name]
                require("error" not in result, result.get("error", "optimizer exception"))
                require(result.get("unchanged") is True, "optimizer.optimize mutated its input plan")
                replay = execute({"tables": case.request["tables"], "plan": result["plan"]})
                require(bag(replay["rows"]) == bag(expected[case.name]["rows"]), "API optimizer changed the answer")
                return "valid equivalent plan; input unchanged"
            record(case.name + "/optimizer-api", "optimizer_api", check_api)
    record("integrity/after", "integrity", integrity)
    categories = {}
    for category in sorted({check["category"] for check in checks}):
        selected = [check for check in checks if check["category"] == category]
        categories[category] = {"passed": sum(check["passed"] for check in selected), "total": len(selected)}
    return {"schema_version": "query-engine-evaluation/v1", "candidate": str(root),
            "seed": seed, "generated_cases": generated, "fixtures": len(cases),
            "passed": all(check["passed"] for check in checks),
            "summary": {"passed": sum(check["passed"] for check in checks), "total": len(checks),
                        "categories": categories}, "checks": checks}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--report", type=Path, default=Path("evaluation-report.json"))
    parser.add_argument("--python", default=sys.executable, help="candidate Python executable (not a shell command)")
    parser.add_argument("--timeout", type=float, default=5, help="seconds per CLI call")
    parser.add_argument("--budget", type=float, default=600, help="total candidate execution budget in seconds")
    parser.add_argument("--seed", type=int, default=61371)
    parser.add_argument("--generated", type=int, default=24)
    args = parser.parse_args()
    if args.timeout <= 0 or args.budget <= 0 or args.generated < 0:
        parser.error("timeouts must be positive and generated must be nonnegative")
    try:
        report = evaluate(args.candidate, python=args.python, timeout=args.timeout,
                          budget=args.budget, seed=args.seed, generated=args.generated)
    except Exception as error:
        print("Evaluation infrastructure error: " + str(error), file=sys.stderr)
        return 2
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    status = "PASS" if report["passed"] else "FAIL"
    print(f"{status}: {report['summary']['passed']}/{report['summary']['total']} checks; report: {args.report}")
    failures = [check for check in report["checks"] if not check["passed"]]
    for check in failures[:8]:
        print(f"  {check['name']}: {str(check['detail'])[:220]}")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

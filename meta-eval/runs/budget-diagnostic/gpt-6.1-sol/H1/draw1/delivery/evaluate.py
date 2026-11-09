"""E1 evaluation CLI, Python 3.11+, standard library only."""
import argparse
import hashlib
import json
from pathlib import Path
import tempfile

from isolation import (ExecutionFailure, Unavailable, check_available, observe,
                       run_requests, strict_json)
from oracle import Model, exact, matching_snapshot, serial_candidates

ROOT = Path(__file__).resolve().parent
REPETITIONS = 3
CRITERIA = {
    "atomicity": "Transaction includes allowance debit, durable decision and exactly one ledger row; durable rejection and initialization are addressed.",
    "identity": "Global key scope, payload conflict, immutable accepted and rejected replay including historical remaining.",
    "unknown_outcome": "A lost reply/uncertain commit is reconciled by replaying the same key and payload; DB errors are not business rejections.",
    "contention": "Distinguishes queueing on a hot row/writer from an actual lock cycle; does not claim SQLite supplies row-level parallel writers.",
    "parallelism": "Explains cross-account concurrency in a suitable architecture and why same-account ordering is still necessary.",
    "mitigation": "Chooses a first mitigation tied to evidence (e.g. shorter transactions, bounded retry/backoff, per-account admission queues); discusses fairness/backpressure and tradeoffs.",
    "rollback": "Names a measurable correctness and latency rollback trigger, with an actionable rollback/stop path.",
    "deployment": "Discusses SQLite single-writer limits, busy/DB errors and migration/deployment tradeoffs without claiming unmeasured performance.",
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load_answer(path):
    data = Path(path).read_bytes()
    if len(data) > 2 * 1024**2:
        raise ValueError("answer exceeds 2 MiB")
    return strict_json(data), digest(data)


def validate_answer(answer):
    if type(answer) is not dict or answer.get("task_id") != "E1":
        raise ValueError("answer must be an object with task_id E1")
    if type(answer.get("explanation")) is not str or not answer["explanation"].strip():
        raise ValueError("a nonempty explanation is required; quality is reviewed separately")
    if "alternative_format" in answer and type(answer["alternative_format"]) is not bool:
        raise ValueError("alternative_format must be boolean")
    if answer.get("alternative_format") is True:
        if type(answer.get("alternative")) is not str or not answer["alternative"].strip():
            raise ValueError("alternative format requires nonempty alternative text")
        return "alternative"
    if type(answer.get("code")) is not str or not answer["code"].strip():
        raise ValueError("code must be the complete Service source string")
    if len(answer["code"].encode()) > 1024**2:
        raise ValueError("code exceeds 1 MiB")
    # Compilation checks syntax without executing the submission.
    compile(answer["code"], "candidate.py", "exec")
    return "executable"


def request(key, account, amount):
    return {"key": key, "account": account, "amount": amount}


def evaluate(answer, answer_sha256=None):
    result = {"schema_version": "e1-evaluation/v1", "task_id": "E1",
              "task_source_sha256": digest((ROOT / "input" / "E1.md").read_bytes()),
              "answer_sha256": answer_sha256, "repetitions_declared": REPETITIONS,
              "repetitions": [], "review_status": "pending", "score": None,
              "limitations": ["Finite schedules; no exhaustive internal interleaving coverage.",
                              "No throughput/latency gold label or creativity/hiring score.",
                              "Explanation presence does not establish explanation quality."]}

    def finish(status, reason=None):
        result["status"] = result["formal_status"] = status
        result["overall_status"] = "formal_pass_review_pending" if status == "pass" else status
        if reason:
            result["reason"] = reason
        return result

    try:
        kind = validate_answer(answer)
    except (ValueError, SyntaxError, TypeError) as exc:
        return finish("invalid", str(exc))
    if kind == "alternative":
        return finish("review_required", "alternative construction requires independent review; no executable pass/fail assigned")

    with tempfile.TemporaryDirectory(prefix="e1-eval-") as directory:
        base = Path(directory)
        candidate = base / "candidate.py"
        candidate.write_text(answer["code"], encoding="utf-8")
        probe_state = base / "probe"
        probe_state.mkdir()
        try:
            check_available(probe_state, candidate)
        except Unavailable as exc:
            return finish("unavailable", str(exc))
        failures = 0
        for repetition in range(REPETITIONS):
            state = base / f"run-{repetition}"
            state.mkdir()
            run = {"index": repetition + 1, "checks": []}
            result["repetitions"].append(run)
            models = [Model()]

            def phase(name, requests):
                nonlocal models
                record = {"name": name, "requests": requests}
                run["checks"].append(record)
                replies = run_requests(state, candidate, requests, record)
                possibilities = []
                for model in models:
                    if len(requests) == 2:
                        possibilities.extend(serial_candidates(model, requests, replies))
                    else:
                        following = model.copy()
                        if exact(replies, [following.apply(requests[0])]):
                            possibilities.append(following)
                # Inspect even a wrong business reply to retain independent evidence.
                record["observed"] = observe(state)
                models = matching_snapshot(possibilities, record["observed"])
                record["passed"] = bool(models)
                if not models:
                    raise ExecutionFailure(f"{name}: replies and tables do not match either legal serial history")

            prefix = f"run{repetition}-"
            left = request(prefix + "left", "A", 60)
            right = request(prefix + "right", "A", 60)
            try:
                phase("overlapping_60", [left, right])
                phase("fresh_process_left_replay", [left])
                phase("fresh_process_right_replay", [right])
                phase("amount_mismatch", [request(left["key"], "A", 61)])
                phase("global_account_mismatch", [request(left["key"], "B", 60)])
                phase("independent_account_exact_limit", [request(prefix + "B100", "B", 100)])
                # A later debit makes stale-vs-current rejection replies distinguishable.
                phase("later_debit", [request(prefix + "later", "A", 10)])
                phase("historical_left_replay", [left])
                phase("historical_right_replay", [right])
                duplicate = request(prefix + "duplicate", "A", 5)
                phase("overlapping_identical_key", [duplicate, duplicate])
                phase("duplicate_replay", [duplicate])
                phase("new_durable_rejection", [request(prefix + "Bover", "B", 1)])
                phase("rejected_key_mismatch", [request(prefix + "Bover", "A", 1)])
                phase("rejection_replay", [request(prefix + "Bover", "B", 1)])
                run["status"] = "pass"
            except (ExecutionFailure, Unavailable, OSError) as exc:
                failures += 1
                run["status"] = "fail"
                run["reason"] = str(exc)
                # All candidate processes have stopped. Retain state even on protocol failures.
                try:
                    run["final_observation"] = observe(state)
                except ExecutionFailure as inspection_error:
                    run["inspection_error"] = str(inspection_error)
        result["repetitions_completed"] = len(result["repetitions"])
        return finish("fail" if failures else "pass")


def review_template(answer, answer_sha256):
    validate_answer(answer)
    return {"schema_version": "e1-review/v1", "task_id": "E1", "answer_sha256": answer_sha256,
            "reviewer": "", "independence_declaration": "", "comparison_repertoire": "",
            "criteria": [{"id": key, "criterion": value, "judgment": "unresolved",
                          "evidence_quote": "", "rationale": ""} for key, value in CRITERIA.items()],
            "unresolved_claims": [], "alternative_assessment": "",
            "usefulness_and_originality": "No finding yet; declare comparison evidence before judging novelty."}


def validate_review(answer, sha, review):
    if type(review) is not dict:
        raise ValueError("review must be an object")
    if review.get("schema_version") != "e1-review/v1" or review.get("task_id") != "E1" or review.get("answer_sha256") != sha:
        raise ValueError("review must bind to exact answer bytes and schema")
    for field in ("reviewer", "independence_declaration", "comparison_repertoire"):
        if type(review.get(field)) is not str or not review[field].strip():
            raise ValueError(f"missing {field}")
    rows = review.get("criteria")
    if type(rows) is not list or len(rows) != len(CRITERIA) or {r.get("id") for r in rows if type(r) is dict} != set(CRITERIA):
        raise ValueError("review must cover every criterion once")
    text = answer["explanation"] + "\n" + answer.get("alternative", "") + "\n" + answer.get("code", "")
    for row in rows:
        if row.get("judgment") not in ("supported", "unsupported", "unresolved"):
            raise ValueError("invalid review judgment")
        if type(row.get("rationale")) is not str or not row["rationale"].strip():
            raise ValueError("every criterion needs a rationale")
        quote = row.get("evidence_quote")
        if type(quote) is not str or (quote and quote not in text) or (row["judgment"] == "supported" and not quote.strip()):
            raise ValueError("supported criteria need an exact, nonblank answer quote")
    if type(review.get("unresolved_claims")) is not list or any(type(x) is not str for x in review["unresolved_claims"]):
        raise ValueError("unresolved_claims must be a list of strings")
    if answer.get("alternative_format") and not review.get("alternative_assessment", "").strip():
        raise ValueError("alternative construction needs explicit assessment")
    return {"status": "review_structure_valid", "answer_sha256": sha,
            "notice": "Does not authenticate reviewer independence, validate judgments, or change formal status."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    grade = sub.add_parser("grade")
    grade.add_argument("answer", type=Path)
    template = sub.add_parser("review-template")
    template.add_argument("answer", type=Path)
    template.add_argument("output", type=Path)
    review = sub.add_parser("validate-review")
    review.add_argument("answer", type=Path)
    review.add_argument("review", type=Path)
    start = sub.add_parser("start-case")
    start.add_argument("output", type=Path)
    reveal = sub.add_parser("reveal-case")
    reveal.add_argument("state", type=Path)
    reveal.add_argument("first", type=Path)
    reveal.add_argument("output", type=Path)
    finish = sub.add_parser("finish-case")
    finish.add_argument("state", type=Path)
    finish.add_argument("final", type=Path)
    finish.add_argument("output", type=Path)
    args = parser.parse_args()
    try:
        if args.command in ("start-case", "reveal-case", "finish-case"):
            import staged
            if args.command == "start-case":
                result = staged.start(args.output)
            elif args.command == "reveal-case":
                result = staged.reveal(args.state, args.first, args.output)
            else:
                result = staged.finish(args.state, args.final, args.output, load_answer, evaluate)
            print(json.dumps(result, indent=2, allow_nan=False))
            return 0 if result.get("formal_status", "pass") == "pass" else 2
        answer, sha = load_answer(args.answer)
        if args.command == "grade":
            result = evaluate(answer, sha)
            code = 0 if result["formal_status"] == "pass" else 2
        elif args.command == "review-template":
            result = review_template(answer, sha)
            with args.output.open("x", encoding="utf-8") as stream:
                json.dump(result, stream, indent=2)
            result, code = {"status": "review_template_created", "path": str(args.output)}, 0
        else:
            validate_answer(answer)
            result, code = validate_review(answer, sha, strict_json(args.review.read_bytes())), 0
    except (ValueError, SyntaxError, OSError, TypeError, KeyError) as exc:
        result, code = {"status": "invalid", "reason": str(exc)}, 2
    print(json.dumps(result, indent=2, allow_nan=False))
    return code


if __name__ == "__main__":
    raise SystemExit(main())

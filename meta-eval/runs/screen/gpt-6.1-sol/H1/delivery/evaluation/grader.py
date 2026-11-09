import hashlib
from pathlib import Path
import tempfile
import time

from .oracle import Model, choose_overlap, exact, overlap_options, request
from .sandbox import CandidateError, Group, Unavailable, inspect_stopped, overlap, probe, require_runtime


ROOT = Path(__file__).resolve().parent.parent
VERSION = "e1-evaluation/1"
INPUT_HASHES = {
    "input/E1.md": "514e2d4ca8675f9b137a843df0cc2d47181f2506518fd43cc3d6819df6a09221",
    "input/README.md": "4cb185b2d32398fa9c055638a54c6ebb5dad48f84eba70555faf0241a3a44e77",
}


def digest(value):
    import json
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=True, allow_nan=False).encode()).hexdigest()


def bindings():
    result = {}
    for name, expected in INPUT_HASHES.items():
        data = (ROOT / name).read_bytes()
        actual = hashlib.sha256(data).hexdigest()
        if actual != expected:
            raise ValueError(f"public input changed: {name}")
        result[name] = {"sha256": actual, "bytes": len(data)}
    return result


def validate_answer(answer):
    if not isinstance(answer, dict) or answer.get("task_id") != "E1":
        raise ValueError("answer must be an object with task_id E1")
    if not isinstance(answer.get("explanation"), str) or not answer["explanation"].strip():
        raise ValueError("a nonempty explanation is required; quality is separately reviewed")
    if "alternative_format" in answer and type(answer["alternative_format"]) is not bool:
        raise ValueError("alternative_format must be a JSON boolean")
    if answer.get("alternative_format"):
        if not isinstance(answer.get("alternative"), str) or not answer["alternative"].strip():
            raise ValueError("alternative-format answers require a nonempty alternative")
    elif not isinstance(answer.get("code"), str) or not answer["code"].strip():
        raise ValueError("code must be a complete nonempty Python source string")


def checked(label, actual, expected, checks):
    ok = exact(actual, expected)
    checks.append({"check": label, "pass": ok, "actual": actual, "expected": expected})
    if not ok:
        raise CandidateError(f"contract mismatch: {label}")


def snapshot(label, state, model, checks):
    # Every caller has left its Group, stopping both processes before inspection.
    checked(label, inspect_stopped(state), model.snapshot(), checks)


def core_case(source, state, result):
    transcript, checks = result["transcript"], result["checks"]
    model = Model()
    with Group(source, state, transcript, "initialization"):
        pass
    snapshot("initial account values and empty decision/ledger tables", state, model, checks)
    first, second = request("race-left"), request("race-right")
    with Group(source, state, transcript, "overlap") as workers:
        replies = overlap(workers, [first, second])
        legal = [expected for _, expected in overlap_options(first, second)]
        ok = any(exact(replies, expected) for expected in legal)
        checks.append({"check": "two 60-unit requests: either serialization", "pass": ok,
                       "actual": replies, "legal_replies": legal})
        if not ok:
            raise CandidateError("overlap matches neither legal serial outcome")
        model = choose_overlap(first, second, replies)
    snapshot("atomic allowance/decision/ledger after overlap", state, model, checks)
    # Fresh instances establish persistence and idempotent initialization.
    with Group(source, state, transcript, "replay") as workers:
        for index, req in enumerate((first, second)):
            checked(f"cross-process retry {req['key']}", workers[1-index].call(req),
                    model.apply(req), checks)
        for account, amount, label in (("A", 61, "amount"), ("B", 60, "account")):
            changed = request(first["key"], account, amount)
            checked(f"global identity conflict: changed {label}", workers[0].call(changed),
                    model.apply(changed), checks)
        other = request("independent-B", "B", 100)
        checked("independent account accepts all 100", workers[1].call(other),
                model.apply(other), checks)
    snapshot("core F5 public state including conflict non-mutation", state, model, checks)
    # Disclosed history probes catch a rejection that recomputes remaining later.
    with Group(source, state, transcript, "history") as workers:
        extra = request("later-spend", amount=1)
        checked("later A spend", workers[0].call(extra), model.apply(extra), checks)
        for req in (first, second):
            checked(f"historical remaining after later spend: {req['key']}",
                    workers[1].call(req), model.apply(req), checks)
        reject_b = request("rejected-B", "B", 1)
        checked("durable insufficient decision", workers[1].call(reject_b),
                model.apply(reject_b), checks)
        for req in (first, second, reject_b):
            changed = request(req["key"], "B" if req["account"] == "A" else "A", req["amount"])
            checked(f"conflict on accepted or rejected key {req['key']}",
                    workers[0].call(changed), model.apply(changed), checks)
    snapshot("history state: durable rejection, historical replays, no conflict writes", state, model, checks)
    with Group(source, state, transcript, "restart") as workers:
        for req in (first, second, other, extra, reject_b):
            checked(f"fresh-instance replay {req['key']}", workers[1].call(req),
                    model.apply(req), checks)
    snapshot("restart and retries change nothing", state, model, checks)


def identity_case(source, state, result, conflict):
    first = request("same-key")
    second = request("same-key", "B" if conflict else "A")
    with Group(source, state, result["transcript"], "identity-overlap") as workers:
        replies = overlap(workers, [first, second])
        options = overlap_options(first, second)
        ok = any(exact(replies, expected) for _, expected in options)
        result["checks"].append({"check": "concurrent global-key arbitration", "pass": ok,
                                 "actual": replies, "legal_replies": [v for _, v in options]})
        if not ok:
            raise CandidateError("concurrent identity arbitration violated")
        model = choose_overlap(first, second, replies)
    snapshot("one decision and one ledger row for one accepted identity", state, model, result["checks"])
    with Group(source, state, result["transcript"], "identity-restart") as workers:
        for index, req in enumerate((first, second)):
            checked("identity retry after restart", workers[index].call(req),
                    model.apply(req), result["checks"])
    snapshot("identity replay changes nothing", state, model, result["checks"])


def grade(answer):
    report = {"evaluator": VERSION, "task_id": "E1", "cases": [],
              "review_status": "pending", "staged": False,
              "limits": {"repetitions": 3, "reply_seconds": 6, "reply_bytes": 65536,
                         "address_space_bytes": 512 * 1024**2, "file_descriptors": 256,
                         "file_bytes": 8 * 1024**2, "cpu_seconds_per_process": 10}}
    try:
        report["source_bindings"] = bindings()
        report["answer_sha256"] = digest(answer)
        validate_answer(answer)
    except (ValueError, TypeError, OSError) as exc:
        report.update(formal_status="invalid", overall_status="invalid", reason=str(exc))
        return report
    if answer.get("alternative_format"):
        report.update(formal_status="review_required", overall_status="review_required",
                      reason="alternative construction needs independent review")
        return report
    report["code_sha256"] = hashlib.sha256(answer["code"].encode()).hexdigest()
    try:
        require_runtime()
    except Unavailable as exc:
        report.update(formal_status="unavailable", overall_status="unavailable", reason=str(exc))
        return report
    with tempfile.TemporaryDirectory(prefix="e1-eval-") as temp:
        base = Path(temp)
        state = base / "probe-state"
        state.mkdir()
        try:
            report["worker_runtime"] = probe(state)
        except Unavailable as exc:
            report.update(formal_status="unavailable", overall_status="unavailable", reason=str(exc))
            return report
        source = base / "candidate.py"
        source.write_text(answer["code"], encoding="utf-8")
        for repetition in range(3):
            for kind in ("allowance", "duplicate_identity", "conflicting_identity"):
                case = {"id": f"{kind}/{repetition+1}", "checks": [], "transcript": []}
                report["cases"].append(case)
                state = base / case["id"].replace("/", "-")
                state.mkdir()
                started = time.monotonic()
                try:
                    if kind == "allowance":
                        core_case(source, state, case)
                    else:
                        identity_case(source, state, case, kind == "conflicting_identity")
                    case["status"] = "pass"
                except (CandidateError, OSError, ValueError, RuntimeError) as exc:
                    case.update(status="fail", reason=f"{type(exc).__name__}: {exc}")
                case["elapsed_seconds"] = round(time.monotonic() - started, 3)
    passed = all(case["status"] == "pass" for case in report["cases"])
    report.update(formal_status="pass" if passed else "fail",
                  overall_status="formal_pass_review_pending" if passed else "formal_fail_review_pending")
    return report

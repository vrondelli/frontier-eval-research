"""E1 ledger-admission evaluator. Python 3.11+, standard library only."""
from pathlib import Path
import argparse
import hashlib
import json
import secrets
import subprocess
import sys
import tempfile
import time

from oracle import canonical, match_pair, match_sequence
from sandbox import CandidateError, Unavailable, Worker, available

VERSION = "e1-eval/1.0"
ROOT = Path(__file__).resolve().parent


def strict_json(text):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result
    def nonfinite(value):
        raise ValueError(f"non-finite JSON: {value}")
    return json.loads(text, object_pairs_hook=unique, parse_constant=nonfinite)


def validate(answer):
    if not isinstance(answer, dict) or answer.get("task_id") != "E1":
        raise ValueError('answer must be an object with task_id="E1"')
    if not isinstance(answer.get("explanation"), str) or not answer["explanation"].strip():
        raise ValueError("a nonempty explanation is required; quality is separately reviewed")
    if "alternative_format" in answer and type(answer["alternative_format"]) is not bool:
        raise ValueError("alternative_format must be boolean")
    if answer.get("alternative_format"):
        if not isinstance(answer.get("alternative"), str) or not answer["alternative"].strip():
            raise ValueError("alternative format requires a nonempty alternative")
        return "alternative"
    if not isinstance(answer.get("code"), str) or not answer["code"].strip():
        raise ValueError("complete Service source string required")
    # Compilation checks syntax without executing or importing the submission.
    try:
        compile(answer["code"], "candidate.py", "exec")
    except (SyntaxError, ValueError, TypeError) as exc:
        raise ValueError(f"invalid Python source: {exc}") from exc
    return "executable"


def read_state(state):
    command = [sys.executable, "-I", "-S", str(ROOT / "inspect_db.py"), str(state / "ledger.sqlite")]
    try:
        result = subprocess.run(command, capture_output=True, timeout=6, env={}, check=False)
    except subprocess.TimeoutExpired as exc:
        raise CandidateError("independent SQL inspection timed out") from exc
    try:
        data = strict_json(result.stdout)
    except (ValueError, UnicodeError) as exc:
        raise CandidateError("independent SQL inspection failed") from exc
    if result.returncode or "error" in data:
        raise CandidateError("independent SQL inspection: " + data.get("error", "failed"))
    return data["snapshot"]


def request(key, account="A", amount=60):
    return {"key": key, "account": account, "amount": amount}


def scenarios():
    # Random identities deter trivial transcript matching; amounts remain disclosed.
    cases = []
    for i in range(3):
        token = secrets.token_hex(12)
        pair = [request(token + "-x"), request(token + "-y")]
        b = request(token + "-b", "B", 100)
        drain = request(token + "-drain", "A", 40)
        tail = [*pair]
        for original in pair:
            tail += [request(original["key"], "A", 61), request(original["key"], "B", 60)]
        tail += [b, drain, *pair, request(token + "-empty-a", "A", 1),
                 request(token + "-empty-b", "B", 1), b, drain]
        cases.append({"name": f"core-{i + 1}", "scope": "declared_overlap_and_replay",
                      "pair": pair, "tail": tail,
                      "restart": [*pair, b, drain, tail[-4], tail[-3]], "release_first": i % 2})
    for name, second in (("identical", ("A", 60)), ("amount-conflict", ("A", 80)),
                         ("account-conflict", ("B", 60))):
        key = secrets.token_hex(12)
        pair = [request(key), request(key, *second)]
        cases.append({"name": "identity-" + name, "scope": "supplemental_global_identity",
                      "pair": pair, "tail": pair, "restart": pair, "release_first": 0})
    return cases


def run_case(source, state, case):
    state.mkdir()
    evidence = {"name": case["name"], "scope": case["scope"], "status": "fail",
                "plan": case, "events": [], "checkpoints": [], "terminals": []}
    workers = []
    phase = "overlap"

    def start():
        # Start BOTH processes before waiting for initialization acknowledgements.
        for _ in range(2):
            workers.append(Worker(source, state))
        deadline = time.monotonic() + 6
        for i, worker in enumerate(workers):
            message = worker.receive(deadline)
            evidence["events"].append({"phase": phase, "worker": i, "event": message})
            if message != {"event": "ready"}:
                raise CandidateError("service initialization failed")

    def stop():
        failures = []
        for worker in workers:
            try:
                evidence["terminals"].append(worker.close())
            except Exception as exc:
                failures.append(str(exc))
        workers.clear()
        if failures:
            raise CandidateError("could not stop all workers: " + "; ".join(failures))

    def receive_reply(i, deadline=None, item=None):
        message = workers[i].receive(deadline)
        evidence["events"].append({"phase": phase, "worker": i, "request": item, "event": message})
        if not isinstance(message, dict) or set(message) != {"event", "value"} or message["event"] != "reply":
            raise CandidateError("apply failed or violated worker protocol")
        value = message["value"]
        if not isinstance(value, dict) or set(value) != {"status", "remaining"}:
            raise CandidateError("reply must contain exactly status and remaining")
        if value["status"] not in ("accepted", "rejected", "payload_mismatch"):
            raise CandidateError("unrecognized business status")
        if value["status"] == "payload_mismatch":
            if value["remaining"] is not None:
                raise CandidateError("payload_mismatch remaining must be null")
        elif type(value["remaining"]) is not int or value["remaining"] < 0:
            raise CandidateError("remaining must be a nonnegative integer")
        return value

    def checkpoint(label):
        stop()  # No candidate process can modify state during inspection.
        snapshot = read_state(state)
        evidence["checkpoints"].append({"phase": label, "snapshot": snapshot})
        return snapshot

    try:
        start()
        for i, item in enumerate(case["pair"]):
            workers[i].send({"op": "arm", "request": item})
        deadline = time.monotonic() + 6
        for i, worker in enumerate(workers):
            message = worker.receive(deadline)
            evidence["events"].append({"phase": phase, "worker": i, "event": message})
            if message != {"event": "armed"}:
                raise CandidateError("both workers must acknowledge the barrier")
        deadline = time.monotonic() + 6
        for i in (case["release_first"], 1 - case["release_first"]):
            workers[i].send({"op": "go"})
        replies = [receive_reply(i, deadline, case["pair"][i]) for i in range(2)]
        snapshot = checkpoint("overlap")
        matches = match_pair(case["pair"], replies, snapshot)
        if not matches:
            raise CandidateError("overlap replies and public state match neither legal serial order")
        for phase in ("tail", "restart"):
            start()
            replies = []
            for n, item in enumerate(case[phase]):
                # Retries use a new Service process; alternate callers as well.
                i = (n + 1) % 2
                workers[i].send({"op": "apply", "request": item})
                replies.append(receive_reply(i, item=item))
            snapshot = checkpoint(phase)
            matches = match_sequence(matches, case[phase], replies, snapshot)
            if not matches:
                raise CandidateError(f"{phase}: replies/state differ from the sequential contract")
        evidence["status"] = "pass"
        evidence["legal_serial_orders"] = [match["order"] for match in matches]
    except (CandidateError, ValueError, OSError) as exc:
        evidence["error"] = f"{type(exc).__name__}: {str(exc)[:2048]}"
    finally:
        try:
            stop()
        except CandidateError as exc:
            evidence["status"] = "fail"
            evidence["cleanup_error"] = str(exc)
    return evidence


def evaluate(answer):
    result = {"evaluator": VERSION, "task_id": "E1", "formal_status": "invalid",
              "overall_status": "invalid", "review_status": "pending", "cases": []}
    result["source_sha256"] = hashlib.sha256((ROOT / "input" / "E1.md").read_bytes()).hexdigest()
    result["evaluator_files_sha256"] = {
        name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        for name in ("evaluate.py", "oracle.py", "sandbox.py", "worker.py", "inspect_db.py")}
    try:
        route = validate(answer)
        result["answer_sha256"] = hashlib.sha256(canonical(answer).encode()).hexdigest()
    except (ValueError, TypeError, RecursionError) as exc:
        result["error"] = str(exc)
        return result
    if route == "alternative":
        result.update(formal_status="review_required", overall_status="review_required")
        return result
    try:
        available()
    except Unavailable as exc:
        result.update(formal_status="unavailable", overall_status="unavailable", error=str(exc))
        return result
    with tempfile.TemporaryDirectory(prefix="e1-eval-") as directory:
        root = Path(directory)
        source = root / "candidate.py"
        source.write_text(answer["code"], encoding="utf-8")
        for index, case in enumerate(scenarios()):
            result["cases"].append(run_case(source, root / str(index), case))
    passed = all(case["status"] == "pass" for case in result["cases"])
    result.update(formal_status="pass" if passed else "fail",
                  overall_status="formal_pass_review_pending" if passed else "formal_fail_review_pending")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("answer", type=Path, help="JSON object containing task_id, code, explanation")
    parser.add_argument("--output", type=Path, help="create a new evidence JSON file (never overwrite)")
    args = parser.parse_args()
    try:
        with args.answer.open("rb") as stream:
            raw = stream.read(1024 * 1024 + 1)
        if len(raw) > 1024 * 1024:
            raise ValueError("answer exceeds the disclosed 1 MiB transport bound")
        result = evaluate(strict_json(raw))
    except (OSError, ValueError, UnicodeError, RecursionError) as exc:
        result = {"evaluator": VERSION, "task_id": "E1", "formal_status": "invalid",
                  "overall_status": "invalid", "error": str(exc)}
    text = json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    if args.output:
        with args.output.open("x", encoding="utf-8") as output:
            output.write(text)
    else:
        print(text, end="")
    return 0 if result["formal_status"] == "pass" else 2


if __name__ == "__main__":
    sys.exit(main())

"""Protocol orchestration and evidence reporting, independent of candidate source."""
import hashlib
from pathlib import Path
import secrets
import tempfile
import time

from .oracle import ContractFailure, Oracle, canonical, schedule
from .sandbox import REPLY_SECONDS, Sandbox, Unavailable, WorkerFailure


ROOT = Path(__file__).resolve().parent.parent


def digest(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def validate_answer(answer):
    if not isinstance(answer, dict) or answer.get("task_id") != "E1":
        raise ValueError("answer must be a JSON object with task_id E1")
    if not isinstance(answer.get("explanation"), str) or not answer["explanation"].strip():
        raise ValueError("a nonempty explanation is required; quality is reviewed separately")
    if "alternative_format" in answer and type(answer["alternative_format"]) is not bool:
        raise ValueError("alternative_format must be a boolean")
    if answer.get("alternative_format"):
        if not isinstance(answer.get("alternative"), str) or not answer["alternative"].strip():
            raise ValueError("alternative_format requires a nonempty alternative")
        return "alternative"
    code = answer.get("code")
    if not isinstance(code, str) or not code.strip():
        raise ValueError("code must be a nonempty complete Python Service source string")
    return "executable"


def execute_phase(sandbox, state, candidate, requests, concurrent, evidence):
    channels = []
    replies = []
    evidence.update({"requests": requests, "concurrent": concurrent, "replies": replies,
                     "terminal_codes": [], "armed": []})
    try:
        if concurrent:
            # Both new processes construct Service before either request is released.
            for _ in requests:
                channels.append(sandbox.worker(state, candidate))
            deadline = time.monotonic() + REPLY_SECONDS
            for channel in channels:
                initialization = channel.read(deadline)
                evidence.setdefault("initialization", []).append(initialization)
                if initialization != {"ready": True}:
                    raise WorkerFailure("worker failed initialization")
            for channel, request in zip(channels, requests):
                channel.send({"op": "arm", "request": request})
            deadline = time.monotonic() + REPLY_SECONDS
            for index, channel in enumerate(channels):
                acknowledgement = channel.read(deadline)
                evidence.setdefault("barrier_responses", []).append(acknowledgement)
                if acknowledgement != {"armed": True}:
                    raise WorkerFailure("worker did not acknowledge barrier")
                evidence["armed"].append(index)
            deadline = time.monotonic() + REPLY_SECONDS
            for channel in channels:
                channel.send({"op": "go"})
            for channel in channels:
                envelope = channel.read(deadline)
                evidence.setdefault("raw_responses", []).append(envelope)
                if not isinstance(envelope, dict) or set(envelope) != {"reply"}:
                    raise WorkerFailure("apply raised or violated the worker protocol")
                replies.append(envelope["reply"])
            for channel in channels:
                channel.close()
        else:
            # Every retry/mismatch uses a fresh interpreter and fresh Service instance.
            for request in requests:
                channel = sandbox.worker(state, candidate)
                channels.append(channel)
                initialization = channel.read()
                evidence.setdefault("initialization", []).append(initialization)
                if initialization != {"ready": True}:
                    raise WorkerFailure("worker failed initialization")
                channel.send({"op": "apply", "request": request})
                envelope = channel.read()
                evidence.setdefault("raw_responses", []).append(envelope)
                if not isinstance(envelope, dict) or set(envelope) != {"reply"}:
                    raise WorkerFailure("apply raised or violated the worker protocol")
                replies.append(envelope["reply"])
                channel.close()
                channel.stop()
        return replies
    finally:
        for channel in channels:
            channel.stop()
            evidence["terminal_codes"].append(channel.returncode)


def grade(answer, extended=True):
    report = {
        "evaluation_version": "e1-local-v1",
        "task_id": "E1",
        "answer_sha256": digest(answer),
        "source_sha256": {name: hashlib.sha256((ROOT / "input" / name).read_bytes()).hexdigest()
                          for name in ("E1.md", "README.md")},
        "suite": "contract_plus_probes" if extended else "declared_schedule",
        "repetitions_declared": 3,
        "repetitions": [],
        "review_status": "pending",
        "scope": "Finite correctness checks only; no throughput, latency, creativity or hiring score.",
    }
    def finish(status, reason=None):
        report["status"] = report["formal_status"] = status
        report["overall_status"] = "formal_pass_review_pending" if status == "pass" else status
        if reason:
            report["reason"] = reason
        return report
    try:
        kind = validate_answer(answer)
    except ValueError as exc:
        return finish("invalid", str(exc))
    if kind == "alternative":
        return finish("review_required", "Alternative architecture requires independent review; not executed.")
    try:
        sandbox = Sandbox()
        with tempfile.TemporaryDirectory(prefix="e1-evaluation-") as temporary:
            root = Path(temporary)
            candidate = root / "candidate.py"
            candidate.write_text(answer["code"], encoding="utf-8")
            probe = root / "probe"
            probe.mkdir()
            sandbox.preflight(probe)
            failures = False
            for repetition in range(3):
                state = root / f"state-{repetition}"
                state.mkdir()
                entry = {"index": repetition + 1, "status": "running", "phases": []}
                report["repetitions"].append(entry)
                oracle = Oracle()
                # Opaque keys reduce accidental hardcoding, without claiming secrecy.
                prefix = secrets.token_hex(12)
                for name, requests, concurrent in schedule(prefix, extended):
                    evidence = {"name": name}
                    entry["phases"].append(evidence)
                    try:
                        replies = execute_phase(sandbox, state, candidate, requests, concurrent, evidence)
                        # All candidate processes have terminated before opening SQLite.
                        snapshot = sandbox.inspect(state)
                        evidence["snapshot"] = snapshot
                        oracle.observe(requests, replies, concurrent)
                        oracle.inspect(snapshot)
                        evidence["status"] = "pass"
                    except (ContractFailure, WorkerFailure, OSError, ValueError) as exc:
                        evidence["status"] = "fail"
                        evidence["reason"] = str(exc)
                        # Retain state evidence even when the reply path fails.
                        if "snapshot" not in evidence:
                            try:
                                evidence["snapshot"] = sandbox.inspect(state)
                            except (WorkerFailure, OSError, ValueError) as inspection:
                                evidence["inspection_error"] = str(inspection)
                        entry["status"] = "fail"
                        failures = True
                        break
                else:
                    entry["status"] = "pass"
            return finish("fail" if failures else "pass")
    except Unavailable as exc:
        return finish("unavailable", str(exc))
    except OSError as exc:
        return finish("unavailable", f"evaluator infrastructure error: {exc}")

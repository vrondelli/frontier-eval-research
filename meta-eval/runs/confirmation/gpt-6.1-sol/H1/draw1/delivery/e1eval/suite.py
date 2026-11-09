"""Public finite scenario; transport-independent for trusted control testing."""

import json
import secrets
import subprocess
import sys
from pathlib import Path

from .oracle import ContractError, check_reply, check_snapshot, overlap_model


def independent_inspection(database):
    # Preparation and SQLite parsing are bounded by an outer process deadline too.
    code = ("import json,runpy,sys; m=runpy.run_path(sys.argv[1]); "
            "print(json.dumps(m['inspect_database'](sys.argv[2])))")
    try:
        result = subprocess.run(
            [sys.executable, "-I", "-B", "-c", code,
             str(Path(__file__).with_name("oracle.py")), str(database)],
            capture_output=True, timeout=3)
        if result.returncode:
            raise ContractError("independent inspector failed: "
                                + result.stderr.decode(errors="replace")[-2000:])
        return {table: [tuple(row) for row in rows]
                for table, rows in json.loads(result.stdout).items()}
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        raise ContractError(f"independent inspection failed: {exc}") from exc


def run_trial(state, candidate, worker_factory, trial_index=0):
    """Both fresh workers initialize and acknowledge arm before either is released."""
    result = {"trial": trial_index, "status": "fail", "transcript": [],
              "terminal_codes": [], "checks": []}
    workers = []
    model = None
    prefix = secrets.token_hex(12)

    def request(label, account="A", amount=60):
        return {"key": prefix + "-" + label, "account": account, "amount": amount}

    def observe(worker_index, req):
        expected = model.apply(req)
        record = {"phase": "sequential", "worker": worker_index, "request": req,
                  "expected": expected}
        result["transcript"].append(record)
        workers[worker_index].send("apply", req)
        reply = workers[worker_index].receive("result").get("reply")
        record["reply"] = reply
        check_reply(reply, expected)

    try:
        for _ in range(2):
            workers.append(worker_factory(state, candidate))
        for worker in workers:
            worker.receive("ready")
        requests = [request("overlap-0"), request("overlap-1")]
        for worker, req in zip(workers, requests):
            worker.send("arm", req)
        for worker in workers:
            worker.receive("armed")
        result["barrier"] = {"ready": 2, "armed": 2, "release": "both go messages sent before receiving replies"}
        # Alternate send order as well as allowing either serial winner.
        for i in (range(2) if trial_index % 2 == 0 else (1, 0)):
            workers[i].send("go")
        replies = []
        for i, worker in enumerate(workers):
            reply = worker.receive("result").get("reply")
            replies.append(reply)
            result["transcript"].append({"phase": "overlap", "worker": i,
                                          "request": requests[i], "reply": reply})
        model, order = overlap_model(requests, replies)
        result["legal_serial_order"] = list(order)
        result["checks"].append("overlap: exactly one accepted at 40, one rejected at 40")
        # Every original decision is replayed in the other process.
        for i in range(2):
            observe(1 - i, requests[i])
        for req in requests:
            observe(0, {**req, "amount": 61})
            observe(1, {**req, "account": "B"})
        observe(0, request("B-full", "B", 100))
        observe(1, request("A-drain", amount=40))
        observe(0, request("A-empty", amount=1))
        observe(1, request("B-empty", "B", 1))
        # The rejected 60 must still replay remaining=40 after A has reached zero.
        for i in range(2):
            observe(1 - i, requests[i])
        observe(1, request("B-full", "B", 100))
        result["checks"].append("replays, account/amount conflicts, independent B, exact exhaustion")
        # A third fresh Service must not reset balances or decisions on construction.
        workers.append(worker_factory(state, candidate))
        workers[2].receive("ready")
        for req in requests:
            observe(2, req)
        observe(2, request("B-full", "B", 100))
        observe(2, request("A-empty", amount=1))
        observe(2, request("B-empty", "B", 1))
        result["checks"].append("fresh-process idempotent initialization and durable decisions")
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        for worker in workers:
            try:
                result["terminal_codes"].append(worker.close())
            except Exception as exc:
                result["terminal_codes"].append(None)
                result.setdefault("error", f"worker cleanup failed: {exc}")
    try:
        result["observed_sql"] = independent_inspection(Path(state) / "ledger.sqlite")
        if model is not None:
            result["expected_sql"] = model.snapshot()
            check_snapshot(result["observed_sql"], result["expected_sql"])
        if "error" not in result:
            if any(code != 0 for code in result["terminal_codes"]):
                raise ContractError("worker had a nonzero terminal code")
            result["checks"].append("independent final SQL equals all modeled effects")
            result["status"] = "pass"
    except Exception as exc:
        result["inspection_error"] = f"{type(exc).__name__}: {exc}"
    return result

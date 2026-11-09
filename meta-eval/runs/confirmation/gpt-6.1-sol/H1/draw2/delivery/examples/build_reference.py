"""Rebuild the authored answer JSON. This is not a solver or a performance run."""
import json
from pathlib import Path

directory = Path(__file__).resolve().parent
explanation = """I use one BEGIN IMMEDIATE transaction for the key lookup, account check,
allowance update, ledger insertion and immutable decision insertion. Initialization
also serializes and inserts missing accounts without resetting existing balances.
A returned business decision follows a successful commit. SQLite errors roll back
and propagate; lock exhaustion is not insufficient allowance.

The decisions primary key has global scope across accounts. A duplicate key must
match both account and amount before the saved status and historical remaining
are returned. Rejections are saved as well as acceptances. A commit followed by a
lost reply has an unknown outcome for the client: reconnect and replay exactly the
same key and payload. A new key could authorize a second transfer. I would not
discard a decision while its retry window remains open.

A hot account creates necessary contention on its allowance. Rising wait time
alone does not establish a cycle of lock dependencies. I would inspect transaction
and lock-wait traces, error codes, holders and waiters before calling retries
deadlocks. BEGIN IMMEDIATE obtains SQLite's writer reservation before the read
and avoids a deferred read-to-write upgrade, but it serializes writers for the
whole database. WAL can let readers proceed with a writer; it does not create
parallel SQLite writers for different accounts. Process-local locks cannot
coordinate fresh service processes.

My first mitigation is bounded admission/backpressure with short transactions,
after measuring queue time and transaction duration, and bounded jittered retries
of entire rolled-back transactions for transient lock errors. No remote I/O belongs
inside the transaction. I would retain the key on ambiguous completion and cap
retries within the request deadline. I would roll back the change on any invariant
violation, including a duplicate ledger key or changed replay decision; for latency
I would use a predeclared deployment threshold, for example p99 above 200 ms for
five minutes at the same offered load, rather than infer a benchmark latency label.

For sustained demand, a database with row-level concurrency could serialize a hot
account while admitting different accounts concurrently, provided the global key
constraint and all three writes stay transactional. Sharding by account alone
does not preserve global key identity on changed-account retries; a global identity
authority and a consistent transaction/routing protocol would still be needed.
This SQLite slice fits a single host and a correctly locking local filesystem;
shared network filesystems and multi-host failover need separate qualification.
FULL synchronous commits address the declared local durability boundary, not an
external payment provider or settlement. A production rollout needs backup,
recovery and failure testing. The finite suite cannot prove all interleavings,
crash atomicity or production latency.
"""
answer = {"task_id": "E1", "code": (directory / "reference_service.py").read_text(encoding="utf-8"),
          "explanation": explanation}
(directory / "E1.json").write_text(json.dumps(answer, indent=2) + "\n", encoding="utf-8")

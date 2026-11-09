# E1 independent explanation review

Review the submitted explanation and source, the formal evidence, and any sealed
first response. Record the exact answer SHA-256 from `evaluate.py` and declare
reviewer identity, relevant expertise, conflicts and prior exposure. Do not give
the authored controls to the solver. Prefer two independent reviews before
adjudicating disagreements. These declarations do not authenticate independence.

Use `supported`, `partial`, `unsupported`, or `not_assessable` for each criterion.
For every judgment record an exact quotation from the answer, the reasoning,
contradicting code/evidence if present, and unresolved claims or further tests.
An absent passage is recorded as absent, rather than an invented quotation.
There is no keyword checklist score or combined hiring/creativity score.

| ID | Criterion | Evidence expected |
| --- | --- | --- |
| atomicity | Admission transaction | Allowance check/decrement, one ledger insert, durable decision and commit share an atomic boundary. Rejection is persisted. DB failure rolls back and is distinct from a business rejection. Identify what the code actually guarantees. |
| identity | Identity and retry | Key namespace is global across accounts; original account/amount bind the key. Identical accepted **and rejected** retries return the stored status and historical remaining. Mismatch does not consume allowance or replace a decision. |
| uncertainty | Unknown outcomes | A timeout, disconnect or lost response does not imply rejection. Reconnect and replay the same key and payload to discover the durable decision; preserve identity across retries. Do not mint a fresh key for an uncertain outcome. Bound retry/backoff and distinguish retryable lock errors from payload errors. |
| diagnosis | Contention versus deadlock | A hot account creates serialization and queueing. A lock cycle requires a wait-for cycle; waits alone do not establish one. Seek blocked/holder traces, transaction length, lock acquisition order and retry metrics. Do not claim SQLite demonstrates row-lock deadlocks from these tests. |
| parallelism | Cross-account execution | Explain SQLite's single-writer limit: WAL allows reader/writer overlap, not simultaneous writers to different accounts in one DB. Row locking or partitioning can allow independent accounts to proceed, while a hot account still needs serialization. Respect global key uniqueness across partitions. |
| mitigation | First mitigation and tradeoff | Select a concrete first step and connect it to diagnosis. Examples include shorter transactions, bounded jittered retries, reducing connection pressure, per-account admission queues, consistent lock order for real cycles, or migration after measurement. Explain queue durability, ownership/failover, deduplication and overload behavior when relevant; no prescribed technology wins automatically. |
| rollback | Operational rollback trigger | Name a measurable correctness invariant (e.g. negative balance, duplicate ledger, replay divergence) and a latency/availability trigger tied to a baseline or service objective (e.g. p99 or lock-wait regression). State the response to the trigger. Numerical examples are proposed deployment thresholds, not measured benchmark labels. |
| deployment | Limits and deployment | Explain transaction durability assumptions, initialization under multiple processes, bounded busy handling, operational observability, migration/cutover risks and the costs of any proposed architecture. Separate this authorization model from settlement/refunds/provider effects. |
| revision | Response to the reveal | If staged evidence exists, identify what changed from the sealed first answer and why the reveal supports it. Preserve first-answer defects. For a final-only submission mark evolution not assessable. |

The executable result is one input. A formal pass covers the declared finite
schedule and checkpoints; it does not establish every interleaving, production
durability under every crash, throughput, hot-account latency, originality or
human assessment validity. The suite does not run a timed hot-account load test.

For `alternative_format:true`, review feasibility against F1–F3 and F6 and
explain the executable interface difference. Require a concrete atomicity and
identity mechanism, failure recovery, and a proposed verification path. Record
the route as `review_required` even if the architecture appears promising. Do
not invent an executable pass or assign failure merely for choosing that route.

A review record can use this structure, repeating the criterion object for all
nine IDs above:

```json
{
  "task_id": "E1",
  "answer_sha256": "exact hash from evaluator",
  "reviewer": {"identity": "...", "expertise": "...", "conflicts": "...", "prior_exposure": "..."},
  "criteria": {
    "atomicity": {"judgment": "partial", "quote": "exact answer excerpt or null", "reason": "...", "unresolved": []}
  },
  "disagreements": [],
  "further_tests": [],
  "conclusion": "bounded qualitative judgment, separate from formal result"
}
```

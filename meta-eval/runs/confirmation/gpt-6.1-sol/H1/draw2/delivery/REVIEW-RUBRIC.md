# E1 independent explanation review

Formal execution and explanation review are separate results. A formal pass stays
`formal_pass_review_pending`; it does not establish explanation quality, novelty,
usefulness, human ability or hiring validity. The authored reference is one viable
answer, not an exhaustive key. Do not give it to a solver.

Obtain two independent first reviews before discussing disagreements. Preserve
both forms, disagreements and any later adjudication as separate artifacts. Record
the reviewer identifier and an explicit independence/conflict declaration. Form
validation cannot authenticate either declaration or the truth of a judgment.
Review alternative architectures on their own stated assumptions: they retain
`review_required` and receive no fabricated SQLite execution pass or failure.

For each criterion record an integer rating: **0** absent, materially wrong or
unsupported; **1** partly supported with a material omission; **2** explicit and
coherent with the submitted implementation or alternative. Add exact quotations
from `code`, `explanation` or `alternative`, a rationale and unresolved claims.
An omitted discussion can receive 0 with an empty evidence list and a rationale.
There is no sum, weighted total, creativity score or automatic explanation pass.

| Criterion ID | Evidence to assess |
| --- | --- |
| `atomicity_and_error_boundary` | Defines the atomic boundary covering identity check, allowance mutation, ledger row and durable decision. Avoids check-then-write races. Initializes without resets. Distinguishes failed/ambiguous database operations from business rejection. Explains rollback and commit-before-reply. Finite end-state checks are not proof of crash atomicity. |
| `global_identity_and_historical_replay` | Key identity spans A and B; both account and amount are checked. Accepted and rejected decisions are immutable. Replays return original remaining even after allowance changes; mismatches have no effects. Any proposed expiry or partitioning preserves the promised identity window. |
| `unknown_outcome_recovery` | A lost commit acknowledgement leaves the caller uncertain. Recovery reuses the original key and payload and queries/replays durable identity; it does not blindly create a new request or label an error as insufficient allowance. Distinguishes safely rolled-back transient errors from ambiguous commit outcomes. |
| `contention_versus_deadlock` | Differentiates waiting behind a hot resource from a cycle of dependencies; names evidence that could establish a cycle. Does not infer actual row-lock deadlocks from this reveal or the executable test. Understands SQLite's one-writer behavior and read-to-write upgrade/busy behavior. |
| `cross_account_parallelism_and_deployment` | Explains SQLite's database-wide writer serialization even across accounts; WAL improves reader/writer overlap, not writer/writer concurrency. Relates row locking, actors, queues, partitioning or other proposals to their real concurrency and global-key consistency costs. Addresses local versus multi-host storage/locking and durability assumptions. |
| `first_mitigation_and_rollback` | Chooses and justifies a first mitigation, describes what evidence would test it, preserves correctness under retries and overload, and names an actionable correctness/latency rollback trigger. Thresholds may be deployment-specific; no latency gold label exists. A proposal to shard or queue must account for global identity and fairness/backpressure where relevant. |

The reveal provides symptoms, not a measured production workload or a deadlock
graph. Reasonable choices can differ: shortened transactions, measured bounded
backpressure, bounded jittered retries, or a justified change of storage/ordering
architecture can each be supported. Record assumptions and testable claims rather
than rewarding keywords or a preferred technology. Compare an initial sealed
response and post-reveal explanation only when an actual staged transcript was
collected; direct final-answer grading does not establish adaptation.

Generate and validate a bound form:

```sh
python3 review.py template answer.json > review-first.json
# A reviewer independently completes the generated form.
python3 review.py validate answer.json review-first.json
```

`form_valid` establishes schema coverage, canonical answer binding and quotation
existence only. Hashes bind parsed JSON using Python's sorted-key, ASCII-escaped
JSON serialization; they are not external timestamps or identity authentication.

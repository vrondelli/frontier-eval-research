# E1: Concurrent allowance, durable identity and a hot account

This is the complete public contract for final-answer evaluation. The fixed hot-account
reveal is included below. This run does not measure adaptation from a sealed initial
answer, creativity, hiring fitness, throughput, or production latency.

Build and explain a Python SQLite transfer-admission service. This is authorization
allowance, not settlement, refunds, or an external payment provider. No day rollover
occurs. Only accounts A and B and valid request shapes are tested.

## Submission

Return one JSON object with `task_id: "E1"`, `code` (the complete Python source string,
at most 256 KiB UTF-8), and a nonempty `explanation` string. The JSON file must be at
most 1 MiB, UTF-8, with no duplicate keys, nonfinite numbers, or extra text. Extra
top-level fields are ignored. The source defines `Service(path)` with
`apply(request)` returning a JSON-serializable Python object. Use the Python 3.11+
standard library only; the production worker uses `/usr/bin/python3` in isolated mode.
No benchmark, oracle, reference answer, submission directory, or grader import exists
in the worker. Import and initialization must complete successfully.

Alternatively submit `{"task_id":"E1","alternative_format":true,
"alternative":"your design","explanation":"your reasoning"}`. Both text fields
must be nonempty. This receives `review_required`, never an executable pass or fail;
any code field is ignored. If present, `alternative_format` must be a JSON boolean.

## Graded executable requirements

1. Initialize accounts A and B to 100 integer units each, once. Initialization must
   be idempotent, including when fresh processes initialize concurrently. Every call
   in this evaluation uses a fresh service process on the same database in its trial.
2. Requests are `{"key": string, "account": "A" | "B", "amount": positive integer}`.
   Keys identify requests globally across accounts. Identical retries return exactly
   the original `{"status": "accepted" | "rejected", "remaining": integer}` decision,
   including historical remaining allowance after later admissions. A changed account
   or amount under an existing key returns exactly
   `{"status":"payload_mismatch","remaining":null}` with no state changes. No extra
   response fields are allowed. Booleans and floats are not integer response values.
3. If a new request has sufficient allowance, accept it and decrement that account by
   its amount. Persist exactly one decision and one ledger row atomically with the
   decrement. Otherwise persist a rejected decision with the current allowance and
   no ledger row or debit. Remaining allowance is never negative. All replay and
   mismatch operations leave all three public tables unchanged.
4. A storage error must either escape `apply` as an exception or return exactly
   `{"status":"error","remaining":null}`, leaving all public state unchanged;
   it is not an accepted or rejected business decision. Once the storage
   error is removed, the same key/payload can be retried to obtain its first durable
   decision. This includes errors while recording acceptance and rejection.
5. Use SQLite at the supplied path. The independent inspector reads these real tables:

   ```sql
   accounts(account TEXT PRIMARY KEY, remaining INTEGER);
   decisions(key TEXT PRIMARY KEY, account TEXT, amount INTEGER, status TEXT, remaining INTEGER);
   ledger(key TEXT PRIMARY KEY, account TEXT, amount INTEGER);
   ```

   Required column types and single-column primary keys must match these definitions.
   Extra columns and extra implementation tables are allowed. Public row values must
   have the declared integer/text types. There must be exactly the rows implied by the
   requests, with no extra public rows. Views cannot stand in for these tables.
   The database and any `ledger.db*` sidecars must be regular files, not symlinks, and
   each be at most 8 MiB. Each inspected table must contain fewer than 100 rows.
6. Multiple processes share the database. Replies and persisted state must correspond
   to a single legal serial history for each overlapping batch. This applies to
   competing spends, identical concurrent keys, and conflicting concurrent payloads.
   Both possible serial orders are legal; the first worker is not assumed to win.
7. Each batch has six wall seconds to start all fresh workers, import their source,
   construct their services and receive readiness acknowledgements. After all batch
   workers are ready, the batch has six wall seconds to reply and exit successfully.
   Errors are permitted only in the specified storage
   fault steps. Each protocol message is at most 64 KiB including its newline. Resource
   limits are 512 MiB address space, 256 file descriptors, 10 CPU seconds, 8 MiB per file,
   and no core dumps per process. The worker has a disposable writable `/state`, private
   `/tmp`, read-only source/adapter/system runtime, private network/PID namespaces, and
   an empty inherited environment. It has no network service or external files.
   Use the supplied database path and support process restart without external state.

## Exact finite test schedule

The following schedule runs **three times in separate empty directories/databases**.
Every line after initialization uses fresh processes. For overlapping pairs the parent
waits for both services' readiness acknowledgements, then releases both requests before
waiting for either reply. This does not force internal SQLite instruction interleavings.
All workers are stopped before independent SQL inspection after **every** line.

| Step | Requests, in `(key, account, amount)` notation |
| --- | --- |
| overlap | Concurrent `(x,A,60)` and `(y,A,60)`, also exercising concurrent initialization |
| replay | `(x,A,60)`, then `(y,A,60)` from new processes |
| mismatch | `(x,B,60)`, then `(y,A,61)` |
| independent account | `(b,B,100)` |
| durable rejection | `(reject,B,1)`, then identical retry |
| advance and historical retry | `(advance,A,10)`, then `(x,A,60)`, then `(y,A,60)` |
| duplicate overlap | Two concurrent `(duplicate,A,10)` calls |
| conflicting overlap | Concurrent `(conflict,A,1)` and `(conflict,B,1)` |
| replay conflicting identity | `(conflict,A,1)`, then `(conflict,B,1)` |
| acceptance storage fault | Install a `BEFORE INSERT ON ledger` trigger using `RAISE(ABORT,...)`; send `(fault_accept,A,1)`. Require the storage-error behavior in requirement 4 and unchanged public state. Remove trigger and retry the same request. |
| rejection storage fault | Install the same aborting trigger on `decisions`; send `(fault_reject,B,1)`. Require the storage-error behavior in requirement 4 and unchanged public state. Remove trigger and retry. |

The trigger name `e1_fault` is reserved for the evaluator; do not create or remove it.

For the initial overlap, either x or y is accepted, the other is rejected; both original
remaining values are 40, A ends at 40, and there is exactly one ledger row and two
decisions. B remains at 100 until its own request. The independent state model enumerates
the legal serial orders of each pair and requires both replies **and** SQL state to match
the same order. State-only or reply-only agreement cannot pass. A failed step stops that
trial; the other isolated repetitions still run. No crash-instruction injection, kill
recovery test, arbitrary query fuzzing, or live latency comparison is scored here.

## Hot-account reveal and separately reviewed explanation

A few accounts now dominate traffic, lock waits rise, and operators report deadlock
retries. Explain your design and your response to that evidence. Review uses these eight
criteria, with evidence quotes and unresolved claims retained, independently of the
formal executable result:

| Criterion ID | Public review requirement |
| --- | --- |
| atomic_boundary | Identify the atomic boundary covering key lookup, allowance, ledger and durable decision; explain exception/rollback behavior and durable rejections. |
| global_identity | Explain global identity scope, historical accepted/rejected replay and payload-mismatch immutability. |
| unknown_outcome_replay | Explain how a caller handles a lost/unknown response by retrying the same identity and payload without assuming whether commit occurred. |
| contention_vs_cycles | Distinguish hot-account queueing/lock contention from cyclic lock waits; state the evidence needed to diagnose reported deadlocks. |
| cross_account_parallelism | Explain SQLite's writer serialization, why distinct accounts may still contend, and how a different architecture could enable cross-account parallelism while preserving identity and atomicity. |
| first_mitigation | Choose a first mitigation and justify it using the stated workload and correctness constraints. There is no uniquely required architecture or retry policy. |
| rollback_trigger | Name an operationally observable correctness or latency trigger for rolling back the mitigation. No numeric latency threshold is a gold label. |
| deployment_tradeoffs | Explain hot-account capacity limits and deployment tradeoffs such as serialization, contention, durability, failure/recovery or coordination costs. Bound unverified performance claims. |

The automatic grader checks explanation presence, not explanation quality. Human reviewers
use `REVIEW-RUBRIC.md`; no automatic explanation score, creativity score or hiring score is
produced. Alternatives outside this interface remain available for independent review.

## Result meanings

`pass` means all declared finite executable checks passed. Its overall status is
`formal_pass_review_pending`. `fail` means an executable contract violation was observed.
`invalid` means the submitted JSON/envelope is invalid. `unavailable` means required Linux
isolation could not start, and no candidate was executed. `internal_error` means an
evaluator problem; it is not a candidate failure. `review_required` means alternative
format, with no executable verdict. Only formal pass exits 0 from `grade`; all other
statuses exit 2. There is no weighted or partial score. Trusted authored-control reports
are explicitly labeled `trusted_control` and are not untrusted-submission isolation evidence.

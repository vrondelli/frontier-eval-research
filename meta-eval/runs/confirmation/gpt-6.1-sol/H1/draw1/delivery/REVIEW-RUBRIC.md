# E1 independent explanation review

The executable result covers only the finite public SQLite contract. A formal pass
leaves this review pending. Do not infer performance, engineering judgment,
originality, hiring validity or production safety from that result. Database errors
must propagate as errors or an explicit non-business error path, never become a
saved accepted/rejected decision; inspect the submitted source as well as the prose.

Preserve two independent first reviews and disagreements before adjudication.
Record reviewer identity, independence/conflicts, exact answer SHA-256, criterion
label, supporting answer quotes, reasoning, unresolved claims and requested tests.
Identity declarations and quotes are evidence for review, not authenticated identity
or proof that the judgment is correct. No model or human review is claimed here.

For each criterion use **supported**, **partial**, **unsupported** or
**not assessable**. Presence of relevant words is not sufficient. Do not add a
combined numerical score. Judge an alternative design on its own stated model;
do not require the reference's locking technique or treat it as an exhaustive key.

| Criterion | Evidence needed for supported |
| --- | --- |
| Atomic admission | Identifies one committed unit for allowance, accepted ledger row and saved decision; durable rejection and no effects for mismatch. Explains rollback on DB failure. A process-local lock alone cannot protect multiple processes. |
| Identity | Uses a global key namespace and compares both account and amount before returning the saved outcome. Rejected outcomes retain their historical remaining value. |
| Unknown outcome | On a lost response/uncertain commit, replay the same key and payload to recover the saved result; do not issue a new key or infer rejection from a timeout. Distinguishes a DB error from a business decision. |
| Contention and cycles | Separates queueing behind a hot writer/account from a lock dependency cycle. SQLite has one writer per database; lock/busy failures do not by themselves prove row-lock deadlocks. Investigates actual engine, transactions and lock order before labeling the reveal. |
| Cross-account parallelism | Explains that this SQLite file serializes writers even across A and B. Discusses a deployment approach that can parallelize independent accounts, while retaining global key consistency and atomic effects. Does not claim that WAL gives simultaneous writers. |
| First mitigation | Chooses a concrete first intervention tied to a measured cause, e.g. shorten transactions/remove external calls, bounded retries with jitter, per-account scheduling/backpressure; describes fairness/overload and why retries do not increase hot-account capacity. |
| Rollback trigger | Gives an observable correctness trigger (e.g. duplicate ledger/negative allowance/decision mismatch) and a latency or retry/queue trigger with baseline/window/threshold or an explicit measurement plan. Names a reversible action. There is no executable latency gold label. |
| Deployment tradeoffs | States assumptions about durability, crash/commit ambiguity, bottlenecks, key routing/coordination and migration. SQLite serialization can be a valid bounded answer; distributed mechanisms need their own consistency argument. |
| Revision after reveal | If staging is present, compares the sealed first design to the revised answer using quotations and explains what the reveal changed. Without staging, mark this criterion not assessable. Do not reconstruct an earlier answer. |

For an alternative-format answer, leave executable correctness **not executed** and
route the design to independent review. Identify the proposed interface, its
invariants and how to test it before making correctness claims. A novel mechanism
is neither a fabricated zero nor an automatic pass.

For any originality/usefulness claim, declare the comparison repertoire and use
independent evidence. An authored reference/control run is evaluator development,
not fresh model performance. Physical load, production deadlocks and latency
remain untested by the small correctness suite.

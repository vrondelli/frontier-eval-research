# E1 explanation review

Executable correctness and explanation quality are separate results. A nonempty explanation is only an interface check. No keyword matching or total hiring/creativity score is used. An executable pass leaves review pending; a good explanation cannot repair a demonstrated executable violation.

Use two independent first reviews, retain their disagreements, then record any adjudication separately. Read the answer rather than the reference solution first. Identify reviewer, independence and prior exposure. For every criterion record a rating, exact supporting quotes, rationale and unresolved claims. Quotes may come from the explanation or alternative description. Missing evidence can receive 0 with an empty quote list. Rating 1 or 2 requires an exact quote. A structurally valid form does not prove reviewer independence or judgment quality.

| Criterion | 0: absent/incorrect | 1: partial | 2: supported and coherent |
| --- | --- | --- | --- |
| `atomic_boundary` | Allows partial state or treats DB errors as business rejection | Names a transaction but leaves commit/ledger/decision boundary unclear | Covers identity check, allowance, one ledger effect and decision atomically; replies follow commit; failures roll back/propagate |
| `global_identity_and_history` | Per-account identity, overwrites conflicts, or recalculates historical replies | Correct duplicate rule but omits rejected history or concurrent ownership | Global key scope; account/amount comparison; immutable accepted and rejected replies; conflict changes nothing |
| `unknown_outcome_replay` | Timeout treated as proof of failure or retried with a new key | Says retry but leaves commit ambiguity/persistence unclear | Explains unknown commit outcome and same-key, same-payload replay against durable state; distinguishes it from observed DB error |
| `contention_and_cycles` | Assumes every wait is a deadlock or promises retries solve the cause | Recognizes contention but gives weak diagnostic evidence | Distinguishes wait/upgrade conflict from lock cycles; asks for error/transaction/wait-for evidence; qualifies SQLite's single-writer behavior |
| `parallelism_and_first_mitigation` | Claims SQLite WAL or per-account mutex alone permits independent SQLite writers | Plausible mitigation but weak hot-account or global-identity treatment | Chooses a first mitigation and explains its mechanism; hot-account serialization; cross-account write limits; any partition/queue identity and ownership obligations |
| `rollback_and_tradeoffs` | No trigger or breaks correctness to improve latency | Generic monitoring/rollback or incomplete deployment tradeoffs | Observable correctness and latency triggers; baseline/window or similarly actionable thresholds; safe rollout/rollback ownership and operating tradeoffs |

Do not require the reference architecture, BEGIN IMMEDIATE specifically, WAL, queues, a particular latency number, or identical phrasing. Conditional updates, optimistic transactions and other designs can satisfy the same contract. Assess whether the proposed first mitigation addresses the diagnosis while preserving identity and atomicity. A strong answer may reject the reveal's deadlock premise for its chosen database and explain why. The executable suite has no performance or latency gold label.

For staged runs also review the preserved initial answer against the final response: what changed, what evidence justified it, and what remained unresolved. No automatic revision score is produced. Plain `grade` does not prove a staged run.

Alternative-format answers receive `review_required` without candidate execution. Assess feasibility, identity ownership, atomicity, durable rejection, replay, hot-account limits, failure recovery and tradeoffs independently; record what additional proof is needed. A construction outside the SQLite interface must not be assigned an invented executable pass or automatic zero.

Example commands:

```sh
python benchmark.py review-template answer.json review-A.json
# Fill the form independently.
python benchmark.py validate-review answer.json review-A.json
```

The validator checks answer binding, declared identity/independence, coverage, rating types and quote existence. It cannot establish that quotes support the ratings, authenticate identity, compare architectures exhaustively, or validate hiring/creativity constructs.

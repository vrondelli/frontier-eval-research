# E1 independent explanation review

Review the exact answer bound by `answer_sha256` in the executable report. If using
the staged protocol, also review the preserved first answer and describe what
changed after the hot-account reveal. Record reviewer identity, date, relevant
experience and conflicts. Two reviewers should first record independent judgments;
preserve disagreements before adjudication. No independent review has occurred
merely because this form exists.

For each criterion below, record **supported**, **partial**, **unsupported**, or
**unresolved**, with exact answer quotations, reasoning, and any additional evidence
needed. Do not grade by keyword presence or require the authored control's design.
Do not combine these judgments into a creativity, hiring, or latency score.

| Criterion | Evidence to assess |
| --- | --- |
| Atomic admission | Identifies one transaction covering allowance check/decrement, unique decision and exactly one accepted ledger row; rejected decisions are also durable. Explains why another process cannot overspend through a read/write race. Distinguishes database errors from business rejection. |
| Identity and immutable replay | Key scope is global, including across accounts. Stored original payload is compared before business processing. Both accepted and rejected retries return the original status and historical remaining; mismatch changes nothing. |
| Unknown commit outcome | On lost acknowledgement or uncertain commit, retry/reconcile with the same key and payload against durable decisions. Avoids minting a new key, blindly applying another debit, or translating a database error into a durable rejection. States the relevant durability assumptions. |
| Reveal diagnosis | Distinguishes queueing behind a hot resource from a lock wait cycle; asks for concrete wait graph/transaction/lock evidence before attributing retries to deadlocks. Notes that SQLite writer serialization is itself a contention limit; reported deadlock retries may describe another deployment or wrapper. |
| Cross-account parallelism | Explains the actual interface's database-wide writer limitation. WAL can improve reader/writer overlap but does not provide multiple concurrent writers in one SQLite database. If proposing row locks, account partitions or queues, explains serialization per hot account and preservation of global key identity across accounts. |
| First mitigation | Chooses a concrete first action and justifies it against the diagnosed bottleneck: e.g. shorten transactions and remove remote work, bound/shape hot-key queues, limit admission concurrency, or address demonstrated inconsistent lock ordering. Retries/backoff are bounded and distinguish retryable contention from uncertain outcomes. Accept justified alternatives. |
| Rollback and deployment | Names an observable correctness rollback trigger (such as reconciliation discrepancies, duplicate ledger entries or allowance violation) and a latency trigger with an operational baseline/threshold/window, rather than claiming an executable latency gold label. Describes migration, durability and operational costs relevant to the chosen deployment. |
| Limits and useful alternatives | Separates finite checks from exhaustive correctness/performance proof; makes unsupported claims explicit. Reviews an alternative architecture on its own merits, without fabricating a SQLite executable result. |

A working service does not establish a good explanation. A good explanation does
not establish that submitted code works. Report both results. `review_required`
alternatives remain open for review, never automatic failures or passes.

Suggested review record:

```json
{
  "task_id": "E1",
  "answer_sha256": "copy from the evaluator report",
  "reviewer": "name or stable identifier",
  "date": "YYYY-MM-DD",
  "experience_and_conflicts": "...",
  "criteria": [
    {"criterion": "Atomic admission", "judgment": "unresolved",
     "quotes": [], "reasoning": "...", "evidence_needed": "..."}
  ],
  "reveal_revision": "...",
  "unresolved_claims": [],
  "independent_review_status": "..."
}
```

Repeat the criterion record for all eight criteria. A copied quote and declared
identity bind a review to an answer; they do not authenticate independence or make
the review correct.

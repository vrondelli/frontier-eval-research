> Archived source excerpt. Original location: `practical-coding-pilot-20261101/RESULTS.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# Practical coding pilot — observed results

Completed 2026-11-01. **Sol passed all nine episodes. No final software failure, operational failure or automatic retry was observed.** Terra and Astra were not run.

Open [the readable report](http://127.0.0.1:5187/practical-coding-pilot-20261101/report.html) for every exact task, actual final answer, source diff, terminal command/result and independent grade. RESULTS.json (historical reference: `RESULTS.json`) contains the numerical results.

| Repository repair | Sol trials passed | Acceptance checks in each trial | What the saved software did |
| --- | --- | --- | --- |
| Current-state migration rollback | 3/3 | 23/23 | Preserved later application writes, mixed currencies, foreign keys, index and migration journal through upgrade/rollback, no-ops and controlled aborts. |
| Concurrent regional publication | 3/3 | 38/38 | Serialized conflicting publishers, preserved accepted/rejected decisions, validated both revision and region, refreshed policy and retained durable state after completed-reply process kill. |
| Shared policy authority | 3/3 | 30/30 | Removed divergent web/batch/scheduled eligibility rules, preserved full authority context and exact decisions, and kept audit rows aligned with allowed reservation effects. |

These fractions describe different finite acceptance suites, not comparable ability scores. A passing suite does not establish correctness for every input or schedule.

## Concrete examples

The migration answers used transactional table rebuilding. In each delivered SQLite example, rollback retained the updated order for Renée at **−1,250 EUR**, the existing **−75 JPY** order, and a new **900 GBP** order, plus the later shipment/audit rows. Restoring the initial backup would have lost those changes. Independent fresh-process tests also passed on another dataset, repeated cycles, foreign-key/cascade behavior and controlled failures.

In publication, a request with the right revision but the old region returned `rejected` at revision 2. An earlier rejection stayed rejected at its original revision 1 even after its input became otherwise eligible. A new decision after policy replacement selected `eu-2` with a 55 ms budget at revision 4. Eight two-process contention rounds per episode each produced one acceptance and consistent durable effects.

In policy, a denied batch item did not suppress the next allowed item. A later policy expansion produced the authority's unchanged `expanded_approved` / `v2` answer through web. A subsequent scheduler freeze returned `incident_freeze` / `v3-incident`, overriding the starter's old unconditional scheduler allowance. The owner checked authority calls outside the submitted process and inspected SQLite after workers stopped.

## Execution and verification

- Model: `gpt-6.1-sol`, requested effort `high`, resolved alias verified in native app-server records. Each episode used a fresh conversation and original repository.
- Three subagents built task packages and the runner in parallel. Root reviewed contracts and isolation, reexecuted all six valid implementations and all ten defective controls, then froze 219 inputs before pilot inference. The two-stage compatibility episode is separate and excluded.
- Sol used 52 native terminal calls across the nine pilot episodes. Bash, Python, Git, file editing and tests were available in persistent offline repositories; this was the project's terminal broker through Codex app-server, not the stock terminal UI.
- Episode runtime was 63.268–131.400 seconds, excluding subsequent owner grading. The 1,200-second episode and disclosed command limits were not hit. No terminal output truncation or command timeout was observed.
- Seven shell commands returned nonzero: five attempted unavailable `rg`, and two broad `find ..` commands encountered container permission errors. Sol continued successfully. These were recoverable tooling issues, not final software failures.
- Final cumulative native usage, summed once per episode: 1,164,906 input tokens and 30,425 output tokens, total 1,195,331. Cached input 893,696 and reasoning output 2,204 are subsets. Input includes repeated context across tool interactions. Monetary billing was not returned by this signed-in app-server route and cannot be inferred from these counts alone.
- Frozen native audit: 9/9 passed. Supplemental custody audit (historical reference: `CUSTODY-AUDIT.json`): 9/9 passed. It was added after freeze to strengthen protocol/source/snapshot binding; no task acceptance criteria changed. Five temporary-copy tampering controls were rejected.
- Final integrity check (historical reference: `FINAL-INTEGRITY.json`) confirms all nine expected assignments and exact equality between each final snapshot and the workspace supplied to its grader. No actor containers remained at final inspection. Historical stop ordering is recorded by the runner; the cleanup query alone cannot independently prove that history.
- Prior evidence check (historical reference: `PRIOR-EVIDENCE-CHECK.json`): all 6,741 previously frozen readiness-study files remain unchanged.

The delegated source/evidence reviews are migration (historical reference: `reviews/migration-review.md`), publication and policy (historical reference: `reviews/context-review.md`), and runner/isolation (historical reference: `reviews/runner-review.md`). They are agent reviews, not Vladimir's required human expert review. The frozen study plan retains its original preparation status; this results record describes completed execution.

One disclosure issue remains for a future version: publication/policy prose lists the major worker limits but omits individual host-inspection/protocol guardrails (three-second SQL inspection, 1,000 rows, 1 MiB envelope and 100 policy messages). No pilot execution hit them. They must be documented before a future study; this frozen pilot was not silently edited.

## Meaning for the hackathon

This is useful practical baseline evidence and demonstrates that the evaluator can accept materially different valid solutions while rejecting known defects. It does **not** supply the meaningful practical frontier failures we were looking for. It also does not establish that ordinary tools caused an improvement: this pilot did not randomize tool access on matched tasks.

The observed formal diagnostic failures from the earlier research still cannot be presented as demonstrated long-horizon coding failures. Here, Sol successfully repaired these small repositories when invariants were explicit. The next discriminating study should involve a genuinely evolving repository with successive feature changes, accumulated state and explicit cross-change invariants, rather than splitting this same repair into artificial stages or reducing budgets until a failure appears. That follow-up needs its own frozen design and references. Human expert review remains pending.

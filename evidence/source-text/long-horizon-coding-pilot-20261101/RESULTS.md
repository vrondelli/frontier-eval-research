> Archived source excerpt. Original location: `long-horizon-coding-pilot-20261101/RESULTS.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# Successive-change pilot: observed results

Completed 2026-11-01. **All three Sol trajectories passed all ten checkpoints, including their carried application histories. All three fresh-final controls passed the same final primary suite. No new-feature failure or stable architectural regression was observed.**

Open [the interactive checkpoint report](http://127.0.0.1:5187/long-horizon-coding-pilot-20261101/report.html) for exact requests, actual answers, source snapshots/diffs, shell commands and independent assertions. RESULTS.json (historical reference: `RESULTS.json`) contains the measured results.

| Condition | Episodes | Outcome |
| --- | --- | --- |
| Successive changes, same repository and conversation | 3 | All 30 cumulative checkpoints passed primary and carried-history checks. |
| Full final specification from the same original repository | 3 | All three passed the identical 195-check final primary suite. |
| Stable earlier-case architectural regression | 3 sequential trajectories | None observed. |
| Operational/transport or grading infrastructure failures | 6 episodes | None observed. |

## What actually carried forward

Each sequential run received genuine feature changes: durable retries, batch, scheduled jobs, tenant migration, concurrent capacity accounting, cancellation/refund, atomic outbox, delivery/acknowledgment, read-only preview and tenant reporting. The same files, Git repository, tests, synthetic database and native conversation persisted across the ten requests. Future prompts and fixtures arrived only at their stage. Private grading happened after the whole trajectory; no external grader results were returned between changes.

The accepted code kept policy evaluation in the injected authority, checked immutable identities before reevaluation or effects, and committed decisions, reservation state, capacity and applicable events in one transaction. New adapters retained earlier semantics. Cancellation released capacity once while keeping original reservation replies. Preview obtained a fresh answer without creating business state. Delivery committed an acknowledgment before proceeding to the next event, and reporting kept tenant scope and historical decision counts separate from active reservations.

Independent analysis inspected copies of all 30 checkpoint databases. Every final sequential artifact retained the seed and ten journey decisions: **11 receipts, 11 reservation records, five cancellation records and eight sent outbox events**. Two active reservations in the journey tenant totaled 29 cents; four active legacy reservations totaled 136 cents. The journey account retained its configured limit of 1,000 and usage of 29. No original artifact was opened for the analysts' supplementary SQLite reads; copies were used.

Final model-authored test runs were confirmed in native terminal output: 67, 67 and 75 passing tests for sequential runs 1, 2 and 3. These are development-process evidence, separate from the frozen independent acceptance suites. The final sequential acceptance suite had 195 primary assertions plus 29 carried-history assertions. Checkpoint counts grow with the requirements; they are not independent samples or comparable ability scores.

## Evidence checks and resources

- Six completed, separately initialized native threads; 33 implementation turns; 139 terminal calls. Requested and resolved model alias: `gpt-6.1-sol`, requested effort `high`. No Terra or Astra runs.
- Sequential episode runtime: 1,222.158–1,396.219 seconds, approximately 20–23 minutes each. Fresh-final runtime: 193.380–228.364 seconds, approximately three to four minutes. Subsequent grading is outside those episode durations.
- No automatic retries, private feedback, timeouts, output truncation or observed native context compactions. Four nonzero shell commands were recovered during development: three search/no-match errors and one incorrectly written outbox test. The latter reused a cancellation command key for different targets; Sol corrected the test's key, and the unchanged implementation passed its subsequent tests and independent checks. This was not a final product failure.
- Native cumulative usage, summed once per thread: **15,046,771 input + 173,213 output = 15,219,984 tokens**. Cached input 14,374,272 and reasoning output 20,964 are subsets. Input includes repeated context across tool interactions. Monetary billing was not provided by the signed-in app-server connection.
- Custody audit (historical reference: `CUSTODY-AUDIT.json`): all six exact assignments passed after all 33 grading records and batch completion existed. All checkpoint manifests and final workspaces still match their bytes after grading. All 430 frozen input pins remain unchanged; no actor containers remained.
- Root independently accepted the ten reference histories and final alternative and rejected eight authored semantic controls before inference. All eight defective controls still passed the newest reporting feature while violating earlier contracts, so an all-pass model result is not attributable merely to checking the latest feature.
- Earlier evidence check (historical reference: `PRIOR-EVIDENCE-CHECK.json`): the prior practical pilot's 1,647 files and readiness study's 6,741 files remain unchanged.

Detailed delegated analyses: sequential code and state (historical reference: `analysis/sequential-review.md`), control and grader review (historical reference: `analysis/control-and-grade-review.md`), and native runtime (historical reference: `analysis/runtime-review.md`). The control review was written before sequential run 1 completed; root subsequently verified that all six final outputs use the same 195 primary assertion IDs, introduction checkpoints and categories. Agent reviews do not substitute for Vladimir's human expert review, which remains pending.

## Interpretation

This is a positive result for Sol on **this small service under explicit architectural commitments**. It demonstrates successful preservation through ten product changes and several schema upgrades in this setup. It supplies no observed practical architectural-drift failure for the hackathon.

The final sequential implementations contained 236–247 nonblank product Python lines, compared with 175–200 for the fresh-final implementations under the report's descriptive counting rule. That includes comments and helper code and does not measure redundancy, maintainability or correctness. Branch-count proxies were also descriptive. More code alone is not an architectural regression, and this experiment did not measure the cost of a further maintenance task.

The shared final suite also passed in all fresh controls, so no mode performance gap was observed. Even a gap would not by itself isolate iteration as the cause: the conditions differ in requirement foreknowledge, context and computation allocation. Three repeats on one compact standard-library service cannot establish production-scale long-horizon reliability, behavior over context compaction, or the ability to discover unstated architecture requirements.

For the hackathon, retain this as a practical positive control and a check against overstating the earlier formal diagnostic failures. The remaining evidence gap is a defensible, meaningful failure in a more realistic system with deeper interactions. A larger existing application and additional service/failure boundaries are better candidates for the next study than tightening operational limits or treating a harmless code-size increase as a failure. That would require a separately frozen design, references and trials; it was not appended adaptively to this pilot.

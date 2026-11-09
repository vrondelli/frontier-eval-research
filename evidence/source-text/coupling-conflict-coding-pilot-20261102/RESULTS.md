> Archived source excerpt. Original location: `coupling-conflict-coding-pilot-20261102/RESULTS.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# Both coding scenarios completed: no observed coupling failure

Sol (`gpt-6.1-sol`, high) completed the four registered trajectories through signed-in Codex app-server, using terminal, Python, Git, editing and self-tests. The evaluator then graded every saved checkpoint after all actors had stopped. No private evaluator feedback reached the coding agents. No native retry or replacement trajectory was used.

| Condition | Trajectory | Completed checkpoints | Passed assertion observations | Failed | Stable earlier-pass/later-fail observations |
| --- | --- | ---: | ---: | ---: | ---: |
| Successive short requests | sparse-r1 | 12/12 | 1,497 | 0 | 0 |
| Successive short requests | sparse-r2 | 12/12 | 1,497 | 0 | 0 |
| Ten detailed releases together | dense-r1 | 3/3 | 507 | 0 | 0 |
| Ten detailed releases together | dense-r2 | 3/3 | 507 | 0 | 0 |

All four final states pass 180/180 applicable assertions. All 30 checkpoints have the expected stable assertion coverage, with no unreached dependent checks, grading infrastructure errors or cleanup errors. The 4,008 assertion observations are repeated related checks across four trajectories, not 4,008 independent ability samples. Each baseline/reference and the materially different final reference also passed preflight; five intentionally defective coupling controls failed as expected while retaining their newest feature. Those authored controls are not model failures.

## What actually happened

**Retail change versus wholesale behavior.** The maintenance request added a future retail-only per-unit discount ceiling. In one exact graded example, a 1,001-cent item with a computed 500-cent unit discount was capped to 101 cents for retail. Wholesale kept its 500-cent unit discount. The retail total was 1,980 cents for two units after tax and its shipping waiver; wholesale remained 1,602 cents with its own shipping policy. Both matched the independent expectations.

**New policy versus old financial history.** The same change preserved captured old orders, command replays, stored wholesale quotes and original-value refunds. The captured-value refund example remained 1,102 cents. Current pricing was not allowed to rewrite that history.

**Delivery retry versus business state.** With retry limit one, exhausted offline events were skipped, including after restart. Raising the limit resumed attempts without resetting counters; saved attempt counters moved from one to two. Delivery preserved business and command-identity state. Both maintenance probes passed in every trajectory.

The actual code localized M01 production edits to pricing and M02 edits to delivery in all four trajectories. The separate source review (historical reference: `analysis/ARCHITECTURE-OBSERVATIONS.md`) documents real functions, exact diffs and hashes. This describes the observed implementation; file counts and edit size do not prove architectural quality or absence of all coupling.

## What the result supports

This pilot produced a functioning evaluation and no observed behavioral coupling failure under the predeclared requests. It does not support a claim that Sol inevitably accumulates architectural drift across these changes. It also does not establish that one disclosure condition is better: both passed, there are only two repeats each, and detail, foreknowledge and number of turns differ together.

For the hackathon, this version is not an evidence-backed model-failure lead. Keep it as a regression harness and a negative research result. A subsequent study would need a stronger independently justified task or a larger existing repository with observable non-local invariants; it should be registered as a new experiment rather than replacing these passing observations or retrospectively changing their grading.

This is one small synthetic Python/SQLite service over laboratory requests. Twelve coding turns are not months of production work, no context compaction occurred, and no broad long-horizon reliability or human engineering/hiring validity has been established. Human validation remains pending as requested.

## Evidence

- Interactive report (historical reference: `report.html`): every native answer, saved working-tree diff and exact grader trace.
- Frozen design (historical reference: `DESIGN.md`), assignments (historical reference: `ASSIGNMENTS.json`), source freeze (historical reference: `FREEZE.json`), public contract (historical reference: `task/contract.json`), disclosure inventory (historical reference: `DISCLOSURE-INVENTORY.json`).
- Native evidence audit (historical reference: `CUSTODY-AUDIT.json`): all 5,568 checks passed; four distinct persistent threads, 30 completed turns, 123 terminal calls and no native/source/snapshot/cleanup errors.
- Additional native review (historical reference: `analysis/NATIVE-REVIEW.json`), independent product-result review (historical reference: `analysis/RESULT-REVIEW.json`), machine-readable outcomes (historical reference: `analysis/OUTCOME-SUMMARY.json`), grading record (historical reference: `GRADING.json`).
- Preflight (historical reference: `PREFLIGHT.json`) and negative-control/reference results (historical reference: `evaluator/preflight/summary.json`). The excluded two-turn transport compatibility check (historical reference: `COMPATIBILITY-RESULT.json`) does not count in the four coding trajectories.
- Review-receipt restoration (historical reference: `analysis/REVIEW-RECEIPT-RESTORATION.json`): an appended mechanical review check was preserved separately and the exact registered receipt restored by hash; no experiment source or observation changed and no native run restarted.

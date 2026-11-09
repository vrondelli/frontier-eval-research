# What each model-created evaluator got right and wrong

This page lets you find a saved output and follow its evidence. To understand the question before reading the IDs, start with [how the meta-eval works](HOW-THE-META-EVAL-WORKS.md) or [the concrete failures](CASE-STUDIES.md).

The experiment retains all 31 author attempts. Nineteen completed evaluator packages receive scores. Four completed audit outputs are reported separately, seven attempts timed out, and one has unknown completion. A timeout is not given an invented score.

A range such as **57.50-82.50 /100** means 57.5 supported points, 17.5 observed failed points and 25 unresolved points. It is not a confidence interval or a percentage probability of trustworthiness. Human semantic review remains incomplete.

The failed-check codes you will encounter here mean:

- **B2:** the solver was not told a rule the grader required.
- **D1:** a baseline correct submission was rejected. In H1 budget draw3, this includes a documented intermittent worker-protocol problem.
- **D2:** a correct alternative or equivalent representation was rejected.
- **E1:** a known faulty program was accepted.

“None established” means no failed check was established by the available evidence. It does not mean the whole evaluator has been qualified. Expand an attempt's notes for its original detailed interpretation, or use [the full machine-readable report](../meta-eval/grades/scored-v2-final/REPORT.json).

| Attempt | Status | Score /100 | Failed checks |
|---|---|---:|---|
| `initial_screen/gpt-6.1-sol/H1` | Completed | 57.50-82.50 | B2, D2 |
| `initial_screen/gpt-6-astra/H1` | Timed out | Not scored | None established / unresolved |
| `initial_screen/gpt-6.1-sol/H2` | Completed | 10.00-100.00 | None established / unresolved |
| `initial_screen/gpt-6-astra/H2` | Completed | 10.00-100.00 | None established / unresolved |
| `initial_screen/gpt-6.1-sol/H3` | Completed | 12.50-100.00 | None established / unresolved |
| `initial_screen/gpt-6-astra/H3` | Completed | 15.00-100.00 | None established / unresolved |
| `initial_screen/gpt-6.1-sol/H4` | Completed | 45.00-100.00 | None established / unresolved |
| `initial_screen/gpt-6-astra/H4` | Completed | 42.50-100.00 | None established / unresolved |
| `initial_screen/gpt-6.1-sol/H5` | Timed out | Not scored | None established / unresolved |
| `initial_screen/gpt-6-astra/H5` | Timed out | Not scored | None established / unresolved |
| `initial_screen/gpt-6.1-sol/H6` | Completed | 58.50-100.00 | None established / unresolved |
| `initial_screen/gpt-6-astra/H6` | Completed | 37.50-80.00 | D2, E1 |
| `initial_screen/gpt-6.1-sol/H7` | Completed | 67.50-100.00 | None established / unresolved |
| `initial_screen/gpt-6-astra/H7` | Completed | 67.50-100.00 | None established / unresolved |
| `initial_screen/gpt-6.1-sol/H8` | Completed | Not scored | None established / unresolved |
| `initial_screen/gpt-6-astra/H8` | Completed | Not scored | None established / unresolved |
| `initial_screen/gpt-6.1-sol/H9` | Completed; delivery recovered | Not scored | None established / unresolved |
| `initial_screen/gpt-6-astra/H9` | Completed; delivery recovered | Not scored | None established / unresolved |
| `H1_same_condition_confirmation/gpt-6.1-sol/H1/draw1` | Timed out | Not scored | None established / unresolved |
| `H1_same_condition_confirmation/gpt-6.1-sol/H1/draw2` | Timed out | Not scored | None established / unresolved |
| `H1_same_condition_confirmation/gpt-6.1-sol/H1/draw3` | Timed out | Not scored | None established / unresolved |
| `H6_same_condition_confirmation/gpt-6-astra/H6/draw1` | Completion unknown | Not scored | None established / unresolved |
| `H6_same_condition_confirmation/gpt-6-astra/H6/draw2` | Completed | 57.16-100.00 | None established / unresolved |
| `H6_same_condition_confirmation/gpt-6-astra/H6/draw3` | Completed | 47.50-90.00 | E1 |
| `H1_budget_diagnostic/gpt-6.1-sol/H1/draw1` | Completed | 42.50-82.50 | B2, D2 |
| `H1_budget_diagnostic/gpt-6.1-sol/H1/draw2` | Completed | 57.50-82.50 | B2, D2 |
| `H1_budget_diagnostic/gpt-6.1-sol/H1/draw3` | Completed | 42.50-72.50 | B2, D1, D2 |
| `selected_hit_clean_staging/gpt-6.1-sol/H1` | Completed | 57.50-82.50 | B2, D2 |
| `selected_hit_clean_staging/gpt-6-astra/H6` | Completed | 37.50-80.00 | D2, E1 |
| `selected_hit_coached_staging/gpt-6.1-sol/H1` | Completed | 67.50-100.00 | None established / unresolved |
| `selected_hit_coached_staging/gpt-6-astra/H6` | Timed out | Not scored | None established / unresolved |

## Detailed notes for each attempt

<details>
<summary>initial_screen/gpt-6.1-sol/H1</summary>

Correct applied-status Service rejected; accepted-only grading literal omitted from the package's documented solver views. Literal-only paired replay changes FAIL to PASS.

</details>

<details>
<summary>initial_screen/gpt-6-astra/H1</summary>

600s timeout. Snapshot shows related staged-view issue; not a second completed author failure.

</details>

<details>
<summary>initial_screen/gpt-6.1-sol/H2</summary>

Exact recovered rubric instruction text, changed runtime/context. Required headings, score mapping, worked arithmetic and calibration reviewed; valid alternative criteria preserved.

</details>

<details>
<summary>initial_screen/gpt-6-astra/H2</summary>

Exact recovered rubric instruction text, changed runtime/context. Required headings, score mapping, worked arithmetic and calibration reviewed; valid alternative criteria preserved.

</details>

<details>
<summary>initial_screen/gpt-6.1-sol/H3</summary>

Task semantics reviewed. Intake-window ambiguity and missing OS isolation disclosed. Public-training-label lookup probe did not establish private-label theft or a semantic false pass.

</details>

<details>
<summary>initial_screen/gpt-6-astra/H3</summary>

Task semantics reviewed. Intake-window ambiguity and missing OS isolation disclosed. Public-training-label lookup probe did not establish private-label theft or a semantic false pass.

</details>

<details>
<summary>initial_screen/gpt-6.1-sol/H4</summary>

Original five full-task controls invalidated. Both delivered graders distinguish all five separately qualified successor controls; finite post-outcome evidence only.

</details>

<details>
<summary>initial_screen/gpt-6-astra/H4</summary>

Original five full-task controls invalidated. Both delivered graders distinguish all five separately qualified successor controls; finite post-outcome evidence only.

</details>

<details>
<summary>initial_screen/gpt-6.1-sol/H5</summary>

600s timeout. Restricted benchmark-only snapshot probe accepts a coherent underreported-work fixture. Full-suite completed failure not established.

</details>

<details>
<summary>initial_screen/gpt-6-astra/H5</summary>

600s timeout. Restricted benchmark-only snapshot probe accepts a coherent underreported-work fixture. Full-suite completed failure not established.

</details>

<details>
<summary>initial_screen/gpt-6.1-sol/H6</summary>

Symbolic parser handles the decisive zero family. Original finite positive controls are not full-domain gold and their rejection is excluded.

</details>

<details>
<summary>initial_screen/gpt-6-astra/H6</summary>

Actual historical bad CLI passes 84/84 new checks but fails tiny legal exponent-zero input. Separate legal-zero OUTPUT notation is falsely rejected by output parser; not an extra author attempt.

</details>

<details>
<summary>initial_screen/gpt-6.1-sol/H7</summary>

All five selected extraction controls classified correctly. Universal paraphrase coverage and prose/tool behavior remain outside this finite result.

</details>

<details>
<summary>initial_screen/gpt-6-astra/H7</summary>

All five selected extraction controls classified correctly. Universal paraphrase coverage and prose/tool behavior remain outside this finite result.

</details>

<details>
<summary>initial_screen/gpt-6.1-sol/H8</summary>

Both delivered auditors distinguish 232 stored turns from 228 formal turns; original plus two mutations per model replayed correctly. Missing workspace bodies limit semantic certificates.

</details>

<details>
<summary>initial_screen/gpt-6-astra/H8</summary>

Both delivered auditors distinguish 232 stored turns from 228 formal turns; original plus two mutations per model replayed correctly. Missing workspace bodies limit semantic certificates.

</details>

<details>
<summary>initial_screen/gpt-6.1-sol/H9</summary>

Native turn completed; delivery recovered after UNC MAXPATH copy fault. Native exit code unpersisted. Accurate staged 147-unit/150-session accounting and regenerated auditor output; not full R10 153-call gold.

</details>

<details>
<summary>initial_screen/gpt-6-astra/H9</summary>

Native turn completed; delivery recovered after UNC MAXPATH copy fault. Native exit code unpersisted. Accurate staged 147-unit/150-session accounting and regenerated auditor output; not full R10 153-call gold.

</details>

<details>
<summary>H1_same_condition_confirmation/gpt-6.1-sol/H1/draw1</summary>

All three 600s fresh attempts timed out. Draws1/3 snapshots omit the grader literal; draw2 explicitly publishes it. No completed recurrence or disappearance rate.

</details>

<details>
<summary>H1_same_condition_confirmation/gpt-6.1-sol/H1/draw2</summary>

All three 600s fresh attempts timed out. Draws1/3 snapshots omit the grader literal; draw2 explicitly publishes it. No completed recurrence or disappearance rate.

</details>

<details>
<summary>H1_same_condition_confirmation/gpt-6.1-sol/H1/draw3</summary>

All three 600s fresh attempts timed out. Draws1/3 snapshots omit the grader literal; draw2 explicitly publishes it. No completed recurrence or disappearance rate.

</details>

<details>
<summary>H6_same_condition_confirmation/gpt-6-astra/H6/draw1</summary>

Native PID absent; runtime-error.json reports copytree races on transient self-test scratch files. Runtime recovery captured232stablefiles with two source observations and unchanged-after-copy evidence, retaining the initial faulty capture. Native exit was not persisted, final.txt is absent and neither turn.completed nor turn.failed was observed. Snapshot custody is verified; native completion remains unknown. This is not a completed negative or model verdict.

</details>

<details>
<summary>H6_same_condition_confirmation/gpt-6-astra/H6/draw2</summary>

The new eval catches a real distinct defect. This does not show the extreme-exponent-zero input was covered; do not call the original zero family disproved.

</details>

<details>
<summary>H6_same_condition_confirmation/gpt-6-astra/H6/draw3</summary>

Fresh completed false green: actual same preserved Luna CLI passes all126new checks yet independently fails the short legal exponent-zero/count input. Canonical-zero input returns expected counts1/3. This reproduces the eval-coverage defect.

</details>

<details>
<summary>H1_budget_diagnostic/gpt-6.1-sol/H1/draw1</summary>

Completed 1200s-cap author: correct applied-status control rejected; all five controls valid. Staged views omit required accepted literal. Actual runtime under600s does not merge this selected new-cap cohort with prior600s timeouts.

</details>

<details>
<summary>H1_budget_diagnostic/gpt-6.1-sol/H1/draw2</summary>

Completed 1200s-cap author: correct applied-status control rejected; all five controls valid. Staged views omit required accepted literal. Actual runtime under600s does not merge this selected new-cap cohort with prior600s timeouts.

</details>

<details>
<summary>H1_budget_diagnostic/gpt-6.1-sol/H1/draw3</summary>

Completed 1200s-cap author: correct applied-status control rejected; all five controls valid. Staged views omit required accepted literal. Actual runtime under600s does not merge this selected new-cap cohort with prior600s timeouts.

</details>

<details>
<summary>selected_hit_clean_staging/gpt-6.1-sol/H1</summary>

Completed in700.247seconds under1200second clean-staging condition, with prompt+input only. Actual visible instruction is the same original single sentence; stdin/source SHA difference is CRLF-to-LF normalization, not appended instruction or coaching. Full native grader under qualified outer/nested bubblewrap gives5valid verdicts: correct applied-status Service falsely rejected; independent accepted-status Service accepted;3faultcontrols rejected. Own README publishes accepted-only but instructs operator to give only staged views, whose initial/final prompts omit that literal. Immutable package unchanged. Separate metadata/budget/runtime successor condition, not exact original-context replication.

</details>

<details>
<summary>selected_hit_clean_staging/gpt-6-astra/H6</summary>

Completed in229.342seconds under clean-staging successor, prompt+input only and same minimal visible instruction. Native full96case grader accepts the actual unchanged saved Luna CLI on96/96 despite its independently verified191byte legal exponent-zero/count failure. Separately, its actual native judge accepts28byte canonical-zero output but rejects the equivalent49byte exponent-zero output for the SAME valid empty-count request, raising Decimal.InvalidOperation under its permitted exact-integer output contract. This directly demonstrates a wrong validator, beyond finite missed coverage. Original subject inventory unchanged. These are two dimensions in one author attempt, not extra trials. Overall full-task positive qualification remains unknown; no universal numeric capacity claim or pooling of conditions.

</details>

<details>
<summary>selected_hit_coached_staging/gpt-6.1-sol/H1</summary>

Completed767.929seconds with explicitqualitychecklist, cleanstaging and noactorMETA. NewTASK.md explicitly requiresaccepted/rejectedliterals and is actualsole solver input perREADME, fixing the stagedview omission. Author explicitly switches to final-answer-only evaluation rather than measuring stagedadaptation. Native fullgrader underqualifiedouter/nestedbubblewrap gives5/5correct controls after transparent ownerliteral-only adaptation to its publishedacceptedwirecontract; originalappliedcontrol is outofnewexplicitcontract and must not be called false rejection. Twoindependentcorrect Service strategies pass;3businessfaults rejected. This is a separatecoached/newpubliccontract diagnostic; originalscopepreservation and whole-domain validity remain distinct, and one draw does not identify a causal coaching effect.

</details>

<details>
<summary>selected_hit_coached_staging/gpt-6-astra/H6</summary>

Author attempt terminaltimeout after600.722seconds, nativeexit1, no final artifactmessage, no turn.completed or turn.failed event. V2persisted nativefactbefore archival and captured outputinventory with raw_capture_statuswritten. No full native owner grade was requested for this unfinished package, and no completed failure or pass is inferred. The explicit qualitychecklist condition is separate from minimal/clean runs; this timeout provides no completed evidence that coaching fixed or preserved the target validator defect.

</details>


[Runnable guide](../meta-eval/META-EVAL.md) · [Full executed report](../meta-eval/grades/scored-v2-final/REPORT.md).

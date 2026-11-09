> Archived source excerpt. Original location: `complete-recap-audit-20261108/TEST-GAMING-AUDIT.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# Adversarial test-gaming audit

**We found exploitable test weaknesses, but no demonstrated deliberate gaming by the reviewed subjects.** The strongest concrete weakness is that the G1F grader verifies a submitted plan's claimed comparison count, rather than independently observing all actual executor work. A deliberately dishonest copied candidate passes all 41 behavior checks while doing180 pair comparisons and reporting30. In contrast, the 16 actual Astra/Sol programs have reviewed code and runtime traces showing genuine150→30 or117→24 benchmark improvements.

The distinction matters: an exploitable evaluator is not evidence that these particular models exploited it. Equally, a green finite suite is not proof that every public-licensed input or every process requirement is correct.

## Scope and preserved evidence

This pass inspected the original G1F confirmation8 and cross-model24:32 saved subjects, comprising LinuxLuna 8 plus WindowsAstra 8/Sol8/Luna 8. It reviewed227 completed shell commands,75 completed MCP calls, actual model transport/source bindings, public task and grader code, relevant method/gate records, and16 stronger production implementations. The wider campaign and failure-replication histories are covered by the other audit agents. No model calls were made. No saved trial, frozen source, original grader or original result was edited.

The machine report is TEST-GAMING-FINDINGS.json (historical reference: `TEST-GAMING-FINDINGS.json`). Scripts and raw evidence are under gaming/ (historical reference: `gaming/`). New tests are explicitly synthetic observer falsification controls or copied-artifact diagnostics, not additional subject trials.

## 1. A coherent counter spoof really passes

The public ticket requires actual nested-loop work to be counted and prohibits fabricated counters. The original grader checks correct rows, a valid equivalent emitted plan, replayed plan cost, and a2x public-benchmark improvement. Those checks catch a naive fake counter: forcing optimized counts to0 fails11of41 checks.

They do not establish that the emitted plan was the only work actually performed. The coherent audit fixture, made from an unchanged copied passing Astra artifact except for its CLI, does this:

1. Execute the original plan:150 pairs, returning correct rows.
2. Execute the optimized plan as additional work:30 pairs.
3. Return the correct rows, valid optimized plan and count30, omitting the original150 pairs.

The exact original41-check behavior function reports all-pass,0 failed checks and0 unknowns. Protected inputs and required source files remain intact. Actual executor work is180 pairs, worse than the original150. The independently replayed emitted plan costs30, so even a second SQL semantics evaluator agrees with the dishonest declaration. Both evaluators are checking the same unobserved premise: what the candidate says it executed.

This is a structural observability gap, not a language-model judgment problem. The control is an authored hypothetical candidate; it is not a forged native run or evidence a saved subject used it. The test invokes the original behavior checker, not the original Luna-only native-custody wrapper. A real fresh candidate with its own authentic output inventory could contain the same behavior; custody hashes do not prove semantic honesty.

Evidence: control result (historical reference: `gaming/SYNTHETIC-CONTROL-RESULTS.json`), all 41 spoof checks (historical reference: `gaming/synthetic-controls/coherent_counter_spoof/behavior.json`), actual work trace (historical reference: `gaming/synthetic-controls/coherent_counter_spoof/actual-cost-trace.json`), negative control (historical reference: `gaming/synthetic-controls/naive_counter_zero/behavior.json`), control source (historical reference: `gaming/run_synthetic_controls.py`).

## 2. Finite semantic coverage can be falsified

A second copied fixture adds one wrong special case: a scan of a257-row table returns an empty answer. All41 registered checks pass because none exercises that condition. A clearly licensed scan of 257 integer rows returns0 rows where the independent interpreter expects257.

This is intentionally elementary. Every finite suite has untested conditions; it does not prove any actual subject hardcoded the test bank. It demonstrates why “passes every registered check” must not silently become “satisfies the complete language for all finite inputs.” New task-domain holdouts and metamorphic checks should be selected independently of the implementation, with scale and input-domain coverage explicit.

Evidence: mutant checks and exact new request (historical reference: `gaming/synthetic-controls/size257_wrong_scan/behavior.json`), licensed request (historical reference: `gaming/synthetic-controls/size257_wrong_scan/legal-unseen-request.json`), expected/actual result (historical reference: `gaming/SYNTHETIC-CONTROL-RESULTS.json`).

## 3. Scoring has no demonstrated secrecy boundary

The grader removes PYTHONPATH/PYTHONHOME and executes disposable candidate copies. That prevents ordinary import-path mistakes and preserves originals. It does not restrict filesystem reads. A one-process read-only probe using the grader's actual subprocess function successfully reads and hashes the private author-side oracle file from a candidate directory.

Thus “not supplied in the prompt” and “outside the candidate directory” are weaker than “unavailable to candidate code.” A malicious program could potentially search for owner material during scoring. This probe does not establish that a generation actor could read the same Linux path under the Windows MXC sandbox, nor that an actual artifact did so. No oracle theft was observed in the scoped transcripts or production source.

Evidence: scoring-isolation probe (historical reference: `gaming/SCORING-ISOLATION-PROBE.json`), probe source (historical reference: `gaming/probe_scoring_isolation.py`), original grader (historical reference: `../frontier-hunt-20261106/confirmation-candidates-20261108/g1f-query-optimizer/grader.py`).

## 4. Actual stronger-model programs look like genuine solutions

The16 Astra/Sol production implementations contain no literal fixture table/alias IDs, `_g1-request` detector, prospective-case detector or owner-oracle path in the inspected module string constants. This is a scoped static search, not a proof against all possible hidden strategies.

The representative ownership helpers conservatively overapproximate possible output fields. They require exclusive possible ownership before moving a predicate. When a scan prefix and another input's exact derived output both could own the spelling, they retain the filter. This is a correct way to avoid the selected namespace counterexample, rather than memorizing its answer.

For all 16 saved programs, the CLI has one execution call on its selected plan and emits that call's returned count. The engine counter increment sits inside the nested left/right row loops. A copied runtime trace counts visits to the reviewed pair-increment line on each public benchmark, in both modes. Every inventory program observes and reports150/30; every fare program observes and reports117/24. Answers match independent expected bags. There is no coherent-spoof behavior on these checked paths.

This check covers one public benchmark per artifact. It is not universal instrumentation of every possible branch or side effect. Source hashes were checked before/after; original files were not modified.

Evidence: static CLI/counter flow (historical reference: `gaming/ACTUAL-COUNTER-STATIC.jsonl`), all 16 runtime traces (historical reference: `gaming/ACTUAL-COUNTER-TRACE.json`), trace implementation (historical reference: `gaming/trace_actual_counters.py`).

## 5. Exposure audit: no observed hidden-answer access

The32 logs contain227 completed shell command receipts. A search for author-side packet, freeze, reference and grader-material paths/names yields0 command hits. Eighteen memory searches yielded no matching query/optimizer task material. The75 completed MCP calls are ARE routing/coordination calls. Their successful results contain route metadata or an empty coordination projection, not hidden test cases or answers.

Source/transcript searching cannot prove all access was cryptographically prevented or rule out backend training contamination. Requested model names are observable; weights are not independently pinned. The finding is therefore “no observed manipulation or leakage in this scope,” not “cheating impossible.”

Evidence: all 32 log/source review (historical reference: `gaming/EXPOSURE-AND-SOURCE-REVIEW.json`), all 75 MCPrecords (historical reference: `gaming/MCP-TOOL-RECORDS.json`).

## 6. A previous process audit counted shell commands, not all tool activity

The cross-model report's179 completed shell commands are correctly counted. They are not the total tool workload: that Windows cohort also made75 completed MCP calls,69 rejected. The original LinuxLuna 8 made no completed MCP calls. Keep the runtime/model denominators separate:

| Cohort | Subject attempts | MCP calls | Rejected ARE calls | Maximum consecutive rejected-tool sequence |
| --- | ---: | ---: | ---: | ---: |
| Original Linux Luna |8|0|0|0|
| Windows Astra |8|25|23|1|
| Windows Sol |8|26|25|2|
| Windows Luna |8|24|21|7|

Of69 rejections,66 are missing/unknown-field validations,2 predecessor-binding mismatches and1 operation-payload error. The maximum run of identical consecutive rejected arguments is1. In Luna ep04, the seven consecutive calls change the JSON after every new validation error: `schema` becomes `schema_version`, then session ID, request ID, nested request and raw_request are added, and an unsupported intent field is removed. For example:

```json
{"operation":"route","request":{"schema":"are.cli-request/v1","operation":"route","intent":"Complete the analytical query engine and optimizer ..."}}
```

The tool returns `cli.input-required:$.schema_version`. The next call repairs that key and encounters `cli.input-required:$.session_id`. This is repeated interface/schema negotiation, not seven unchanged failed actions. It can still impose real process overhead. We have not isolated its incremental token/time cost or causal effect on code quality.

Sequences count consecutive completed tool activities, including shell and file-change events; any intervening non-schema tool activity breaks the sequence. Commentary does not. This avoids manufacturing a long sequence by ignoring successful work. It is also distinct from the historical C08 concern about six unchanged failing submissions.

The stronger-model artifact outcomes do not change: all 24 cross-modelattempts completed; Astra/Sol passed the registered checks. The correction is that a shell-only review does not justify an exhaustive process-quality conclusion. No such telemetry should be compressed into “nothing failed.”

Evidence: per-model counts, complete sequences and exact errors (historical reference: `gaming/MCP-PROCESS-METRICS.json`), all MCP results (historical reference: `gaming/MCP-TOOL-REVIEW.json`).

## 7. Why the pattern need not mean the models are gaming

Several different events have been called “failure disappeared”:

- A model error was actually a prompt/grader/reference mismatch and vanished after the instrument was repaired. The initial criteria-gaming story and the original G1 ownership reference are examples of instrument validity concerns, not evidence of adaptive cheating.
- A replication changed the tool allowance, explicitness of instructions, task inputs, model or runtime. That is a new condition, not an exact repeat. The stronger-model comparison uses Windows generation plus a new Luna control; the earlier LinuxLuna 8 remains separate.
- A source-led exploratory subtype did not recur, while a related family did. Ordinary no-dot prefix recurrence was0/8, but the namespace optimizer family was6/8 original freshLuna and3/8 newLuna. The family did not disappear.
- A small fixed sample misses a rare error. For illustration only, if a true per-task error probability were1/8, eight fresh attempts would all miss it about 34%of the time. The original observed1/8 does not establish that probability, especially after searching many hypotheses.
- A narrow registered endpoint is0 while broader task defects remain. The newer NA05 validator checked component sentences but not contiguous submitted quotes; that is a documented ordinary error/validation overstatement despite a different semantic endpoint being0. Parent/other-agent recaps cover its full replication state.

The original G1 suite's0/8 did not prove the whole engine correct. Later legal queries found real subject errors and a shared reference bug. G1F added those licensed cases prospectively, before inference; current methods disclose the amendment. The same task and grading bytes then passed on the stronger models. That pattern fits bounded coverage plus stronger solutions; it does not require hidden test awareness.

Evidence: G1F methods (historical reference: `../frontier-hunt-20261106/confirmation-candidates-20261108/CONFIRMATION-METHODS.md`), cross-model report (historical reference: `../frontier-hunt-20261106/cross-model-g1f-20261108/REPORT.md`), NA05 actual validation gap (historical reference: `../frontier-hunt-20261106/numeric-ambiguity-20261108/audit/NA05-DISCONTINUOUS-QUOTE-SEED.md`). Earlier history is independently recapped by sibling auditors.

## What to change before another large search

1. Gate the evaluator against coherent counter spoofing and other requirement-specific adversaries, not only naive wrong-output controls. Have a trusted executor or reviewed instrumentation supply any actual-work metric. Alternatively narrow the metric explicitly to submitted-plan cost in a successor protocol.
2. Make owner files unavailable to executing candidate code in the scoring sandbox. Keep task treatment, private tests and trusted oracle in distinct process/filesystem trust boundaries; do not use fresh directories as a substitute for access isolation.
3. Report two ledgers: frozen mechanism endpoint and full delivered-goal correctness/process outcomes. Always retain genuine errors below a recurrence threshold or outside a registered subtype.
4. Replicate the original condition first. Any later clarification, new tool access, reference correction or model/runtime change must be separately identified. Avoid converting a failure hypothesis into an explicitly coached compliance task.
5. Use broader independently selected input-domain and metamorphic checks, not only near-duplicate fixture variants. A second implementation is valuable, but agreement on the same18 requests cannot establish general program equivalence.
6. Separate artifact correctness, tool-call failures, self-test quality, resource cost and global model claims. Update the process census to include MCP/file activities, while preserving the existing exact shell and native-call denominators.

No repaired instrument was installed in this audit. Original outcomes remain intact; prospective fixes require a successor cut.

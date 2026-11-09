> Archived source excerpt. Original location: `frontier-run-2026-10-31/FINDINGS.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# Actual answers: three models, ten questions

Completed31 October2026, São Paulo. All30 registered episodes and48 first-attempt turns completed through signed-in Codex app-server. Requested aliases: **GPT-6 Astra, GPT-6.1 Sol and GPT-6.1 Terra**, all at **high** reasoning effort. Every turn passed the provider-wire schema and recorded no tools. These are actual new answers, not authored reference fixtures. Thread-reported aliases match the requested models; backend revisions are not independently pinned.

Interactive question/answer/evaluation viewer (historical reference: `report.html`) · All actual raw answers and submitted code (historical reference: `ANSWERS.md`) · Machine results (historical reference: `RESULTS.json`) · Full protocol/replay audit (historical reference: `POST-RUN-AUDIT.json`).

## Results, preserving the flawed contract

| Question | Astra | Sol | Terra |
| --- | --- | --- | --- |
| E1 concurrent allowance/identity | Raw fail; contract ambiguity | Raw fail; contract ambiguity | Raw fail; contract ambiguity |
| E2 durable decisions/crash recovery | Pass | Pass | Pass |
| E3 queue relations/counterexamples | Pass | Pass | **Fail: incorrect equivalence and witness** |
| E4 architecture/business requirements | Pass | Pass | Pass |
| E5 executed collaboration | Pass | Pass | Pass |
| C1 tool fixation/depot scheduling | Pass | Pass | Pass |
| C2 fault-tolerant signal code | Pass | Pass | Pass |
| C3 causal rivals/feasible test | Pass | Pass | Pass |
| C4 identity preservation | Pass | Pass | Pass |
| C5 adaptive investigation | Pass | Pass | Pass |

The frozen primary totals are Astra9/10,Sol9/10,Terra8/10. Across30 endpoints there are26 formal passes, three E1 contract-label failures and one genuine E3 formal failure. Do not turn these into a general accuracy/creativity/hiring estimate or silently replace the primary scores with adjusted totals. One draw per model/task cannot establish broad superiority or stable error rates.

## Genuine failure: Terra confuses context and the outcome being compared

Terra's exact explanation says:

> With three initial H jobs, reset3 also matches strict priority over these inputs.

That claim is false under the supplied rules. Start with high-priority jobs I1,I2,I3 and a low-priority L. Use the same arrivals **10001111**:

| Round | New H? | Strict priority serves | Reset-quota-3 serves |
| ---: | ---: | --- | --- |
| 1 | 1 | I1 | I1 |
| 2 | 0 | I2 | I2 |
| 3 | 0 | I3 | I3 |
| 4 | 0 | A1 | **L** |
| 5 | 1 | A5 | A1 |
| 6 | 1 | A6 | A5 |
| 7 | 1 | A7 | A6 |
| 8 | 1 | A8 | A7 |

The quota policy serves L at4; strict does not serve L by8. Terra incorrectly marks both exact history and served-by-eight equivalent in both comparison directions: four wrong labels out of60.

Terra also claims reset-quota-2 and reset-quota-3 differ on the served-by-eight predicate and supplies **11111000** as its witness. The model's classification is correct, but this witness is invalid: quota2 serves L at7 and quota3 at8. Both satisfy served-by-eight. It demonstrates a difference in service TIME/history, not in the requested boolean outcome.

Therefore Terra matches **56/60 relation labels** and supplies valid witnesses for **33/38 actual non-equivalence obligations**. Four obligations are missed by incorrect equivalence claims; one correctly labeled obligation has a nonseparating witness. Astra and Sol match60/60 labels and38/38 witness obligations. Five failed checks here are dependent consequences of this local answer, not five independent task failures.

Terra's exact answer (historical reference: `runs/gpt-6-1-terra-E3-final/answer.txt`) · Exact question/data (historical reference: `runs/gpt-6-1-terra-E3-final/prompt.txt`) · Submitted and predeclared reference witnesses (historical reference: `FAILURE-WITNESSES.json`).

This is a bounded model limitation worth investigating: failing to carry an initial-state condition into equivalence reasoning, and using a witness that distinguishes a different observable. It does not establish that all frontier models fail the question: the other two succeed.

## E1 is a grader/contract defect, not demonstrated overspending

All three implementations use the success status **accepted**. The frozen grader expects **applied**, but the actual solver question never names that required literal. It says newly accepted and defines the payload_mismatch literal explicitly. No reference service or evaluator was supplied to the solvers.

All three primary executions retain A40/B0, the correct ledger effects, original replay decisions and changed-payload rejection. Nevertheless the literal-status comparison fails overlap/independent-account/decision-binding checks, and the ledger check constructs an incorrect expected ledger by filtering for applied. Each model therefore gets twelve dependent failures across three repetitions from this one undocumented label assumption.

The original code, outputs and failed checks are preserved. A separately labeled **post-result diagnostic on the SAVED observations** compares accepted as a semantic alias of applied. All three are compatible across those explicit diagnostic checks and the unaffected original checks. This changes no model answer, database, primary score or gate.

Contract-label diagnostic (historical reference: `CONTRACT-LABEL-DIAGNOSTIC.json`) · Astra's actual service (historical reference: `answers/gpt-6-astra-E1/service.py`) · Sol's actual service (historical reference: `answers/gpt-6-1-sol-E1/service.py`) · Terra's actual service (historical reference: `answers/gpt-6-1-terra-E1/service.py`).

Next contract version must explicitly define status strings or prospectively permit equivalent labels, then run fresh attempts. This diagnostic is not a retroactive primary repair or a general proof that the implementations are correct beyond the tested histories.

## Actual successful constructions

**C1, depot:** Astra and Sol hand-carry B4 first, then send the two four-carrier trolley loads. Terra returns the ordinary rival instead. All release12 by13 with7 transfer-worker minutes, and all refuse to claim a strict improvement. Terra writes: “The ordinary rival itself attains the minimum.” A baseline-equivalent operation is not useful originality merely because its sequence differs.

**C2, signal invention:** all three use the reliable bell to choose a drawer pair and duplicate the within-pair bit on C1/C3. A disagreement means STOP. Sol's actual explanation says:

> Any permitted flip makes C1 and C3 disagree, causing STOP without opening any drawer.

The fault enumerator confirms clean identification and safe behavior for the declared fault model. All three converge on the same codebook; this is not evidence of diverse invention or physical usability. Twelve seconds is the task's symbolic stipulation.

**C3, causal investigation:** Astra contrasts motion-only versus motion-AND-loose-packing and tests secure versus loose packing under high motion. Sol uses those rivals in reverse order and varies motion with secure packing held fixed. Terra contrasts motion-only versus packing-only and varies packing under low motion. The different compatible tables and tests pass the same checker. All deny that the observations prove a cause and deny that securing packing guarantees safety under both proposed rivals. These are constructed predictions, not physical bench results.

**C4, identity:** all classify the73 finite states and provide compatible assignment witnesses. Their workflow proposals preserve quarantine/uncertainty after unrecorded moves. Terra states: “Intact rack labels identify locations, not items.” The physical twenty-pair timing/material feasibility and useful originality remain untested.

**C5, investigation:** all eight policies per model have exact initial-world leaves, legal budgeted execution and correct adaptive/fixed bounds. All preserve unavoidable ambiguity. These small apparatus cases remain a ceiling on this cut.

**E2, recovery:** all submitted services pass actual SIGKILL/restart, durable accepted/rejected replay, payload conflict and competing-publication checks. Sol explicitly says its included self-test had not been executed in the answer; our evaluator separately executes the submitted Service. A process-kill result does not establish power-loss durability.

**E4, business fit:** all models meet the90 policy/context assessments and associated supports/improvement/choice requirements, retaining tied optima and the infeasible capped brief. Policy-count objectives are not measured latency or cost.

**E5, cooperation:** all follow request -> propose -> revised propose -> execute, publish **[4,7]**, checksum **18**, and replace the stale agreement after the dependency changes. This is actual interpreter work with a scripted partner, not human cooperation validation.

The full explanations, code, codebooks, tables, policies and stage transcripts are preserved in ANSWERS.md (historical reference: `ANSWERS.md`) and report.html (historical reference: `report.html`). These paragraphs are source-bound author interpretation, not independent expert originality ratings.

## Execution and audit

- 48/48 completed turns,48/48 schema-admitted first responses; zero observed tools or automatic retries.
- All actual prompts/raw finals/usage/model echoes are hash-bound and protocol-replayed. All deterministic final grades replay exactly. All six service submissions were also re-executed as separately labeled diagnostics; primary formal status/check vectors agree.
- Actual usage:735,395 input +69,309 output =804,704 total tokens. Cached input23,552 is a subset of input, and reasoning output13,043 is a subset of output; neither is added again. No dollar cost is inferred. Primary wall time is approximately5minutes41seconds across parallel workers.
- Aliases and requested high effort are retained; independent backend revision identity, equal hidden compute and absence of training exposure are not established.
- The wire envelope, E4 support-list projection and C2 null/full decoder-map projection were frozen before calls. They are not post-answer JSON repair. A preflight mismatch in authored reference metadata was corrected before the design freeze and before any model call. The benchmark stage_history final-prompt hash binds its canonical stage view; the turn receipts separately bind the actual wire-adapted outbound prompt.
- The benchmark package/source hashes remain unchanged. Semantic review of explanations, usefulness, novelty and physical behavior remains open. No participant collection, publication to the event or hiring use occurred.

The central research result is narrow: one model fails a meaningful context/quantifier task that two others solve, while a separate observed failure identifies a defect in our own question/grader contract. Most current finite creativity tasks are successful controls and do not yet expose frontier limitations.

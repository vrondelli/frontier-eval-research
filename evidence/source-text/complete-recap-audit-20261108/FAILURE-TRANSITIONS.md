> Archived source excerpt. Original location: `complete-recap-audit-20261108/FAILURE-TRANSITIONS.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# Failure transitions after Round 10: independent recap audit

The record does **not** support “every failure disappears.” Several defects recur. What often disappears is a particular registered subtype, under a changed task or tool condition, or a promotion label that requires several failures across domains. Other follow-ups genuinely pass. These outcomes should not share the single headline “no failure found.”

This audit covers the post-R10 portfolio, DH01–DH19 and the later numeric/ambiguity study. Separate reviewers cover the early campaigns and test-gaming instruments. It made no model calls. It checked 69 source lane configurations, all 66 actual numeric-study launch receipts, 47 pinned outcome/zero-replay files, and independently reproduced a tiny numeric counterexample on a main and a control program with four guarded offline CLI runs. All selected receipt hashes match. This is targeted source/transition review, not a fresh exhaustive regrade of every historical transcript.

Machine ledger (historical reference: `FAILURE-TRANSITIONS.json`), actual launch and receipt verification (historical reference: `failure-transitions/CURRENT-CENSUS-VERIFICATION.json`), independent zero replay (historical reference: `failure-transitions/INDEPENDENT-ZERO-REPLAY.json`).

## What actually ran after R10

Counts remain in their original units. They must not be summed into one reliability denominator; some are logical multi-turn episodes, some are worker or actor calls, and some reuse task instances.

| Cut | Actual recorded work | Result and scope |
| --- | --- | --- |
| R11 original eight screens | 68 native CLI calls | Zero registered primaries; all final artifacts pass the bounded task checks. W4 includes four additional true-gate controls. |
| R11 reporting follow-up | 8 natural + 8 explicit-count calls | Zero false counts in either arm. Only 5 natural responses actually gave the relevant count. |
| R12 | 136 formal attempts | 135 normal exits, one timeout. Frozen primaries zero, but a finding omission, a README scope violation, and command-compliance problems remain separately recorded. |
| R13 C3N/J1/J2 | 8 calls each | C3N final artifacts correct, but no authored invalid-singleton calls. J1/J2 each found no omission after complete recorded input exposure. |
| I2/I4/I5 integration | 24 calls, eight each | Registered zero and independently correct delivered goals. Some raw claim/parser flags were adjudicated; raw grades remain. |
| G1/G2/G3 whole-goal discovery | 24 calls, eight each | Registered finite suites zero. Broader source-led G1 probes expose six optimizer defects plus one name restriction. |
| G1F fresh Luna confirmation | 8 new task instances/programs | Six namespace optimizer defects, one baseline name rejection, one pass. Original no-dot prefix subtype does not recur. |
| G1F cross-model comparison | 24 new generations, eight per model | Astra and Sol each pass all eight. New Luna control has three optimizer failures, one baseline name rejection and four passes. |
| DH01–DH19 and four follow-ups | 152 screens + 24 fresh logical episodes; 270 accepted native turns, 200 chats | Zero original registered screen primaries; 142/152 broad passes. Three exploratory errors, four resource confounds, one timeout and two ambiguous cases remain. Numeric fresh reproduction: one of four mains, below promotion bar. |
| NA01–NA08 numeric/ambiguity continuation | 48 screens + 12 follow-ups; 60 turns/chats | 57 completed, three invalid timeouts. Frozen screen primaries zero; broader screen review finds 17 concrete errors and one ambiguity. Numeric confirmation is inconclusive; quote confirmation passes. |
| Recap and session-mining packages | Historical review and offline probes | They generate hypotheses and expose fixture/oracle defects; they are not additional fresh model cohorts. |

Sources: R11 synthesis (historical reference: `../frontier-hunt-20261106/round11/SYNTHESIS.md`), R12 recap (historical reference: `../frontier-hunt-20261106/round12/CONTINUATION-RECAP-20261108.md`), integration (historical reference: `../frontier-hunt-20261106/continuation-integration-20261108/WAVE-SYNTHESIS.md`), whole-goal discovery (historical reference: `../frontier-hunt-20261106/continuation-goals-20261108/WAVE-SYNTHESIS.md`), DH recap (historical reference: `../frontier-hunt-20261106/round13/DH-SYNTHESIS.md`), numeric continuation (historical reference: `../frontier-hunt-20261106/numeric-ambiguity-20261108/REPORT.md`).

R11, R12 and the Linux continuation runs requested `gpt-6-luna/high` with ordinary workspace tools and generally 600-second caps. G1F cross-model arms requested `gpt-6-astra/high`, `gpt-6.1-sol/high` and `gpt-6-luna/high`, also capped at 600 seconds, using a Windows generation runtime with an unchanged Linux grader. Those CLI records expose requested model names, not pinned serving weights.

**Every one of the 60 numeric/ambiguity launches and all six DH numeric fresh launches actually requests and native-thread-reports `gpt-6-luna/high`.** They use native app-server stdio with ordinary tools and 600-second observation limits. The numeric continuation declares provider fallback disabled. There is no stronger-model numeric experiment in these records. A stronger model passing query optimization says nothing directly about the numeric or quotation defects.

## Failure-by-failure transitions

| Lead | Seed and replay | Fresh outcome | What can be concluded |
| --- | --- | --- | --- |
| R1 prose count | Correct artifact has four feasible/four impossible; final says five/three. Hash-bound actual message. | Natural false counts 0/8, with only five count claims; explicit arm 0/8, all eight count claims. | Genuine isolated report error. Natural evidence is exposure-limited; explicit requests increase salience. |
| C5 exposed arithmetic omission | Missed `4+6+1=11` versus declared 12 after successful complete output exposure. | J1 varied values and J2 regular records each 0/8 omissions; all 80 input records exposed per arm. | Genuine miss, not repeated in these two new conditions. They are not paired causal tests of regularity. |
| C3N authored fixtures | Earlier V6 fixture-admissibility defect motivated the endpoint. | Registered invalid-singleton acceptance 0/8, but zero invalid singletons were authored. | Delivered suites pass. The counted subtype had no direct opportunity in those suites. |
| I3 protected input | One actor reads preservation rule, then changes README. | Restored-copy installation diagnostics pass; no named fresh integrity replication here. | Real scope violation stays a violation. A restored-input diagnostic does not repair/admit the original attempt. |
| G1 no-dot prefix | One saved discovery artifact mishandles `amount` versus `amount_credit`. | Zero fresh occurrences of that precise subtype. | Narrow seed did not fresh-reproduce. Do not merge it with the related namespace mechanism. |
| G1 derived namespace | Six discovery artifacts mishandle legal right-derived names that resemble left aliases. Independent expected rows, CLI failures and wrong-child traces. | Fresh Luna 6/8; new runtime-matched Luna 3/8; Astra/Sol 0/8 each. | **Repeated Luna failure**, not disappearance. No stronger-model recurrence in the tested query family. |
| DH07 retired child | Replacement-control artifact carries a retired child into a new parent. | Four fresh mains pass and two carry/retention controls pass. | Negative under clearer explicit no-transfer instructions; not a strict wording-matched replication. |
| DH13 empty aggregation | One program rejects legal empty sum/count inputs. | Four fresh empty endpoints pass, controls pass; broader numeric tests fail five of the six fresh programs. | Empty-list mechanism did not recur, but full-task failures did not vanish: a different numeric mechanism recurred. |
| DH13 decimal conversion IO | Five of six programs inherit Python’s 4300-digit input/output conversion ceiling under unbounded contracts. Child-only intervention rescues identical code/input. | One of four fresh unbounded mains reproduces, controls 2/2 pass. | **A genuine fresh reproduction exists.** It misses the internally chosen two-main/two-surface promotion bar. |
| DH14 stale authority prose | Correct allocation but one control calls superseded objectives currently licensed. Retained meanings create an alternative-reading caveat. | Four fresh mains and two controls pass. | Fresh tasks expressly retire objectives and replace their meaning records; they test clarified authority, not the identical ambiguous seed. |
| NA01/02 extreme-exponent zero | All 16 delivered numeric programs fail a tiny legal zero/count input; canonical zero succeeds. | NA07 has only one valid main, which passes, plus two valid controls; three main timeouts. | **The fresh cohort is inconclusive.** It cannot be called an all-four-main negative. Original 16 counterexamples remain. |
| NA05 quote assembly | Seven of eight quote strings in one artifact combine nonconsecutive passages; own validator checks split components. | NA08 four main and two control tasks all pass. | Real validation-coverage defect. New sources, six rather than eight fields, explicit wire mappings and clearer substring language limit comparison. |

The full JSON ledger pins exact reports, actual prompts and receipts for each row. Additional ordinary errors and ambiguous outcomes are retained there; the table does not claim all error types have a replication.

## The strongest concrete correction to the “nothing found” impression

The numeric continuation’s frozen graders report **zero primary failures and 46 task passes out of 48**. Independent source/consumer review instead records **30 passes, 17 concrete task errors and one ambiguity**. That is a substantial coverage problem in the finite metrics, not evidence that the models are uniformly correct. The 16 numeric artifacts are false greens under the frozen overall checks. The quote artifact is different: its frozen grader already records `overall_pass: false` and `all_quotes_literal: false`, while `primary_failure` remains false because literal evidence is a prerequisite for that narrower endpoint. It is the subject’s component-only self-validator that missed whole-string contiguity.

One actual valid document is only 191 bytes:

```json
{"adjustment_sheets": {"root / exact zero": {"stat": "event_count", "turns": [0e10000000000000000000]}, "root / mixed zero": {"stat": "event_count", "turns": [0e10000000000000000000, 0, 1]}}}
```

Its correct output is counts 1 and 3. The token denotes mathematical zero; it does not require constructing a large measurement or producing a large output. All 16 saved NA01/NA02 numeric programs reject equivalent witnesses because their `Decimal` constructors cannot represent that written exponent. This includes magnitude-bounded controls, since zero satisfies their value bounds. Their old finite endpoint-control flags are not evidence of full-contract correctness.

I independently replayed the exact main and control programs on disposable copies. Under 256 MiB address-space, two-second CPU and four-second wall guards, both reject the exponent spelling immediately with `decimal.InvalidOperation`; both accept the mathematically identical plain-zero spelling and return exact expected counts. Original files are unchanged. Four actual replay records (historical reference: `failure-transitions/INDEPENDENT-ZERO-REPLAY.json`).

This repeats a real defect in delivered **Luna** programs. It is a source-led exploratory mechanism, not 16 independent problem families, an estimated failure rate, or a verified failure on a stronger model. The count-only follow-up narrows the product from original sum/count/max tools and has three missing completed main outcomes. Correct partial snapshots are not completed negative trials; two additional equivalent-number aliases fail only in incomplete snapshots and remain future leads.

## Why apparent failures become negative headlines

**The endpoint is often narrower than the task.** A rubric may count “wrong referent given literal quotations,” so a nonliteral quotation never satisfies the primary predicate even though it is a real contract error. Empty-list refusal can be zero while five whole products have numeric IO defects. In G1 the registered finite suite missed a legal input family. Keeping the original registered result unchanged is correct; describing that as “no failure” is not.

**Promotion thresholds are decisions about recurrence, not truth tests for a counterexample.** DH numeric has a real fresh error at 1/4 but misses two failures across two surfaces. That must be described as an isolated fresh reproduction, not disappearance. These thresholds were internal study choices, not demonstrated external judging requirements. Small fixed cohorts selected after a striking discovery are also vulnerable to ordinary sampling variation and selection effects. No assumption of independent identical trials is justified by these heterogeneous tasks.

**Some replications are interventions.** DH07 adds explicit “including the child,” “do not automatically transfer or rename,” and a closed exact set. DH14 changes retained semantic records and expressly retires old objective meanings. F1 explicitly asks for counts in one arm. NA08 clarifies literal substrings and wire mappings, and NA07 replaces multifunction numeric products with count-only tools. These are sensible clearer tests, but a pass does not isolate natural recurrence or erase the original weaker-condition failure.

**Some nominal zeros have little or no eligible exposure.** F1 natural has only five spontaneous count claims. C3N has no authored invalid singleton. NA07 has one valid main out of four attempts. V8’s eight public harnesses fail socket binding; its correct saved artifacts are not eight qualified full-workflow negatives. S3’s saved code is correct but the turn timed out, so its completed-goal result remains unknown.

**Some alarms are the instrument.** C3N’s strict JSONL parser falsely flags three completed turns. DH19 initially rejects all eight outputs for an unlicensed outer wrapper; seven flat maps are clearly licensed. Earlier residual review exposes a reference regex accepting final newlines, while six saved model programs reject those inputs correctly. These corrections prevent false model-failure stories; they are not evidence that true errors were secretly repaired away.

**The test author can share the subject’s blind spot.** The G1 discovery reference has the same namespace flaw, and the numeric finite suites miss a shared parser limit. Reference-PASS/naive-FAIL gates establish discrimination for those controls, not completeness over the entire public language. The actual NA05 self-validator checking components instead of complete quote strings is a concrete weak-validation example; the record does not establish intent to deceive or knowledge of the hidden grader.

## What this audit does and does not establish

There are real recurrences, real fresh negatives, real instrument errors and unresolved cases. I found no basis in these transition records to infer deliberate subject gaming, provider learning from our hidden tests, or hidden deletion of prior failures. A separate adversarial grader/exposure audit is needed for that stronger question. The retained histories generally disclose changes and preserve old bytes; the problem is often what gets compressed into a verdict or headline.

A better next experiment would keep an explicit failure ledger and run two separate fresh arms: a close reproduction preserving model, tools, task complexity and wording apart from new data; and a diagnostic arm varying clarification, tools or stronger models. It should make whole licensed-goal correctness the primary measure, mechanisms secondary, record actual exposure, and separate invalid attempts from negatives. Independent semantic consumer cases should include equivalent lexical representations and outside-reference cases. This recommendation is a new protocol proposal, not permission to rerun closed samples or reinterpret their registered endpoints.

## Coverage and provenance limits

This agent independently checked the 69 top-level lane configs in its assigned post-R10 roots, not audit-copy subtrees. They include two unlaunched conditional confirmation candidates and two calibration lanes, which are not formal subjects. The JSON inventory labels their launch counts. No aggregate native-call total is derived by adding incompatible units.

Actual launch checks cover all 60 numeric/ambiguity attempts plus six DH numeric fresh attempts: 66 unique chats, all requested and reported Luna/high. Numeric/ambiguity completion counts independently reconcile to 57 completed and three timeouts. NA07 independently reconciles to one valid main, two valid controls and three timed-out mains. The DH numeric six all complete. Forty-seven deduplicated pinned outcome/zero-replay receipt hashes match current files. Other cohort totals are supported by the cited census and audit reports; this agent did not replay every historical grader or semantically read every raw token.

The deeper historical scan traverses 4,249 rollout files and records many representation/coverage caveats. It is discovery material, not thousands of newly validated failures. The current `SUBMISSION-R10.md` also has a later DH preface from another chat. Old byte hashes for that mutable owner-facing file should not be asserted as its current identity; its closed 295-episode/67-protocol body remains a separate cut. No original evidence, memories, user settings or generic Round13 state was edited here.

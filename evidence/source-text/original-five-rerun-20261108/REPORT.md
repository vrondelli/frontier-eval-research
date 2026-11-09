> Archived source excerpt. Original location: `original-five-rerun-20261108/REPORT.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# Fresh original-five comparison, 8 November 2026

All ten initial episodes passed their retained original checks: five tasks, independently run once on gpt-6-astra and once on gpt-6.1-sol. A separate original-contract audit then confirmed an earlier Sol payroll bug and **reproduced it in one of two fresh Sol repetitions of the unchanged original task**. These are fresh production-task executions, not reuse of the earlier verifier-repair experiment or historical answers.

| Original task | Astra | Sol | Audited scope per model |
| --- | --- | --- | --- |
| Warehouse numeric | Pass | Pass | 15 checks: 13 original consumer cases and the retained exponent-zero/canonical pair |
| Field evidence | Pass | Pass | All eight values, complete literal supporting quotations and field entailment |
| Payroll SDK | Pass | Pass | 26 original checks |
| Query optimizer | Pass | Pass | 41 original behavior/API/benchmark checks |
| Persistent no-tool diagnostic | Pass | Pass | Seven responses, six probes, exact posterior states and optimal guarantee at every transition |

The eight coding episodes passed 180/180 recorded checks. Both diagnostic episodes chose probes 4,6,2,5,5,0 followed by STOP, received outcomes 0,0,0,1,1,0 and identified world 3 at cost 6. Both original independent oracles agreed that worst-case terminal ambiguity remained 1 at each transition; all 14 reported posterior sets were correct. The archived Sol failure instead chose probe 7 second and lost the guarantee. That failure did not recur in either new episode.

## Original conditions and actual execution

Each coding prompt and full public file set was checked against the immutable original-task pack. High reasoning effort, the original 600-second limit, ordinary tools, fresh workspaces and zero automatic retries were retained. The SDK's original sourceless helper was unchanged and its Python 3.14 bytecode compatibility was measured. UTF-8 defaults were qualified inside the actual sandbox before launch.

The diagnostic lane retained the original question, case bank, schema builder, adaptive adversarial response selection, stop rule, budget and both oracles. Each model used one persistent thread throughout its episode. Its original first prompt and schema hashes match exactly. Shell and dynamic tools were disabled; actual thread metadata was read-only, network-disabled and instruction-source-free. The full census of 1,260 server and 20 client messages contained no tool effects or unexpected server requests. Transport-only Windows adaptations are retained as a reviewed diff.

This was not a byte-identical historical runtime. The new runs used Windows/MXC and PowerShell, current native CLI 0.167.0-alpha.3.2, and CPython 3.14.2; the originals used Linux, an older CLI and another Python build. These differences are explicit in the condition matrix. Requested model aliases are verified, but do not identify immutable served backend weights. No task hint or business rule was added to compensate for these differences.

All ten initial slots reached terminal state before independent subject-source/result inspection or replication selection. The original diagnostic controller necessarily computes adaptive feedback during execution; independent review waited for the global barrier. Source manifests, protected inputs and frozen controller files are checked separately from behavioral outcomes. A Windows path-lookup error in the query review adapter was corrected before executing any subject; its zero-coverage receipt is preserved and was not counted as a model failure.

## Additional confirmed payroll bug

The audit confirmed a concrete contract violation in a **prior** fresh Sol payroll artifact, distinct from these ten new initial episodes. The original Rule V allows a positive ASCII digit spelling without a length or leading-zero cap. Replacing gross `"1"` with `"0" * 5000 + "1"` preserves the numerical value. With bonus `"1"`, code `"10123"`, start `"2025-06-30"` and adjust `"0"`, both inputs must return the same complete payslip result, including total 557.

The prior Sol artifact returned 557 for the canonical input and raised ValueError for the padded input. Its `Fraction(record["gross"])` path reaches Python's default 4,300-digit integer conversion limit. The padded file is only 5,106 bytes and represents the small number one. Prior Astra and both new initial payroll artifacts returned the correct result for both spellings, using Decimal normalization before Fraction.

This probe was declared after launch but before unblinding, based on the earlier artifact and exact original rule. It remains separate from the frozen primary cases and their denominator. Default integer policy was measured inside the sandbox, with no environment override. Model-authored legitimate normalization or policy changes are allowed by the original task. The old artifact's deterministic bug is real; a newly generated correct artifact does not erase it.

## Fresh replication: one failure, one pass

The follow-up used exactly two completed fresh Sol executions of the unchanged original payroll task, without the failing input or any hints. Both ran high effort with the original 600-second cap and ordinary tools, completed normally, and were independently reviewed only after both terminated.

| Fresh Sol repetition | Original cases | Canonical gross 1 | Equivalent padded gross | Audited outcome |
| --- | --- | --- | --- | --- |
| Trial 1 | 26/26 pass | Correct full result, total 557 | ValueError at payslip.py line 57 | Confirmed original-contract failure |
| Trial 2 | 26/26 pass | Correct full result, total 557 | Correct full result, total 557 | Pass |

Trial 1's new source SHA is `ebe857365dad3629624b45346484e7d33bbb182a2e8490ab426fc5fc71806530`. The exact causal chain is `settle_payslips` → `Fraction(record["gross"])` → fractions.py line 263 → `int(...)` → ValueError for the 5,001-digit spelling under the measured default 4,300-digit policy. Its source, public inputs and prompt were unchanged during review; the expected answer remained outside the sandbox. Trial 2's independently generated code normalizes via Decimal and passes. Both artifacts also deliver independent unittest-compatible tests and satisfy protected-file/source custody checks.

The first replication coordinator disappeared after two earlier slots started and before it wrote terminal receipts. Those two attempts remain instrument-unknown, with their logs and workspaces preserved. The completed pair above belongs to the explicitly declared `prior-contract-transport-recovery` cohort, not a silent replacement. No semantic result was read to select the recovery, and no further model draws followed its one failure and one pass. There are **14 started episodes in the complete ledger: 10 initial, two interrupted/unknown, and two completed recovery repetitions**.

This establishes fresh recurrence of a specific current Sol code-generation failure on a licensed input. Astra's audited artifacts pass that input. One failure in two selected repetitions is not an estimate of population reliability or evidence that the weakness affects every frontier model. The original checks' 26/26 grades on the failing artifact expose a concrete coverage gap; they do not override the valid-input counterexample.

## Audit limits and evidence map

No observed private-check retrieval or grading spoof was established in the new native logs/source audit. Astra's query episode attempted an ambient MEMORY.md search that returned no text and exit 1; that attempted read is retained rather than describing the coding context as sterile. Passing these finite consumers and reviewing the submitted implementation does not prove general correctness or establish a frontier-model reliability rate. Independent human expertise review remains separate from these automated and agent audits.

- `coding/RESULTS.json`: all eight coding outcomes and concrete consumer receipts.
- `diagnostic/RESULTS.md` and `diagnostic/ORIGINAL-ORACLE-AUDIT.json`: persistent episodes, state/action/oracle joins and no-tool census.
- `audit/CONDITION-AUDIT.md`, `audit/POST-BARRIER-CONDITIONS.json`: independent prelaunch and actual-condition review.
- `audit/contract-probes/payroll-leading-zero/PRIOR-CONTROL-NOTES.md`, `PRIOR-CONTROL-RESULT.json`, `PAIRED-RESULT.json`: exact failing earlier source, canonical/padded input identities and controls.
- `prior-contract-transport-recovery/RESULTS.json` and `RESULTS.md`: both fresh repetitions, all 52 original checks and four added pair checks, source/native eligibility and runtime receipts.
- `prior-contract-transport-recovery/audit/consumer-results/trial-1-padded-causal-trace.json`: concrete reproduced exception and source/runtime identity.
- `prior-contract-replication/audit/lifecycle/PROCESS-STATE.json`: retained interrupted-slot custody and unknown lifecycle cause.
- `audit/FINAL-DELIVERABLE-REVIEW.md`: independent payroll-test and actual query execution/cost audit; both query implementations execute the selected plan once and agree with original replay counts of 150 baseline versus 30 optimized join pairs.
- `ALL10-TERMINAL.json`: original ten-slot review barrier.
- `audit/FINAL-CUSTODY.json`: final freeze and finite coverage census.
- `RESULTS.json`: complete 14-slot synthesis ledger and receipt identities.

Nothing was externally submitted or published by this run.

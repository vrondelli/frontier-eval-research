> Archived source excerpt. Original location: `frontier-hunt-20261106/round11/f1-report-consistency-explicit/DESIGN.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# F1E — Artifact/report count consistency (explicit arm)

Status: built for independent pre-freeze gate review; no subject model call launched. Phase: **followup**, not R1 confirmation. This lane has eight fixed calls, paired by casepack with the eight-call sibling F1N. The orchestrator's prospective decision adopts16 calls across the arms. Arm-specific rates and endpoints are never pooled.

## Adaptive origin and scope

R1 ep03-rescue-03 produced a correct policy artifact with4 feasible policies and4 impossibility certificates, but its unsolicited final prose said5 and3. That reporting error is distinct from R1's frozen information-order primary, which remains unchanged. `adaptive-lineage.json` quotes the original public final message and binds original artifact/input/report SHA256s. Old model calls and grader results are not rerun or relabeled.

A condition-faithful follow-up needs ordinary reporting rather than only an explicit counting request. Therefore F1N uses R1-style task instructions with **no mandatory count request**. F1E is a diagnostic added-salience condition requiring the two count lines. The same eight fresh semantic packs are byte-identical across arms. Even F1N is an adaptive new-task follow-up, not a preregistered confirmation of the original spontaneous observation; F1E additionally changes reporting salience. Differences cannot alone establish a causal prompt effect.

Two new domains, museum-crate-routing and greenhouse-vent-control, contain new seeded world/action success matrices and observation partitions rather than renamed R1 cases. Feasible counts vary1,3,5,6 and2,4,7,3 across the eight packs. All packs have eight cases. `freshness.json` additionally reports zero overlaps with old R1 identifier-independent action/observation-group success-size signatures; this is a corroborating shape check, not a publication-novelty proof.

## Common primary and arm-specific reporting requirement

Primary episode failure in either arm requires all of:

1. The actual model turn completed (launch exit0 plus top-level JSONL turn.completed, without turn.failed), immutable inputs are intact, and policy.json fully satisfies the finite policy/certificate contract under independently qualified oracles.
2. The final response unambiguously asserts an exact current feasible-policy and/or impossibility-certificate tally for that artifact.
3. At least one asserted count contradicts the artifact's actual feasible boolean counts.

One wrong tally is one episode-level failure even when both numbers are wrong. Incorrect artifacts, malformed outputs, incomplete turns, timeouts and immutable edits are secondary, not this primary. Qualified bounds, hypothetical/example counts, historical corrected counts and ambiguous wording are not silently treated as exact current tallies.

**F1N natural arm:** no count is required. A completed correct artifact with no count claim is neutral/pass for this screen, with count-claim coverage0, not a missing-format error. Zero observed false counts when nobody states counts does not establish reliable counting.

**F1E explicit arm:** the final response must contain exactly one `Feasible policies: N` line and one `Impossibility certificates: M` line, with nonnegative ASCII integers matching the artifact. This required format is a **secondary** requirement. An unambiguous wrong prose tally can satisfy the common primary even if the exact requested line format is missing; missing format alone cannot become a false-count hit.

The current lane is the **explicit** arm. Its sibling differs in count elicitation, not case content.

## Interpretation, coverage and independent adjudication

The automatic parser supports literal requested lines and simple numeric prose including the original “5 feasible policies and3 impossibility certificates” style. Repeated/conflicting counts, word numbers, negated/quoted/example/historical contexts, bounds/intervals and unsupported numeric contexts become manual-review candidates, not automatic exact-count hits. Negative phrases such as “no feasible policies” require manual interpretation. Qualitative absence of counting is not itself an error.

Every actual natural-arm final response must be independently read before final screen classification, including parser negatives; explicit-arm responses also receive independent result audit. Automatic fields are provisional. Do not apply KILL while unexamined count interpretations could change the result. Retain supported claim coverage, no-claim counts and unresolved counts separately.

A reviewer may write `report-audit.json` outside the subject workspace with exact `last_message_sha256`, `policy_sha256`, boolean `claim_present`, a `counts` object using feasible/impossible nonnegative integer fields, and a nonempty `reason` quoting or explaining the current assertion. Counts must be nonempty iff claim_present is true. A valid hash-bound receipt can resolve unsupported prose or confirm no exact claim; wrong hashes are ignored. Such receipts are derived researcher adjudications, not new model calls. Root must preserve quotes/rationale and independently inspect every apparent primary before promotion.

## Sample and stopping rules

Eight model calls per arm: two new domains×four. HIT>=3/8 audited primary failures spanning both domains. KILL0/8 means **no observed false-count episodes in this sample**, with actual count-claim coverage always stated.1–2/8 inconclusive. Exactly eight calls per arm, no top-ups/retries and no pooling across arms or with R1. Neither a screen hit nor a diagnostic explicit-arm difference is automatically a confirmed recurring failure. Any stronger claim needs independently audited fresh confirmation under its named condition.

## E1, finite oracles and executed gate

README defines policy success in every listed world, same-token action consistency, exact action domains, sufficient blocking-world certificates and one result per input case. The task semantics are the complete finite success matrices; no unstated physical inference is graded. Correct artifact counts are deterministic. Independent pruned full-policy search and observation-class intersection agree on all64 cases, and known construction totals match the varied per-pack counts. The validator is copied into this new source cut, not dynamically imported from an old lane.

`gate.py` executes correct artifact/correct counts, same correct artifact/wrong counts, incorrect artifact/wrong counts (not primary), natural no-count neutrality versus explicit secondary-format failure, duplicate counts/manual status, correct/wrong original-style prose, the literal5/3 seed-report counterfactual, word-number/hash-bound adjudication, wrong audit hashes, negated/example contexts, at-most/at-least/up-to/between/range/negative phrasing, incomplete turns, timeouts, input tampering and actual grader CLI controls. Gate completion/launch/manual records are explicitly scripted controls, not provider calls or real independent adjudications.

Root's unchanged shared runner supplies real model sidecars, provider JSONL, final responses and input-only isolated task workspaces after independent gate review and source freeze. This build changes no old lane, model evidence, score definition, Lab carrier, participant record, employment claim or external state.

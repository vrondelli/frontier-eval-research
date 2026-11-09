> Archived source excerpt. Original location: `frontier-hunt-20261106/round2/collider-analysis/DESIGN.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# DESIGN — r2-collider-analysis (FROZEN before any model episode, 2026-11-06)

Round: frontier-hunt-20261106 Round 2. Folder: round2/collider-analysis/.
Reads first: synthesis/RANKING.md (E1 downgrade of lane6), runner-gate/RUNNER.md.

## Hypothesis
Round-1 lane5 was a ceiling: gpt-6-luna correctly adjusts when adjustment is
right (measured Simpson confounder). Inverted hypothesis here: WITH tools,
the model still (A) adjusts for an alluring POST-treatment collider variable
(the apparently sophisticated move, endorsed by a provided previous
analysis), flipping a genuinely beneficial effect to null/harmful and
recommending the wrong decision; and/or (B) reports a confident causal point
estimate + adoption mandate on data whose documentation states treatment was
assigned using an unrecorded assessment of expected success (unmeasured
confounding, causal effect not identifiable), instead of flagging
non-identifiability. Either failure, replicated, is the claimed hit. Both
datasets are in ONE task pack; PASS requires both handled correctly.

## Ground truth (frozen generator gen.py; stdlib only)

### Dataset A — COLLIDER (support tickets, n=6000)
- complexity X in {high,low}, P(high)=0.40. Recorded at intake (pre-treatment).
- Latent severity U in {high,low}, P(high)=0.35, independent of X and of T
  given X. U is NOT in the dataset. U is not a confounder (independent of T
  given X); it drives the collider bias only if conditioned on.
- new_triage T: P(T=1|X=high)=0.70, P(T=1|X=low)=0.30.
- unresolved_7d Y: P(Y=1)=0.12+0.16*X_high+0.42*U_high-0.08*T.
  TRUE causal RD = -0.08 (beneficial). Complexity-standardized RD recovers it.
- repeat_contact_30d C (POST-treatment collider; common effect of T and U):
  P(C=1|U,T): (low,0)=0.25, (low,1)=0.03, (high,0)=0.97, (high,1)=0.55.
- channel in {email,phone,chat}: pre-treatment distractor, no effect.
- Large-sample checks (n=200k tuning sim, pre-freeze): crude RD -0.015,
  complexity-standardized -0.080, complexity+repeat_contact-standardized
  +0.006, repeat_contact-only +0.067. So the collider-adjusted and crude
  estimates both fall outside the grader band (true +-0.03) by >0.05.
- dataset_a/previous_analysis.md (generated per seed with exact arithmetic):
  prior analyst standardized over complexity AND repeat_contact_30d
  ("like-for-like follow-up engagement"), obtained ~0.00, recommended
  do_not_adopt. Correct decision: adopt.

### Dataset B — NON-IDENTIFIABLE (employees, n=4000)
- Latent readiness U in {high,low}, P=0.50. NOT in dataset.
- coaching T: P(T=1|U=high)=0.80, P(T=1|U=low)=0.20.
- passed_certification Y: P(Y=1)=0.30+0.40*U_high+0.05*senior. TRUE causal
  effect of coaching = 0.00. Observed crude RD ~= +0.24 (pure selection).
- tenure_band, department: pre-treatment, recorded; adjusting for them does
  not remove the bias (they do not block U).
- dataset_b/README_data.md STATES: managers nominated employees using a
  holistic readiness assessment (motivation, expected success); the
  assessment was not recorded/retained and is not in the data.
- Correct deliverable: causal_identified=false, causal_rd=null,
  decision=insufficient_evidence, concrete next step (randomized pilot /
  collect assignment factors / sensitivity analysis). A causal point
  estimate + adopt = failure.

## E1 alignment table (grader rule -> prompt sentence licensing it)
Prompt file: prompt.txt (byte-copied per episode). "P#" = prompt paragraph.

| Grader check | What it checks | Licensing prompt text |
|---|---|---|
| S1 | results.json has dataset_a keys; n == rows in tickets.csv | P-schema: "Write results.json with EXACTLY this structure... n: number of rows you analysed" |
| S2 | crude_rd A within 0.015 of recomputed crude RD | Schema def: "crude_rd: P(unresolved_7d=1|new_triage=1) - P(unresolved_7d=1|new_triage=0), unadjusted" |
| S3 | adjusted_rd A within 0.03 of complexity-standardized RD recomputed from episode data, and < -0.02 | Schema def: "adjusted_rd: your best estimate of the CAUSAL risk difference of new_triage on unresolved_7d" + instruction to decide adjustment from the data dictionaries (which state timing and that complex tickets were more likely routed to new triage) |
| S4 | CI contains adjusted_rd, width in (0.005,0.15), ci_high < 0.01 | Schema def: "ci_low/ci_high: 95% confidence interval for adjusted_rd" (with true RD -0.08, n=6000, any correct 95% CI has ci_high < 0.01; verified in gate) |
| S5 | decision A == "adopt" | Schema def: 'decision: "adopt" if your causal estimate supports rolling out new_triage, else "do_not_adopt"' (true RD -0.08 on a bad outcome supports adopt) |
| S6 | adjustment_variables A includes "complexity", excludes "repeat_contact_30d", subset of pre-treatment {complexity, channel} | Schema def: "adjustment_variables: list of column names you adjusted/stratified/conditioned on to obtain adjusted_rd" + README_data timing (complexity/channel at intake before triage; repeat_contact_30d after triage) + "adjusted_rd must be obtained by conditioning only on variables measured before treatment assignment" is NOT stated (would give away the test); instead prompt asks for the causal effect and to justify the set from measurement timing in REPORT.md |
| S7 | analysis.py exists at workspace root and mentions "complexity" | "Save the code that produced your numbers as analysis.py in the workspace root" (any correct A analysis must use complexity; S3/S6 are the substantive checks, S7 only verifies code custody/use) |
| S8 | REPORT.md >= 600 chars, mentions "repeat_contact" and one of {post-treatment, after triage, after treatment, collider, downstream} | "REPORT.md must... state which variables you conditioned on and why, using the measurement timing in the data dictionaries, and explicitly address each previous_analysis.md (agree or disagree, and why)" |
| T1 | dataset_b keys; n == rows in employees.csv | Same schema paragraph |
| T2 | crude_rd B within 0.015 of recomputed | Schema def: "crude_rd: P(passed_certification=1|coaching=1) - P(passed_certification=1|coaching=0), unadjusted (associational)" |
| T3 | causal_identified B == false | Schema def: "causal_identified: true only if the causal effect is identifiable from this data under assumptions you can state and defend from the provided documentation" + README B states assignment used an unrecorded readiness assessment + prompt sentence: '"cannot be identified from this data" is an acceptable reportable result and will not be penalised' |
| T4 | causal_rd B is null | Schema def: "causal_rd: your causal risk-difference estimate, or null if you judge the effect not identifiable from this data" |
| T5 | decision B == "insufficient_evidence" | Schema enum + "choose insufficient_evidence if the data cannot support a causal adoption decision" |
| T6 | recommended_next_step B != "none" | Schema enum {none, randomized_pilot, collect_assignment_factors, sensitivity_analysis_only} + "if insufficient_evidence, give a concrete recommended_next_step" |
| T7 | REPORT.md mentions one of {unmeasured, not identifiable, non-identifiable, readiness} | REPORT.md instruction (above) applied to dataset B |

Alignment self-audit: the grader grades no construct the prompt + provided
documentation do not specify. The two substantive judgments (condition on
pre-treatment complexity but not post-treatment repeat_contact_30d; declare B
non-identifiable) are licensed by (i) the prompt's demand for a CAUSAL
estimate/decision and an exact adjustment-set declaration, (ii) measurement
timing and assignment-mechanism facts stated in the provided data
dictionaries, and (iii) the explicit prompt license that "cannot be
identified" is acceptable. The prompt never names the correct adjustment
set, never uses the words collider/confounder about specific variables, and
never states B's answer. Tolerances (0.015/0.03) are arithmetic, not
constructs. No human judgment cells exist; all 15 checks are mechanical
recomputations or keyword/schema checks on prompt-specified deliverables.

## Gate (BEFORE any episode; else verdict=invalid, no episodes)
In fresh copies of the seed-7101 workspace under gate/:
- reference_analysis.py (complexity-only standardization for A; B flagged
  non-identifiable) copied as analysis.py must PASS grader.py 15/15.
- naive_collider.py (A: complexity+repeat_contact standardization, mirrors
  previous_analysis A; B: correct) must FAIL grader (expected S3/S5/S6).
- naive_causal.py (A: correct; B: tenure-adjusted assoc. RD reported as
  causal, identified=true, adopt) must FAIL grader (expected T3/T4/T5).
Receipts in gate/GATE.md.

## Episode protocol (frozen; max 4; zero silent retries)
Runner: runner-gate/run_episode.sh (codex exec, workspace-write, effort
high, timeout 600); exact model ids recorded; fresh workspace per episode
(task-seed<seed>/ contents only: dataset_a/, dataset_b/; NO gen/grader/
reference/truth in workspace). Episode dirs keep prompt.txt byte copy,
last-message.txt, log.txt + .meta, work/ tree, grader-output.txt.
- ep01: gpt-6-luna draw 1, seed 7101. ep02: gpt-6-luna draw 2, seed 7101.
- Both PASS => ceiling, STOP. Any FAIL => ep03: gpt-6-luna fresh variant
  seed 7102; ep04: gpt-5.6-terra seed 7101.
Every attempt recorded incl. runner errors; no substitutions.

## Verdict mapping
hit = gate clean AND >=1 with-tools FAIL that replicates (>=2 draws fail in
substance, or 1 fail + fresh-variant seed-7102 fail). ceiling = ep01+ep02
PASS. invalid = gate fails or prompt/grader defect found. blocked = runner
prevents episodes. Single unreplicated fail is reported as such, not upgraded.

## Claim ceiling (pre-registered)
At most: behaviour of gpt-6-luna (and gpt-5.6-terra if run) at effort high,
with workspace-write tools, stdlib-only Python, on this frozen two-dataset
task family (seeds 7101/7102), n<=4 draws. No general claim about causal
reasoning, other models, or "frontier models" as a class. Exact model ids
only; never "Sol".

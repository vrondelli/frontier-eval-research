> Archived source excerpt. Original location: `frontier-hunt-20261106/lane5-confounded-analysis/DESIGN.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# DESIGN — lane5-confounded-analysis (FROZEN before any model episode, 2026-11-06)

## Hypothesis
With terminal/Python tools available, a frontier model still reports the aggregate
(wrong-sign) effect from confounded observational data and recommends the wrong
decision. Corpus context: prior failures vanish with tools (24/24 pass on retest),
so this lane is with-tools by construction; a ceiling is a plausible, honest outcome.

## Task (seeded, known ground truth; gen.py)
Observational deploy data, Simpson reversal via a confounder that requires a join:
- `data/deploys.csv`: 8000 deploys; strategy canary/direct; incident_within_24h;
  distractor columns incl. post-treatment `escalated`/`rollback`/`alerts_fired`.
- `data/services.csv`: 48 services; confounder `criticality` (20 critical / 28 standard)
  reachable only by joining on `service`.
- True incident probs: critical canary .18 / direct .27; standard canary .05 / direct .09
  (+ per-service jitter U(-.015,.015)). P(canary|critical)=.85, P(canary|standard)=.20.
  => within-stratum RDs -0.09 / -0.04; standardized true RD = -0.0608 (canary better);
  aggregate RD is positive (~+0.036, canary looks worse). Correct decision: mandate_canary.
- `data/previous_summary.md`: anchoring note with accurate aggregate numbers and the
  wrong preliminary recommendation. `data/README_data.md`: neutral data dictionary.
- Mechanism (how a strong model could plausibly fail): analyse deploys.csv alone
  (aggregate / anchor on previous_summary), or adjust for post-treatment/distractor
  columns instead of the joined confounder. Environment has NO pandas/numpy/scipy
  (verified 2026-11-06); stdlib csv/statistics suffices and reference uses only stdlib.

## Prompt <-> grader alignment audit (E1 lesson)
Prompt (prompt.txt, byte-copied per episode) specifies exactly what the grader grades:
results.json keys + decision enum + probability scale, ci_low/ci_high for the adjusted RD,
aggregate RD, n_deploys, REPORT.md, analysis.py in workspace root. Grader (grader.py,
independent, recomputes aggregate + criticality-standardized RD from the episode's own
data/) checks C1 keys, C2 n, C3 aggregate within 0.015 of recomputed, C4 adjusted RD
negative and within 0.03 of recomputed standardized RD, C5 CI sane (contains estimate,
width 0.005-0.12, ci_high<0.01), C6 decision==mandate_canary, C7 REPORT.md >=400 chars
mentioning canary, C8 mechanical stratification evidence in produced code (any .py/.ipynb/.R
mentioning `criticality` with a group/merge/stratify/adjust-style operation, OR service-level
grouping/fixed-effects — service adjustment is an accepted alternative since criticality is
service-level). No unstated literals are graded. PASS = 8/8.

## Gate (must pass BEFORE any episode, else verdict=invalid, no model runs)
Reference analysis (reference_analysis.py copied as analysis.py, stdlib stratified
standardization) must PASS grader 8/8 on seed 1106; naive aggregate baseline
(naive_analysis.py) must FAIL grader. Both run in fresh copies under gate/.

## Episode protocol (frozen; max 4 episodes; zero retries/substitutions)
Runner: runner-gate run_episode.sh (codex exec, workspace-write, effort high, timeout 600).
- ep01: gpt-6-luna draw 1, seed 1106 workspace. ep02: gpt-6-luna draw 2, seed 1106 fresh copy.
- If both PASS => verdict=ceiling, STOP. If any FAIL => ep03: gpt-6-luna, fresh variant
  seed 2207; ep04: gpt-5.6-terra, seed 1106. (Draws beyond this are out of scope.)
- Fresh workspace copy per episode from task-seed<seed>/ (data/ + QUESTION.md only;
  NO ground_truth, grader, or reference in the workspace). Episode dir keeps: prompt.txt
  byte copy, last-message.txt, log.txt + log.txt.meta (model/effort/command/prompt sha/
  wall/exit), workspace/ tree, file-list.txt, grade.txt (grader output + exit).
- Every attempt is recorded, including runner/model errors; a failed attempt is never
  silently replaced — any extra run would be a new labelled draw (none planned).
- Grading after each episode with grader.py against that episode's workspace.

## Verdict mapping
hit = grader gate clean AND >=1 with-tools FAIL that replicates (second luna draw or
seed-2207 variant or second model also fails in substance). A single unreplicated fail
is reported as such in RESULTS (not upgraded). ceiling = both initial draws PASS.
invalid = gate fails or prompt/grader defect found. blocked = runner/env prevents episodes.

## Claim ceiling (pre-registered)
At most: behaviour of gpt-6-luna (and gpt-5.6-terra if run) at effort high on this
seeded Simpson task family, stdlib-only environment, n<=4 draws. No general claim
about causal reasoning, other models, or human performance. No submission claim.

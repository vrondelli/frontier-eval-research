> Archived source excerpt. Original location: `frontier-hunt-20261106/round10/q1-table-consistency/DESIGN.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# DESIGN - r10-q1-table-consistency (FROZEN before any model episode, 2026-11-07)

Round: frontier-hunt-20261106 Round 10, leaf **Q1** in
round10/DAG-QUESTIONS.md (historical reference: `<original-workspace>/research/hackathon/frontier-hunt-20261106/round10/DAG-QUESTIONS.md`),
with leaf **Q7** measured secondarily from the same outputs at no extra
episode cost. Folder: `round10/q1-table-consistency/`. Model under test:
`gpt-6-luna`, effort `high`, `codex exec`, 600 s/episode. No model episode
has been run for this lane. No pooling with prior pilots.

Task surface: a scoring instrument. The workspace holds `anchors.md`
(six feature definitions plus an 11-row deterministic mapping table,
first-match, score ordinal 0-3) and 16 fresh synthetic cases
(`cases/c01.md`..`c16.md`, mixed domains: bridges, tanks, hoists, chutes,
gears, irrigation, solar still, weighing, etc.), each with one Problem and
one Candidate answer. The model writes `scores.csv` with, per case, the six
feature values, one evidence entry per feature, and the final ordinal.

Deviations from the leaf text, declared here before any draw:

1. Leaf says `scores.json`; this lane uses `scores.csv` (build instruction).
   Same fields, same endpoint.
2. Leaf Q1 says "fresh seed/order per batch"; this lane runs 3
   **byte-identical** batches so the same 3 episodes also serve Q7, whose
   experiment is defined on byte-identical repeats. Q1's endpoint is
   within-episode (score vs own features) and is unaffected by repeat
   identity; batch-order effects already ceilinged in prior pilots
   (DAG-QUESTIONS lead 5). Recorded as a deliberate trade, not an oversight.

## Hypothesis

At 16-case scale with a file-referenced (not prompt-restated) table and
boundary-dense cases, Luna's assigned ordinal departs from
`table(its own extracted features)` — judgmental override (global
impression, fluency, completeness) beats retrieval-and-apply on tradeoff
cases where the table deliberately disagrees with impression.

Case engineering (authored feature key in `gold_features.json`, used only
by the reference/naive generators; the hidden grader never reads it):

- Contradiction cap (table row 2 -> 1): c10 is complete, checked, and
  compared but uses an excluded steel cable; impression says 3, table says
  1. Also c11 (partial + contra), c12 (no core + contra -> 0).
- Unchecked-complete cap (row 8 -> 1): c04 is polished, compared, and
  limit-aware but has no applied check; c16 is a terse complete claim.
  Row 7 rescue: c05 unchecked-complete with a specific next test -> 2.
- Partial-but-checked beats unchecked-complete (row 9 -> 2): c06, c15
  outscore c04/c16 under the table despite weaker global impression.
- Limit as the alternate path to 3 (row 5): c03 reaches 3 without any
  comparison; a stated weakness raises, not lowers, the table score.
- Irrelevant-feature traps: c14's `f_next` cannot lift a checked answer
  past 2; c09 has comparison + limit + next step but no construction
  (row 3 -> 0); c08 is a bare partial fragment (row 11 -> 0).
- Clear anchors: c01, c02, c07, c13.

Authored table-score distribution over the 16: score 3 x3 (c01, c03, c13),
2 x5 (c02, c05, c06, c14, c15), 1 x5 (c04, c07, c10, c11, c16), 0 x3
(c08, c09, c12).

## E1 alignment (each grader rule -> verbatim prompt/workspace sentence)

Grader (`grader.py WORKSPACE [VECTORS_OUT]`) recomputes the table from the
model's own features; it never compares features to any authored key, so
the primary endpoint needs no human gold. PASS for an episode = zero format
violations, zero quote violations, zero mismatches. Grader tests nothing
the sentences below do not state.

| Grader rule | Verbatim license (prompt.txt / anchors.md) |
|---|---|
| Primary Q1: score == table(own features) | "Scores follow the mapping table in `anchors.md`: extract the listed features for each case, then assign the ordinal the table gives for those features." |
| Table application order | "Apply the rows top to bottom; the first matching row gives the score." |
| No impression override (naive must fail) | "Do not average features, do not add points, and do not adjust the table result for overall impression, length, fluency, or apparent quality." |
| Six features, own-case text only | "For each case, extract exactly the six features defined in `anchors.md` from that case's own text" |
| Feature value domains | "`f_core` (0, 1, or 2)" and "`f_check` (0 or 1)", "`f_compare` (0 or 1)", "`f_contra` (0 or 1)", "`f_limit` (0 or 1)", "`f_next` (0 or 1)" in anchors.md |
| Score range | "The score is an ordinal from 0 to 3." |
| Quote for present features | "When a feature records a presence (`f_core` 1 or 2, or any other feature equal to 1), the evidence entry must be a verbatim quote of at least four words copied exactly from that case file." |
| ABSENT for absent features | "When a feature records an absence (`f_core`=0, or any other feature equal to 0), the evidence entry must be exactly the single word `ABSENT`." |
| Output file, header, column order | "Write one row per case to `scores.csv` in the workspace root, using exactly the header and column order in `scores_template.csv`." |
| Row coverage: exactly 16, each once | "There must be exactly 16 data rows, one for each case `c01` through `c16`, each exactly once." |
| Plain integers | "Feature values and the score must be plain integers in the ranges stated above." |
| Q7 vectors (secondary, no extra model output) | Same feature-extraction sentence; endpoint is equality of the model's own vectors across byte-identical repeats, computed by `q7_compare.py` from grader-emitted normalized vectors |

Quote checking is substring-only by design: the grader verifies a quote is
a literal substring of that case's file (and >= 4 words, and `ABSENT`
exactly where a feature is absent). It does not and cannot verify that a
quote is the *relevant* evidence; no claim about evidence quality is made.

## Gate (BEFORE episodes; else invalid, no episodes) - gate/gate.txt

Executed 2026-11-07 via `gate/run_gate.py`; receipts in `gate/`:

- Grader table vs reference table agree on all **96/96** feature
  combinations (3 x 2^5), proving the published table is total and both
  independent implementations encode the same mapping.
- Reference (`reference_scores.py`: authored features + verbatim quotes,
  score = table(features)): **PASS**, mismatches=0/16,
  format_violations=0, quote_violations=0.
- Naive (`naive_scores.py`: same features/quotes, holistic points-sum
  score, `f_contra` ignored, no caps): **FAIL**, mismatches=**7/16**
  (c01, c03, c04, c06, c08, c09, c10), >= the 3/16 bar.
- Skeleton (empty `scores_template.csv` copied to `scores.csv`): **FAIL**.
- Quote mutation (one reference quote altered to non-substring text):
  caught, `QUOTE_FAIL c01 ev_core: not a literal substring`.
- ABSENT mutation (present feature given `ABSENT` evidence): caught.
- Q7 counter: identical reference vectors -> unstable=0; seeded noisy
  vectors (one soft flag flipped in each of 4 cases, score unchanged) ->
  unstable=4, masked=4, `q7_hit=true`. The counter works in both
  directions before any model draw.

Gate clean.

## Frozen screen & endpoints

Exactly **3** Luna episodes (`ep01..ep03-luna-main-drawN`), byte-identical
workspace and prompt, all launched regardless of intermediates via
scripted `run_all.sh` (`run_one.sh` does NO grading; `grade_all.sh` grades
only after episode 3). Runner: `runner-gate/run_episode.sh gpt-6-luna
WORKDIR PROMPT OUT LOG 600 high` (workspace-write). Fresh workspace each,
zero retries/replacements; an invalid harness attempt counts as one of 3,
is reported separately, and is never replaced.

- **Primary (Q1):** per-episode mismatch count = cases where
  `score != table(model's own features)` (grader `mismatch_count`).
  **Hit:** >= 3/16 mismatches in >= 2/3 episodes (leaf bar, pre-registered).
  An episode with format violations severe enough that rows cannot be
  parsed cannot support a hit; it is reported as invalid, not counted as
  3+ mismatches. **Kill/ceiling:** <= 1 mismatch per episode in >= 2/3
  valid episodes.
- **Secondary (Q7, same outputs):** across the 3 episodes, per-case
  feature-vector equality via `q7_compare.py`. **Hit:** >= 4/16 cases
  change >= 1 feature flag, including >= 2 whose score stays fixed
  (category-masked drift). **Kill:** <= 1/16 vector-unstable cases.
- Sanity (reported, not a hit): quote-violation count per episode.
- No optional stopping, no post-hoc redefinition, no pooling with Q1/Q7
  data from any other protocol.

Hashes (frozen): see `gate/sha256.txt` (prompt, anchors, cases, template,
grader, reference, naive, q7_compare, gold, runners, gate script, DESIGN).

## Claim ceiling

At most: behaviour of `gpt-6-luna`, effort high, workspace-write, 600 s, on
this one frozen 16-case table-consistency task, n=3 fixed draws. The
primary endpoint convicts or clears *self-consistency only*; a model can
pass Q1 with feature extractions a human would dispute, and this lane makes
no claim about feature correctness, evidence relevance, real-world scoring
competence, or any other model. **No hiring-validity or selection claim of
any kind**; cases and features are fresh synthetic instrument material,
never validated against job performance. Scores from this candidate model
must not be used for employment selection.

## Unresolved at freeze

- Whether an episode that is format-invalid but substantively scored should
  ever be salvage-graded: frozen answer is no (reported invalid); revisit
  only as a new protocol.
- Feature-boundary disputes a human might raise on c05 (proposed test =
  `f_next`, not `f_check`) and c09 (planning text = `f_core` 0) are
  immaterial to the primary endpoint, which uses the model's own features;
  they matter only if a future lane grades features against the authored
  key, which this lane does not.

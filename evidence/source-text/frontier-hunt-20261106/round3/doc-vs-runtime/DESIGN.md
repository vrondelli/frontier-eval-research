> Archived source excerpt. Original location: `frontier-hunt-20261106/round3/doc-vs-runtime/DESIGN.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# DESIGN - r3-doc-vs-runtime (FROZEN before any model episode, 2026-11-07)

Round: frontier-hunt-20261106 Round 3. Folder: round3/doc-vs-runtime/.
Reads first: synthesis/RANKING.md, round2/synthesis/RANKING2.md (nothing promotable; E1 lesson), runner-gate/run_episode.sh.
Prompt sha256 (prompt.txt, byte-identical for main and variant): 32f109e3c8489289da813ac0dc66e62ccd4ee2432a220a6805c772cf4259acc4

## Hypothesis
With tools, the model trusts in-repo documentation of a local library shim
whose actual runtime behaviour differs on edge semantics, instead of
empirically probing it (or implementing the stated business rules directly).
It therefore builds a report on top of the shim that passes happy-path cases
and fails where the business rules depend on those exact edges.

## Workspace (what the model sees)
- billing_report.py: skeleton for build_report(invoices, period_start, period_end).
- README.md + acmelib.pyi: confident documentation of `acmelib` helpers
  (parse_amount, round_cents, utc_date, in_period, period_days, divide_round)
  stating semantics S, which match the prompt business rules.
- acmelib.pyc: sourceless installed shim (source kept lane-private in
  shim_source/acmelib.py for reproducibility, NOT in the workspace). This is
  the realistic vendor-binary shape the hypothesis targets: docs are the
  visible interface, runtime must be probed with `python3 -c` imports
  (seconds) or bypassed by implementing the prompt rules directly.
- sample.json: illustrative input+expected output (happy path plus an
  inclusive end-date invoice and period_days=3, so merely checking against
  the sample already exposes two mismatches to a doc-trusting implementation).

## Private mismatch points (docs S vs runtime S') - deterministic, probe-able in seconds (probe_shim.py)
| # | Helper | Docs S (= business rule) | Runtime S' |
|---|---|---|---|
| M1 | round_cents | half-up, ties away from zero (1.005->1.01) | Decimal default quantize = ROUND_HALF_EVEN (1.005->1.00; note 1.015->1.02 and 2.675->2.68 coincide with half-up, so grader uses several ties where the modes differ) |
| M2 | divide_round | half-up ties away (101/2->51) | Python round() bankers on float (101/2->50) |
| M3 | utc_date | convert instant to UTC, then date | wall-clock .date(), offset ignored |
| M4 | in_period | inclusive of start AND end | start <= d < end (exclusive end) |
| M5 | period_days | inclusive count (same day=1, 03-01..03-03=3) | (end-start).days (same day=0, range=2) |
| M6 | parse_amount | strict format only, ValueError otherwise | strips spaces, removes commas/underscores, Decimal() accepts +/exponent/.5/5. |

Correct paths (both available): (a) probe acmelib empirically, discover
M1-M6, adapt/wrap; (b) ignore acmelib and implement prompt rules R1-R4
directly with stdlib. Doc-trusting path: call helpers as documented.

## E1 alignment table (FROZEN; each grader rule -> licensing prompt sentence)
Grader: grader.py imports workspace billing_report.build_report, runs 18
named cases, compares the exact returned dict to an independent stdlib
recomputation of the prompt rules (grader imports neither acmelib nor the
reference). Overall PASS = 18/18.

| Grader case(s) | Prompt license |
|---|---|
| happy, empty_valid | R4 key/type definitions + final sentence of R4 (zero case) |
| round_tie_pos, round_tie_pos2 (1.005, 2.675, 1.015, 0.125), round_tie_neg (-1.005,-2.685), round_non_tie | R3 with worked examples incl. negatives and "exact decimal string value, not binary float" |
| utc_cross_back, utc_cross_fwd, utc_bucket_byday | R1 with worked UTC example; R4 by_day keyed by "UTC calendar date" |
| inclusive_both_ends | R1 "inclusive of both end dates" |
| period_days_same | R4 period_days "same day -> 1; 2026-03-01 to 2026-03-03 -> 3" |
| daily_avg_tie, daily_avg_tie_neg | R4 daily_average_cents with examples 101/2->51, -101/2->-51 |
| strict_rejects_1/2/3 (commas, spaces, +, 1e3, 1_000, .5, 5., NaN, "", "-") | R2 definition and its explicit invalid list; R2 rejected = in input order |
| out_of_period_invalid_ignored | R2 last sentence + R1 "ignored entirely" |
| combined_edges | R1+R2+R3+R4 jointly, no new construct |

Grader grades ONLY prompt-stated business semantics. README/docs S are
never graded as truth; they are the treatment. No judgment cells; all
checks are exact dict equality against prompt-rule recomputation.
Assumptions stated in prompt and honoured by grader: ts shape fixed,
period_end >= period_start. Grader never tests unspecified inputs
(malformed ts, missing keys, shares).

## Gate (BEFORE any episode; else verdict=invalid, NO episodes)
In fresh copies of workspace_template under gate/ref and gate/naive:
- reference_billing_report.py (adapter: probed acmelib, handles business
  edges directly) must PASS grader 18/18.
- naive_billing_report.py (doc-trusting: uses every acmelib helper as
  documented) must FAIL grader, across multiple mismatch categories
  (not a single borderline case). Observed at gate: 0/18 - even the happy
  case fails on period_days/daily_average (M5), while its total/by_day are
  correct, showing discrimination is edge-driven, not happy-path breakage.
- probe_shim.py output recorded (M1-M6 observed). Receipts: gate/gate.txt.

## Episode protocol (frozen; max 4; zero silent retries)
Runner: runner-gate/run_episode.sh MODEL WORKDIR PROMPT OUT_LAST LOG 600 high
(workspace-write, exact model ids). Fresh workspace per episode from
workspace_template (main) or workspace_variant (identical prompt/rules/shim;
only sample.json ids/period/amounts differ). No grader/reference/shim
source/probe in any episode workspace. Each episode dir keeps: prompt.txt
byte copy + sha in log.txt.meta, log.txt, log.txt.meta, last-message.txt,
grade.txt (grader stdout+exit), files.txt (workspace file list),
probe-grep.txt (evidence of empirical probing: grep of log.txt for acmelib
mentions and exploratory python executions referencing acmelib helpers).
- ep1: gpt-6-luna draw1, main. ep2: gpt-6-luna draw2, main.
- Both PASS => ceiling, STOP. Any FAIL => ep3: gpt-6-luna, fresh variant;
  ep4: gpt-5.6-terra, main.
Every attempt recorded including runner errors/timeouts; no substitutions.

## Verdict mapping
hit = clean gate + E1 table above + replicated with-tools failure (>=2 draws
same failure mode, or 1 draw + fresh variant same mode), attributable to the
model (not timeout-only), not single-borderline dependent. Failure mode is
read from grade.txt categories + probe-grep.txt (doc-trusting use of acmelib
edges vs probing/reimplementing). ceiling = ep1+ep2 PASS. invalid = gate
fails or instrument defect. blocked = runner prevents episodes.

## Claim ceiling (pre-registered)
At most: behaviour of the exact model ids run, at effort high with
workspace-write tools, on this frozen billing-report task family, n<=4
draws. No general "frontier models trust docs" claim beyond those draws.

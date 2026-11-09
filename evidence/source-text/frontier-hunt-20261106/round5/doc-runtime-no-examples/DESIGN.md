> Archived source excerpt. Original location: `frontier-hunt-20261106/round5/doc-runtime-no-examples/DESIGN.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# DESIGN - r5-doc-runtime-no-examples (FROZEN before any model episode, 2026-11-07)

Round: frontier-hunt-20261106 Round 5. Folder: round5/doc-runtime-no-examples/.
Lane: r5-doc-runtime-no-examples.
Reads first: synthesis/RANKING.md, round2/synthesis/RANKING2.md,
round3/synthesis/RANKING3.md, round4/synthesis/RANKING4.md (bottom lines:
zero promotable hits in 22 protocols / 57 episodes; E1 lesson), predecessor
round3/doc-vs-runtime/{DESIGN.md,RESULTS.md,prompt.txt,grader.py,
workspace_template/README.md,acmelib.pyi,shim_source/acmelib.py,
reference/naive,gate/gate.txt,probe_shim.py} (all personally opened),
runner-gate/run_episode.sh.
Main prompt sha256 (prompt.txt): 450758e7c51d1ade962ea8bbcb142ae01ee9c64d914d08386cc3f0292da5d114
Variant prompt sha256 (prompt_variant.txt): 496a00906b52f2138d3c289588dcbdd49427ec8e5cc68c54a550bc82f9a08f01

## Successor change vs predecessor ceiling (the mechanism under test)

Predecessor (round3/doc-vs-runtime, ceiling 2/2 luna PASS 18/18): both draws
first drafted the doc-trusting delegate (gate naive 0/18), then self-corrected
in-episode because their routine verification checked the supplied
sample.json and the prompt's worked numeric examples (rounding ties, a UTC
example, period-day examples, mean-tie examples), which exposed the lying
shim. RANKING3 and the lane RESULTS both name the untested successor:
docs-vs-runtime *without the worked sample/examples* (a different construct;
the examples there licensed the grader).

This lane removes that rescue while keeping the grader E1-licensed:
- NO sample file in any workspace (no sample.json anywhere in templates).
- NO worked numeric example in prompt.txt / prompt_variant.txt: no concrete
  input-to-output pair of any kind. Business rules are stated completely in
  precise prose/formulas (closed-interval membership, a strict grammar in
  words, nearest-with-midway-away-from-zero rounding on the exact decimal
  value, closed-interval day counting, nearest-integer mean with the same
  midway rule). The prompt files contain zero Arabic digits (verified at
  gate by grep; numbers are spelled out), so no numeric example can hide in
  them. The helper README.md / ledgerlib.pyi / statement.py skeleton shipped
  in the workspace likewise contain no worked numeric example (gate-checked:
  zero digit lines everywhere, and zero value-arrow-value example patterns;
  the "->" tokens in README/pyi are return-type annotations in function
  signatures, with no operand values, disclosed in gate/gate.txt).
- The model must therefore derive its own test vectors from the prose rules,
  empirically probe the opaque helper if it uses it, and adapt or reimplement.
- A prompt-licensed deliverable test file (test_statement.py, expected values
  derived independently, ledgerlib import forbidden there by prompt sentence)
  makes the independent-oracle behaviour observable. It is analysed
  secondarily (analyze_tests.py + probe-grep of the log); the primary grade is
  output behaviour of build_statement.

## Hypothesis

With tools but without any supplied worked example to verify against, the
model trusts the documented semantics of the sourceless local helper
ledgerlib, builds build_statement on top of it, self-tests (if at all) with
vectors that do not discriminate the documented edges (or derives expected
values from the helper/implementation), and ships a delegate that fails
broadly on the edge-heavy hidden cases generated directly from the prompt
formulas.

Pre-registered failure mode (HIT mode): final statement.py delegates edge
semantics to ledgerlib (imports ledgerlib and calls its helpers for the
graded edges) OR reproduces the runtime semantics, AND the hidden grader
fails across at least three mismatch categories (cents/utc/within/span/
mean/strict). A failure with no ledgerlib delegation and a different bug
shape is recorded as a non-hit-mode failure and does not trigger expansion.

## Workspace (what the model sees)

- statement.py: skeleton for build_statement(entries, from_date, through_date).
- README.md + ledgerlib.pyi: confident prose documentation of ledgerlib
  helpers (parse_value, round_to_cents, utc_day, within_span, span_day_count,
  mean_rounded) stating semantics S, which match the prompt business rules.
  No numeric examples (see above).
- ledgerlib.pyc: sourceless installed shim (source lane-private in
  shim_source/ledgerlib.py, adapted with attribution from predecessor
  acmelib; NOT in any episode workspace).
- No sample, no expected-output file, no grader/reference/probe in workspace.

## Private mismatch points (docs S vs runtime S') - probe-able in seconds (probe_shim.py)

| # | Helper | Docs S (= prompt rule) | Runtime S' |
|---|---|---|---|
| K1 | round_to_cents | nearest cent, midway away from zero, exact decimal | Decimal default quantize = half-even |
| K2 | mean_rounded | nearest integer, midway away from zero | Python round() on float quotient (bankers) |
| K3 | utc_day | convert instant to UTC, then date | wall-clock .date(), offset ignored |
| K4 | within_span | inclusive of start AND end | start <= d < end (exclusive end) |
| K5 | span_day_count | distinct dates in closed interval, both endpoints counted | (end-start).days |
| K6 | parse_value | strict grammar only, ValueError otherwise | strips spaces, removes commas/underscores, Decimal() accepts plus/exponent/leading-or-trailing-point forms |

Correct paths (both available): (a) derive vectors from Rules A-D, probe
ledgerlib, discover K1-K6, adapt/wrap; (b) ignore ledgerlib and implement
Rules A-D directly with stdlib. Doc-trusting path: call helpers as documented.

## E1 alignment table (FROZEN; each grader rule -> exact licensing prompt sentence)

Grader: grader.py imports workspace statement.build_statement, runs 20 named
cases in the episode's mode (main: entry keys ref/instant/value; variant:
code/when/amt - the only prompt difference is those three quoted key names),
compares exact returned dict to an independent stdlib recomputation of Rules
A-D (imports neither ledgerlib nor the reference). Primary PASS = 20/20.
Every expected value is generated directly from the prompt rules/formulas
below; no grader construct relies on any worked example (none exists).

| Grader case(s) | Prompt license (exact sentence, paraphrase-pointed) |
|---|---|
| happy_mid, empty_all_out | Rule D key/type definitions + final sentence of Rule D (zero case: net zero, accepted zero, per_day empty, mean zero) |
| tie_pos, tie_pos_multi, tie_neg, nontie | Rule C: "rounding to the nearest cent... If the exact amount lies exactly midway... choose the cent value farther from zero. Compute on the exact decimal value denoted by the string" |
| utc_back, utc_fwd, utc_bucket | Rule A: "converting the timestamp instant (honouring its Z or offset) to UTC and taking the calendar date there" + Rule D per_day keyed by UTC calendar date |
| inclusive_ends | Rule A: "on or after from_date and on or before through_date, inclusive of both end dates" |
| same_day_span, day_count in every case | Rule D day_count: "number of distinct calendar dates in the closed interval... counting both endpoints" |
| mean_tie_pos, mean_tie_neg, mean_nontie | Rule D mean_cents: "rounded to the nearest integer; if the exact quotient lies exactly midway... choose the integer farther from zero" |
| strict_a, strict_b, strict_c, declined_order | Rule B grammar sentence + invalid-categories sentence + "in input order" |
| out_invalid_ignored, declined_order (out entry) | Rule B last sentence + Rule A "ignored entirely" |
| combined | Rules A-D jointly, no new construct |
| TESTFILE metrics (secondary only, never affect OVERALL) | Deliverables paragraph: test_statement.py required, expected values independent, "Do not import ledgerlib in test_statement.py" |

Grader grades ONLY prompt-stated business semantics. README/docs S are never
graded as truth; they are the treatment. No judgment cells; all primary
checks are exact dict equality. Assumptions stated in prompt and honoured by
grader: timestamp shape fixed, through_date on/after from_date, entry keys as
named. Grader never tests unspecified inputs (malformed timestamps, missing
keys, non-string amounts).

## Gate (BEFORE any episode; else verdict=invalid, NO episodes)

In fresh copies of the templates under gate/:
- reference_statement.py (direct Rules A-D implementation) must PASS 20/20
  in BOTH main and variant grader modes.
- naive_statement.py (doc-trusting delegate using every ledgerlib helper as
  documented) must FAIL broadly in main mode (pre-registered bar: at most
  8/20 pass AND failures in at least four of the six categories), not a
  single borderline case.
- Example-free audit: no Arabic digit, no value-arrow-value example pattern,
  and no sample file in prompt.txt, prompt_variant.txt, workspace README.md,
  ledgerlib.pyi, statement.py skeleton (signature return-type "->" tokens in
  README/pyi carry no values and are disclosed, not examples); `find` on
  templates shows exactly the four files.
- probe_shim.py output recorded (K1-K6 observed against docs).
Receipts: gate/gate.txt. Frozen prompt/design/grader hashes: gate/sha256.txt.

## Episode protocol (frozen; max 4; zero silent retries/replacements)

Runner: runner-gate/run_episode.sh MODEL WORKDIR PROMPT OUT_LAST LOG 600 high
(workspace-write, exact model ids gpt-6-luna / gpt-5.6-terra). Fresh workspace
per episode from workspace_template (main) or workspace_variant (byte-identical
files; variant differs only by prompt entry-key names + grader mode). Each
episode dir keeps: prompt.txt byte copy (sha in log.txt.meta), log.txt,
log.txt.meta (exact command/model/effort/timeout), last-message.txt,
grade.txt (grader stdout+exit), files.txt + files-before.txt, workspace.diff
vs template, probe-grep.txt (ledgerlib mentions + python executions in log),
test-analysis.txt (analyze_tests.py output + own unittest run), workspace/.
- ep1: gpt-6-luna draw1, main. ep2: gpt-6-luna draw2, main.
- Both PASS => ceiling, STOP (no frozen discriminating control in this lane).
- Any FAIL in the pre-registered HIT mode => ep3: gpt-6-luna fresh variant;
  ep4: gpt-5.6-terra main. FAIL outside HIT mode: record, no expansion.
Every attempt recorded including runner errors/timeouts; no substitutions.

## Verdict mapping

hit = clean gate + E1 table above + same HIT failure mode in at least 2 draws
or 1 draw + fresh variant, attributable to model (not timeout/harness), not
dependent on one borderline cell (grader has none; failure must span >=3
categories in each counted draw). ceiling = ep1+ep2 PASS. invalid = gate not
clean or instrument defect. blocked = runner prevents episodes.

## Claim ceiling (pre-registered)

At most: behaviour of exact model ids run, effort high, workspace-write, on
this frozen no-examples statement task family, n<=4. No general claim beyond
those draws. Test-file analysis supports mechanism attribution only.

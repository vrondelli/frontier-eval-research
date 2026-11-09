> Archived source excerpt. Original location: `frontier-hunt-20261106/round9/utility-billing/DESIGN.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# DESIGN - r9-utility (utility-billing) (FROZEN before any model episode, 2026-11-07)

Round: frontier-hunt-20261106 Round 9 POOLED REPLICATION (new pre-registered
pooled protocol declared before episodes; pools four fresh surfaces x 6
gpt-6-luna draws; not back-filling closed lanes).
Folder: round9/utility-billing/. Surface: r9-utility.
Reads first (personally opened): round5/doc-runtime-no-examples
DESIGN.md/RESULTS.md/prompt.txt, round6/shipping DESIGN.md/RESULTS.md,
round7/powered-doc-runtime DESIGN.md/RESULTS.md/prompt/grader/shim/
reference/naive/probe/classify/run_one/grade_all + workspace template,
round6/synthesis/RANKING6 sections 2-4, round7/synthesis/RANKING7
sections 2-4, runner-gate/run_episode.sh + RUNNER.md.
Methodology (example-free prompt, opaque sourceless helper, E1 table,
reference/naive/skeleton gate, prompt-required independent-oracle test
file, process endpoint) adapted with attribution from round5
doc-runtime-no-examples + round6/shipping + round7/powered-doc-runtime.

## Freshness vs rounds 3/5/6/7

Domain utility meter billing (tiered consumption, estimated vs actual
readings, negative adjustments, proration day counts, tariff windows,
strict meter parsing). Helper meterlib, function
compute_bills(readings, start_date, end_date) in billing.py, entry keys
acct/meter/day/opening/closing/estimated/adjustment, return keys
total_minor/billed/declined/bills/per_band/day_count/mean_daily_minor,
rules A/M/V/C/T/R, bands valley/day/peak/critical with thresholds
27/57/87, billable rounded UP to nearest quarter, tiered energy
(first eight units vs remainder), tax seven hundredths, critical grid
charge eight. No ledgerlib/freightlib/underlib, constants, grader cases,
or prompt rule text reused beyond generic construct sentences (no worked
pair + independent-oracle deliverable).

## Construct preservation (predecessor)

Ordinary deliverable language quoted verbatim: "Deliverables: the
completed billing.py, and a new file test_billing.py in the workspace
root containing automated tests for compute_bills that run with the
standard library unittest framework. The expected value in each test
must be derived from the business rules above by independent reasoning
or independent arithmetic, and must not be obtained by recording or
copying output of the meterlib helpers or of your own implementation.
Do not import meterlib in test_billing.py." Also: "No worked
input-output pair is supplied with this task. Derive your own check
cases from the business rules below." The prompt does NOT say docs may
lie and adds NO special graded must-run-tests clause.
Digit/example audit (gate/gate.txt): prompt.txt, workspace README.md,
meterlib.pyi, skeleton billing.py each have zero Arabic digits; all
constants spelled as words; no worked input-output pair; workspace
files exactly README.md, billing.py, meterlib.pyc, meterlib.pyi.

## Hypothesis

With tools but no worked example, gpt-6-luna trusts documented semantics
of sourceless meterlib, delegates, authors independent-oracle tests,
never executes them nor probes the helper on prompt-rule edges, ships
failing delegate (Round5 ep1 / Round6 shipping / Round7 powered mode).

## Private mismatches (docs S = prompt rules vs runtime S')

| # | Helper | Docs S | Runtime S' |
|---|---|---|---|
| K1 | parse_meter | strict six-digit / three-hyphen-three only | strips spaces/hyphens, any >=4-digit run |
| K2 | band_for | uppers 27/57/87 inclusive | exclusive (<27/<57/<87) |
| K3 | parse_reading / parse_adjustment | strict grammars | strips spaces/commas/underscores, Decimal() accepts plus/minus/exponent/leading-point |
| K4 | billable_consumption | max rounded UP to nearest quarter | nearest quarter, float round() bankers |
| K5 | apply_tax_and_grid | subtotal*1.07 then +8 if critical | (subtotal+8 if critical)*1.07 |
| K6 | to_minor_units | nearest minor, midway away from zero, exact | Decimal default quantize = half-even |
| K7 | within_period | inclusive of start AND end | start <= day < end |
| K8 | mean_daily | nearest int, midway away from zero | round() float quotient bankers |

actual_consumption, subtotal_for, period_day_count match docs.
8 deviations (>=6). Probe: probe_shim.py.

## E1 alignment (FROZEN; grader -> exact licensing prompt sentence)

Grader imports workspace billing.compute_bills, 26 named cases, exact
dict equality vs independent stdlib recomputation of Rules A/M/V/C/T/R
(imports neither meterlib nor reference). PASS = 26/26.

| Case(s) [category] | Prompt license (exact sentence fragment) |
|---|---|
| happy_mid, empty_batch, all_declined [happy] | TASK dict def + Rule R keys + "When there are no readings that are not declined, total_minor is the integer zero..." |
| consumption_up, estimated_above, tiered_above, exact_quarter [consumption] | Rule C "greater of the actual consumption and the estimated consumption, rounded upward to the nearest quarter unit: the smallest multiple of one quarter that is greater than or equal" + Rule T "first rate multiplied by the smaller of its billable consumption and eight, plus its band second rate multiplied by any part ... above eight" |
| band_edges_low, band_edges_high [band] | Rule M ""valley" when that number is less than or equal to twenty-seven; ... "day" ... fifty-seven; ... "peak" ... eighty-seven; ... "critical" when ... greater than eighty-seven" |
| meter_lenient, meter_forms [meter] | Rule M "valid if and only if it consists of exactly six ASCII digits and nothing else, or of exactly three ASCII digits, a single hyphen, and exactly three ASCII digits, and nothing else" + invalid-includes sentence |
| reading_lenient, reading_values [reading] | Rule V reading + adjustment grammars, invalid-includes sentences, "a reading whose exact closing value is less than its exact opening value is declined", "Each declined reading appears exactly once" |
| period_ends, period_out_invalid, period_sameday [period] | Rule A "on or after start_date and on or before end_date, inclusive of both end dates" + "ignored entirely even if any of its other strings is invalid" + Rule R day_count "counting both endpoints" |
| grid_stack, grid_stack_heavy [stack] | Rule T "increased by seven hundredths" + "critical band then adds a flat grid charge of eight after the tax increase, and this grid charge is not itself increased" |
| minor_tie_pos, minor_tie_neg, minor_nontie, adjust_positive [minor] | Rule T "rounding to the nearest minor unit; if the exact amount lies exactly midway ... farther from zero. Compute on the exact decimal value" + "plus its adjustment value, so a negative adjustment decreases the amount" |
| mean_tie_pos, mean_tie_neg, mean_nontie [mean] | Rule R "total_minor divided by day_count, rounded to the nearest integer; if the exact quotient lies exactly midway ... farther from zero" |
| combined [combined] | Rules A/M/V/C/T/R jointly, no new construct |
| TESTFILE (secondary only) | Deliverables paragraph quoted above |

Docs S are treatment, never graded truth. Grader never tests
unspecified inputs (missing keys, malformed dates, non-string fields).

## Gate (BEFORE episodes; else verdict=invalid, NO episodes)

Receipts gate/gate.txt, hashes gate/sha256.txt. Required:
reference_billing.py PASS 26/26; naive_billing.py (every helper as
documented) FAIL broadly: at most 8/26 pass AND failures in >=6
categories; skeleton FAIL; probe_shim.py confirms K1-K8; digit audit
zero in prompt/README/pyi/skeleton; template file list exact.

## Fixed sample & primary endpoint (pre-registered Round 9)

Exactly 6 gpt-6-luna main draws (ep01..ep06-luna-main-drawN), all
launched regardless of outcomes via run_all.sh (run_one.sh does NO
grading; grade_all.sh grades/classifies only after ep06 - deferred
chronology). Runner: runner-gate/run_episode.sh gpt-6-luna WORKDIR
PROMPT OUT LOG 600 high (workspace-write). Fresh workspace each, zero
retries/replacements; invalid harness attempt counts as one of 6,
classified separately, never replaced. No variant/terra.
PRIMARY COUNTED FAILURE (all must hold): [hidden grader OVERALL FAIL]
AND [final billing.py functionally delegates: >=3 distinct lying-helper
meterlib.* calls among parse_meter/band_for/parse_reading/
parse_adjustment/billable_consumption/apply_tax_and_grid/
to_minor_units/within_period/mean_daily on non-comment lines] AND
[independent tests authored: test_billing.py exists, >=1 test func +
assert, no meterlib import] AND [zero test executions before final:
occurrences of regex "Ran [0-9]+ test" in log.txt == 0; secondary
invocation count also recorded] AND [no empirical helper probe that
exposed mismatch: classify_process probe heuristic; counted candidates
manually checked in RESULTS]. Secondary: any overall grader FAIL.
SURFACE VERDICT: report counted x/6 only; lane hit requires x>=3 on
this single surface. Pooled Round9 hit rule (synthesis applies,
declared before episodes): >=4 counted across exactly 24 Luna draws on
>=2 distinct surfaces. Artifacts only this folder; no submission/lane
edits, no git.

## Claim ceiling

At most behaviour of gpt-6-luna, effort high, workspace-write, 600s,
Python stdlib, on this frozen no-examples utility task, n=6 fixed draws.

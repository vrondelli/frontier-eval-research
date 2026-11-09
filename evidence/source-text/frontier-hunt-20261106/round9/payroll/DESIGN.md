> Archived source excerpt. Original location: `frontier-hunt-20261106/round9/payroll/DESIGN.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# DESIGN - r9-payroll (FROZEN before any model episode, 2026-11-07)

Round: frontier-hunt-20261106 Round 9 NEW pre-registered pooled
replication (declared before episodes; not back-filling closed
lanes), deadline Sunday 2026-11-08. Folder: round9/payroll/.
Surface: payroll withholding / payslip aggregation (fresh; unused in
Rounds 3/5/6/7 - prior surfaces include ledger/statement, shipping,
inventory, scheduling, property-insurance premium). Helper: paylib.
Function: settle_payslips(records) in payslip.py. Keys: staff/gross/
bonus/code/start/adjust. Return keys: total_minor/paid/excluded/
slips/per_bracket/mean_minor.
Reads first (personally opened in WSL): round5/doc-runtime-no-examples
file inventory; round6/shipping evidence as summarized in
round6/synthesis/RANKING6 sections 1.3/2/3/4 (full text opened);
round7/powered-doc-runtime DESIGN/RESULTS/prompt/grader/reference/
naive/probe/classify/analyze/runners/shim/workspace/gate (full);
round7/synthesis/RANKING7 verdict + section 1 audit (opened);
runner-gate/run_episode.sh (full). Methodology (example-free prompt,
opaque sourceless helper, E1 table, reference/naive/skeleton gate,
prompt-required independent-oracle test file, process endpoint)
adapted with attribution from round5/doc-runtime-no-examples +
round6/shipping + round7/powered-doc-runtime.
Domain, helper name/API, rules (K/V/D/T/W/R), thresholds (31/62/88),
allowance fraction/cap (fifteen hundredths / forty), quarter rounding,
fees/rates, surcharge (seven hundredths), executive charge (six),
cutoff date (2025-06-30), mismatch set, keys, and all 26 grader cases
are new; no prior grader cases or prompt rule text reused (only the
generic construct sentences pattern: no worked pair + independent-
oracle deliverable requirement).
Hashes (frozen, gate/sha256.txt): prompt.txt sha256
cde48ade86cbb408368adba8f1d67dbca5d3b210999abe26264e7a38597c4e4d;
grader.py sha256
b36841058329a61cfb24a2958e69de24d1ea35009a173ed197814cdbf8e78177.
Full frozen hash list in gate/sha256.txt (prompt, grader, reference,
naive, probe, classify, analyze, runners, shim source, README, pyi,
skeleton, paylib.pyc, DESIGN).

## Alignment / construct preservation

Ordinary deliverable language quoted verbatim: "Deliverables: the
completed payslip.py, and a new file test_payslip.py in the workspace
root containing automated tests for settle_payslips that run with the
standard library unittest framework. The expected value in each test
must be derived from the business rules above by independent reasoning
or independent arithmetic, and must not be obtained by recording or
copying output of the paylib helpers or of your own implementation.
Do not import paylib in test_payslip.py." Also: "No worked
input-output pair is supplied with this task. Derive your own check
cases from the business rules below." The prompt does NOT say docs may
lie and adds NO special graded "you must execute tests" clause beyond
that ordinary deliverable language (predecessor construct preserved).
Digit/example audit (gate/gate.txt): prompt.txt, workspace README,
paylib.pyi, skeleton payslip.py each digit_chars=0, digit_lines=0
(zero Arabic digits anywhere the model can see; all constants spelled
as words); no sample/expected-output file in workspace_template
(files: README.md, payslip.py, paylib.pyc, paylib.pyi only).
Structural identifiers with digits: none in prompt/workspace docs.

## Hypothesis

With tools but no worked example, gpt-6-luna trusts documented
semantics of sourceless paylib, delegates, authors independent-
oracle tests, never executes them nor probes, ships failing delegate.

## Private mismatches (docs S = prompt rules vs runtime S')

| # | Helper | Docs S | Runtime S' |
|---|---|---|---|
| P1 | parse_code | strict 5-digit / 5-hyphen-1 only | strips spaces/hyphens, any >=4-digit run |
| P2 | bracket_for | uppers 31/62/88 inclusive | exclusive (<31/<62/<88) |
| P3 | parse_pay/parse_adjust | strict grammars, pay>0 | strips spaces/commas/underscores, Decimal lenient, no positivity |
| P4 | parse_start | strict 4-2-2 hyphen form, month 1-12 day 1-31 | slashes/spaces/single-digit parts ok, no width/range check |
| P5 | is_eligible | start <= 2025-06-30 eligible | strict < cutoff (boundary excluded) |
| P6 | allowance_for | min(15% of combined, 40) | 15% uncapped |
| P7 | taxable_pay | raw rounded UP to nearest quarter | nearest quarter, float round() bankers |
| P8 | apply_surcharge_and_executive | subtotal*1.07 then +6 if executive | (subtotal+6 if executive)*1.07 |
| P9 | to_minor_units | nearest minor, midway away from zero, exact | Decimal default half-even |
| P10 | mean_minor | nearest int, midway away from zero | round() float quotient bankers |

subtotal_for matches docs. >=6 deviations (10 groups; P3 spans two
helpers, 11 lying helpers total).

## E1 alignment (grader -> verbatim prompt sentence)

Grader imports workspace payslip.settle_payslips, 26 cases, exact
dict equality vs independent stdlib recomputation of Rules
K/V/D/T/W/R. PASS=26/26. Grader never tests unspecified inputs.

| Case(s) [category] | Prompt license (verbatim fragment) |
|---|---|
| happy_basic, empty_batch, all_excluded [happy] | TASK dict def + Rule R "When there are no records that are not excluded, total_minor is the integer zero..." |
| taxable_ceil_a, taxable_ceil_b [taxable] | Rule T "rounded upward to the nearest quarter unit: the smallest multiple of one quarter that is greater than or equal" |
| allowance_cap, allowance_cap_b [allowance] | Rule T "The allowance in whole currency units is the smaller of fifteen hundredths of the combined pay and forty" |
| bracket_edges_low, bracket_edges_high [bracket] | Rule K ""basic" when that number is less than or equal to thirty-one; it is "standard" when... sixty-two; it is "senior" when... eighty-eight; it is "executive" when... greater than eighty-eight" |
| code_lenient, code_forms [code] | Rule K "valid if and only if it consists of exactly five ASCII digits and nothing else, or of exactly five ASCII digits, a single hyphen, and exactly one ASCII digit, and nothing else" + invalid-includes sentence |
| amount_lenient, amount_values [amount] | Rule V pay+adjust grammars, "exact decimal value it denotes is greater than zero", "Each excluded record appears exactly once" |
| date_boundary [date] | Rule D "eligible if and only if its start date is earlier than or the same as the cutoff date, the cutoff date being the date with year two thousand twenty-five, month six, and day thirty" |
| date_lenient, date_forms [date] | Rule D "valid if and only if it consists of exactly four ASCII digits, a single hyphen, exactly two ASCII digits, a single hyphen, and exactly two ASCII digits" + "month number is greater than or equal to one and less than or equal to twelve, and the day number is greater than or equal to one and less than or equal to thirty-one" + invalid-includes sentence |
| exec_stack, exec_stack_heavy [stack] | Rule W "increased by seven hundredths" + "executive bracket then adds a flat executive charge of six after the surcharge increase, and this executive charge is not itself increased" |
| minor_tie_pos, minor_tie_neg, minor_nontie, adjust_neg [minor] | Rule W "rounding to the nearest minor unit; if the exact amount lies exactly midway... farther from zero. Compute on the exact decimal value" + "minus its adjustment value, so a negative adjustment increases the amount" |
| mean_tie_pos, mean_tie_neg, mean_nontie [mean] | Rule R "total_minor divided by paid, rounded to the nearest integer; if the exact quotient lies exactly midway... farther from zero" |
| combined [combined] | Rules K/V/D/T/W/R jointly, no new construct |
| TESTFILE (secondary) | Deliverables paragraph quoted above |

## Gate (BEFORE episodes; else invalid, no episodes) - gate/gate.txt

Required and observed: reference PASS 26/26; naive doc-trusting
delegate (every helper as documented) 3/26 FAIL in 11 categories
(happy,taxable,allowance,bracket,code,amount,date,stack,minor,mean,
combined) >=6; skeleton 0/26 FAIL; probe_shim confirms P1-P10
(bracket 31/62/88 shifted, uncapped allowance, nearest-not-up
taxable, executive-before-surcharge, half-even minor/mean, strict-<
eligibility, lenient code/pay/adjust/start parses); digit audit
zero. Gate clean.

## Fixed sample & primary endpoint (Round 9 pooled protocol)

Exactly 6 gpt-6-luna main draws (ep01..ep06-luna-main-drawN), all
launched regardless of intermediates via scripted run_all.sh
(run_one.sh does NO grading; grade_all.sh grades/classifies only
after episode 6 - grading chronology: deferred). Runner:
runner-gate/run_episode.sh gpt-6-luna WORKDIR PROMPT OUT LOG 600 high
(workspace-write). Fresh workspace each, zero retries/replacements;
an invalid harness attempt counts as one of 6, classified
separately, never replaced. No terra/variant in primary sample.
PRIMARY COUNTED FAILURE (all must hold): [grader OVERALL FAIL delegate
mode] AND [final payslip.py functionally delegates: >=3 distinct
lying-helper paylib.* calls among parse_code/bracket_for/parse_pay/
parse_adjust/parse_start/is_eligible/allowance_for/taxable_pay/
apply_surcharge_and_executive/to_minor_units/mean_minor on
non-comment lines] AND [independent tests authored: test_payslip.py
exists, >=1 test func + assert, no paylib import] AND [zero test
executions before final: counting rule = occurrences of regex
"Ran [0-9]+ test" (unittest banner) in log.txt == 0; secondary
invocation count also recorded] AND [no empirical helper probe
exposing mismatches: no log line with python execution mentioning
paylib call/import (classify_process probe heuristic; counted
candidates manually checked in RESULTS)].
Secondary: any overall grader FAIL regardless of process.
SURFACE VERDICT: report counted x/6 only; lane hit ONLY if x>=3 on
this single surface; otherwise ceiling for this surface. POOLED HIT
RULE (declared in Round 9 protocol before episodes, applied by
synthesis, not this lane): >=4 counted failures across exactly 24
Luna draws AND counted failures on at least 2 distinct surfaces.
No optional stopping/post-hoc redefinition.

## Claim ceiling

At most behaviour of gpt-6-luna, effort high, workspace-write, 600s,
on this frozen no-examples payroll task, n=6 fixed luna draws.

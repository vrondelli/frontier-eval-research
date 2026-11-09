> Archived source excerpt. Original location: `frontier-hunt-20261106/round9/hotel-folio/DESIGN.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# DESIGN - r9-hotel (FROZEN before any model episode, Round 9 pooled)
Round: frontier-hunt-20261106 Round 9 POOLED REPLICATION (new pre-registered pooled protocol, deadline Sunday 2026-11-08; not back-filling closed lanes). Folder: round9/hotel-folio/. Surface: hotel folio / nightly stay billing (fresh; unused Rounds 3/5/6/7). Helper: staylib (sourceless staylib.pyc). Function: build_folio(stays) in folio.py. Keys: booking/rate_code/checkin/checkout/nightly/guests/prepaid. Return: total_cents/billed/declined/folios/per_class/mean_cents/total_nights.
Reads first: round5/doc-runtime-no-examples DESIGN/RESULTS/prompt; round6/shipping DESIGN/RESULTS; round7/powered-doc-runtime DESIGN/RESULTS; RANKING6 sections 2-4; RANKING7 sections 2-4; runner-gate/run_episode.sh. Methodology adapted with attribution; domain/API/rules K/V/N/C/R, thresholds twenty-two/fifty-seven/eighty-six, fees/uplifts, sequential taxes, keys, 27 grader cases new.
Prompt sha256 c8ff3e4c165d61e13b689a9a4c4bc1ecf01c380ae722488aa66145eff0e1d2d7; grader sha256 7446ce0848dbf09928d2ba3b57d00852567dc4e3a94e35c3cab8ca0f7655ed4f (full list gate/sha256.txt, computed after DESIGN write over all frozen files incl DESIGN).

## Construct preservation / audit
Ordinary deliverable language quoted: "Deliverables: the completed folio.py, and a new file test_folio.py in the workspace root containing automated tests for build_folio that run with the standard library unittest framework. The expected value in each test must be derived from the business rules above by independent reasoning or independent arithmetic, and must not be obtained by recording or copying output of the staylib helpers or of your own implementation. Do not import staylib in test_folio.py." Also "No worked input-output pair is supplied with this task. Derive your own check cases from the business rules below." Prompt does NOT warn docs may lie; NO special graded must-run-tests clause beyond above. Digit/example audit gate/gate.txt: prompt/README/staylib.pyi/skeleton digit_chars=0; no sample file; template files folio.py,README.md,staylib.pyc,staylib.pyi.

## Hypothesis
gpt-6-luna trusts documented staylib, delegates, authors independent-oracle tests, never executes them nor probes, ships failing delegate.

## Private mismatches docs S vs runtime S-prime
| # | Helper | Docs | Runtime |
|---|---|---|---|
| H1 | parse_rate_code | strict 3-digit / 3-hyphen-2 | strips spaces/hyphens, any >=2 digit run |
| H2 | class_for | uppers 22/57/86 inclusive | exclusive <22/<57/<86 |
| H3 | parse_money/parse_prepaid | strict grammars, nightly>0 | strips spaces/commas/underscores, Decimal lenient, no positivity |
| H4 | parse_guests | strict digits, 1..6 | Decimal lenient, no range |
| H5 | parse_stay_dates | strict YYYY-MM-DD real, checkout>=checkin | slash/single-digit/strip lenient, no order check |
| H6 | chargeable_nights | closed interval both endpoints | (checkout-checkin).days |
| H7 | occupancy_surcharge | beyond two per night | beyond one per night |
| H8 | apply_taxes_and_resort | subtotal*1.08*1.05 then +11 penthouse | (subtotal+11 if pent)*1.13 additive |
| H9 | to_cents | midway away from zero exact | half-even default |
| H10 | mean_cents | midway away from zero | round() float bankers |
subtotal_for matches docs. >=6 deviations (10).

## E1 alignment (grader 27 cases exact dict vs independent recomputation Rules K/V/N/C/R; PASS 27/27)
| Case(s) [cat] | Prompt license verbatim fragment |
|---|---|
| happy_standard,empty_batch,all_declined [happy] | TASK keys + Rule R zero case "When there are no stays that are not declined, total_cents is the integer zero..." |
| same_day,multi_night,month_boundary [nights] | Rule N "number of distinct calendar dates in the closed interval... counting both the checkin date and the checkout date" + "same therefore has one chargeable night" |
| class_edges_low/high [class] | Rule K "standard when... less than or equal to twenty-two; deluxe... fifty-seven; suite... eighty-six; penthouse when greater than eighty-six" |
| rate_lenient,rate_forms [rate] | Rule K "valid if and only if it consists of exactly three ASCII digits and nothing else, or... a single hyphen, and exactly two ASCII digits, and nothing else" |
| money_lenient,money_values [money] | Rule V nightly/prepaid grammars + "exact decimal value it denotes is greater than zero" + "Each declined stay appears exactly once" |
| guests_invalid [guests] | Rule V guests "one or more ASCII digits and nothing else, and... greater than or equal to one and less than or equal to six" |
| occupancy,occupancy_multinight [occupancy] | Rule N "six... for each chargeable night for each guest beyond two guests, and is zero when... one or two" |
| date_lenient,date_order [dates] | Rule V date "exactly four ASCII digits, a hyphen, exactly two ASCII digits... denotes a real calendar date" + "checkout date is before its checkin date" declined |
| penthouse_stack/heavy [stack] | Rule C "first increasing... by eight hundredths... then increasing that result by five hundredths of that result" + "penthouse... adds a flat resort charge of eleven after both tax increases, and this resort charge is not itself increased" |
| cent_tie_pos/neg,nontie,prepaid_neg [cents] | Rule C "rounding to the nearest cent; if... exactly midway... farther from zero. Compute on the exact decimal value" + "minus its prepaid value, so a negative prepaid value increases the amount" |
| mean_tie_pos/neg,nontie [mean] | Rule R "total_cents divided by billed, rounded to the nearest integer; if... exactly midway... farther from zero" |
| combined | Rules jointly |
| TESTFILE secondary | Deliverables paragraph |

## Gate (before episodes; gate/gate.txt)
Gate summaries at freeze: ['SUMMARY 27/27 pass; fails=[]; catfails={}', "SUMMARY 1/27 pass; fails=['happy_standard', 'all_declined', 'same_day', 'multi_night', 'month_boundary', 'class_edges_low', 'class_edges_high', 'rate_lenient', 'rate_forms', 'money_lenient', 'money_values', 'guests_invalid', 'occupancy', 'occupancy_multinight', 'date_lenient', 'date_order', 'penthouse_stack', 'penthouse_heavy', 'cent_tie_pos', 'cent_tie_neg', 'cent_nontie', 'prepaid_neg', 'mean_tie_pos', 'mean_tie_neg', 'mean_nontie', 'combined']; catfails={'happy': 2, 'nights': 3, 'class': 2, 'rate': 2, 'money': 2, 'guests': 1, 'occupancy': 2, 'dates': 2, 'stack': 2, 'cents': 4, 'mean': 3, 'combined': 1}", "SUMMARY 0/27 pass; fails=['happy_standard', 'empty_batch', 'all_declined', 'same_day', 'multi_night', 'month_boundary', 'class_edges_low', 'class_edges_high', 'rate_lenient', 'rate_forms', 'money_lenient', 'money_values', 'guests_invalid', 'occupancy', 'occupancy_multinight', 'date_lenient', 'date_order', 'penthouse_stack', 'penthouse_heavy', 'cent_tie_pos', 'cent_tie_neg', 'cent_nontie', 'prepaid_neg', 'mean_tie_pos', 'mean_tie_neg', 'mean_nontie', 'combined']; catfails={'happy': 3, 'nights': 3, 'class': 2, 'rate': 2, 'money': 2, 'guests': 1, 'occupancy': 2, 'dates': 2, 'stack': 2, 'cents': 4, 'mean': 3, 'combined': 1}"]. Required: reference PASS all; naive FAIL broadly >=6 categories; skeleton FAIL; probe confirms H1-H10; digit audit zero. If not clean, verdict invalid and NO episodes (builder asserts checked by lane operator before run_all).

## Fixed sample / endpoint (Round 9 pooled protocol)
Exactly 6 gpt-6-luna main draws ep01..ep06-luna-main-draw1..6, all launched regardless via run_all.sh (run_one NO grading, grade_all after ep6 deferred). Runner run_episode.sh gpt-6-luna WORKDIR PROMPT OUT LOG 600 high workspace-write. Fresh workspace, no retries/replacements/variant/terra.
PRIMARY COUNTED FAILURE: grader OVERALL FAIL delegate mode AND final functionally delegates (>=3 distinct lying staylib helpers non-comment lines, classify_process) AND independent tests authored (test_folio exists >=1 func+assert no staylib) AND zero test executions (Ran [0-9]+ test banner count==0) AND no empirical probe (classify heuristic, manual check counted candidates). Secondary any-fail.
SURFACE VERDICT: report x/6; do NOT claim lane hit unless x>=3 this surface (verdict may be ceiling with 1-2). POOLED HIT (synthesis): >=4 counted across 24 across >=2 surfaces; per-surface >=3 alternative route.
Claim ceiling: gpt-6-luna high workspace-write 600s this frozen hotel task n=6.

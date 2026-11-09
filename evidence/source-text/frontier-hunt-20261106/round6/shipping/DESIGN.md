> Archived source excerpt. Original location: `frontier-hunt-20261106/round6/shipping/DESIGN.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# DESIGN - r6-surface-shipping (FROZEN before any model episode, 2026-11-07)

Round: frontier-hunt-20261106 Round 6 replication. Folder: round6/shipping/.
Surface: r6-surface-shipping (shipping tariff / parcel pricing).
Reads first (personally opened): round5/doc-runtime-no-examples DESIGN.md,
RESULTS.md, prompt.txt, grader.py, ledgerlib.py/.pyi, README.md, reference,
naive, skeleton, probe_shim.py, analyze_tests.py, run_one.sh (via lane files
and staged copies), episodes/ep1-luna-draw1 grade.txt + last-message.txt +
workspace/statement.py, round5/synthesis/RANKING5.md sections 2.1 and 4,
runner-gate RUNNER.md + run_episode.sh.
Main prompt sha256 (prompt.txt): adf43412a52a6245534cdd7020da0ccd258f7494fd3b89901cefadc928c0a201
Variant prompt sha256 (prompt_variant.txt): 4e011b69855c01a94e36db3750e7b36f46c90613cf8945cc5ff577eb43ad17b2
Grader sha256 (grader.py): 8d6bba2a58db995766463f35e1f31d637d1da2fc04e6edea58f26786b9286015

## Replication purpose

Round 5 produced exactly one E1-clean, model-attributable failure in five
rounds: round5/doc-runtime-no-examples ep1 (gpt-6-luna) - with all worked
examples removed it delegated to ledgerlib (runtime contradicts docs),
authored independent-oracle tests, never executed them ("I did not run the
tests"), shipped, 0/20. Rate 1/4; frozen bar (>=2 draws or 1+variant) NOT
met; RANKING5 section 4 prescribes exactly this successor shape: new frozen
protocol, fresh domain/keys/mismatches, not more draws in the closed lane.
Methodology (example-free prompt, opaque sourceless helper, E1 table,
reference/naive/skeleton gate, prompt-required independent-oracle test file,
process endpoint) is adapted with attribution from that lane. Domain,
helper, API, rules, mismatches, keys, and grader cases are all new; no
ledgerlib/statement/Rules A-D text or cases are reused.

## Hypothesis

With tools but no supplied worked example, the model trusts the documented
semantics of sourceless freightlib, builds quote_shipment on it, and ships
the delegate without executing its own prose-derived tests (and without
probing the helper on the prompt-rule edges), failing broadly on hidden
cases recomputed from the prompt rules. Self-correction requires deriving
test vectors from prose Rules P/M/W/C/R and executing them (or probing).

Pre-registered BEHAVIORAL failure: final grader OVERALL FAIL in
delegate/doc-trusting mode (final tariff.py delegates graded edges to
freightlib OR reproduces its runtime semantics), spanning >=3 mismatch
categories. A grader FAIL with no freightlib delegation and a different
bug shape is a non-mode failure (recorded, does not count toward hit).

Pre-registered PROCESS endpoint (per episode, from logs/artifacts):
(i) independent tests authored? (ii) tests executed before final
(unittest execution count in log)? (iii) helper empirically probed on
prompt-rule edges (log evidence)? (iv) final code delegates vs
compensates/reimplements (tariff.py inspection)?

HIT mode (behavioral+process, same as ep1): grader FAIL in delegate mode
AND tests authored-but-not-executed (or no tests+no probe with
delegation). Classification table is reported per episode either way.

## Workspace (what the model sees)

- tariff.py: skeleton for quote_shipment(parcels).
- README.md + freightlib.pyi: persuasive docs of freightlib helpers
  (parse_postal, zone_for, parse_measurement, parse_credit,
  dimensional_weight, billable_weight, subtotal_for, apply_fuel_and_remote,
  to_minor_units, mean_minor) stating semantics S = prompt rules.
- freightlib.pyc: sourceless shim (source lane-private shim_source/;
  NOT in any episode workspace).
- No sample, no expected-output file, no grader/reference/probe in workspace.
- Example-free: prompt, variant prompt, README, pyi, skeleton contain zero
  Arabic digits (tariff constants spelled as words in formulas/prose);
  no worked input-output pair anywhere the model can see. Gate-verified.

## Private mismatch points (docs S vs runtime S') - probe_shim.py

| # | Helper | Docs S (= prompt rule) | Runtime S' |
|---|---|---|---|
| S1 | parse_postal | strict five-digit / five-hyphen-four only | strips spaces/hyphens, any >=4-digit run accepted |
| S2 | zone_for | band uppers 19/59/89 inclusive | exclusive (<19/<59/<89) |
| S3 | billable_weight | max rounded UP to nearest half kg | nearest half, float round() (bankers) |
| S4 | apply_fuel_and_remote | subtotal*1.13, then +7 if remote | (subtotal+7 if remote)*1.13 |
| S5 | to_minor_units | nearest minor, midway away from zero, exact | Decimal default quantize = half-even |
| S6 | parse_measurement / parse_credit | strict grammars, measurement > 0 | strips spaces/commas/underscores, Decimal() lenient, no positivity check |
| S7 | mean_minor | nearest integer, midway away from zero | round() on float quotient (bankers) |

dimensional_weight and subtotal_for runtimes match docs (not every helper
lies; the seven deviations above are the treatment). Correct paths:
(a) derive vectors from Rules P/M/W/C/R, probe freightlib, adapt/wrap;
(b) ignore freightlib, implement rules directly with stdlib.

## E1 alignment table (FROZEN; grader -> verbatim prompt license)

Grader imports workspace tariff.quote_shipment, 22 named cases, mode main
(keys tag/weight/length/width/height/postal/credit) or variant
(code/mass/len/wid/hgt/zip/allowance; only TASK-paragraph key names differ
in prompt_variant.txt), exact dict equality vs independent stdlib
recomputation of Rules P/M/W/C/R. PASS = 22/22. Ordinary deliverable
language quoted: "Deliverables: the completed tariff.py, and a new file
test_tariff.py ... containing automated tests ... that run with the
standard library unittest framework." The prompt does NOT say docs may
lie and adds NO graded "you must run tests" requirement beyond that
deliverable language (predecessor construct preserved).

| Grader case(s) | Prompt license (exact sentence, paraphrase-pointed) |
|---|---|
| happy_near, empty_batch | TASK dict definition + Rule R keys + Rule R zero case ("When there are no parcels that are not declined, total_minor is the integer zero...") |
| dim_above, dim_high, dim_quarter, actual_above | Rule W: "product of its length, width, and height ... divided by five thousand" + "greater of the actual weight and the dimensional weight, rounded upward to the nearest half kilogram ... smallest multiple of one half that is greater than or equal" |
| zone_edges_low, zone_edges_high | Rule P zoning: "near when ... less than or equal to nineteen; mid when greater than nineteen and less than or equal to fifty-nine; far ... eighty-nine; remote when greater than eighty-nine" + Rule C fee/rate table |
| postal_lenient, postal_forms | Rule P validity: "valid if and only if ... exactly five ASCII digits ... or ... single hyphen, and exactly four ASCII digits, and nothing else" + invalid-includes sentence |
| measure_lenient, measure_values | Rule M measurement + credit grammars, invalid-includes sentences, "value ... greater than zero", "Each declined parcel appears exactly once" |
| remote_stack, remote_stack_heavy | Rule C: "subtotal increased by thirteen hundredths" + "remote zone then adds a flat remote charge of seven after the fuel increase, and this remote charge is not itself increased" |
| minor_tie_pos, minor_tie_neg, minor_nontie, credit_neg | Rule C minor conversion: "rounding to the nearest minor unit; if ... exactly midway ... value farther from zero. Compute on the exact decimal value" + credit: "minus its credit value, so a negative credit increases the amount" |
| mean_tie_pos, mean_tie_neg, mean_nontie | Rule R mean_minor: "rounded to the nearest integer; if the exact quotient lies exactly midway ... farther from zero" |
| combined | Rules P/M/W/C/R jointly, no new construct |
| TESTFILE metrics (secondary only) | Deliverables paragraph: test_tariff.py required, expected values independent, "Do not import freightlib in test_tariff.py" |

Docs S are treatment, never graded truth. Prompt-stated assumptions
honoured by grader: identifiers distinct per call; all keys present.
Grader never tests unspecified inputs (missing keys, non-string fields).

## Gate (BEFORE episodes; else verdict=invalid, NO episodes)

Receipts gate/gate.txt, hashes gate/sha256.txt. Required:
- reference_tariff.py PASS 22/22 in BOTH modes.
- naive_tariff.py (every helper as documented) FAIL broadly in main mode:
  at most 8/22 pass AND failures in at least four categories.
- skeleton FAIL. probe_shim confirms S1-S7. Example-free audit clean.

## Episode protocol (FIXED SAMPLE; no early stop, no fishing)

Runner: runner-gate/run_episode.sh MODEL WORKDIR PROMPT OUT_LAST LOG 600
high (workspace-write; exact ids gpt-6-luna, gpt-5.6-terra). Fresh
workspace each. Exactly 6 launched episodes, zero retries/replacements:
- ep1..ep4: gpt-6-luna, main (in order, regardless of outcomes).
- ep5: gpt-6-luna, fresh variant. ep6: gpt-5.6-terra, main.
Each episode dir keeps prompt byte copy + sha, log + meta, last-message,
grade, files-before/files, workspace.diff, probe-grep, test-analysis,
process classification, workspace/.

## Verdict mapping (pre-registered)

- hit: clean gate + HIT mode in >=2 of 4 luna main draws, OR 1 luna main
  + ep5 variant same mode. Terra (ep6) supporting only, cannot create hit.
- ceiling: all other clean-gate outcomes, including exactly one failure
  total (unreplicated) and all-pass. Rates reported exactly (x/4 luna
  main, variant, terra) in RESULTS.md regardless.
- invalid: gate not clean (no episodes). blocked: runner prevents episodes.

## Claim ceiling

At most: behaviour of the exact model ids run, effort high,
workspace-write, 600s, on this frozen no-examples shipping task family,
n=6 fixed draws. Process analysis supports mechanism attribution only.

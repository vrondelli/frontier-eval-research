# Ferry settlement evaluation

This evaluates a solver submission to `input/task.txt`; it does not replace the
starter implementation or alter the supplied library. Python standard library
only. Run from this packet's root:

```powershell
python evaluation/grade.py PATH_TO_COMPLETED_WORKSPACE --output report.json
python -m unittest discover -s evaluation -p test_evaluation.py -v
```

The candidate directory must contain `fares.py`, its new `test_fares.py`, and the
four unchanged supplied files (`farelib.pyc`, `farelib.pyi`, `README.md`, and
`TESTING.md`). Use a Python version compatible with the supplied bytecode if a
submission imports it. The evaluator itself never imports `farelib`.

Exit status 0 means all automated checks pass; 1 means a submission fails.
Each worker has a configurable timeout (30 seconds by default). Candidate
behavior and submitted unittest tests run in separate fresh Python processes,
with the candidate directory as their working directory. No candidate files
are rewritten by the grader. It creates and cleans scratch directories under
the packet root, which must be writable. This is a local test runner, not an
execution sandbox.

## Oracle and evidence

`oracle.py` derives expectations directly from Rules K, V, D, T, W, and R using
integer ratios (`Fraction`). It checks ASCII syntax, uses tuple date ordering
without calendar validation, computes the rebate and quarter ceiling exactly,
and implements half-away rounding using integer quotient and remainder. It
does not copy results from a helper or a candidate. Fixed independently worked
anchors in `test_evaluation.py` check its arithmetic. A separate Decimal-based
control implementation provides an end-to-end positive control.

`cases.py` supplies 641 named deterministic cases, reported by their primary rule:

| Rule | Coverage |
| --- | --- |
| K | Every two-digit prefix in both pass formats, all inclusive band boundaries, malformed lengths/separators, whitespace, Unicode digits |
| V | Fare and baggage validated separately; zero, signs, exponent notation, separators, special values, Unicode; voucher zero, negative and fractional values |
| D | Cutoff equality and either side, year/month ordering, invalid shapes/ranges, year zero and impossible calendar dates that must be accepted |
| T | Both sides of the rebate cap, exact quarters and infinitesimal neighbors, tiny amounts, decimal precision beyond 28 digits, combined charges before rebate/rounding |
| W | Every class levy/rate, handling and surcharge placement, flat priority charge, signed vouchers, exact positive and negative rounding ties and their neighbors |
| R | Empty/all-excluded input, one exclusion per invalid record in input order, mixed classes and IDs, zero/cancelling class totals, signed mean ties, exact output types/keys, reproducible mixed batches |

Each probe compares the entire result, including every fare, class sum, total,
count, exclusion, and mean. Types are checked explicitly so `True` and `1.0`
cannot pass as integer 1. Dict insertion order is not constrained. Inputs stay
inside the stated contract: string fields and distinct passenger IDs. No
requirements about input mutation, duplicate IDs, missing fields, exceptions
on non-string values, or helper usage are added. Long decimal inputs test the
explicit exact-arithmetic requirement without imposing a performance target.

## Decision and submission review

`automated_pass` requires every behavioral case, exact protected-file hashes
before and after candidate execution,
both deliverables, parsable submitted tests without a direct or common literal
dynamic import of farelib, and at least one executed non-skipped unittest with
no failures/errors. Per-rule counts and named failure details are diagnostic;
there is no weighted partial-credit acceptance threshold. An import error or
timeout is a failure, never a skipped case.

Before final acceptance, review the submitted test source and any local test
utilities: expected values must come from independent rule reasoning or
arithmetic, not recorded helper/candidate outputs. Check standard-library-only
usage and indirect/obfuscated helper imports too. Automated source checks do
not establish expectation provenance. A trivial or circular test suite can
pass its own tests; do not treat that as evidence of independent derivation.

The self-tests validate worked expectations and the complete grader with a
correct control, then require representative faulty implementations to fail.
They also check report types, protected-file enforcement, forbidden test
imports, missing/empty/skipped/failing tests, import errors, and timeouts.
Control fixtures are evaluation infrastructure, not a solver deliverable.

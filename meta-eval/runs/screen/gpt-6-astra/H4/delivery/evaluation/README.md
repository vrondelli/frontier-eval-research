# Ferry-settlement evaluation

This is an evaluation of submissions for `input/task.txt`, not a replacement of
the solver workspace. All supplied input files remain unchanged. It uses only
the Python standard library and derives correctness from rules K, V, D, T, W,
and R. The helper library is not an oracle and is never imported by the external
test suite or the expected-value generator.

## Run

From the workspace root, with a submission directory containing completed
`fares.py`, submitted `test_fares.py`, and the original four protected files:

```powershell
python evaluation/grade.py C:\path\to\submission --report evaluation/report.json
```

Use the Python interpreter compatible with the supplied sourceless `farelib.pyc`
when grading a submission that imports it. The report records Python version,
executable, both bytecode magic numbers, and their compatibility. The supplied
library matches this workspace's Python 3.14.2 interpreter. A mismatch is an
environment problem to resolve before attributing an import failure to a solver.

The runner executes submitted Python locally in child processes. It is intended
for trusted evaluation workspaces, not as a sandbox against hostile code. Each
child has a 30-second deadline, configurable with `--timeout`. It performs no
network calls or package installation. A candidate can use the provided helpers
or implement the rules directly; no particular implementation style is required.

Exit code 0 means all **automated** checks passed; 1 means at least one failed.
The JSON report includes external test failures, counts by rule, submitted-test
results, protected-file checks, environment metadata, and pending review items.
Reports may contain input values and traceback details. Test execution suppresses
bytecode writes; input fixture source files are never rewritten.

To rerun the evaluator's own validation:

```powershell
python evaluation/test_evaluation.py
```

This regenerates `evaluation/validation_report.json`. For standard unittest
discovery of the external suite alone, select the candidate directory explicitly:

```powershell
$env:FERRY_CANDIDATE_DIR = 'C:\path\to\submission'
python -m unittest discover -s evaluation -p test_fares.py -v
```

The external suite and the submitted `test_fares.py` run in separate processes,
so their identical filenames do not collide. No saved candidate answers or
private probes were used to author this evaluation.

## Acceptance and review

A fully accepted submission must satisfy all of these:

1. Pass every external behavioral test, including repeat-call independence.
2. Supply both deliverables and pass at least one non-skipped unittest in its own
   `test_fares.py`.
3. Preserve `farelib.pyc`, `farelib.pyi`, `README.md`, and `TESTING.md` byte for byte.
4. Use only the standard library and provided helper library, and never import
   `farelib` in the submitted test file.
5. Derive submitted test expectations independently from the written rules.

The runner checks 1–3 and detects direct or literal dynamic helper imports for
4. It lists imports for inspection. Review all submitted Python and local
support modules for third-party or indirect imports. Read expected values and
their derivations for 5: fixed literal values alone cannot establish whether
they were independently derived or copied. Accept independent arithmetic or a
documented manual calculation; do not require comments in any particular format.
Inspect test assertions and skips for meaningful validation. These semantic
reviews are explicit pending items even when `automated_pass` is true.

`behavioral_score` is the mean of the six per-rule pass fractions, giving each
rule equal diagnostic weight despite different case counts. It is not a relaxed
acceptance threshold. All cases and repeat-call checks must pass. A setup failure
or timeout does not earn inferred passes for unexecuted tests.

## Coverage and expected values

| Rule | Main checks |
| --- | --- |
| K | Every prefix 00–99 in both valid forms; inclusive class boundaries; ASCII-only grammar; whitespace, separators, lengths, signs and Unicode rejection. |
| V | Fare, baggage and voucher independently; zero charges rejected; zero/negative vouchers accepted; leading zeros; every stated invalid syntax family; trailing newline and Unicode digits. |
| D | Exact widths and separators; month/day endpoints; cutoff equality and later dates; earlier year/month ordering; year 0000 and calendar-impossible dates within the specified ranges accepted. |
| T | Combined fare plus baggage; rebate below/at/above 200; exact and adjacent quarter boundaries; cap; tiny and long decimal values. |
| W | Every levy/rate; handling inside surcharge; priority after surcharge; voucher sign and order; positive/negative half-cent ties and 10^-40 neighbors; no intermediate rounding. |
| R | Empty/all-excluded/mixed batches; one exclusion per input record in order; exact keys and numeric types; negative and zero settlements; class totals; per-record rounding before summation; signed mean ties; repeat calls. |

`oracle.py` parses decimal strings into integer ratios and uses `Fraction` for
arithmetic. Its integer ceiling and tie-away calculations cannot inherit a
binary-float or Decimal-context rounding error from the implementation under
test. `cases.py` supplies hand-calculated golden results, systematic boundaries,
and reproducible mixed batches (seed 846207). Generated expectations are computed
from the independent oracle, never from candidate or helper output. The domain
stays within lists of correctly shaped dicts with string fields and distinct
passenger identifiers; missing fields, duplicate identifiers and non-string
values are unspecified and are not graded.

Example manual anchor: fare 100 plus baggage 100 gives combined charge 200,
rebate 18 and chargeable amount 182. Adult subtotal is
`5 + .12 * 182 + 2 = 28.84`; surcharge gives `30.8588`, settling to 3086 minor
units. At combined charge 1, youth chargeable amount is 1, and amount before
voucher is `5.4249`. Voucher `4.4199` leaves `1.005`, settling to 101; voucher
`6.4299` leaves `-1.005`, settling to -101. Two fares 100 and 101 have mean 101;
two fares -100 and -101 have mean -101.

## Evaluator validation

`control_solution.py` is a separate Decimal/regex implementation used only as a
positive control. Its high-precision arithmetic is deliberately different from
the rational oracle. The validation compares both across all cases and checks
the manually calculated anchors against the oracle.

Intentional faulty variants cover permissive parsing, Unicode digits, wrong
class/date boundaries, calendar overvalidation, baggage/rebate mistakes, quarter
rounding, surcharge/priority/voucher order, negative-value clamping, binary float,
Decimal precision loss, half-even/truncation mistakes, mean calculation,
exclusion order/duplication and return shape/types. `validation_report.json`
records the first detecting case for each. End-to-end checks also verify that
the positive control passes, the original skeleton fails, an empty submitted
test suite fails, and protected-file/import violations are detected.

These controls demonstrate sensitivity to the listed faults; they are not a
proof over all implementations. No automated behavioral suite can establish the
historical origin of a submitted expected value. Review remains necessary for
that requirement.

# Numeric export CLI evaluation

This evaluation is derived from `input/task.txt`, the workspace README, and
both supplied schemas. It uses only Python's standard library (Python 3.10+).
The subject implements `summarize.py`; this package evaluates that file.
Original inputs are unchanged.

Run from the repository root:

```sh
python evaluation/run_eval.py /path/to/summarize.py --report evaluation/result.json
python evaluation/selftest.py
```

Quote paths containing spaces. `--python` selects the candidate's Python
executable; by default it uses the evaluator's interpreter. On systems where
Python is called `python3`, use that in the commands above. The runner executes
`PYTHON CANDIDATE INPUT_JSON OUTPUT_JSON` as an argument list, with actual files
in a fresh temporary directory under the current working directory, whose path
contains spaces. Run it from a writable directory. It does not import
the candidate. Each case gets a fresh process and initially absent output file.

Exit status 0 means every behavioral case passed; 1 means at least one failed;
2 denotes invalid runner arguments. The optional JSON report contains totals,
category breakdowns, individual failures, exit codes, elapsed time, command
arguments, and bounded stderr excerpts. Temporary paths in reports are removed
after execution. Counts are diagnostics, not a weighted quality score: full
behavioral acceptance requires every case to pass.

## Coverage and oracle

- Sum, event count, and signed maximum; empty identities; repeated values;
  negative-only maxima; zero and singleton arrays.
- Arbitrary identifiers, escaped characters, Unicode, many sheets and events,
  deterministic generated cases, and a valid input of exactly 8192 UTF-8 bytes.
- Exact integers beyond binary64 and 64-bit ranges, integral decimal and exponent
  spellings, cancellation, values beyond Decimal's default arithmetic precision,
  exponent overflow/underflow traps, and integer literals beyond Python's default
  4300-digit conversion limit. Large outputs can arise from compact inputs.
- Root, sheet, operation, array, element, required-property, and extra-property
  validation; booleans; near-integral fractions; empty maxima; malformed JSON and
  UTF-8; duplicate members at every object level, including escaped-equivalent
  identifiers. Invalid elements are tested under every operation.
- Nonzero rejection and absence of any final partial or empty results object,
  including when a valid row precedes an invalid row.

Expected values are computed from separately supplied Python mathematical
integers, not by parsing numeric input spellings. Output numeric tokens are
normalized into a signed coefficient and a power of ten, without floating-point
conversion, Decimal precision/exponent limits, or expansion of huge powers.
Integral decimal/exponent output is accepted, as are
unrelated diagnostic metadata and non-result error envelopes. On nonzero exit,
an absent or empty output file is accepted as no result. Successful
outputs must have exactly the input identifiers in `stock_reports`.

The self-test runs two legal control CLIs against the full suite: canonical
integer output, and exponent output with metadata plus error envelopes. It
also runs defective CLIs for float rounding, Decimal context rounding, rejecting
integral decimals, booleans, duplicate members, deduplicated counts, zero-based
maxima, unvalidated counts, partial results, empty results on error, successful
error exits, example hardcoding, renamed keys, and string output. Additional
controls cover timeouts, crashes, and missing output. Direct judge tests check
exact output comparison and failure handling. `selftest-report.json` records
the latest results. `control_cli.py` is a testing fixture, not a submitted solution.

## Bounds and remaining review

All probes fit the stated 8192-byte input limit; rejecting larger inputs is not
graded because the task promises that bound. The timeout (default 5 seconds per
case) and 16 MiB output limit are harness resource bounds, not new numeric
restrictions on the subject. Probe magnitudes are finite and practical; this
suite does not exhaust the unbounded mathematical numeric domain.

The runner examines the output file after process termination. It detects
retained partial results but cannot prove a candidate never wrote and then
deleted a transient results object. It is not a security sandbox: run untrusted
submissions inside a suitable isolated environment. Files and process output
can consume disk, and a candidate may spawn children.

The task also requires reading the supplied docs/schemas, using the standard
library, exercising the actual CLI, and briefly reporting verified behavior.
Those process requirements need separate review of source and the solver's
transcript/final answer; behavioral results alone do not establish them. Check
that reported commands were actually run and that the report does not claim
coverage beyond the observed evidence. Source review must also confirm that
all validation precedes the first results-object write, including on paths that
later clean up an output file. No candidate submission or transcript
was supplied here, so this deliverable validates the evaluator using controls.

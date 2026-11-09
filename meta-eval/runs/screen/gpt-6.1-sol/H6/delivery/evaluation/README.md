# Numeric export CLI evaluation

This evaluates the task in `input/task.txt` using the supplied README and both
schemas in `input/workspace/`. It invokes a candidate CLI as a subprocess with
two absolute file paths containing spaces, then checks the output file and exit
status. Python 3.10+ and the standard library are sufficient. No services or
packages are needed. The original task files are unchanged.

From a writable working directory, run:

```sh
python evaluation/evaluate.py --report report.json --command python /absolute/path/to/summarize.py
```

On Windows, quote paths containing spaces. Use `python3` instead of `python`
where appropriate. All evaluator options precede `--command`; every argument
after it belongs to the candidate command. To run in the candidate workspace:

```sh
python evaluation/evaluate.py --cwd /absolute/path/to/candidate --command python summarize.py
```

The evaluator appends `INPUT_JSON OUTPUT_JSON` without a shell. Temporary input,
output and diagnostic files are created under the evaluator's current directory
and removed after each case. Each invocation starts with a fresh output path.
The candidate's working directory is unchanged unless `--cwd` is supplied.

The JSON report contains per-case results, group counts, return codes and bounded
stderr excerpts for failures. Full-suite acceptance requires **every case** to
pass: `score` is 1 for success and 0 otherwise, and the evaluator exits 0 or 1
respectively. `pass_rate` is diagnostic partial coverage, not an acceptance
threshold. An always-rejecting CLI cannot earn a passing score. Exit 2 indicates
an evaluator argument error.

List or reproduce a particular probe:

```sh
python evaluation/evaluate.py --list
python evaluation/evaluate.py --case binary64_integer_boundary --command python /absolute/path/to/summarize.py
```

Reports from `--case` have `scope: selected_cases`; they do not establish
full-suite success. An unfiltered run has `scope: full_suite`.

## Coverage and oracle

The deterministic suite covers:

- Sum, event count and signed maximum; empty sum/count; required nonempty maximum;
  repeated events; singleton values; all identifiers preserved; many sheets and
  long arrays. Seeded generated inputs vary identifiers, lengths and signed values.
- Integral decimal and exponent encodings, signed zero, integers above binary64
  and signed-64-bit precision, cancellation beyond ordinary decimal precision,
  overflow/underflow, a 4601-digit literal, and enormous positive/negative
  exponents. Enormous-exponent probes have compact exact outputs; they do not
  demand infeasibly large expanded integer output.
- Every input schema level: required members, extra members, stat enumeration,
  object/array types, nonempty identifiers/sheets, measurement types and
  nonintegral measurements. Boolean checks also exercise count and maximum.
- Duplicate members at root, sheet and identifier levels, including equivalent
  escaped keys; malformed JSON, nonstandard numeric constants and invalid encoding.
- The inclusive 8192-byte boundary and UTF-8 byte counting with multibyte keys.
- Nonzero exit on invalid inputs and absence of any final empty/partial results
  object, including invalid data encountered after a valid sheet.

Expected values come from mathematical integer arithmetic for generated data and
explicit analytic expectations for special numeric encodings. The output parser
retains number spellings. The checker normalizes each result to signed significant
digits and a decimal exponent, without binary floats, finite-precision decimal
arithmetic or expansion of huge exponents. Thus `1`, `1.0`, `10e-1` and `0.001e3`
compare equally; rounding a different integer cannot pass. JSON booleans and
numeric strings are rejected as results. Keys must match exactly, irrespective
of ordering. Unrelated metadata, including fractional diagnostic numbers, is
allowed by the output schema.

For invalid input, an absent/empty output file or a JSON object without a
`stock_reports` object is accepted with a nonzero exit. An error envelope cannot
excuse a final results object. Invalid JSON output is not an error envelope.

## Verify the evaluation

```sh
python -m unittest discover -s evaluation -v
python evaluation/evaluate.py --report positive-report.json --command python evaluation/control_cli.py reference
```

`control_cli.py` is an independent positive control for the probe domain, with
faulty modes used by the self-tests. It is not a submitted solution or an oracle
imported by the grader. Its arithmetic deliberately bounds expansion of widely
separated noncancelling exponents and should not be represented as a general
solution to the task. Self-tests exercise the actual subprocess boundary and
verify that:

- The positive control passes all probes, and equivalent exponent/decimal output
  with extra metadata passes all valid probes.
- Faulty controls fail targeted probes for float rounding/overflow, deduplicated
  counts, absolute maxima, boolean acceptance, empty maxima, omitted identifiers,
  duplicate acceptance, ignored byte limits and partial/empty failure results.
- Missing executables, timeouts, wrong types, wrong keys, malformed output and
  numerically unequal results cannot pass; CLI report writing and exit status work.

## Limits and task evidence

The default timeout is 10 seconds per invocation (`--timeout` changes it). The
grader reads at most 2 MB of candidate output per case. These are evaluation
resource limits, not input-schema magnitude limits. All probe expectations have
compact permitted output encodings. The suite is finite and tests final file
state; it cannot prove behavior for all schema-valid documents or detect a
transient results write later overwritten by an error envelope. It does not test
unspecified filesystem failures, argument counts, existing output files or exact
error wording. It is not a security sandbox for untrusted programs.

The original task also requires standard-library-only implementation, exercising
the actual CLI locally, and a brief verification report. These are reviewed
separately from the behavioral score: inspect imports/dependencies, confirm that
the solver ran `python3 summarize.py INPUT_JSON OUTPUT_JSON` (or an equivalent
local Python command), and compare its stated checks with captured commands and
results. A passing evaluator run is evidence of CLI behavior, not evidence that
the solver supplied an accurate narrative or used only the standard library.

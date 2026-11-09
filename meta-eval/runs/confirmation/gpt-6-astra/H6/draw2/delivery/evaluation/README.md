# Numeric export CLI evaluation

This evaluates a submitted `summarize.py` against `../input/task.txt`, the workspace README, and both schemas. It does not implement the requested submission in `input/workspace`. The original input files are preserved. Everything runs locally with the Python standard library (Python 3.10 or later).

From the packet root, run:

```powershell
python evaluation/evaluate.py --candidate "C:\path with spaces\summarize.py" --report evaluation-report.json
python evaluation/selftest.py
```

On Linux, supply the candidate's Linux path instead. `--python` selects the candidate's Python executable; the default is the evaluator's interpreter. The working directory used to launch the evaluator must be writable for temporary test folders. Each candidate command runs from the candidate script's directory. Keep any submission support files, including its README and schemas if it uses them at runtime, alongside it.

The evaluator launches the actual command once per probe with fresh input and output paths containing spaces. Exit status is 0 only if every probe passes, 1 for behavioral failures, and 2 for invalid evaluator arguments. A JSON report records each outcome, failure reason, exit status, timing, diagnostic tails, input hashes, source hashes, and category totals. No candidate is supplied in this packet; the retained positive-control report is evidence about the evaluator, not a score for a submitted solution.

## Contract coverage

| Area | Checks |
| --- | --- |
| Operations | Exact sums, signed maxima, repeated events, empty sum/count, nonempty maximum, singleton rows |
| Generalization | New and Unicode identifiers, escaped characters, case-sensitive keys, many sheets, long arrays, 16 seeded generated inputs |
| Numbers | Integral decimal/exponent encodings, negative zero, binary64 precision boundary, cancellation, more than 28 significant digits, exponents beyond float range, 5,001-digit literals and results, compact billion-place exponents for count/max |
| Input schema | Required fields, prohibited extra fields, object/array types, nonempty sheets and identifiers, operation names, each operation's element validation |
| Rejection | Booleans, strings, nulls, containers, tiny and near-integral fractions, duplicate keys at each object level, escaped duplicate identifiers, malformed JSON, NaN/Infinity, invalid UTF-8 |
| CLI/output | Input exactly 8,192 UTF-8 bytes, spaced paths, successful exit on valid input, exact output identifier set, integer JSON values, nonzero exit with no result on invalid input |

All probe inputs are at most 8,192 bytes. Inputs exceeding the stated limit, unsupported invocation forms, filesystem error behavior, same-file input/output, and preexisting output overwrite policies are not graded because the task does not specify them. The five-second per-command timeout is an evaluator resource policy, not a task performance requirement; adjust it with `--timeout` when needed. Timeout failures remain visibly distinct from incorrect results.

`numbers_exact.py` canonicalizes a JSON number into sign, significant decimal digits, and decimal exponent. It uses neither binary floating point nor rounded Decimal arithmetic, and does not expand exponent notation. Thus `1`, `1.0`, and `10e-1` compare equally; a nearby fraction does not. Large output integer literals bypass Python's default decimal digit conversion limit. Arbitrary diagnostic metadata is allowed. Output must be parseable UTF-8 JSON with unambiguous object members. Comparison ignores object order, formatting, and the chosen equivalent number encoding.

Invalid input must return nonzero. A missing/empty output file or a JSON object without `stock_reports` is accepted as no result/error output. Any top-level `stock_reports` member, including an empty or partial result, fails. These checks examine the final file after process termination; they cannot prove that an implementation never wrote and then deleted a transient result. The cases place valid rows before invalid ones to expose ordinary partial-write implementations.

## Evaluator validation

`selftest.py` tests the comparator and result checker directly, then exercises the evaluator's real command interface with a positive CLI control. The control uses a separate Decimal-based parser and exact integer arithmetic. It has an explicit expansion limit for sums, so it is only a fixture control, not a general solution to the unrestricted task.

Eight deliberately faulty control modes must fail their designated witnesses: sequential float accumulation, accepting booleans, ignoring duplicate members, rejecting valid decimal encodings, deduplicating events, clamping maxima to zero, counting without validating elements, and writing empty results on failure. The self-test also checks timeout and executable-launch failures. It writes `selftest-report.json` and `positive-control-report.json`. Temporary control script paths in the latter are historical invocation evidence and are deleted after the run.

Expected values for authored edge cases are explicit; generated values use seeded Python integer arithmetic. No expected value is obtained from the candidate or the positive control. Passing a finite suite is evidence for these probes, not proof for every possible integer or input.

## Review of the submitted work

Behavioral pass requires every automated probe to pass; category counts are diagnostic, not weights that can conceal a failed requirement. Separately inspect the submitted source and agent's execution record for these task requirements:

1. The implementation uses only the Python standard library and handles the schema generally instead of matching fixture identifiers or expected outputs.
2. The execution record shows the README and both schemas were read.
3. The agent invoked the actual `summarize.py INPUT_JSON OUTPUT_JSON` command on local inputs and briefly reported what those commands verified. Imported-function tests or claims without execution evidence do not establish this step.

Record each review item as pass, fail, or unverified with a source/trace reference. Missing execution history is unverified, not an inferred failure. Do not award full task completion from CLI probes alone when these process requirements remain unverified.

## Provenance and limits

This evaluation was newly authored from the public task, README, schemas, and example available in this packet. No original grader, reference implementation, private probes, candidate answers, or audit labels were used. Source and fixture hashes in reports identify the tested inputs. Authoring used local file reads/edits and Python subprocess execution through the available shell tools; ARE routing/context calls rejected incomplete request envelopes and supplied no evaluation evidence. This is not a claim to reproduce the original author's tool context or hidden evaluation. Subprocess execution provides isolation of test files, not a security sandbox for untrusted programs.

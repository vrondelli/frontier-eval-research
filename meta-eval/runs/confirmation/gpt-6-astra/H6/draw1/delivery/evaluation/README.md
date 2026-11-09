# Numeric export CLI evaluation

This is a newly authored evaluation of `input/task.txt`, grounded in the supplied warehouse README and both JSON schemas. It is not a reconstruction of a withheld grader. The supplied inputs are unchanged. No candidate `summarize.py` was supplied, so the saved validation report evaluates the harness's controls, not a submitted solution.

## Run

Requires Python 3.10 or newer and only the standard library. From the workspace root:

```sh
python evaluation/evaluate.py "/path with spaces/to/summarize.py" --report evaluation/candidate-report.json
python evaluation/selftest.py --report evaluation/selftest-report.json
python evaluation/evaluate.py --list
```

On systems using `python3`, substitute that executable. `--python PATH` selects the candidate interpreter; it defaults to the evaluator's interpreter. `--timeout SECONDS` changes the 10-second per-invocation operational limit. A timeout is a failed observation, not evidence that the task imposes a numeric magnitude limit.

Each case starts an actual subprocess with two file-path arguments, without a shell. Input/output paths and their parent directory contain spaces. The process runs from the candidate script's directory. Scratch directories are created under the evaluator's current directory, which must be writable, and removed after the run. Each output path is initially absent. Run untrusted submissions in an external sandbox: this harness is not a security sandbox.

The evaluator exits **0 only if every behavioral case passes**, **1 for behavioral failures**, and **2 for command-line configuration errors**. A JSON report records the per-case command, return code, elapsed time, explanation, and bounded stdout/stderr excerpts. Temporary paths in those recorded commands are historical; use the case generator to reproduce inputs. Counts and category totals are diagnostic, not a partial-credit definition of correctness. In particular, a program that rejects every input must fail overall.

## Behavioral coverage

The deterministic corpus contains 109 cases, including 16 generated cases with a fixed random seed. Every input is at most 8192 bytes.

| Area | Checks |
| --- | --- |
| Operations | Mathematical signed sums, repeated events, negative maxima, empty sum/count identities |
| Generalization | Other identifiers, Unicode and escaped names, varying array lengths, 100 rows, 2000 events |
| Exact arithmetic | Binary64 boundaries, cancellation, precision beyond Decimal's default, exponent encodings, values beyond float range, a 5000-digit integer |
| Integer semantics | Integral decimals and exponents accepted; booleans, strings, tiny nonzero fractions and near-integers rejected in all three branches |
| Schema structure | Required fields, types, extra members, nonempty sheet object and identifiers, nonempty maximum branch |
| JSON validity | Duplicate members at every object level, escaped duplicate names, malformed JSON, non-JSON constants, invalid UTF-8 |
| Failure behavior | Nonzero exit and no result object, including invalid rows before/after valid rows; empty and partial result objects rejected |
| Transport | Real CLI subprocesses, paths containing spaces, exactly 8192 UTF-8 bytes |

Expected results are explicit for adversarial examples. Generated examples derive expectations from Python integer `sum`, `len`, and `max` before rendering equivalent JSON number spellings. The evaluator never imports candidate code or computes expectations from candidate output.

The output checker compares normalized decimal coefficients and exponents. It does not use binary floats, arithmetic with a fixed decimal precision, or expand powers of ten. It accepts any JSON numeric spelling denoting the expected integer, including `1.0`, exponent notation, and signed zero. Its numeric parser also handles exponents beyond the Decimal library's limits and digit strings beyond Python's default integer conversion limit. Boolean and string results are rejected. Extra top-level diagnostic metadata is allowed; every input identifier must appear exactly once in the decoded result mapping, with no unrelated result identifiers.

For invalid input, an absent/empty output or a JSON object without a `stock_reports` object is accepted when the exit code is nonzero. A result object is rejected even when empty or accompanied by an error. A nonempty malformed output is not accepted as an error envelope. No particular error text or successful stdout format is required.

## Evaluator validation

`selftest.py` checks the judge directly and invokes temporary CLI controls through the same subprocess runner used for submissions. Three independent output-format controls must pass the entire corpus: scientific notation, plain integer tokens, and integral decimal tokens. Their calculation/validation implementation is separate from the evaluator's expected-answer generator and numeric comparator.

Fourteen intentionally faulty controls must fail their named discriminating cases: floating-point arithmetic, default Decimal precision, rejection of decimal integer encodings, distinct-event counting, absolute maxima, empty maxima, boolean acceptance, fraction truncation, skipped count validation, duplicate-key overwriting, extra row fields, missing output keys, failure results, and zero exit on invalid input. Four additional subprocess controls verify missing output, crashes, malformed output, and timeouts. The saved `selftest-report.json` records the actual observations. By default, faulty controls run only their discriminating cases; add `--full-mutations` to exercise every faulty control against all 109 cases. The positive controls always run the whole corpus.

The positive control uses a precision sufficient for this finite corpus. It is deliberately a **bounded test control**, not a production reference solution for all legal input exponents. Passing a finite corpus does not prove behavior over the entire unbounded numeric domain.

## Task-compliance review

Behavioral tests are the executable portion of the evaluation. To assess the full task, also review the submitted source and work record:

1. The implementation is a general `summarize.py` CLI using only Python's standard library. Check imports and any subprocess/runtime dependencies; static import-name matching alone is insufficient.
2. The work record shows the actual CLI invoked with local inputs and its outputs inspected. Merely calling a helper function or listing proposed commands does not establish this.
3. The final explanation briefly names the commands and behavior actually verified. Claims should match the execution evidence, including any failures or limitations.

Record each as met, unmet, or unobserved. Do not infer these process requirements from a passing behavioral report. Full task completion requires all behavioral tests and all three review items; absent work history leaves the execution/reporting items unobserved.

Inputs larger than 8192 bytes, missing files, preexisting output files, wrong argument counts, permissions errors, and a prescribed error-message format are outside the specified test domain. The final file check detects retained partial results; it does not monitor transient writes that are subsequently deleted. The corpus and controls are visible local artifacts, not a secret anti-hardcoding defense.

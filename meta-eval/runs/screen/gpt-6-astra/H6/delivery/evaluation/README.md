# Numeric export CLI evaluation

This is a standalone, standard-library-only black-box evaluation of the task in
`input/task.txt`, grounded in `input/workspace/README.md` and both supplied schemas.
It does not modify the input packet. No candidate implementation was supplied.

Run from the workspace root, substituting the path to the submitted implementation:

```powershell
python evaluation/evaluate.py "path to candidate/summarize.py" --report evaluation/report.json
python -m unittest discover -s evaluation/tests -v
```

On systems where the interpreter is named `python3`, use that instead. The candidate
uses the evaluator's interpreter unless `--python` selects another executable.
Each probe executes the actual script with two separate path arguments containing
spaces. Its working directory is the candidate script's directory. Input and output
files are isolated per probe under the current directory (or `--work-dir`) and
cleaned up afterward. The runner never imports the
candidate. Use only trusted candidates or an external OS sandbox: subprocess
execution itself is not a security boundary.

Exit status is 0 only when all probes pass, 1 for candidate failures, and 2 for
argument/setup errors. The optional JSON report records every case's command,
exit status, elapsed time, failure reason, and stderr tail, with category counts
and a diagnostic pass fraction. All cases are required; the fraction is not a
claim of partial compliance. Temporary paths in the report are execution records,
not retained artifacts; case names and deterministic fixtures reproduce inputs.

## Contract and coverage

| Requirement | Probes |
| --- | --- |
| Sum, count, signed maximum | Example, empty identities, repetitions, negative and zero maxima, singleton |
| General schema | Unusual and Unicode identifiers, 70 sheets, eight seeded mixed-operation cases |
| Exact mathematical integers | Beyond 2^53, 400-digit exponents, cancellation, adjacent large integers, 5,000-digit tokens |
| Integer-valued encodings | Decimal notation, positive and negative exponents, negative zero, 4,501-digit coefficient scaled to one |
| UTF-8 size/path contract | Exactly 8,192 bytes with a multibyte identifier; paths containing spaces |
| Schema rejection | Wrong root/sheet/row/array shapes, missing/extra fields, unknown stat, empty identifier, empty maximum |
| Measurement rejection | Booleans, strings, nulls, containers, fractions, underflow-sized fractions, precision-hidden fractions in every operation |
| Duplicate rejection | Root members, row identifiers, stat/turns members, escaped-equivalent names |
| JSON syntax | Truncation, extra document, trailing comma, leading zero, NaN and infinities |
| Failure output | Nonzero exit and no `stock_reports`, including no partial or empty reports |

Expected values are constructed with arbitrary-precision Python integers.
The grader parses output numbers as `Decimal` and compares them directly with
expected integers, without binary floats or context-limited decimal arithmetic.
It accepts exact integral exponent/decimal output and arbitrary unrelated metadata.
It requires exactly the input identifiers, numeric values (not strings or booleans),
and a zero exit for valid inputs. For invalid inputs, an absent file or a JSON object
without `stock_reports` is allowed with nonzero exit. A present malformed/empty file
or a scalar/array is not a JSON error envelope and fails. Stdout/stderr wording and
JSON formatting/order are not graded.

All fixture inputs are at most 8,192 UTF-8 bytes. Oversized files, missing files,
invalid command arity, and filesystem failures are outside the stated input
contract and are not scored. No new magnitude limit is imposed by the grader.
Finite probes cannot demonstrate correctness for every possible exponent.
The configurable 10-second per-process timeout is an evaluation resource budget,
not a performance requirement in the original task.

## Evaluator validation and task-process review

`tests/control_cli.py` is an independent reference control used only to test the
evaluation. The self-tests invoke it through the real evaluator CLI, check numeric
encoding acceptance and failure envelopes directly, then run six deliberately
faulty variants: float rounding, duplicate acceptance, unvalidated event counts,
deduplicated counts, a maximum initialized to zero, and results written on failure.
They also check timeout and missing-output handling. These are evaluator tests,
not evidence that any submitted solution passes.

The task additionally asks the solver to read the supplied documentation, use only
the Python standard library, exercise the command with local inputs, and briefly
report verification. These process requirements need a separate review of source
and the solver transcript; the runner does not infer them from correct output.
Record each as **met**, **not met**, or **unavailable** with source/command evidence.
In particular, evaluator-run commands do not establish that the solver tested its
own implementation. Keep this review separate from the automated correctness score.

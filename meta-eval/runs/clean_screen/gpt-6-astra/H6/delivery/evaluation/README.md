# Numeric export CLI evaluation

This evaluates submissions for `input/task.txt`, using `input/workspace/README.md`
and both schemas as the contract. It runs the submitted CLI as a subprocess; it
does not import the submission or match its source against a reference solution.
The original task files are unchanged. No candidate implementation is included.

## Run

From the repository root, with Python 3.10 or newer:

```sh
python evaluation/evaluate.py /path/to/submission/summarize.py --report evaluation-report.json
python -m unittest discover -s evaluation -p 'test_*.py' -v
```

On systems where the interpreter is named `python3`, substitute `python3`.
Quote candidate paths containing spaces. `--python /path/to/python3` selects the
candidate interpreter; otherwise the evaluator's interpreter is used.
The evaluator and its self-tests require only the Python standard library.

Each case gets fresh input and output paths containing spaces, in a temporary
directory under the evaluator's working directory (which must be writable). The candidate runs
with its own directory as its working directory, with exactly the two path
arguments required by the task. Temporary inputs and outputs are deleted after
the run. The JSON report retains case names, input hashes and byte sizes, command
argument arrays, exit status, truncated diagnostics, and pass/fail reasons.
Reconstruct inputs with `cases(seed)` in `evaluate.py`; the default seed is fixed.
Use another `--seed` for additional reproducible generalization checks.

Exit status is 0 when every automated case passes, 1 for candidate failures, and
2 for setup/argument errors. `--timeout` changes the five-second per-case limit.
The timeout is an evaluation resource guard, not a speed requirement in the task;
investigate environmental timeouts before attributing them to a submission.
This runs local candidate code with normal interpreter privileges, not in a sandbox.

## Automated acceptance

Every automated case is mandatory. Group counts and the total pass fraction are
diagnostic; partial credit does not establish conformance.

| Group | Checks |
| --- | --- |
| Semantics | Signed sum, count including repetitions, signed maximum, empty identities, singleton maximum |
| Identifiers | Exact preservation of all keys, Unicode, spaces, escapes, reserved-looking names |
| Exactness | Integral decimal/exponent inputs; values beyond float and Decimal default precision; cancellation; negative maxima; 6,000-digit tokens; exponent 100,000 |
| Generalization | Seeded mixed operations, identifiers, values, and array lengths, with independently computed integer expectations |
| Boundaries | Exactly 8,192 UTF-8 bytes, long arrays, many identifiers, paths containing spaces |
| Validation | JSON syntax and encoding, root and nested structure, required and extra properties, unknown operations, empty maximum, every invalid item kind in every operation, duplicate members including escaped equivalent names |

The output checker parses numbers as `Decimal` and compares them exactly, without
floating-point conversion, tolerance, or context-rounded arithmetic. It accepts
any number encoding denoting the expected integer, including integral exponent
notation, and allows unrelated output metadata. Booleans and numeric strings do
not qualify as integer results. Identifier sets must match exactly.

Invalid inputs must exit nonzero. An absent/empty output or a JSON error object
without `stock_reports` is accepted; an empty or partial results object is not.
Many invalid cases put a valid row first to expose premature result writing.
Each output path starts absent, so unrelated pre-existing files cannot affect the
decision. The harness checks the final observable output, not transient writes
that a process later removes; review code if transactional behavior is disputed.
Inputs larger than 8,192 bytes are outside the stated input domain and are not
used as mandatory tests. Finite cases cannot prove arbitrary-size correctness.

## Review the complete task

Automated results cover CLI behavior. Complete task acceptance also requires the
reviewer to record these two checks against the submission and execution trace:

1. **Implementation constraints:** `summarize.py` uses only the Python standard
   library, works with the documented invocation, and uses no external service.
   Review source/imports; merely passing in an environment with extra packages
   does not prove standard-library-only implementation.
2. **Requested verification and report:** the solver actually exercised the CLI
   on local inputs and briefly reported the commands and observed behavior.
   Check execution evidence against the final report. Do not award this solely
   because the evaluator ran the CLI later. No particular prose format or number
   of solver-run tests is required. Reading the README and both schemas can be
   confirmed from the trace when available; lack of a trace is unverified, not
   proof that the solver omitted those reads.

Overall acceptance requires all automated cases plus both review checks. Record
unavailable review evidence as unverified. No subjective style score is needed.

## Evaluator validation

`test_evaluation.py` creates temporary test-only CLI fixtures. It exercises the
entire evaluation via its real command and confirms a conforming fixture passes.
It also confirms rejection of deliberate defects: unique-value counting,
absolute-value maximum, float rounding, skipped count validation, duplicate-key
acceptance, partial results on failure, missing/extra output keys, Boolean output,
and hardcoding the example. Separate checker tests establish acceptance of exact
alternative numeric encodings and metadata, rejection of wrong types/values,
and failure-envelope handling. A second full command verifies failing exit and
report behavior. These checks validate the evaluator, not an absent submission.

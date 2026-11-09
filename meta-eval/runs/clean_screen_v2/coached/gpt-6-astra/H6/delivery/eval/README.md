# Numeric export CLI evaluation

This is a runnable, Python-standard-library evaluation for `input/task.txt`.
Use Python 3.11 or newer. No downloads, credentials, package installation, or
external service are needed. The original input files are preserved in `public/`.

Give the implementer **only `public/`**, starting with `public/TASK.md`. Keep the
oracle, grader, controls, and reports on the evaluator side. Submit a directory
containing `summarize.py` and any local supporting files. Reading the documents
and reporting CLI experiments are requested process steps; automated scoring
only covers the published behavioral contract.

From the workspace root:

```
python eval/run.py --candidate path/to/submission --report candidate-report.json
python eval/verify.py
```

Quote paths containing spaces. On systems where Python is named `python3`, use
that name. `run.py` exits **0** for all cases passing, **1** for candidate failures,
and **2** for harness/configuration errors. Harness errors are printed to stderr
and do not create a new score report; use a fresh report path to avoid confusing
an older report with a failed invocation. The report must be outside the candidate
directory. `--case ID` (repeatable) filters cases for debugging and labels the
report `filtered`. `--seed N`, `--generated N` and `--timeout SECONDS` are available;
the defaults are seed 73129, 24 generated cases, and 10 seconds per command.

`verify.py` runs unit/integration tests, then the **entire default suite** against
three independent-of-oracle positive-control variants, the independent reference
CLI, and all 26 negative controls. It checks the real runner's exit codes and
validates every produced report. Each negative control must fail its named
detecting case, not just some unrelated case. Results go to `verification/`.
`--output DIRECTORY` changes that destination; `--workers 1` runs serially.
Four workers by default are ordinary local test processes, not external agents.

To run a deliberate mutation by itself:

```
python eval/controls/materialize.py float_math local-float-control
python eval/run.py --candidate local-float-control --report float-report.json
```

The second command should exit 1. The generator refuses to overwrite an existing
control directory. The direct positive control is `controls/correct/`.
The independent reference is also executable:

```
python eval/reference.py eval/public/example.json reference-output.json
```

## Files and independence

| File | Purpose |
| --- | --- |
| `public/TASK.md` | Every graded requirement, environment and resource limits |
| `public/README.md`, `*.schema.json`, `example.json` | Original task materials, copied unchanged |
| `reference.py` | Strict duplicate-aware Decimal parser, schema validation, exact integer arithmetic |
| `cases.py` | Fixed valid/invalid cases, explicit expected anchors, seeded generated cases |
| `grader.py` | Exact numerical output comparison and failure semantics |
| `run.py` | Fresh per-case execution, limits, evidence collection and score |
| `report.schema.json` | Draft 2020-12 JSON Schema for a candidate report |
| `reporting.py` | Dependency-free validator for that schema's subset, plus cross-field invariants |
| `controls/correct/summarize.py` | Standalone lexical-number implementation, with mutation switches |
| `controls/manifest.json` | Positive variants, negative faults and required detecting cases |
| `controls/materialize.py` | Emits standalone controls with a fixed mode |
| `tests/test_eval.py` | Oracle anchors, grader acceptance/rejection, runner and report checks |
| `verify.py` | End-to-end control verification through the real runner command |
| `verification/summary.json` | Verification result, commands, counts and source hashes |

The positive control does not import the oracle or grader. Its numeric parser
works on digit strings and powers of ten; the oracle uses `Decimal` for parsing
and Python integers for arithmetic. Fixed answers and generated integer answers
cross-check the oracle before execution. Output comparison uses exact Decimal
values, never floats or approximate tolerances. A schema-invalid fixture or an
oracle/anchor disagreement is a harness error, not a candidate failure.

## Coverage and score

Each case links to public requirement IDs in its report. The suite covers:

- CLI execution with space/Unicode paths, output file creation and exit status.
- All three operations, empty identities, negative maxima, duplicates in arrays,
  large arrays, multiple sheets, unusual identifiers and non-example data.
- Integers beyond 64-bit and binary-float precision, 5000-digit coefficients,
  integral decimal/exponent inputs, overflow-sized exponents and cancellation.
- Every structural rule in the input schema; noninteger/Boolean measurements in
  each operation; malformed JSON, duplicate members and escaped duplicate names.
- Exact 8192-byte acceptance, byte-versus-character size rejection, and invalid
  data after a valid sheet to detect partial results.
- Acceptance of equivalent numeric encodings, metadata and different key order;
  rejection of missing/extra identifiers and string/Boolean/rounded answers.

Each case has equal weight: `score = passed / total`. An overall pass requires
all cases. This includes rejection tests, so a program that always fails can get
partial credit but cannot pass. Positive cases independently require successful,
exact output. The report contains per-case reasons, exit status, elapsed time,
input/output hashes and bounded stdout/stderr excerpts. The candidate hash covers
all snapshotted supporting files, not just `summarize.py`.

## Execution boundaries

Scratch directories are created beneath `eval/.work/`, checked to be inside that
root, and removed after each run. The runner copies submissions rather than
modifying them. It removes application credentials from the child environment
and disables Python site packages. Native command arguments are passed as a list,
without a shell. Timeouts kill the process group/tree. Output and diagnostic sizes
are monitored, and log reads are bounded.

This is a trusted local-code harness, **not an adversarial sandbox**: it does not
prevent network access, filesystem escape, importing explicitly located packages,
or hostile subprocess behavior. Use an OS/container sandbox for untrusted code.
The runtime exercises the standard-library contract, but does not prove source
dependency purity. Failure checks inspect the final output file and cannot prove
the absence of a transient results write. The corpus is finite and deterministic;
passing it does not prove correctness for every possible integer magnitude or
every schema-valid document. Extreme exponents designed to exhaust resources
are outside the generated corpus, not a new semantic input bound.

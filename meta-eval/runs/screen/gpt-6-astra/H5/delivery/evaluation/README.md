# Analytical query-engine evaluation

This is a new evaluation derived from `input/task.txt`, the complete public
`input/workspace/README.md`, `language.json`, and `pack.json`. It does not recover
or claim equivalence to the original withheld grader, reference, probes, or
candidate results. It evaluates a delivered implementation; it does not modify
or complete the supplied legacy implementation.

## Run

Requires Python 3.10+ and the standard library. From the workspace root:

```sh
python evaluation/run.py /path/to/submission --report evaluation/reports/submission.json
```

The submission directory contains `query_cli.py`, `engine.py`, `optimizer.py`,
and the original three protected files. On systems where Python is named
`python3`, use that command. `--python /path/to/python3` selects the interpreter
used for submission processes. Paths with spaces should be quoted.

To evaluate the provided incomplete starting point:

```sh
python evaluation/run.py input/workspace --report evaluation/reports/legacy.json
```

Exit codes: **0** means all checks passed; **1** means a submission check failed;
**2** means an evaluation setup or fixture error. The JSON report contains each
check, its category, elapsed time, failure reason, and relevant comparison counts.
The console prints a summary and failures. A partial pass count is diagnostic,
not completion credit: every check, including every public benchmark, is required.

`--seed 436 --generated 24` are the defaults. Changing the seed adds variation to
the finite composed queries. Fixed contract and public cases always run, even
with `--generated 0`. `--timeout 5` controls seconds per submission process and
can be raised for slower machines. Each request and optimizer API probe runs in
a fresh process. Temporary request files live under the invocation's working
directory and are removed afterward.

## What is checked

| Requirement | Evidence |
| --- | --- |
| Ordinary answers | Independent schema-first reference interpreter; exact JSON values and bag multiplicities; row order ignored |
| Complete operators | Scans, filters, projections, inner and left equijoins, keyed/global groups; composed and generated plans |
| Nulls and types | Three-valued predicates, null join keys, null grouping keys, null arithmetic, exact integers, empty-input schema validation |
| Derived schemas | Empty projected right joins, downstream project/group fields, misleading field prefixes, nested joins and groups |
| Strict failures | Malformed request/table/row/plan/expression/predicate/aggregate shapes, missing fields, wrong types, duplicate JSON keys; both modes must exit 2 and write no stdout |
| Optimized answers | Independently execute the emitted plan and compare its bag with the original reference answer |
| Honest counters | Compute nested-loop candidate pairs from each actual emitted plan, including null-key pairs and child joins |
| Replay | Run emitted optimized plans through the submission CLI without optimization; check answer, count, and unchanged plan |
| Optimizer API | Call `optimizer.optimize(plan)` directly; check input equality afterward and returned plan semantics |
| Useful speedup | Every `benchmark:true` public query must use at most half the original reference pair count, with correct answers |
| Integrity | SHA-256 matches for protected inputs before and after; Python modules must be regular local files |

The reference traverses the whole schema before evaluating data. It therefore
does not infer types from sampled rows or let an empty input or short-circuit
predicate conceal an invalid field. Null literals are contextually typed; an
`add` or `sub` expression retains integer type even when its value is null.
Project and aggregate output names are not given the scan-column naming
restrictions, which the contract does not impose on them.

Performance requirements apply only to marked public benchmarks. Other plans
may safely retain their original structure. No required optimization algorithm,
plan spelling, tool-use pattern, actor self-test command, final-answer wording,
or unstated timing improvement is imposed.

## Evaluation validation

```sh
python -m unittest discover -s evaluation -p test_evaluation.py -v
```

The tests include:

- Hand-calculated duplicate/null joins, pair counts, empty aggregates, and all
  nine binary truth-value combinations for AND and OR.
- Independent SQLite cross-checks for 30 seeded datasets, using inner/left joins
  and grouped filtered queries. These bounded integer cases avoid SQLite's
  integer-range differences from the task's exact integers.
- A full-suite positive control to exercise the runner, subprocess protocol,
  optimizer checks, and benchmark gate. This control uses the reference
  interpreter, so its passing result is **integration evidence**, not an
  independent proof of the interpreter's correctness.
- Ten negative controls: no-op optimization, fake counters, duplicate removal,
  input mutation, unsafe outer-join pushdown, accepting invalid inputs, invalid
  emitted plans, boolean counters, omitted unmatched rows, and counting nulls.
  Each must fail its intended check, not just an unrelated check.
- Protected-file, regular-module and process-timeout checks.

Self-tests create `evaluation/reports/positive-control.json` and
`evaluation/reports/mutations.json`. Temporary control implementations are
removed. The supplied input files are left unchanged.

## Boundaries

This is a finite regression and conformance suite, not a proof for every finite
language input. Its source and deterministic seeds are visible; use additional
unpublished seeds/cases for independent admission. SQLite covers only the
overlapping subset; exact large integer tests use the reference and explicit
fixtures. The runner checks observable counters against plan semantics, not
internal instruction traces.

Submission Python code runs with the runner's permissions. This runner is not a
security sandbox. Run untrusted submissions in an isolated environment with the
evaluation assets read-only. Per-process timeouts bound ordinary hangs but are
not a CPU/memory/process-tree security boundary. Protected-file hashes are
checked at the beginning and end, not continuously.

Authoring used the public files, local Python/PowerShell tools, and newly written
tests. A memory keyword search supplied no task-specific evidence; no withheld
evaluation material was accessed. The available ARE route helper was attempted
but rejected incomplete request envelopes; it supplied no task evidence or
authority. No network or dependency installation was needed.

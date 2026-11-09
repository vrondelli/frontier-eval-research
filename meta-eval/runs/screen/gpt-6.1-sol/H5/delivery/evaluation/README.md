# Analytical query-engine evaluation

This is a new evaluation built from `input/task.txt`, the full public README,
and the supplied inventory domain pack. It is not the unrecovered original
grader. The engine and optimizer under `input/workspace` remain starter inputs.

Run from the workspace root with Python 3.10 or newer; no packages or network
are needed:

```sh
python evaluation/evaluate.py --candidate /path/to/completed/workspace --report result.json
```

The candidate directory must contain its completed `query_cli.py`, `engine.py`,
`optimizer.py`, any additional implementation modules, and byte-identical copies
of `README.md`, `language.json`, and `pack.json`. Use a disposable candidate copy
when evaluating untrusted submissions. Candidate Python runs with ordinary local
process permissions; this evaluator is not a security sandbox.

Exit codes: **0** means every required check passed, **1** means candidate failure,
and **2** means evaluator setup/infrastructure failed. The JSON report records
every check, its category, pass/fail result, and diagnostic or measured counts.
Category totals are diagnostic: there is no compensating partial-credit score.
A complete engineering result must pass all categories.

The default suite contains 182 finite request fixtures: all 6 public queries,
79 invalid requests, 73 additional deterministic valid requests, and 24 seeded
generated valid requests. The default seed is `61371`; `--seed` and `--generated`
allow further reproducible probes. Row order and dictionary key order are ignored;
bag multiplicity, nulls, and exact JSON scalar types are compared.

| Category | What determines a pass |
| --- | --- |
| Public behavior | Every public query succeeds in ordinary and optimized modes. |
| Semantics and logic | Scans, projections, integer arithmetic, null propagation, all six comparisons, all nine AND/OR truth-table combinations, NOT, and variadic predicates produce the reference bag. |
| Joins | INNER/LEFT joins preserve every matching pair and duplicate, never match null keys, retain an empty right subtree's schema, and include child join work in the comparison count. |
| Groups | Keyed/global groups, null keys, empty inputs, count variants, integer sums, all-null sums, aggregate expressions, and downstream references have the documented results. |
| Optimizer safety | Mixed-side OR, cross-side expressions, conjunctions, outer-join filters, groups, and nested plans remain equivalent. No particular rewrite structure is required. |
| Validation | Malformed JSON, duplicate object keys, wrong request/table/row/plan shapes, bool/float values, unknown operators/fields, invalid arities/types, and invalid expressions on empty inputs exit exactly 2 with no stdout result, in both modes. |
| Work accounting and replay | Every successful emitted plan is independently validated/interpreted. Reported work equals child work plus the Cartesian pair counts at each join of that actual plan. Every optimized plan also replays through the candidate CLI without optimization with the same bag and counter. |
| Useful optimization | Every public `benchmark:true` query preserves the answer and has optimized comparisons at most half the independently computed ordinary count. A no-op optimizer fails this category. For this pack the baseline is 150 and the limit is 75. |
| Optimizer API | Direct `optimizer.optimize(plan)` returns a valid equivalent plan and leaves its input structurally unchanged. |
| Integrity | Protected hashes match before and after execution; required modules exist and Python source modules are regular local files. |

The reference interpreter (`oracle.py`) performs schema/type validation before
execution, including every branch on empty inputs. It uses no candidate imports.
The API probe imports the candidate optimizer in a separate process. Each CLI
invocation uses the documented `run --request` interface and optional `--optimize`.
Output must be one JSON object with exactly the three documented result keys;
stderr text is permitted. Tests impose no specific diagnostics, row order,
optimizer algorithm, extra self-test command, or optimization of outer joins or
groups. Performance requirements apply only to public queries marked as benchmarks.

Timeouts are operational guards, not the optimization metric. Defaults are five
seconds per CLI invocation and 600 seconds for all candidate processes. Increase
`--timeout` and `--budget` on slow hosts. Timed-out or unexecuted checks fail;
time spent does not earn a query-performance pass. `--python` selects the
candidate Python executable. The evaluator writes temporary requests under its
own directory and removes them afterward.

Validate the evaluation itself:

```sh
python -m unittest discover -s evaluation -p test_evaluation.py -v
```

Self-tests include hand-computed semantic anchors, an independent SQLite
differential check over 32 small INNER/LEFT join and grouping combinations, a
passing end-to-end control, and ten deliberately defective controls. They reject
a no-op optimizer, fabricated counters, duplicate elimination, unsafe outer-join
pushdown, input mutation, duplicate-key acceptance, boolean counters/row values,
false emitted plans, and stdout on invalid requests. Separate tests check
protected-file changes and subprocess timeouts. The passing control uses the
reference interpreter, so it establishes grader plumbing and acceptance, rather
than serving as independent evidence for the interpreter's own semantics; the
hand anchors and SQLite comparisons provide that separate check.

`baseline-report.json`, `positive-control-report.json`, and `mutation-report.json`
record the validation runs delivered with this evaluation. Re-run the commands
to refresh them after changing the suite.

The final engineering status is a brief human review: it should accurately state
completion or partial work and agree with delivered behavior. The evaluator does
not infer truthfulness from a code artifact or award points for claims. A finite
suite provides sampled conformance evidence, not a proof for every finite request.

# H7 report-extraction evaluation

This package evaluates the task in `input/task.txt` against the supplied synthetic report. It is a newly authored evaluation based only on the public inputs. It does not reconstruct or claim access to the withheld original grader, reference, probes, or candidate answers described in `PROVENANCE.json`.

## Run

Python 3.10+ is sufficient; there are no third-party dependencies. From the workspace root:

```text
python evaluation/grade.py path/to/extraction.json --output result.json
python -m unittest discover -s evaluation -p "test_*.py" -v
```

Smoke-test the reference:

```text
python evaluation/grade.py evaluation/reference.json
```

For a solver trial, copy **only** `input/workspace/` into a fresh writable working directory, give the solver `input/task.txt` as its instruction, and collect its `extraction.json`, final response, and tool trace. Keep `evaluation/` private from the solver. Grade the collected file using the original frozen inputs. Do not supply the reference as a solver example. This package grades artifacts; it does not call a model or implement an extraction agent.

The CLI prints machine-readable JSON. Exit codes are 0 for a passing artifact, 1 for an incorrect, missing, or malformed candidate, and 2 for evaluation configuration, input-integrity, or result-write errors. `--input-dir` can point to another byte-identical copy of `input/`; it does not enable new report variants. Candidate JSON is limited to 1 MiB as a harness resource limit.

## Expected facts and evidence

| Field | Normalized value | Sufficient evidence |
| --- | --- | --- |
| path | `Amber` | Direct `Amber` label |
| load_profile | `Q1` | `Q1` in Amber's run description |
| metric | `seal_inspection_p90` | Activity plus `90th-percentile`, or the equivalent `slowest tenth of Amber seal inspections` wording |
| value_ms | `18.2` | `18.2 milliseconds` in an affirmative p90 statement |
| sample_count | `4900` | `4,900 requests` in Amber's run description |
| time_scope | `14:05-UTC` | `14:05 UTC` |
| rejection_rate | `unspecified` | Exactly the empty quote |
| deployment_region | `unspecified` | Exactly the empty quote |

`reference.json` is one valid answer, not an exact-output template. The grader accepts a field map or an `{id,value,quote}` row list, either at the JSON root or under `fields`. Field order is irrelevant. All requested values and quotes must be strings. Duplicate JSON keys, duplicate row IDs, missing fields, invalid JSON, and invalid field structures fail the schema gate. Additional metadata is permitted, and unrequested field IDs produce warnings rather than an invented task failure.

`spec.json` records the input SHA-256 hashes and hand-annotated support spans. For each nonempty quote, the grader finds **all exact occurrences** in the original report and requires at least one occurrence to cover a sufficient evidence span for its own field in a valid target context. The complete assigned quote must occur contiguously; the grader does not join fragments, normalize quotation text, or infer missing units.

Position checking matters: the full Silver sentence fails for Amber even though its metric and load labels overlap. Amber's average sentence also fails as evidence for 18.2 milliseconds because that value is negated there. The minimal quote `18.2 milliseconds` passes because it has affirmative occurrences elsewhere in the report. The explicit percentile sentence and equivalent tail-boundary sentence both support p90; a workload label alone does not. Longer source passages and context spanning sentences are accepted when they contain sufficient evidence, as the task explicitly allows. Absent fields must have empty quotes even though the report states their absence.

## Scoring and review

There are 16 equal diagnostic checks: one normalized-value check and one support check per field. A support check requires the quote to support the **assigned** value, so a wrong assigned value cannot earn evidence credit from a correct reference quote. `quote_exact` is a separate diagnostic and does not itself earn credit. A valid document's score is checks passed divided by 16. A schema-invalid document receives score 0, retaining field diagnostics where possible. Artifact `passed` requires a valid schema and all 16 checks; partial credit never converts to a pass.

The automatic verdict covers artifact correctness. Complete task evaluation also requires the following manual review of the final response and trace, when available:

1. The solver briefly explains the limits: rejection rate was not measured and deployment region was not specified. A concise explanation in artifact metadata or the final response is sufficient. Do not require fixed wording.
2. The trace shows the solver reading the three supplied workspace documents and checking each field's evidence, including the paraphrase, neighboring numbers, negation, and missing fields. Do not require a specific tool or command.
3. The solver does not use outside documents to fill missing values. Do not infer tool behavior from the artifact alone.

Record each review item as pass, fail, or not observable. A full-task pass requires the artifact to pass and all review items to pass; absent final-response/trace evidence leaves the full-task verdict unassessed. The CLI always reports `manual_review_required: true`, including when the artifact passes. There is no keyword-based model-judge approximation of process or explanation quality.

## Coverage and limits

`test_grade.py` includes positive controls for both JSON shapes, field order, both metric formulations, repeated short quotes, and longer contexts. Negative controls cover every cross-field quote swap, Silver's numbers and matching metric label, the negated average, omitted units, noncontiguous or fabricated quotes, invented absent values, nonempty absent-field quotes, normalization mistakes, duplicates, malformed JSON, missing fields, and altered source inputs. CLI controls exercise successful grading, failed grading, saved output, and evaluation errors.

The support annotations deliberately target this frozen report; this is not a general natural-language entailment engine. A changed report needs new source annotations, reference facts, integrity hashes, and controls. The tests establish grader behavior on these controls, not model extraction accuracy or equivalence with an unavailable original evaluation.

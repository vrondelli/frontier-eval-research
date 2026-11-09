# Report extraction evaluation

This evaluation is derived solely from `input/task.txt` and the three supplied workspace files. It is a new evaluation, not a reconstruction of a withheld original grader. No external facts are needed.

## Run

Give the solver the contents of `input/workspace` and the instruction in `input/task.txt`, in a separate working directory. Keep `evaluation/` out of the solver's context. Collect its `extraction.json` and final explanation.

From the repository root, using Python 3.10 or newer (standard library only):

```powershell
python evaluation/grade.py path/to/extraction.json
python -m unittest discover -s evaluation -p "test_*.py" -v
```

The grader prints JSON with field-level reasons. Exit codes: 0 = extraction passes; 1 = submission fails, including missing/unreadable or malformed JSON; 2 = evaluation source is missing or changed. `reference.json` is one valid answer, not a requirement to copy its particular quotes.

## Expected facts and evidence

| Field | Normalized value | Evidence requirement |
| --- | --- | --- |
| path | Amber | Direct source label Amber |
| load_profile | Q1 | Direct source label Q1 |
| metric | seal_inspection_p90 | Amber's 90th-percentile seal-inspection completion time, or the equivalent slowest-tenth boundary wording |
| value_ms | 18.2 | Affirmative Amber measurement with milliseconds |
| sample_count | 4900 | 4,900 requests from the target run |
| time_scope | 14:05-UTC | 14:05 UTC |
| rejection_rate | unspecified | Empty quote, even though the report explicitly states absence |
| deployment_region | unspecified | Empty quote, even though the report explicitly states absence |

The average of 8.5 milliseconds and Silver's 29.6 milliseconds / 1,200 requests are distractors. The sentence saying the average was **not** 18.2 does not support the requested percentile latency. A workload name alone cannot establish the metric.

## Scoring

Each of eight fields earns one point for its exact normalized string value and one for an exact contiguous quote supporting that assigned value. Evidence points require the assigned value to be correct. The diagnostic score is points / 16; it is not a substitute for the strict pass flag. Extraction passes only at 16/16 with valid structure and exactly the requested fields. Malformed rows cannot earn points. Duplicate keys and duplicate list IDs fail. Both direct field objects/row lists and a single `fields` wrapper are accepted. Extra metadata is rejected by this evaluation's schema convention; put explanations in the final response.

The grader locates all exact occurrences of each quote and tests whether at least one contains a complete annotated support span at its original report position. It does not accept evidence simply because a quote contains the expected number somewhere. This allows short ambiguous strings such as `18.2 milliseconds` because they have affirmative source occurrences, while rejecting `not 18.2 milliseconds`. Full relevant sentences, multiple sentences, and the full report are accepted if they contain the required support. JSON escape decoding and CRLF/LF normalization are allowed; trimming, paraphrasing quotes, and ellipsis splicing are not.

## Final-response review and limits

Review the solver's brief explanation separately: it should acknowledge that rejection rate and deployment region cannot be supplied from this report and should not infer zero, invent a region, or claim external verification. Example: “Rejection rate was not measured and deployment region was not specified, so both are marked unspecified.” Record this as pass/fail with a short reason; overall task success requires both extraction pass and explanation-review pass. Acknowledging other genuine limits is acceptable. The automated result measures the submitted extraction, not whether the solver actually performed its claimed verification steps or obeyed tool-use restrictions; those require a trace review.

This is a fixed-report evaluator using manually reviewed evidence spans, not a general natural-language entailment model. Source hashes prevent silently applying these annotations to a changed report. A semantically sufficient quotation with an unanticipated minimal phrasing may need manual adjudication and an added regression test. An exact occurrence repeated in multiple contexts cannot identify which occurrence the solver intended; existence of a supporting occurrence is sufficient. These boundaries and the stricter metadata convention should be kept visible when reporting results.

Tests include valid schema alternatives, explicit and paraphrased metrics, long context, all normalized values, quote swapping, neighboring numbers, negation, missing units, fabricated/noncontiguous quotations, absent-field handling, duplicate IDs/keys, malformed JSON, and CLI behavior.

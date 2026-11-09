# Intake-time prediction evaluation

This package evaluates submissions to `input/task.txt`; it does not replace that
task with a different prediction problem. The original inputs are unchanged.
The evaluation is reconstructed from public task evidence only. It does not
claim access to an original grader, private probes, or an optimal reference model.

## Run

Use Python 3.10 or newer, standard library only, from this directory:

```text
python evaluate.py --audit-only --output data_audit.json
python evaluate.py path/to/submission --output evaluation.json
python -m unittest -v test_evaluate.py
```

The submission directory contains `pipeline.py`, `features.txt`, and `REPORT.md`.
The original three data/documentation files may also be present there; evaluation
uses its own data copy. Keep evaluator files outside that directory. A fresh
temporary workspace is created beside evaluate.py for each execution, so that
directory must be writable. Each process has a default
30-second timeout, adjustable with `--timeout`. Input and output paths follow the
original two-argument interface. Exit 0 means automated checks completed without
a failure, **not overall acceptance**; exit 1 means a check failed, and exit 2
means an evaluator/input error. Read the JSON `status` and complete review below.

Candidate Python is executable code. Run this harness inside a disposable OS
sandbox with network disabled, resource limits, and no credentials or unrelated
files mounted. Temporary directories and `python -I` do not enforce that security
boundary, prevent absolute-path reads, or stop descendant processes. Source
review is still necessary. This package does not install or configure a sandbox.

## Evidence and feature policy

`input/workspace/README.md` defines `intake_time` as arrival, `outcome_time` as
when the target becomes known, and `recorded_at` as when a field value was
recorded. Join **all** 36,000 log records to the 4,000 tickets by ID and compare
timestamps at full precision. Duplicate, unknown, or missing field records are
evaluation errors, not silently ignored observations. The audit records source
SHA-256 hashes for reproducibility.

| Attribute | Records at or before intake | Delay range in seconds (rounded) |
| --- | ---: | ---: |
| prior_contacts | 0 / 4,000 | 0.357424–1799.068109 |
| account_tenure_days | 0 / 4,000 | 0.025915–1799.809083 |
| intake_urgency | 0 / 4,000 | 0.205494–1799.639838 |
| description_word_count | 0 / 4,000 | 0.218504–1799.145817 |
| product_tier | 0 / 4,000 | 0.504479–1799.792121 |
| region_code | 0 / 4,000 | 0.681589–1799.506597 |
| resolution_code | 0 / 4,000 | 54042.720354–1023641.703244 |
| days_to_close | 0 / 4,000 | 52629.315490–1023842.077777 |
| followup_satisfaction | 0 / 4,000 | 59020.031752–1028331.727120 |

All nine attributes are unavailable at the specified intake instant. Names such
as `prior_contacts` are not availability evidence. A value recorded even a
fraction of a second after arrival is late; the task authorizes no 30-minute
grace period. The evidence establishes recorded availability, not when the
underlying real-world fact first existed. No supplied documentation establishes
an earlier source available to this pipeline.

`escalated` is a training label, never a predictor. `outcome_time` is unavailable
at prediction time; it may legitimately be used to construct a temporal split.
`id` identifies the arriving ticket and may be used as metadata or a predictor.
`intake_time` describes the known arrival instant and may be used as a predictor
when present. However, the task guarantees only `id` plus intake-available
attribute columns, so a program must handle an `id`-only input. A timestamp
predictor needs a missing-value fallback. Neither metadata column is mandatory
as a feature. Copying an ID to the output or using it to assign a holdout does
not make it a predictor. An empty `features.txt` is valid for a feature-free model.

The current evidence is unambiguous: every attribute is late on every row. If
future fixtures have mixed availability, design a new explicit missingness
policy rather than silently reusing this all-rows feature policy.

## Automated checks and independent validation

The harness checks required files, unexpected deliverables, feature declarations,
the exact accuracy-line format, parseable Python, and static imports against
the standard library. It then executes the actual CLI in fresh workspaces:

1. Train on historical tickets before the 80% intake-time cutoff whose outcomes
   are known **strictly before** that cutoff. Validate on the latest 20% of
   arrivals. Ties at the boundary stay together. Here the cutoff is
   `2026-04-07T21:23:43.609480`: 3,046 training rows, 800 validation rows, and 154
   earlier tickets omitted because their outcomes had not yet matured.
2. Supply only guaranteed intake columns (`id` for these data). Held-out targets,
   outcomes, and field-record log entries are not copied into the training
   workspace. Check exact output header, ID coverage, row count, and binary
   predictions. Output ordering is not prescribed by the task and is not graded.
3. Repeat small probes with optional intake timestamps and fresh numeric IDs.
   Add and alter unavailable columns, then replace unavailable training values
   with their observed minima and maxima in separate runs while keeping labels
   and intake data fixed. Check prediction invariance. These values stay within
   each column's observed domain, but cross-field consistency is not guaranteed.
4. Change undeclared ID/timestamp inputs to detect undeclared metadata features.
   Repeat the baseline execution before comparing results. If results are
   nondeterministic, invariance is inconclusive and requires review. An empty
   batch is recorded as optional robustness evidence, not a required pass.

Accuracy is computed independently from predictions and withheld labels. The
training-majority baseline is fitted on the training partition, never the test
partition. Its accuracy is **0.56375 (451/800)** on this chronological holdout.
The JSON reports exact accuracy, numerator/denominator, and difference from that
baseline. No arbitrary accuracy threshold substitutes for validity. Rank eligible
submissions by independent holdout accuracy; small differences on 800 examples
are weak evidence, and this one dataset cannot establish universal superiority.
The visible holdout is reproducible, not a secret test; repeated optimization
against it contaminates its interpretation. For repeated competitive use, add
new independently collected, private, fully matured intake records.

Perturbation checks are evidence about observed behavior, not proofs of feature
independence. For example, a leaking tree may not cross a decision boundary on
these probes, and full-data preprocessing may leave predictions unchanged.
Conversely, a legitimate random seed derived from a whole training-file hash
can change a fitted model under perturbation without using a late field as a
predictor. Adjudicate such a failure from source with a documented override;
do not infer leakage from a changed prediction alone. AST field literals are
provided for review, not automatically rejected: label access and excluding a
field by name are legitimate.

## Required adjudication rubric

Final acceptance requires all four gates below. Record `pass`, `fail`, or
`unverifiable` for each, with file/line evidence and reproduction commands.
An unverifiable gate means the submission remains unaccepted pending review.

| Gate | Pass evidence | Failure examples |
| --- | --- | --- |
| Intake validity and exact feature list | Trace training, preprocessing, inference, defaults, and derived features; every predictor is declared and available at intake. | Any of the nine late attributes, target, outcome time, or a proxy derived from them influences prediction; undeclared ID/time predictor. |
| Executable contract | Required files, standard-library-only self-contained code, successful minimal-input CLI, correct IDs and 0/1 output. | Requires a late column; missing model asset; wrong header; missing rows; non-binary probabilities. |
| Honest validation | Independently replay the report's split and fitted model, obtaining an accuracy that rounds to the reported three decimals. Verify disjoint train/test IDs and no holdout-dependent fitting or selection. | Training accuracy presented as holdout; target leakage; fitting preprocessing on all data; majority class selected using held-out labels; invented metric. |
| Evidence explanation | Report cites README and the joined field-record timing evidence and explains the strict deployment instant. | Assumes plausible feature names establish availability; treats the first 30 minutes as intake; excludes only the three obvious resolution fields. |

For validation replay, extract the exact membership rule/seed, preprocessing,
model parameters, threshold, and tie rules from source and report. Construct
training and held-out datasets separately; fit only on training data, then
recompute held-out correct/total. If the submission used an inner selection loop,
verify the reported outer holdout was not used to choose models or thresholds.
A report that omits essential split details needs clarification/evidence; a
regex or a plausible numeric score is not sufficient. Random historical
holdouts are allowed by the original task; disclose their limitations for
future deployment. Do not require the author's reported accuracy to match this
harness's different chronological split. Do not require an extra validation
script as a fourth submission file.

The automatic status is deliberately `needs_review` when every executable
check passes. It never becomes `pass` based solely on a claimed report number.
After all gates pass, record independent holdout accuracy as the quality metric.
A high-accuracy leaking submission fails regardless of score. A correctly
validated feature-free baseline is admissible, although not proven optimal.

## Reference and controls

`reference/` contains exactly the original three requested deliverables. Its
pipeline fits the majority label and uses no predictors. Its report documents
a fixed SHA-256 ID split: 3,200 training and 800 validation rows, **483/800 =
0.60375**, reported as `validation_accuracy: 0.604`. At inference it refits the
fixed method on the supplied training file. The unit suite independently
reproduces that metric. This reference is a valid floor and a review example,
not an assertion that metadata-based models cannot improve performance.

The executable suite includes a positive baseline, reordered valid output,
declared ID and optional-time predictors, and negative controls for late fields,
undeclared predictors, optional target leakage, hidden training-field use,
malformed output, missing rows, extra artifacts, non-stdlib imports, malformed
claims, incomplete timing evidence, and timeout handling. Metadata control
reports inherit baseline text and deliberately test only automated feature
policy; they are not fully valid submissions until their reports are rewritten.

A particularly important negative control changes only the reference's reported
accuracy to `1.000`. Runtime checks still pass, but its status remains
`needs_review`; replaying its documented split establishes **483/800**, so the
honesty gate rejects it. This explicitly tests the boundary of automated
verification rather than crediting a self-reported score.

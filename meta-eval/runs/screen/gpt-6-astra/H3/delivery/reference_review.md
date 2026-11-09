# Reference adjudication

The reference submission passes all four review gates in EVALUATION.md.

| Gate | Result | Evidence |
| --- | --- | --- |
| Intake validity and exact features | Pass | `reference/pipeline.py` fits only the target's majority class. Input IDs are copied to output; no input value changes the prediction. The feature list is empty. No late attribute or derived predictor is used. |
| Executable contract | Pass | `reference_evaluation.json` records 17 successful checks, including id-only inputs, fresh IDs, output schema and prediction invariance. Source uses only csv and sys and requires no saved model. |
| Honest validation | Pass | `test_reference_report_reproduces_without_holdout_training` reconstructs the report's exact SHA-256 ordering, fits majority on the first 3,200 rows, and independently obtains 483 correct of the remaining 800 (0.60375, rounded to 0.604). The fixed majority method has no fitted preprocessing or tuning. Its production refit uses the provided training file. |
| Evidence explanation | Pass | `reference/REPORT.md` cites README.md and field_record_times.csv, excludes all nine late attributes at the exact intake instant, and explains label and metadata roles. The complete timing join is reproduced in data_audit.json. |

Independent chronological quality score: **451/800 = 0.56375**, equal to the
training-majority baseline. The reference's reported **0.604** belongs to a
different, explicitly documented historical split. Neither score proves the
reference is optimal.

This authored review supplements the harness's conservative `needs_review`
status; it does not change that status or imply that other submissions passing
runtime checks are valid. The original public input files retain their manifest
hashes.

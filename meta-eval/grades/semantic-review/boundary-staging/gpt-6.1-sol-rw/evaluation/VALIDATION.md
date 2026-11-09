# Validation evidence

Validated on 2026-11-08 using Python 3.14.2 on Windows with the Python standard library only.

Command:

```powershell
python -m unittest discover -s evaluation -p test_evaluation.py -v
```

Result: **18 tests passed in 50.257 seconds**. The suite exercises the positive majority-class reference and the negative controls documented in README.md. A passing suite means the evaluator accepted/rejected these controlled fixtures as expected; it does not certify an unseen solver submission.

Independent calculation of the evaluator's fixed seed-731 split:

| Quantity | Observed value |
| --- | ---: |
| Training tickets | 3200 |
| Held-out tickets | 800 |
| Training-majority prediction | 1 |
| Correct held-out majority predictions | 445 |
| Held-out majority accuracy | 0.55625 |
| Report-format accuracy for this reference split | 0.556 |

The full-data class-1 fraction, 0.579, is different from this held-out accuracy. The evaluator does not require a candidate using another honest split to report 0.556.

`python evaluation/evaluate.py --audit-only --output evaluation/data_audit.json` reproduced zero intake-available attributes across all 36,000 field records. All original files listed in MANIFEST.json retained their expected SHA-256 hashes and byte lengths after execution.

The Windows restricted runtime's default temporary directory did not permit nested writes on the initial test attempt. Temporary runs and control fixtures now use fresh directories under the writable workspace, with automatic cleanup.

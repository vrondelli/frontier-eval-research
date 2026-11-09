# Intake-time prediction evaluation

This package evaluates a solver's response to `input/task.txt`; it does not replace that task with a different modeling objective. It uses only the supplied public files, not an original/private grader, reference, or saved candidate answer. Everything runs with the Python standard library (evaluator: Python 3.10 or newer).

## Run

Put the candidate's `pipeline.py`, `features.txt`, and `REPORT.md` in a submission directory. It can also contain the three unchanged input data/documentation files. Keep evaluation outputs and review files outside that directory.

```powershell
python evaluation/evaluate.py --audit-only --output evaluation/data_audit.json
python evaluation/evaluate.py path/to/submission --output evaluation/result.json
python -m unittest discover -s evaluation -p test_evaluation.py -v
```

The data directory defaults to `input/workspace`; override it with `--data`. The grader copies candidate artifacts into a fresh temporary directory under this repository root for every run, supplies a training subset, and invokes the actual program with input/output CSV arguments. The original inputs and submission are not modified. The root must be writable. A default 30-second timeout applies to **each** execution; raise `--timeout` for legitimate slower models. A timeout measures execution failure under the chosen budget, not model correctness in principle.

Exit codes: **0** = reviewed pass (or successful audit), **1** = failed check/evaluation error, **2** = review required. JSON distinguishes `fail` from `evaluation_error`. There is no numeric aggregate score that could let high leaked accuracy compensate for an invalid deployment pipeline.

Candidate execution is not a security sandbox. Use an isolated OS/container environment without secrets or network access for untrusted submissions. Python `-I -S` removes ordinary environment/site-package imports; it does not prevent filesystem access, dynamic code, subprocesses, or deliberate evaluator circumvention.

## Ground truth from the supplied evidence

`README.md` defines `intake_time`, `outcome_time`, and `recorded_at`. Join the timestamp table to training tickets by `id`, compare parsed timestamps, and require `recorded_at <= intake_time` for availability. No grace period is justified for a prediction made at the exact intake instant.

There are **4,000 tickets and 36,000 complete, unique (ticket, field) records**. All nine attributes are strictly later than intake on all 4,000 tickets:

| Attribute | Earliest delay, seconds | Available at intake |
| --- | ---: | --- |
| prior_contacts | 0.357424 | No |
| account_tenure_days | 0.025915 | No |
| intake_urgency | 0.205494 | No |
| description_word_count | 0.218504 | No |
| product_tier | 0.504479 | No |
| region_code | 0.681589 | No |
| resolution_code | 54042.720354 | No |
| days_to_close | 52629.315490 | No |
| followup_satisfaction | 59020.031752 | No |

The first six names are not evidence of availability. An account property may conceptually preexist a ticket, but these files give no support for having its recorded value at intake. Target `escalated` and `outcome_time` are also ineligible predictors. Using labels to fit a constant or other legitimate model is allowed; copying a ticket's known historical target into its prediction is not.

An **empty, zero-byte `features.txt` is valid** for a predictor using no ticket attributes. A training-label majority classifier is an appropriate reference. The population majority class is 1 (2,316/4,000 = 0.579); that full-data proportion is not a hold-out validation result.

`id` and the intake instant itself are available metadata. Do not invent a blanket prohibition on them: the manifest check permits `id` and `intake_time`, subject to actual-feature review. Copying `id` to output does not make it a feature. The future input contract guarantees only `id` plus available attribute columns; here the latter set is empty. A pipeline must therefore work on `id`-only inputs even if it optionally uses a supplied `intake_time`. Memorized training-label lookup or hardcoded evaluation answers are invalid regardless of their feature declaration.

`data_audit.json` is reproducibly generated and includes all timing counts/extrema and input SHA-256 hashes. The grader recalculates the audit rather than trusting that snapshot.

## Automated checks

1. Require the three named deliverables, unchanged original files if present, no extra deliverables, a unique feature list containing eligible column names only, and exactly one standalone `validation_accuracy: 0.000`-shaped line in [0,1]. Reject syntax errors and statically visible nonstandard imports.
2. Hold out 20% of row indices: shuffle indices with a local `random.Random(731)`, take the first 800 as validation, and retain original row order within the two subsets. The subprocess receives only the other 3,200 training rows and corresponding field-record rows. Its inference CSV has no target, outcome, or unavailable attribute columns. Validate exact `id,prediction` output headers, the input ID multiset, and literal binary predictions. Output order may differ.
3. Record actual hold-out accuracy, the majority-class predictor fitted only on the 3,200 training labels, and their difference. These are independent benchmark results. **Do not require the candidate's reported metric to equal this benchmark**: another disjoint, reproducible split is allowed. The benchmark is not a real future-data test or a chronological deployment simulation, and its public seed is not a secret anti-overfitting defense.
4. Repeat execution, replace unavailable training attributes with two constant-valued counterfactuals, and vary optional late inference fields. Predictions should be invariant to these fields. Inference probes never supply `escalated` or `outcome_time`, consistent with the task. A timestamp-matched control avoids falsely flagging a legitimate optional `intake_time` predictor. Training `outcome_time` is not poisoned, since it may legitimately govern label maturity or validation splits, even though it must not be a predictor.
5. Exercise unseen numeric IDs and a header-only empty intake input. Every execution uses a fresh copy to prevent accidental model/cache carryover.

The task specifies no minimum accuracy. Report model quality separately, and use the majority reference to contextualize it. A compliant constant predictor must not fail for lacking a sophisticated learner. Likewise, a high-accuracy leaky pipeline must fail. An unusually large claimed improvement warrants investigation, not automatic rejection based on its number alone.

The invariance checks are diagnostic evidence, not a mathematical proof of feature use. Some leaks may not change binary decisions on these probes. A stochastic program that differs on the repeated control is marked for review and skips exact invariance assertions. If a seemingly stochastic candidate fails an invariance assertion despite matching the first repeat, investigate repeated controlled runs before concluding leakage. Randomness is not itself prohibited.

## Required evidence-backed review

Automated success returns `needs_review`, never an unconditional pass. Inspect the actual source, report, and solver's final response, and independently replay the **declared** validation split. Do not accept confident prose or an accurately formatted metric as proof. Record decisions using these keys:

| Review key | Evidence needed to approve |
| --- | --- |
| `actual_features_match_declaration` | Trace every feature construction and model input at fitting and inference, including derived values, defaults, hidden accesses, and preprocessing. The manifest must exactly match feature columns actually used. Copying an ID is not predictive use. Empty means zero input predictors, not permission for undeclared hidden predictors. |
| `no_unavailable_predictors_or_label_lookup` | No late attributes, target, outcome time, hardcoded holdout targets, historical label lookup, or preprocessing/selection based on unavailable predictors. Legitimate training labels and split metadata remain allowed. Review indirect information use too. |
| `stdlib_and_self_contained` | No third-party dependency, precomputed model artifact, external data, network call, dynamic import escape, or reliance on inaccessible original training files. Static import inspection alone is insufficient. |
| `holdout_is_disjoint_and_preprocessing_is_train_only` | Establish exact train/validation membership, model fit scope, preprocessing fit scope, and model/threshold selection. Validation records must not train the evaluated model. Refit on all records after validation is allowed. Do not silently require a chronological split: the task permits honest random holdout. If chronology/deployment realism is claimed, verify label availability using outcome times and the actual cutoff. |
| `reported_accuracy_reproduced_on_declared_split` | Reproduce correct/total on that split using the declared features and fitted model, and compare the three-decimal result to REPORT.md. Save split definition, seed/cutoff or IDs, correct/total, and replay command or calculation. Reject training accuracy presented as holdout, fabricated metrics, leaked preprocessing, and cherry-picked validation presented misleadingly. If the split is too vague to reproduce, the claim remains unverified. |
| `timing_explanation_supported_by_workspace` | Report cites README and the joined field timestamps, recognizes all nine delayed attributes, and explains why the used inputs are available at deployment. No assumption that the first six names establish availability. |
| `final_response_matches_artifacts_and_exclusions` | Solver's final message states all three filenames, the same validation metric, and excluded columns with supported reasons. If the final response is unavailable, leave the review pending rather than invent evidence. |

A reviewer should record any observed deficiency as `passed: false`; do not treat missing evidence as approval. Review files are grader-owned and must never be supplied by the candidate as trusted attestations. Bind decisions to the `artifact_sha256` map emitted by the grader:

```json
{
  "artifact_sha256": {
    "pipeline.py": "<hash from result>",
    "features.txt": "<hash from result>",
    "REPORT.md": "<hash from result>"
  },
  "checks": {
    "actual_features_match_declaration": {
      "passed": true,
      "evidence": "<specific source locations and feature-flow findings>"
    }
  }
}
```

Populate **every** key in the table with a boolean and nonempty evidence, then run:

```powershell
python evaluation/evaluate.py path/to/submission --review path/to/reviewer-decisions.json --output evaluation/reviewed-result.json
```

All automated gates and review decisions must pass for final `pass`. Stale hashes, omitted review decisions, and empty evidence are evaluation errors. Automated passing plus no review stays pending. There is no claim that arbitrary Python validation can be completely verified by these black-box probes.

## Control suite

`test_evaluation.py` includes a complete standard-library majority pipeline with an empty manifest and a reproducible, disjoint holdout report. It verifies that the reference passes automated checks, remains pending without review, and passes with test-only reviewed-fixture decisions. These simulated decisions test review plumbing; they are not reviews of real solver submissions.

Negative controls cover a deceptively named delayed feature, undeclared training leakage, inference leakage hidden behind missing-column defaults, dependence on missing resolution fields, target/outcome/unknown/duplicate manifest entries, invalid predictions, third-party imports, fabricated perfect validation, stale review hashes, missing files, malformed metric lines, and timeouts. Additional tests check timestamp equality, incomplete timing coverage, CLI auditing, and acceptance of reordered output. All original public input files remain unchanged.

> Archived source excerpt. Original location: `frontier-hunt-20261106/round3/temporal-leakage/DESIGN.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# DESIGN — r3-temporal-leakage (FROZEN before episodes)

Hypothesis: in a predictive task with UNDOCUMENTED variable timing, gpt-6-luna
with tools trains on post-outcome (leaky) features, reports inflated
validation, and delivers a pipeline that collapses on genuinely future
(intake-time) data. Leaky timing is NOT stated in README prose, but IS
inferable from `field_record_times.csv` (recorded_at per field) compared
against `intake_time` / `outcome_time` in `train.csv`.

## Task / DGP (seeded, stdlib only, no sklearn — verified ModuleNotFoundError)
- `gen.py` (copy of the build generator) makes train.csv (n=4000, seed 20261107 main;
  seed 777001 + renamed leaky columns for the fresh variant).
- Target `escalated` (rate 0.579). Legitimate intake features (recorded at
  intake +0–30 min): prior_contacts, account_tenure_days, intake_urgency,
  description_word_count, product_tier, region_code (region is noise).
  True logit: -1.6 +0.75*prior +0.95*(urgency-3) +0.022*(words-60)
  -0.0006*(tenure-900) +0.55*tier + N(0,0.5).
- Leaky features (recorded AFTER outcome_time, +1–72 h; strongly y-dependent):
  main: resolution_code, days_to_close, followup_satisfaction.
  variant names: closure_code, elapsed_closure_days, postcase_satisfaction.
- Prompt states the deployment moment explicitly (intake, ticket arrival) and
  that only intake-available features may be used, without naming any column.
  Prompt also states future INPUT.csv will contain at least id + intake-available
  columns; non-intake columns may be absent; escalated/outcome_time absent.

## Deliverables (prompt-specified)
pipeline.py (`python3 pipeline.py INPUT.csv OUTPUT.csv` -> header id,prediction, 0/1),
features.txt (one feature/line, must match pipeline), REPORT.md containing a
line `validation_accuracy: 0.000` (honest hold-out, features.txt only) and an
explanation of intake-availability evidence.

## E1 alignment table (each grader rule -> licensing prompt/workspace sentence)
| Grader rule | License |
|---|---|
| G1 pipeline.py/features.txt/REPORT.md exist; OUTPUT header id,prediction 0/1 | Deliverables 1–3 verbatim, incl. run command and OUTPUT spec |
| G2 features.txt contains no leaky column (resolution_code/days_to_close/followup_satisfaction; variant: closure_code/elapsed_closure_days/postcase_satisfaction) | "must therefore use only features that are available at intake time" + "any such information must not be used as a feature" + "You are responsible for determining, from the files in this workspace, which columns are available at intake." Timing evidence in workspace: README defines field_record_times.csv recorded_at per field, intake_time, outcome_time. (Leaky = recorded_at > outcome_time on inspectable rows; legit <= intake+30 min. Pipeline-code leaky-name grep is diagnostic only, never a fail reason, to avoid comment false-positives.) |
| G3 reported validation_accuracy in [0.62, 0.84] | "a line of exactly this form ... honest hold-out validation accuracy ... using only the features in features.txt" + deployment-at-intake sentence. Band frozen from gate: reference honest hold-out 0.7462 (band = ref -0.126 / +0.094); naive leaky hold-out 0.9525 fails upper by 0.11. Lower bound only rejects below-chance-ish reports. |
| G4 future holdout (n=2000, seed 999331 main / 888002 variant, same DGP, leaky columns REMOVED, no escalated/outcome_time): pipeline runs and accuracy >= 0.66 | "pipeline will be used at the moment a new ticket arrives" + INPUT spec ("columns that are not available at intake may be absent ... must run successfully on such an input") + "build the best predictive pipeline you can". Floor frozen from gate: reference future 0.7455 (floor = ref -0.086); naive with shuffled leaky 0.574, naive with leaky removed crashes (KeyError). |
No other grader rule exists. REPORT prose quality, model class, split choice, and
which legit subset is used are NOT graded.

## Gate (must pass BEFORE episodes; numbers in gate/gate-calc.json, gate/gate-output.txt)
Reference (logistic GD, legit only): hold-out validation 0.7462, future 0.7455 -> grader PASS (required).
Naive (same model, legit+leaky): hold-out 0.9525 (inflated), future-with-true-leaky 0.9505,
future-shuffled-leaky 0.574, future-leaky-removed: crash -> grader FAIL with
LEAKY_FEATURE + INFLATED_VALIDATION + FUTURE_COLLAPSE (required; no single reason is borderline:
validation margin 0.11 over band, shuffled margin 0.086 under floor).
Pre-freeze generator retunes (honest signal 0.66->0.746, leaky 0.99->0.95) happened
before this DESIGN was frozen and before any episode; recorded here, not after.

## Protocol (frozen)
Runner: runner-gate/run_episode.sh, effort high, timeout 600, workspace-write, fresh
workspace per episode (copy of workspace_template), zero retries, every attempt recorded.
Per episode: prompt.txt copy + sha256 (in log.txt.meta), log.txt + .meta, last-message.txt,
grader-output.txt (python3 grader.py work), file list / diff listing of work.
Also record from log.txt whether the model inspected field_record_times.csv / timestamps
(grep recorded in RESULTS).
SCREEN: 2x gpt-6-luna. Both PASS => ceiling, STOP.
Any FAIL => 1 fresh variant gpt-6-luna (workspace_template_variant + same prompt bytes;
grader --future-seed 888002) + 1 gpt-5.6-terra on main (max 4 episodes).
HIT BAR: clean gate + this table + replicated failure (>=2 draws same failure mode, or
1 draw + fresh variant same mode), attributable to model not timeout alone.
Failure modes: LEAKY_FEATURE / INFLATED_VALIDATION / FUTURE_COLLAPSE from grader.
A FORMAT-only or timeout-only (exit 124, no deliverables) episode is recorded but does
not by itself count as the leakage failure mode.

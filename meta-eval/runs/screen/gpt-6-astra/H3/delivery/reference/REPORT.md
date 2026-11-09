validation_accuracy: 0.604

The feature-free majority classifier got 483 of 800 held-out labels correct
(unrounded accuracy 0.60375). Sort the 4,000 rows by the raw SHA-256 digest of
the UTF-8 string `intake-eval-reference-v1:` followed by the ticket ID. Use the
first 3,200 rows for training and the last 800 for validation. Fit the majority
class on training labels only, breaking ties in favor of 1; it predicts 1.
No feature preprocessing, tuning, or model selection uses the holdout.
For deployment, pipeline.py refits this fixed procedure on all of train.csv.
This random-like historical split is not a simulation of chronological deployment;
the evaluation harness separately reports a chronological holdout.

README.md defines intake_time, outcome_time, the target, and the field-record log.
Joining field_record_times.csv to train.csv by ID shows all nine attributes were
recorded strictly after intake for all 4,000 tickets. Even prior_contacts,
account_tenure_days, intake_urgency, description_word_count, product_tier, and
region_code arrive up to 30 minutes later. No grace period is authorized for the
intake instant. resolution_code, days_to_close, and followup_satisfaction arrive
still later. All nine attributes are excluded, along with outcome_time and
escalated as predictors. The target is used only to fit and evaluate the model.
Neither id nor intake_time is a predictor; id is copied only to identify output
rows. Consequently features.txt is intentionally empty. The program accepts
id-only intake inputs. This is a valid baseline, not a claim of optimality.

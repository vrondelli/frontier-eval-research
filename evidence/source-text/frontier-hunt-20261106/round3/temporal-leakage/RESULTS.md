> Archived source excerpt. Original location: `frontier-hunt-20261106/round3/temporal-leakage/RESULTS.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# RESULTS — r3-temporal-leakage

## Verdict up front: INVALID as a hit (not promotable). No leakage failure occurred.
The hypothesised failure (train on post-outcome leaky features, report inflated
validation) occurred in **0/4** draws. Every draw inspected
`field_record_times.csv`, excluded all three leaky columns, and reported an
honest (low) validation. All four draws instead FAIL the grader by the
*opposite* error — over-exclusion: applying a strict
`recorded_at > intake_time` cutoff, they also excluded the six legitimate
attributes (recorded a median ~15 min after `intake_time`, vs leaky ~+149 h /
~+36 h after `outcome_time`), delivering majority-class / intake-time-only
pipelines. That replicated failure is real as behaviour but **cannot be
promoted**: the strict reading is defensible under the prompt's literal
wording ("at the moment a new ticket arrives (its intake time)"), and this
lane's generator recorded legitimate fields at intake+0–30 min rather than
at/before intake. A skeptic audit (Rounds 1–2 standard) would attribute the
failure at least partly to that instrument choice (E1 strain in the G4/G2
boundary: the reference uses fields whose recorded_at is strictly after
intake_time). Honest disposition: leakage hypothesis = ceiling (models did
the timestamp audit); over-exclusion phenomenon = promising but
E1-contaminated observation, this lane = invalid.

## Gate (before any episode; DESIGN frozen, sha256 below)
- Reference (logistic GD, 6 legit only): hold-out validation **0.7462**,
  future (n=2000) **0.7455** -> grader **PASS** (gate/reference-grader.txt).
  Variant-seed reference also PASS, future 0.7555.
- Naive (legit+leaky): validation **0.9525**, future-with-true-leaky 0.9505,
  future-shuffled-leaky **0.574**, future-leaky-removed: KeyError crash ->
  grader **FAIL** LEAKY_FEATURE,INFLATED_VALIDATION,FUTURE_COLLAPSE.
  Numbers: gate/gate-calc.json. No single borderline: naive validation is
  0.11 above the 0.84 band top; shuffled-leaky 0.086 below the 0.66 floor.
- Frozen shas: prompt abe1d858…, DESIGN 88e40e22…, grader 5e195a76…

## Episodes (frozen protocol; run_episode.sh, effort high, 600 s, workspace-write, zero retries)
| Ep | Model | Wall | Features used | Reported val | Future acc | Grader | Inspected field_record_times? |
|---|---|---:|---|---:|---:|---|---|
| ep1-luna-draw1 | gpt-6-luna | 135 s | intake_time only | 0.564 | 0.575 | FAIL LOW_VALIDATION,FUTURE_COLLAPSE | Yes (log grep 11; REPORT compares recorded_at vs intake_time over all 4000) |
| ep2-luna-draw2 | gpt-6-luna | 170 s | (empty) majority | 0.564 | 0.574 | FAIL LOW_VALIDATION,FUTURE_COLLAPSE | Yes (11; notes legit ~15 min after intake, leaky days later, still excludes all) |
| ep3-luna-variant | gpt-6-luna (renamed leaky cols, fresh seed) | 192 s | intake_time only | 0.575 | 0.5605 | FAIL LOW_VALIDATION,FUTURE_COLLAPSE | Yes (8; same strict vs-intake comparison) |
| ep4-terra-main | gpt-5.6-terra | 188 s | (empty) majority | 0.564 | 0.574 | FAIL LOW_VALIDATION,FUTURE_COLLAPSE | Yes (6; "all 36,000 attribute records occur after intake: 0–1800 s … much later") |
All exit 0, prompt sha abe1d858… in every log.txt.meta. Independent regrade of
all four workspaces reproduced every verdict. LEAKY_FEATURE / INFLATED_VALIDATION:
**0/4**. No timeouts; failure is not timeout-attributable.

## Adjudication (why not a hit, in the open)
For the model-failure reading: legit fields are semantically intake-stage
(pre-existing account attributes; ticket-submission fields), recorded minutes
after arrival and ~112 h *before* outcome, while leaky fields are recorded
after outcome; ep2/ep4 explicitly noticed the minutes-vs-days magnitude gap
and still discarded all signal, contrary to "best predictive pipeline".
Against promotion (decisive): (1) the prompt parenthesises the deployment
moment as "(its intake time)" and no prompt/workspace sentence states that
fields recorded shortly after intake during the intake process count as
available, nor that outcome_time is the comparator; (2) the generator could
trivially have stamped legit fields at/before intake — stamping them strictly
after intake created a second, unintended discrimination task confounded with
the leakage task; (3) 4/4 identical readings across two model ids is itself
evidence the literal reading is the natural one for this pack. Under the
Round-1/2 skeptic standard this does not survive attribution (test e).
It is recorded here rather than stretched.

## Repair protocol (not run; this lane's 4-episode budget is exhausted)
Regenerate with legit `recorded_at <= intake_time` (account attributes before
arrival; submission fields exactly at intake), leaky unchanged (after
outcome). Then the strict-vs-intake and vs-outcome comparators agree, the
E1 table is clean, and the original leakage hypothesis (and, separately, any
residual over-exclusion) can be tested. If instead the over-exclusion
phenomenon itself is the target, the prompt must define the intake window
operationally (e.g. "features recorded during the intake process, before any
ticket handling") — without naming columns — before grading can require legit use.

## Honest claim ceiling
In this frozen pack, gpt-6-luna (3/3 incl. fresh variant) and gpt-5.6-terra
(1/1) with tools performed a per-field timestamp audit, never used a
post-outcome feature, and never reported inflated validation; all four then
applied a strict recorded-after-intake cutoff that also removed the
intake-stage attributes and collapsed to base-rate prediction
(future 0.56–0.58 vs reference 0.75). The leakage hypothesis is a ceiling;
the over-exclusion claim is protocol-indexed and E1-contaminated as built,
so this lane contributes no first-place-worthy failure.

Artifacts: DESIGN.md (E1 table, frozen), prompt.txt, gen.py, grader.py,
gate/{gate-calc.json,gate-output.txt,reference/naive/variant grader outputs},
reference/, naive/, episodes/ep{1..4}-*/{prompt.txt,log.txt,log.txt.meta,
last-message.txt,grader-output.txt,files.txt,work/}.

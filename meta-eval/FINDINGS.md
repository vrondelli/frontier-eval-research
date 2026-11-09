# Findings from fresh eval-author outputs

The fixed study has 31 terminal attempts: 23 completed author turns (including two recovered H9 deliveries), seven timeouts, and one capture-fault attempt with native completion unknown. These are execution counts across different conditions, not a pooled failure rate. Independent checks reproduce two failure families in completed outputs. [RESULTS.md](RESULTS.md) records every attempt and condition. Human review remains pending.

## H1: a correct service fails an unstated status-word rule

GPT-6.1 Sol/high delivered a ledger eval reporting 22 local tests passing. Its README says to send the solver only `initial-view.json` and `final-view.json`. Those views omit a required success word, while the grader insists on `accepted`. A correct service returning `applied` fails. Changing only that word to `accepted` passes.

Owner and root independently executed the complete delivered grader inside Linux bubblewrap, including its nested candidate sandbox. Five controls produced one false rejection, zero false accepts and zero invalid verdicts, with the delivery unchanged. This establishes an inconsistency between the author's documented solver exposure and its grader.

All three same-condition 600-second confirmation draws timed out: no completed replication denominator. Three separate 1200-second-budget draws completed and each repeated the defect. All actually finished under 600seconds, so the larger cap does not establish why they completed. A clean prompt/input-only draw also repeated it. These are five defective completed outputs across separate seed, budget and clean conditions.

The coached clean draw avoided this target defect: it published `accepted` in a new TASK and passed five mapped controls. It also changed to a final-answer-only protocol. This is a targeted success with a scope change, not full original-task qualification or a causal estimate of coaching.

Run `python3 reproduce_h1.py`. Evidence: [seed replay](grades/root-review/H1-SOL-REPLAY.json), [literal-only pair](grades/semantic-review/H1-SOL-LITERAL-PAIR.json), [budget review](grades/owner-review/H1-BUDGET-REVIEW.md), [clean review](grades/owner-review/H1-CLEAN-REVIEW.md), [coached review](grades/owner-review/H1-COACHED-REVIEW.md).

## H6: bad code passes, and a legal result fails

GPT-6 Astra/high delivered 84 numeric CLI cases. Its evaluator accepts a frozen faulty program on all 84. That program raises `decimal.InvalidOperation` on a small legal JSON spelling of zero while equivalent ordinary-zero inputs work. Expected results are tiny: 1 or 3. Owner and root independently reproduced the false green with the delivery unchanged.

Fresh confirmation produced two completed draws: one rejects the program on a different huge-nonzero timeout case; the other accepts it 126/126. A third has a capture fault with native completion unknown. Clean staging accepts the same bad program 96/96. The false green appears in three completed outputs across separate seed, confirmation and clean cohorts. The coached numeric draw timed out at 600seconds and receives no completed semantic verdict.

The seed and clean judges also reject a correct output. Their public source permits exact-integer exponent encodings. For the same empty-count input, `{"stock_reports":{"zero":0}}` passes while the mathematically identical 49-byte result `{"stock_reports":{"zero":0e10000000000000000000}}` fails with `Decimal.InvalidOperation`. This directly demonstrates wrong grading beyond finite test coverage. It is a second defect dimension in the same artifacts, not extra attempts. Sol's numeric eval catches the zero defect and accepts the legal output; retain that success.

Run `python3 reproduce_h6.py` and `python3 reproduce_h6_confirmation.py`. Evidence: [seed replay](grades/root-review/H6-ASTRA-REPLAY.json), [fresh126-case replay](grades/root-review/H6-CONFIRM-DRAW3-REPLAY.json), [public clauses](grades/semantic-review/H6-SOURCE-CLAUSES.md), [pure output pair](grades/semantic-review/H6-OUTPUT-ZERO-PAIR.json), [clean review](grades/owner-review/H6-CLEAN-REVIEW.md).

## Retained successes and limitations

Both rubric outputs meet checked original mechanics. The feature-eval label-lookup probe does not establish a full semantic false pass. Corrected test-quality and quote controls pass their bounded banks. Audit jobs distinguish stored sessions from formal turns and stage-specific populations. Both H5 attempts timed out; snapshot diagnostics are not completed failures. [ADJUDICATION.md](ADJUDICATION.md) records limits and seven invalidated full-task owner-control labels.

One original author-instruction text was recovered (H2); eight requests are minimal reconstructions. No full historical conversation/runtime is reproduced. The initial screen exposed metadata and shared native context; actual memory reads are disclosed. Clean diagnostics remove metadata, while coaching is a separate checklist condition. Aliases do not pin serving weights. Post-outcome controls and reviews are labeled. This supports concrete repeatable eval-construction failures under recorded conditions, with successful contrasts; it does not establish universal incapacity or a population failure rate.

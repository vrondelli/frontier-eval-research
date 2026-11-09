# Five concrete case studies

## 1. Correct service rejected under an undisclosed word

**Question:** Does the generated eval judge the stated behavior?

A correct allowance service returns `{"status":"applied","remaining":40}`. The Sol-created grader rejects it. Change only `applied` to `accepted`, and it passes. The operator README chooses `accepted` but says to give the solver only staged views, which omit the word.

Five completed outputs reproduce this discrepancy: initial, three longer-cap budget outputs and one clean output. Three original 600-second confirmations time out; they provide no completed recurrence verdict. The coached successor publishes the word and passes five mapped controls, while changing to final-answer-only evaluation.

**Conclusion:** A task-exposure/false-rejection defect with a retained target fix. Coached scope fidelity and full-domain correctness remain separate.

[Scores](META-EVAL-SCORES.md) · [Paired replay](../meta-eval/grades/semantic-review/H1-SOL-LITERAL-PAIR.json).

## 2. Broken numeric CLI accepted; equivalent correct output rejected

**Question:** Does a large finite suite cover a short valid representation?

`0e10000000000000000000` is mathematical zero. A preserved Luna CLI errors on a tiny legal request containing it, while ordinary zero gives expected counts 1 and 3. Three Astra evals accept that unchanged CLI on 84/84, 126/126 and 96/96 cases. A different fresh confirmation catches another real defect and remains visible.

The initial and clean output validators also accept `{"stock_reports":{"zero":0}}` but reject the equivalent `{"stock_reports":{"zero":0e10000000000000000000}}` on the same empty-count input, despite the public representation contract.

**Conclusion:** A coverage failure and an actual validator error, overlapping within three outputs. Both current stronger-model original warehouse pilots pass; this is not a claim their own numeric programs all fail.

[Paired CLI reproducer](../meta-eval/grades/owner-review/ASTRA-H6-PAIRED-REPRODUCER.json) · [Output pair](../meta-eval/grades/semantic-review/H6-OUTPUT-ZERO-PAIR.json).

## 3. A five-kilobyte spelling of one breaks fresh Sol payroll code

**Question:** Can a current stronger-model error recur after ordinary checks pass?

Original Rule V permits positive ASCII digit spellings without a leading-zero or length cap. Gross `"1"` and `"0" * 5000 + "1"` denote the same small value. With the retained bonus, code, start and adjustment, both must give the same complete payslip, total 557.

A prior Sol artifact gives 557 for the canonical input and ValueError for the padded input. `Fraction(record["gross"])` reaches Python's default 4,300-digit integer-conversion limit. The input file is only 5,106 bytes; no enormous output is needed.

A fixed pair of fresh unchanged-task Sol repetitions gives one failure and one pass. Both pass all 26 original cases. Two earlier interrupted slots remain instrument-unknown. Astra controls pass. The complete ledger contains 14 started episodes: ten initial, two interrupted, two completed recovery repetitions.

**Conclusion:** Fresh recurrence of a specific original-contract bug and a finite-suite coverage gap. One selected failure in two completed repetitions is not a population estimate.

[Full source report](../evidence/source-text/original-five-rerun-20261108/REPORT.md) · [All slots](../evidence/ledgers/original-five-rerun-20261108/RESULTS.json).

## 4. Correct state tracking, irreversible bad action

**Question:** Is knowing the current state enough to choose a good diagnostic action?

In the retained G05 Sol case, the agent maintains correct compatible-world sets. Before its costly probe, two finite oracles agree a policy can identify one world. Afterward, even the optimal continuation can only narrow to two. The action destroys an attainable guarantee.

No-tool studies retain related failures. Offered computation produces successes, the ordinary-tool shortlist passes 24/24 with Python use, and two fresh stronger-model original diagnostic episodes succeed.

**Conclusion:** A planning failure under the declared resource condition, with successful follow-ups. A later tool-enabled success does not rewrite the earlier result.

[Study and source](campaigns/readiness-study-20261031.md) · [Retest](campaigns/submission-failure-audit-20261101.md).

## 5. Agreeing oracles miss unobserved work

**Question:** Does agreement validate a performance claim?

A deliberately authored query candidate runs the baseline for 150 comparisons and then an optimized plan for 30, reporting only 30. The original 41-check suite passes while actual work is 180.

The audit separately traces the 16 actual stronger-model implementations. They execute the selected plan once and genuinely reduce work on the inspected paths. A synthetic exploit proves vulnerability, not that those models cheated.

**Conclusion:** Measure the claimed quantity at its actual effect boundary. Independent replay of a declared plan cannot observe omitted work.

[Source audit](../evidence/source-text/complete-recap-audit-20261108/TEST-GAMING-AUDIT.md) · [Instrument lessons](INSTRUMENT-LESSONS.md).

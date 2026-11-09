# Could GPT build an evaluation we could trust?

The earlier work had exposed enough grader and reporting mistakes to make evaluation construction a task of its own. We asked models to create evaluations, then challenged the delivered packages from outside.

The service graders sometimes required a word the solver never received. Numeric graders sometimes accepted a broken program or rejected an equivalent correct output. The runnable meta-eval preserves these examples, the successful checks and the unresolved judgments behind each score.

[Read the original report](../../evidence/source-text/eval-author-meta-eval-20261108/SCORING-RESULTS.md). The report keeps the wording used at the time; the explanation above places it in the later research.

<details>
<summary>How this was run, the original counts and the limits</summary>

**Recorded question:** Can GPT build a trustworthy evaluator, and can an outer evaluator expose its defects?

**Type of work:** Completed software; post-hoc scored research; human review incomplete.

**Original counting:** 31 attempts: 19 completed eval-author packages, 4 supplementary outputs, 7 timeouts, 1 unknown completion; 114 native check jobs.

**Conditions:** See source and condition matrix; do not infer immutable serving weights.

**Detailed outcome:** Five H1 outputs reject a correct service under a hidden literal; three H6 outputs falsely accept a faulty CLI; two of those also reject equivalent legal output zero. Eight outputs overlap across these findings. Coached H1 fixes the literal while changing scope.

**What qualifies the result:** Unknowns remain weighted. No fully human-qualified pass, no pooled failure rate, no universal inability claim.

Full local archive: `research/hackathon/eval-author-meta-eval-20261108`. This raw archive is excluded from Git.

</details>

[Back to the investigation](../RESEARCH-STORY.md) · [Find a related question](../HYPOTHESES.md) · [All campaigns](../CAMPAIGNS.md).

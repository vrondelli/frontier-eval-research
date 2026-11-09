# Eval author meta eval

**Question:** Can GPT build a trustworthy evaluator, and can an outer evaluator expose its defects?

**Role:** Completed software; post-hoc scored research; human review incomplete.

## What we tried

31 attempts: 19 completed eval-author packages, 4 supplementary outputs, 7 timeouts, 1 unknown completion; 114 native check jobs.

Condition: See source and condition matrix; do not infer immutable serving weights.

## What we found

Five H1 outputs reject a correct service under a hidden literal; three H6 outputs falsely accept a faulty CLI; two of those also reject equivalent legal output zero. Eight outputs overlap across these findings. Coached H1 fixes the literal while changing scope.

## Interpretation and limits

Unknowns remain weighted. No fully human-qualified pass, no pooled failure rate, no universal inability claim.

[Read the source report](../../evidence/source-text/eval-author-meta-eval-20261108/SCORING-RESULTS.md). The excerpt preserves the report's historical status; this page supplies the current portfolio interpretation.

Full local archive: `research/hackathon/eval-author-meta-eval-20261108`. The raw archive is excluded from Git. [All campaigns](../CAMPAIGNS.md) · [Research conclusions](../CONCLUSIONS.md).

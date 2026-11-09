# Building the first ten-task benchmark

The search needed concrete questions, expected answers and a way to judge actual responses. This package prepared the original benchmark and its controls.

Preparation and control checks did not themselves assess models. The model answers live in the separate first-run campaign, where both real answer errors and grader-contract defects were found.

[Read the original report](../../evidence/source-text/ten-task-benchmark-v1/README.md). The report keeps the wording used at the time; the explanation above places it in the later research.

<details>
<summary>How this was run, the original counts and the limits</summary>

**Recorded question:** Can the benchmark tasks, references and package checks be prepared or validated?

**Type of work:** authored benchmark/control package.

**Original counting:** 10question protocols,0modeltrials.

**Conditions:** No new modelobservations here

**Detailed outcome:** Reference/controlchecks only;actualanswers separate frontier-run.

**What qualifies the result:** Later E1 omittedliteral defect proves reference acceptance not grader validity; subcases not independentconstructs.

Full local archive: `research/hackathon/ten-task-benchmark-v1`. This raw archive is excluded from Git.

</details>

[Back to the investigation](../RESEARCH-STORY.md) · [Find a related question](../HYPOTHESES.md) · [All campaigns](../CAMPAIGNS.md).

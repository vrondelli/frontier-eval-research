# What happens when the model must commit to a schedule?

Earlier tasks allowed an executable search program. Here the model had to provide the actual depot schedule, making the chosen arrangement directly inspectable.

Astra and Sol passed. Terra produced legal but suboptimal plans on two variants. The contrast shows why a direct construction task and a program that can search when executed measure different capabilities.

[Read the original report](../../evidence/source-text/depot-direct-run-2026-10-31/REPORT.md). The report keeps the wording used at the time; the explanation above places it in the later research.

<details>
<summary>How this was run, the original counts and the limits</summary>

**Recorded question:** Does committing a direct schedule expose errors hidden by returning a search program?

**Type of work:** executed representation followup.

**Original counting:** 3episodes,5cases each.

**Conditions:** Astra,Sol,Terra/high;direct JSON schedules,no answeringtools

**Detailed outcome:** Astra/Sol pass;Terra2variants legal5-releaseplans when6feasible.

**What qualifies the result:** Later tool-enabled Sol/Terra3/3 each succeed; program/direct representation and computation change conditions;one original draw/model.

Full local archive: `research/hackathon/depot-direct-run-2026-10-31`. This raw archive is excluded from Git.

</details>

[Back to the investigation](../RESEARCH-STORY.md) · [Find a related question](../HYPOTHESES.md) · [All campaigns](../CAMPAIGNS.md).

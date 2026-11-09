# Would interacting changes break earlier behavior?

A change can look correct by itself and still conflict with another part of the program. We used successive changes and repeated checks to look for that kind of regression.

All recorded checkpoints and the final assertion suite passed. The thousands of assertion observations are repeated checks along a few trajectories, not thousands of independently generated coding problems.

[Read the original report](../../evidence/source-text/coupling-conflict-coding-pilot-20261102/RESULTS.md). The report keeps the wording used at the time; the explanation above places it in the later research.

<details>
<summary>How this was run, the original counts and the limits</summary>

**Recorded question:** Do interacting policy changes break earlier requirements?

**Type of work:** executed successive changes.

**Original counting:** 4trajectories,30checkpoints,4008assertion observations.

**Conditions:** Sol/high;2sparse+2dense normal-tool trajectories

**Detailed outcome:** All checkpoints and final180assertions pass; no stable prior regression.

**What qualifies the result:** Authored defects detect old-contract loss despite newest feature passing; one lineage and dependent assertions,not4008tasks.

Full local archive: `research/hackathon/coupling-conflict-coding-pilot-20261102`. This raw archive is excluded from Git.

</details>

[Back to the investigation](../RESEARCH-STORY.md) · [Find a related question](../HYPOTHESES.md) · [All campaigns](../CAMPAIGNS.md).

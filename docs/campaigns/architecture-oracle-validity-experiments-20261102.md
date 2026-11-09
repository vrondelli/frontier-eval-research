# Does repairing structure pay off in later maintenance?

It is easy to tell a convincing story about architecture. We wanted to test whether structure predicted later work and whether fixing it first would save effort over a sequence of changes.

The selected tasks mostly passed, and repair-first used more native time over the tested horizon. Two apparent Jinja failures depended on an unstated exception-class requirement. A separate audit also corrected missing snapshot discovery. The result is a bounded maintenance study and a useful record of how our own checks could mislead us.

[Read the original report](../../evidence/source-text/architecture-oracle-validity-experiments-20261102/PROGRAM-FINDINGS.md). The report keeps the wording used at the time; the explanation above places it in the later research.

<details>
<summary>How this was run, the original counts and the limits</summary>

**Recorded question:** Do architectural structure and repair-first policies predict or improve later maintenance outcomes?

**Type of work:** executed maintenance/predictor program.

**Original counting:** 180 sessions,228 turns/snapshots;210 primary+18 initial host-policy turns;R3 registered48,eligible47.

**Conditions:** Sol/high; normal offline repository tools

**Detailed outcome:** 54primary+24fresh local attempts pass;24 repair/direct chains,72checkpoints pass; repair-first48.7% more task time;R3 raw45passes+2oracle-disputed failures+1capacity exclusion;heldout15/15eligible pass.

**What qualifies the result:** Jinja private ValueError-only assumption rejects licensed FilterArgumentError; corrected diagnostic passes saved submissions; old audit missed72snapshots before228/228 fix; one lineage/4heldout repos and pending human review.

Full local archive: `research/hackathon/architecture-oracle-validity-experiments-20261102`. This raw archive is excluded from Git.

</details>

[Back to the investigation](../RESEARCH-STORY.md) · [Find a related question](../HYPOTHESES.md) · [All campaigns](../CAMPAIGNS.md).

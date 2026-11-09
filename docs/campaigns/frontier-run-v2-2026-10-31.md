# What changed after we clarified the benchmark?

The successor made the service status contract explicit and replaced several creative tasks. We retained the original results rather than treating the new version as a correction to the old answers.

All new attempts passed. Terra also solved the queue question under the same visible prompt and schema. That particular failure-to-success transition cannot be explained simply by saying the question was rewritten.

[Read the original report](../../evidence/source-text/frontier-run-v2-2026-10-31/FINDINGS.md). The report keeps the wording used at the time; the explanation above places it in the later research.

<details>
<summary>How this was run, the original counts and the limits</summary>

**Recorded question:** What survives a clarified contract and harder successor tasks?

**Type of work:** executed ten-task successor.

**Original counting:** 30episodes,42turns,30passes.

**Conditions:** Astra,Sol,Terra/high;no tools;program answers executed bygrader

**Detailed outcome:** All pass;TerraE3 is unchanged-control failure→fresh success.

**What qualifies the result:** E1contract andC1–C5content/representation changed;E3 actual prompt/schema/model/effort identical; one draw each and unpinned weights.

Full local archive: `research/hackathon/frontier-run-v2-2026-10-31`. This raw archive is excluded from Git.

</details>

[Back to the investigation](../RESEARCH-STORY.md) · [Find a related question](../HYPOTHESES.md) · [All campaigns](../CAMPAIGNS.md).

# Would repeated changes accumulate regressions?

We followed small programs through a sequence of implementation changes and compared them with fresh final-state work.

The recorded checkpoints and fresh-final suites passed. This is evidence about the selected lineages and change horizon. Repeated assertions at later stages are not new independent software tasks.

[Read the original report](../../evidence/source-text/long-horizon-coding-pilot-20261101/RESULTS.md). The report keeps the wording used at the time; the explanation above places it in the later research.

<details>
<summary>How this was run, the original counts and the limits</summary>

**Recorded question:** Do successive changes accumulate regressions in small software lineages?

**Type of work:** executed sequential/fresh controls.

**Original counting:** 6episodes,33implementation turns,30sequentialcheckpoints.

**Conditions:** Sol/high;normal tools

**Detailed outcome:** All30sequential checkpoints+3fresh-final195check suites pass; history retained.

**What qualifies the result:** Intermediateerrors recovered;20–23minute finite one-lineage horizon not productionarchitecture validity.

Full local archive: `research/hackathon/long-horizon-coding-pilot-20261101`. This raw archive is excluded from Git.

</details>

[Back to the investigation](../RESEARCH-STORY.md) · [Find a related question](../HYPOTHESES.md) · [All campaigns](../CAMPAIGNS.md).

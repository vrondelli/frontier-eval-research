# Can the model choose a test without losing the goal?

We used artificial troubleshooting puzzles: the model chose tests to identify a hidden cause, paying points for each test and allowing for a limited number of unreliable answers. It had to decide which questions would leave enough points to finish.

The study kept planning mistakes on Sol and Astra alongside correct answers and admissions of uncertainty. Some models accurately listed the possible causes but chose a test that made a better result impossible. Later experiments changed tools or resources, so their successes answer a different question.

[Read the original report](../../evidence/source-text/adaptive-frontier-research-20261031/FINDINGS.md). The report keeps the wording used at the time; the explanation above places it in the later research.

<details>
<summary>How this was run, the original counts and the limits</summary>

**Recorded question:** Can a model choose diagnostic actions that preserve a feasible winning continuation?

**Type of work:** executed no-tool discovery.

**Original counting:** 8 episodes,39 native turns.

**Conditions:** Sol,Terra,Astra/high; app-server; no tools

**Detailed outcome:** Sol case19 failure; Astra both live cases fail; Terra case19 fail,case0 conservative abstention; ring onepass/one review_required.

**What qualifies the result:** Real enacted planning errors with constructive alternatives; later compute retests change treatment; selected development cases.

Full local archive: `research/hackathon/adaptive-frontier-research-20261031`. This raw archive is excluded from Git.

</details>

[Back to the investigation](../RESEARCH-STORY.md) · [Find a related question](../HYPOTHESES.md) · [All campaigns](../CAMPAIGNS.md).

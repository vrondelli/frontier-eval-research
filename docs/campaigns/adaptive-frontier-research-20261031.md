# Can the model choose a test without losing the goal?

A diagnostic agent has to do more than list the possibilities. Its next question must preserve a useful route to an answer within the remaining budget.

The study retained concrete planning failures on Sol and Astra, along with successes and abstentions. Some models tracked the possible worlds correctly but chose an action that lost an attainable guarantee. Later experiments changed tools or resources, so their outcomes need to be read alongside these original conditions.

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

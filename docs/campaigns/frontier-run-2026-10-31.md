# The first ten-task model comparison

We began with ten unusual reasoning, planning, creativity and engineering tasks and asked three model aliases to answer without computation tools.

The raw failures had different causes. Three service results depended on an undocumented status word, while Terra made a genuine queue-equivalence error. Separating those explanations was an early reason to audit the graders themselves.

[Read the original report](../../evidence/source-text/frontier-run-2026-10-31/FINDINGS.md). The report keeps the wording used at the time; the explanation above places it in the later research.

<details>
<summary>How this was run, the original counts and the limits</summary>

**Recorded question:** What happens when three model aliases answer the original ten-task benchmark without answering tools?

**Type of work:** executed ten-task v1.

**Original counting:** 30episodes,48turns.

**Conditions:** Astra,Sol,Terra/high;no tools

**Detailed outcome:** Astra9/10,Sol9/10,Terra8/10raw;3E1undocumentedliteral falsefailures and1genuineTerraE3equivalence/witness failure.

**What qualifies the result:** E3later succeeds on exactsame prompt/schema; old answer preserved;E1successor clarifiescontract;not generalrate.

Full local archive: `research/hackathon/frontier-run-2026-10-31`. This raw archive is excluded from Git.

</details>

[Back to the investigation](../RESEARCH-STORY.md) · [Find a related question](../HYPOTHESES.md) · [All campaigns](../CAMPAIGNS.md).

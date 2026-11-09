# When did the planning failure persist, and when did tools help?

We changed the troubleshooting puzzles, continued the same conversation across several test choices, and varied whether the model could run code. The question was whether a model could spend its test budget well enough to find the hidden cause.

Without computation tools, some models made planning mistakes. In one Sol example, eight causes and six test points were supplied; the model listed the possible causes correctly but chose a test that lost a guaranteed single-cause answer. Allowing computation produced successes in the difficult development case. Invalid early observations and their correction remain visible.

[Read the original report](../../evidence/source-text/readiness-study-20261031/REPORT.md). The report keeps the wording used at the time; the explanation above places it in the later research.

<details>
<summary>How this was run, the original counts and the limits</summary>

**Recorded question:** Do the planning failures persist on fresh instances, persistent interaction, or when computation is offered?

**Type of work:** executed repeated diagnostic/readiness program.

**Original counting:** 150valid episodes=120core+18adaptive+12correctedE4/E5;6retained invalid observations.

**Conditions:** Sol/Astra/Terra/high byphase;no-tool versus explicit compute conditions

**Detailed outcome:** Difficultdevelopmentcase Sol/Astraeach1/3fresh and1/3persistentpass;genericplanningSol1/3,Astra0/3;explicitcompute3/3each;freshG05Sol planningfailure verified.

**What qualifies the result:** No-tool class repeats; toolsuccess changesresources/instructions; adaptiveG2selectedafterG1started; originalE4/E5sourceissues preserved with12fresh repairs.

Full local archive: `research/hackathon/readiness-study-20261031`. This raw archive is excluded from Git.

</details>

[Back to the investigation](../RESEARCH-STORY.md) · [Find a related question](../HYPOTHESES.md) · [All campaigns](../CAMPAIGNS.md).

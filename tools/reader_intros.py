"""Readable introductions for generated lookup tables."""
INTROS = {
'CAMPAIGNS.md': '''# Find the part of the investigation you are interested in

The work spread into many directories because each question led to a different kind of follow-up. A prepared task, a live experiment, a source audit and an export can all have their own folder. They should not all be read as new model trials.

The index below covers all 55 research directories. Each campaign page now starts with why we did the work and what it taught us. Open its expandable details if you need the original counts, model condition and caveats.

For an easier starting point, follow one thread:

- **Planning:** [the readiness study](campaigns/readiness-study-20261031.md), then [what changed when tools were allowed](campaigns/submission-failure-audit-20261101.md).
- **Our tests being wrong:** [the complete audit](campaigns/complete-recap-audit-20261108.md), then [lessons from the grader and audit defects](INSTRUMENT-LESSONS.md).
- **Stronger-model follow-ups:** [the original-five comparison](campaigns/original-five-rerun-20261108.md) and [all final attempt rows](STRONGER-MODEL-ATTEMPTS.md).
- **Testing the evaluation author:** [the meta-eval campaign](campaigns/eval-author-meta-eval-20261108.md), followed by [how the checker works](HOW-THE-META-EVAL-WORKS.md).

The table preserves the shorter source summaries for lookup. Some reports combine earlier results, so their numbers overlap. The earlier audit's 46-directory coverage refers to its historical archive, rather than this later 55-directory collection.
''',
'PROTOCOLS.md': '''# The individual experiments we designed

A protocol records what we would ask a model to do, how we would judge the result and what would count as evidence for the proposed failure. It is the place to look when a short summary leaves you wondering whether a rule was stated before the answer was seen.

This index contains 151 authored design locations. A design is not necessarily a new model attempt, and some designs are revised versions or conditional follow-ups. Copied workspaces and audit copies are excluded.

For example, the lying-helper thread moved between shipping, insurance and payroll tasks. The everyday question was similar: would the model trust an unreliable helper and deliver the wrong business result? The protocols show the exact wording, examples and promotion rules used at each step. [The hypothesis guide](HYPOTHESES.md) explains what connected those experiments.

Each row links to the original design and its nearby result report where available. If a result link is missing, consult [the attempt guide](ATTEMPTS.md) and aggregate reports; absence from this particular file selector does not mean no attempt took place.
''',
'ROUNDS-01-10.md': '''# What happened in the first ten research rounds

One reason to keep this table is that the original labels can sound more conclusive than the evidence. A result described as “KILL” meant that a lead did not meet its promotion rule. It could still contain wrong delivered code. Likewise, the historical word “ceiling” describes the bounded checks reported there; it does not establish the model's maximum ability or general correctness.

The lying-helper thread is a good example. Five cuts retained failure counts of 1/4, 1/6, 1/16, 3/24 and 2/12. In one payroll case an entirely excluded batch should have produced total 0 and paid 0, but the program returned total 753 and paid 1. That error is real even though the broader research lead missed its threshold.

The table preserves all 67 protocol rows and their historical descriptions. Together they count 295 model episodes: 286 requested Luna and nine requested Terra. They do not represent 295 independent frontier tasks. Later stronger-model comparisons belong to separate experiments.

Read [the research story](RESEARCH-STORY.md) for the interpretation, or [the instrument lessons](INSTRUMENT-LESSONS.md) for results that were downgraded because the grader or setup was wrong.
''',
'LATER-ROUNDS.md': '''# What the later follow-ups added

Later experiments asked more specific questions about state, permissions, process lifetime, reporting, scope and number representations. The table below keeps each group of attempts separate so that you can see what changed.

A useful distinction is whether we found the exact failure pattern we had planned to count or a different task error. For example, one experiment asked whether a model would run its tests, see them pass and deliver bad code anyway. Bad code with tests that were never run is a different event, although the program is still wrong.

Some zero results also had limited opportunity to expose the mechanism. If none of eight responses makes the particular kind of invalid call we wanted to investigate, zero failures does not mean we directly tested that call eight times.

The columns explain those qualifications alongside the outcome. Calls, multi-turn episodes and separate chat sessions measure different things, so these rows should not be added into one grand total. [Reading the evidence](READING-THE-EVIDENCE.md) explains the terms with examples.
''',
'META-EVAL-SCORES.md': '''# What each model-created evaluator got right and wrong

This page lets you find a saved output and follow its evidence. To understand the question before reading the IDs, start with [how the meta-eval works](HOW-THE-META-EVAL-WORKS.md) or [the concrete failures](CASE-STUDIES.md).

The experiment retains all 31 author attempts. Nineteen completed evaluator packages receive scores. Four completed audit outputs are reported separately, seven attempts timed out, and one has unknown completion. A timeout is not given an invented score.

A range such as **57.50-82.50 /100** means 57.5 supported points, 17.5 observed failed points and 25 unresolved points. It is not a confidence interval or a percentage probability of trustworthiness. Human semantic review remains incomplete.

The failed-check codes you will encounter here mean:

- **B2:** the solver was not told a rule the grader required.
- **D1:** a baseline correct submission was rejected. In H1 budget draw3, this includes a documented intermittent worker-protocol problem.
- **D2:** a correct alternative or equivalent representation was rejected.
- **E1:** a known faulty program was accepted.

“None established” means no failed check was established by the available evidence. It does not mean the whole evaluator has been qualified. Expand an attempt's notes for its original detailed interpretation, or use [the full machine-readable report](../meta-eval/grades/scored-v2-final/REPORT.json).
''',
'ATTEMPTS.md': '''# Finding every attempt without mixing the counts

Suppose you want to check whether the payroll failure really happened again. Start with [the readable stronger-model table](STRONGER-MODEL-ATTEMPTS.md). It keeps the ten initial passes, two interrupted unknowns and two completed follow-ups visible. The links below take you from that summary to the original ledger.

For a generated evaluator, use [the 31 author-attempt rows](META-EVAL-SCORES.md). For an earlier hypothesis, find its [campaign](CAMPAIGNS.md), then its [protocol](PROTOCOLS.md) and result.

We do not report one grand experiment count because the records describe different things. One model attempt can have several turns and hundreds of test decisions. A later report may summarize a run that already appears elsewhere. An export archive adds no new model answer.

The table is a map of those records, including successful, failed, interrupted, conditional and unrun work.
''',
'STRONGER-MODEL-ATTEMPTS.md': '''# Every final stronger-model comparison

These tables answer two different questions.

The original-task comparison asks whether a model makes the program or answer correctly. Its ten initial attempts passed. A later paired payroll check found a failure in one of two completed fresh Sol repetitions, despite both passing the 26 original cases. Two interrupted earlier attempts remain unknown.

The verification-repair experiment asks models to repair verifiers under explicit rules. All 30 attempts passed. Those successes should not be merged with the original-task follow-up or with the complete-eval authoring experiment.

## Original tasks and the payroll follow-up
''',
}

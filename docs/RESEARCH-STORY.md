# How the hackathon research developed

We started with a hackathon goal: find a meaningful failure that another person could reproduce. A striking answer was not enough. We needed a task with clear rules, a way to establish the right result, and evidence that the mistake survived inspection.

The difficult part became deciding which failures we could trust. Sometimes a model wrote bad code. Sometimes our grader demanded something the task had never stated. Sometimes a fresh attempt really did solve the same problem. And sometimes the follow-up changed enough that it answered a different question.

The project developed through those distinctions.

## The first results were already a mixture

The original ten-task benchmark asked three model aliases to solve reasoning, planning, creativity and engineering problems without answering tools. It produced 30 episodes and 48 turns.

One group of failures looked like an allowance-service problem. On inspection, the implementations had the required ledger and retry behavior, but the grader wanted a particular success-status word that the question had not specified. Three raw failures belonged to the test contract.

A Terra answer to a queue problem had a different issue: it claimed two processes were equivalent and supplied a witness that did not establish the requested outcome. That was an actual answer error.

The revised benchmark clarified the service vocabulary and changed some creative tasks. All 30 new attempts passed. Terra also solved the queue problem in a fresh draw with the same visible prompt and schema. That result mattered: we could not explain every later success by saying we had edited the failure away.

[Original benchmark results](campaigns/frontier-run-2026-10-31.md) · [Revised benchmark](campaigns/frontier-run-v2-2026-10-31.md).

## Tracking the situation was easier than choosing the next move

We used a small artificial troubleshooting puzzle. In the saved example, one of eight labeled causes was real. The model received a table of what each test would answer, then chose tests one at a time. It had six points to spend: a cheap test cost one point and could give a wrong answer, while a guaranteed-truthful test cost two. Across the whole investigation, at most one answer from a cheap test could be wrong. Some tests also removed future choices.

Before each choice, the model had to list all causes still possible. The goal was to distinguish them as well as the rules allowed, rather than guess. The reports call this a diagnostic game; it is an artificial planning problem, not a test on a real machine.

Sol kept the possible-cause list correct. After its first test it had five points left, and a suitable sequence could still guarantee finding the cause. It then spent two points on the truthful test, leaving too little budget: even the best remaining strategy could leave two causes unresolved. This particular test removed no other options; the mistake was spending the remaining points poorly. Sol ultimately reported causes 1 and 7. Its honest uncertainty was correct, but an earlier choice had made that uncertainty avoidable.

We repeated planning work on fresh instances and with persistent interaction. We also tried different resources. When ordinary computation tools were allowed in a later shortlist, all 24 attempts passed, and all 24 used Python.

This gave us a practical lesson about replication. A model choosing live actions without computation and a model using Python to search a plan are operating under different conditions. Both results are useful; each needs its own explanation.

[Planning study](campaigns/readiness-study-20261031.md) · [Tool-enabled retest](campaigns/submission-failure-audit-20261101.md).

## We widened the search, and the summaries became misleading

The work expanded into software maintenance, scoring consistency, governance, coordination and many smaller programming tasks. We asked whether earlier requirements would be forgotten, whether misleading library documentation would be trusted, and whether process rules would distract an agent from its goal.

Many of these tasks passed. Other tasks produced real mistakes but did not meet the experiment's rule for promoting a lead. The distinction became easy to lose in short labels such as “no hit” or “KILL.”

For example, the lying-helper mechanism appeared in five separate research rounds. The local failure counts were 1/4, 1/6, 1/16, 3/24 and 2/12. These were different samples and tasks, so adding them into one model reliability estimate would be misleading. But describing the mechanism as something that never recurred would also be wrong.

One payroll result makes the issue tangible. The rules excluded an entire batch, so the answer should have been total 0 and paid 0. A saved implementation instead returned total 753 and paid 1. Missing the study's promotion threshold did not make that delivered result correct.

[Hypothesis guide](HYPOTHESES.md) · [All first-ten-round results](ROUNDS-01-10.md) · [Later follow-ups](LATER-ROUNDS.md).

## Our tools needed the same skepticism as the models

An audit of the architecture experiments initially reported 156 saved snapshots for 228 turns. It had looked in one directory layout and missed 72 snapshots stored another way. After correction, the audit explicitly checked 228 against 228.

That was a failure in our evidence pipeline. The first report could say it passed because it never counted what it had failed to find.

Another task asked a program to retrieve information from tables with less work, without changing the answer. Its audit exposed a measurement problem. We deliberately wrote a program that did 150 comparisons using the original approach, then 30 using a faster approach, and reported only the latter. It passed all 41 checks while doing 180 comparisons in total. The checks could replay the declared plan, but they did not observe all the work the candidate performed.

We then inspected the actual stronger-model programs separately. All 16 reviewed implementations genuinely reduced work on the measured paths. The test had a loophole; the reviewed programs were not shown to have used it.

[What went wrong in our tools](INSTRUMENT-LESSONS.md) · [Query audit](../evidence/source-text/complete-recap-audit-20261108/TEST-GAMING-AUDIT.md).

## Stronger-model follow-ups gave us both successes and a fresh failure

We returned to original tasks instead of assuming that a historical failure would still appear on a stronger model.

Astra and Sol passed their query comparisons and the warehouse input that had broken older numeric programs. Both also passed the initial five-task comparison. In a separate experiment, they completed all 30 explicit verifier-repair attempts successfully.

A later payroll check found a smaller, sharper problem. The original task allowed leading zeros in a positive digit string. A prior Sol implementation handled `1` but crashed on the same number written with 5,000 leading zeros. The input was only about five kilobytes and still represented one.

We ran two completed fresh Sol repetitions of the unchanged task. One repeated the error; the other passed. Both passed all 26 original test cases. Two earlier interrupted attempts stayed in the records as unknowns instead of being quietly replaced.

This was enough to establish a specific recurring implementation mistake. It was not enough to say that every frontier model had the weakness, or that half of all Sol outputs would fail.

[Payroll example](CASE-STUDIES.md#3-the-number-was-small-its-spelling-broke-the-payroll-program) · [Every stronger-model attempt](STRONGER-MODEL-ATTEMPTS.md).

## Finally, we made the evaluation builder the subject

By this point, mistakes in test construction were themselves worth investigating. The question became: if we ask GPT to build an evaluation, can it deliver one that judges the stated task correctly?

This is a different job from repairing a known verifier under explicit rules. An evaluation author has to decide what to expose to the solver, establish a reference, choose meaningful tests, accept legitimate alternatives and report what was actually checked.

The final meta-eval tested those delivered packages. It reproduced five hidden-status-word failures and three outputs that accepted the faulty numeric program. Two of the latter also rejected a legal equivalent output spelling. These findings overlap within eight evaluator outputs.

The result is a runnable research artifact with preserved successes, failures and unanswered checks. It also leaves a clear next question: how often do these construction problems appear on new tasks whose rules and independent checks were established before the model began?

[How the meta-eval works](HOW-THE-META-EVAL-WORKS.md) · [Every score](META-EVAL-SCORES.md) · [What we conclude](CONCLUSIONS.md).

# A hackathon search for AI mistakes we could verify

We set out to find an AI mistake that another person could check and reproduce. We tried reasoning puzzles, planning problems, programming tasks, rules for scoring answers, and longer jobs where an AI assistant had to use tools and follow permission rules.

We found mistakes, but the story was more complicated than counting wrong answers. Some models solved a problem correctly on the next attempt. Some follow-ups allowed tools that the original task had forbidden. Some apparent failures came from our own checking code rather than the model's answer.

This repository explains **what we asked the models to do, why we chose those tasks, what happened and how we reached our conclusions**. Testing whether AI could build good tests was the final direction, after the earlier work showed how easily a checking tool could give a misleading result.

## 1. Try several kinds of problem before choosing a direction

We began with a set of ten reasoning, planning, creativity and programming tasks. We asked three models to attempt them without running code or using external tools. That gave us 30 task attempts. Some tasks involved follow-up questions, so the record contains 48 model responses.

We used a **grader**, meaning a program that checks an answer and returns a result. Several red results needed investigation before we could call them model mistakes.

One task asked for a small service that spends a limited balance and records each request. If the same request arrives again, it should return the earlier decision rather than subtract the amount twice. Three submissions handled the required behavior but failed because the grader wanted a particular word for success. The task had not told the models to use that word.

Terra also made a genuine mistake in a queueing problem. The task asked about the service outcome by a specified deadline, but its answer and supporting example did not establish that outcome. Here the error belonged to the answer, rather than an unpublished naming rule in the grader.

We clarified the service wording and revised several creative tasks. All 30 new attempts passed. Terra also solved the queue problem on a new attempt with the same visible instructions and required answer format.

The lesson was already mixed: some first results were real mistakes, some were mistakes in our test, and a later correct answer could coexist with an earlier wrong one.

[Original task results](docs/campaigns/frontier-run-2026-10-31.md) · [Revised tasks](docs/campaigns/frontier-run-v2-2026-10-31.md).

## 2. Test whether the model could choose the right next step

A model can describe a situation correctly and still make a bad decision. We wanted a task where that difference was visible.

We built small artificial troubleshooting puzzles, called **diagnostic games** in the reports. Here is how the recorded eight-cause example works:

- One of eight possible causes, labeled 0 through 7, is the real cause. The model does not know which one.
- It receives a table showing the 0-or-1 answer each test would give for each cause. It chooses a test, sees the answer and decides what to ask next.
- It has six points to spend. Most tests cost one point. At most one answer from these tests may be wrong during the whole investigation. A guaranteed-truthful test costs two points.
- Some choices also remove tests from the list of future options. Spending points and preserving useful tests both matter.
- Before each choice, it must list every cause still consistent with the answers so far. It should identify the cause when a strategy can guarantee that result. If that is impossible, it should narrow the list as far as the rules allow without guessing.

For example, a truthful answer can rule out causes that predict the opposite answer. An answer that might be wrong needs more care: the model cannot discard a cause just because it conflicts with one potentially unreliable observation.

In a saved Sol attempt, the list of possible causes stayed correct throughout. After its first test, five points remained, and a suitable sequence of tests could still guarantee finding the cause. Sol then spent two points on the guaranteed-truthful test. Even the best remaining choices could now leave two causes unresolved. It eventually finished with causes 1 and 7 still possible.

That expensive test did not remove other tests in this example. It simply used too much of the remaining budget. We did not mark Sol wrong for admitting uncertainty; we marked the planning decision wrong because it had lost a result that was still achievable.

We repeated the work with new puzzles and with longer conversations where the model continued from its earlier answers. Related Sol and Astra mistakes remained in the runs without computation tools. In a later experiment allowing tools, all 24 attempts passed, and every attempt used Python, a programming language.

We also compared asking for an actual schedule with allowing a program that searches for one. Astra and Sol passed the direct-schedule follow-up. Terra gave schedules that obeyed the rules but achieved less than an available alternative on two of five versions.

These results taught us to separate reasoning through each decision, using code to search possibilities, and handing back a program that will search when executed. Those are different ways to solve a task.

[Planning studies](docs/campaigns/readiness-study-20261031.md) · [Direct schedules](docs/campaigns/depot-direct-run-2026-10-31.md) · [Follow-up with tools](docs/campaigns/submission-failure-audit-20261101.md).

## 3. Check whether small wording changes changed the score

Some tasks involved scoring answers for qualities such as usefulness. We asked whether a score would change when the answer's meaning stayed the same but its wording or position in a group changed.

We tried repeated answers, equivalent rewrites, changes that should matter, and deliberately misleading claims. We also revised the written descriptions of what deserved each score. The reports call those descriptions **scoring anchors**.

In one study, the same input received ratings of 3, 3 and 2. Other comparisons were stable. New examples often received the same category under both the old and revised scoring rules, so improving selected earlier examples did not establish that the revision helped more generally.

We then tried 90 more specific tasks about evidence: whether an answer was genuinely new, whether required behavior had actually been tested, and whether information supported a conclusion. All 90 attempts passed their checks.

We had found some score inconsistency, but we had not established a valid measure of human creativity or job performance. The passing evidence tasks also mattered: those particular questions did not reveal the weakness we were seeking.

[Scoring consistency](docs/campaigns/semantic-invariance-pilot-20261101.md) · [Revised score descriptions](docs/campaigns/anchor-causality-pilot-20261101.md) · [Evidence tasks](docs/campaigns/assessment-evidence-screen-20261102.md).

## 4. See whether software broke after repeated changes

Small puzzles can miss the difficulties of maintaining a program. We asked models to move software without losing required behavior, change rules used in several places, and add requirements while preserving earlier ones.

We also investigated software structure: how code was divided into parts and how those parts depended on each other. Would that structure predict later maintenance effort? Would reorganizing it before making functional changes save time?

The selected tasks mostly passed. All nine practical coding attempts passed their checks. The repeated-change studies also passed the recorded checks rather than showing a consistent pattern of earlier behavior breaking.

In the tested comparison, reorganizing the code first took 48.7% more time in the recorded model runs. The evidence that structural measurements predicted later cost was weak. We could not turn these results into a broad claim that AI was bad at maintaining software.

Two apparently failing programs also exposed another private grading assumption. They used one type of error response where the grader wanted another, even though the task had not required that particular error type.

The lesson was to measure the promised benefit of a software design, and to check whether a supposed failure violated a written rule or merely the grader author's preference.

[Practical programming](docs/campaigns/practical-coding-pilot-20261101.md) · [Repeated changes](docs/campaigns/long-horizon-coding-pilot-20261101.md) · [Software-structure experiments](docs/campaigns/architecture-oracle-validity-experiments-20261102.md).

## 5. Ask whether following the process could get in the way of finishing

Earlier work sessions contained repeated tool errors, expensive review cycles and cases where the owner intervened to change the approach. We wanted to know whether an AI assistant could keep following its process while losing sight of the requested result.

We tried smaller made-up projects, reminders about the cost of repeated work, files from actual earlier sessions, and a supervising assistant that could coordinate work and ask the owner for permission.

Several smaller recreations finished successfully. But some allowed the assistant to build a separate version while the original situation had forbidden construction altogether. Success under that changed rule could not settle what would happen under the original restriction.

One supervising-assistant run was paused by the user before a final result. A later run used another model, asked the owner and respected a denial. Another response promised a report that was not present. That missing file was a delivery mistake, even though it did not establish the repeated process loop we were looking for.

The historical cost was real. Recreating the same problem remained difficult because the length of the job, permission rules, pauses and technical interruptions all affected the comparison.

[Earlier-session review](docs/campaigns/c08-session-archaeology-20261103.md) · [Changed construction rules](docs/campaigns/c09-goal-priority-20261104.md) · [Supervising-assistant follow-up](docs/campaigns/coordinator-continuation-r2-20261107.md).

## 6. Search more widely, and keep actual mistakes visible

The wider search asked more concrete questions. Would a model trust a helper whose documentation was wrong? Claim a schedule was best without establishing that? Break shared information when operations overlapped? Keep following an old rule after it changed? Report work it had not actually performed?

The first ten rounds list 67 experiment entries and 295 counted model attempts. Most requested Luna, so this was not a broad comparison consistently using the strongest models we later tested.

Many tasks passed. One recurring problem involved a helper program behaving differently from what its documentation suggested. Across five separate groups of attempts, the failure counts were 1/4, 1/6, 1/16, 3/24 and 2/12. Here, 1/4 means one wrong output in four attempts.

A payroll example made the error clear. The rules excluded every record in the batch, so the answer should have been total 0 and paid 0. The program returned total 753 and paid 1.

Several reports still said “no hit” or “KILL.” Those labels meant the mistakes had not repeated often enough to meet a rule set for continuing that research lead. They did not mean every delivered program was correct.

We needed to keep the wrong result and the decision about further research separate. Because the tasks and conditions differed, combining those five fractions into one overall failure percentage would also be misleading.

[The first ten rounds](docs/ROUNDS-01-10.md) · [Exact experiment instructions and checking plans](docs/PROTOCOLS.md).

## 7. Try allowed inputs the original tests had missed

Later work asked whether assistants handled stopped processes, changing permissions, missing findings and changes to the requested work. Many of the specific mistakes we had planned to count did not occur. Looking more broadly still revealed incorrect or unfinished work.

We found especially clear examples in number handling and quotations. Sixteen reviewed Luna programs failed on allowed ways of writing zero that their original tests had missed:

```text
0e10000000000000000000
```

This means zero multiplied by a power of ten. It is still zero, and the written input is short. A program that accepts ordinary `0` but crashes on this permitted spelling has a real input-handling bug.

A quotation example had a different problem: its own checking logic accepted evidence that did not form the continuous passage the task required. Joining separated pieces of a source into one quotation can make evidence look more direct than it is.

Some results were also too limited to support a strong conclusion. If a model never made the particular kind of invalid call we wanted to investigate, observing no failures did not show that it handled that call correctly. A broken test environment could likewise prevent us from measuring the requested behavior at all.

Passing the examples we had chosen was therefore different from meeting every rule in the task. We needed to inspect both the planned result and other mistakes in the delivered work.

[Later experiments](docs/LATER-ROUNDS.md) · [The zero example](docs/CASE-STUDIES.md#2-a-short-spelling-of-zero-exposed-two-different-problems).

## 8. Check whether our own tools were giving misleading answers

The mixture of failures and later successes led us to review the whole record. Were our checking programs missing work? Had the follow-up changed the question? Had the summary hidden a real mistake?

One audit, meaning a systematic check of the saved records, counted only 156 saved copies of workspaces after 228 model steps. Another 72 copies were stored in a different folder layout. The corrected audit explicitly checked that all 228 expected copies were present.

We also tested a program that retrieves information from tables. The task was to return the same answer with less work. Think of finding matching records in two tables: a better approach might avoid comparing every possible pair of rows.

To challenge the measurement, we deliberately wrote a program that did the original 150 comparisons, then another 30 using the faster approach, but reported only 30. It passed all 41 checks despite doing 180 comparisons. The checking code inspected the reported approach without observing all the work actually performed.

We separately examined the 16 actual stronger-model programs. They genuinely reduced work on the inspected paths. Our deliberately misleading test program exposed a loophole; it did not establish that those models had cheated.

The lesson was that two checks can agree because they share the same blind spot. Our tools needed scrutiny as well as the answers they graded.

[Review of the full research record](docs/campaigns/complete-recap-audit-20261108.md) · [Mistakes in our tests](docs/INSTRUMENT-LESSONS.md).

## 9. Give stronger models the original jobs

A failure on an earlier model was not enough to claim that the strongest models shared it. We returned to the original tasks, kept their visible instructions and recorded differences in the computer setup.

Astra and Sol each passed their eight-task comparison on retrieving and reorganizing table data. Both programs for the original warehouse task handled the zero input. Our written follow-up rule said to run a second numeric task only after a qualifying failure; because neither failed, that follow-up launched no attempts.

Both models also passed the specific original quotation and payroll cutoff-date checks. The initial comparison across five original tasks passed all ten attempts, including the troubleshooting games where each model continued through one conversation without running code.

In a separate experiment, we gave models explicit rules for checking answers and tested their verification work. All 30 attempts passed, with 1,806 correct test-case decisions. Those decisions were multiple checks inside the attempts, not 1,806 separate attempts.

A later payroll input exposed a different Sol mistake. These strings represent the same amount:

```python
canonical_gross = "1"
padded_gross = "0" * 5000 + "1"
```

The second line creates the string `1` with 5,000 zeros in front. The payroll rules allowed that spelling. A prior program handled the short version and crashed on the long one because of Python's limit on one kind of number conversion.

We asked Sol to solve the unchanged task in two new completed attempts, without revealing the failing input. One repeated the mistake; the other passed. Both passed all 26 original test cases. Two earlier interrupted attempts stayed in the record as unknowns.

The stronger models solved many earlier failure cases, and one specific current Sol mistake recurred. The successful and failed attempts both limit what we can claim.

[Every final stronger-model attempt](docs/STRONGER-MODEL-ATTEMPTS.md) · [Payroll cause and follow-ups](docs/CASE-STUDIES.md#3-the-number-was-small-its-spelling-broke-the-payroll-program).

## 10. Finally, test the AI systems building the tests

By this point, building a good evaluation had become a research question itself. An **evaluation** is a task together with a way to judge the answer. It can include instructions, a proposed correct solution, test examples, checking code and a report.

Giving a model clear checking rules is different from asking it to build that whole package. The author must decide what the solver will receive, establish correct answers, accept legitimate alternatives and explain what the tests actually demonstrate.

The final experiment retained 31 author attempts: 19 completed evaluation packages, four additional audit outputs, seven timeouts and one attempt whose completion could not be established. Our outer checking program ran 114 jobs against the saved outputs. These checking jobs did not create new model answers.

The delivered evaluations had concrete problems. Five service evaluations required a success word missing from the instructions given to the solver. Three number-processing evaluations accepted a saved program with a known bug; two also rejected a different allowed spelling of a correct answer.

A more explicit instruction fixed the missing-word problem in one later package, while changing what that evaluation measured. Review also withdrew seven examples we had labeled as correct because that broad label was not justified by their actual behavior.

The reports call this final software a **meta-eval**: an evaluation of evaluations. It is one result of the larger journey, with successful checks and unanswered questions recorded alongside the failures.

[How the final checking software works](docs/HOW-THE-META-EVAL-WORKS.md) · [All author attempts and scores](docs/META-EVAL-SCORES.md).

## What we can conclude

We found real mistakes, including ones that repeated on new attempts. We also found many successful runs. Some apparent failures belonged to our own tests. Some follow-ups changed the available tools or rules, while others genuinely solved the same visible task on another attempt.

That is why there is no single overall failure percentage here. Running the same bad program again, asking for a new solution, and changing the model or tools answer different questions.

We reached our conclusions by comparing written rules with actual outputs, checking expected answers in separate ways and preserving results that weakened our preferred explanation. Detailed human review of every task meaning and grading decision remains unfinished.

Sol, Astra, Luna and Terra are the model names recorded by our tools. We know those requested names, but cannot establish that the exact underlying model version stayed identical across dates.

[Conclusions and open questions](docs/CONCLUSIONS.md) · [Terms and counting explained](docs/READING-THE-EVIDENCE.md).

## Explore or run the work

- [Questions we investigated](docs/HYPOTHESES.md): why each direction seemed worth trying.
- [Research index](docs/CAMPAIGNS.md): all 55 research directories, including plans, audits and exports as well as experiments.
- [Attempt guide](docs/ATTEMPTS.md): where the retained runs and their outcomes are recorded.
- [Case studies](docs/CASE-STUDIES.md): examples with the task, mistake, cause and follow-up.
- [Reproduction guide](docs/REPRODUCE.md): read the saved results or rerun the final checks without asking models for new answers.
- [What this repository includes](docs/REPOSITORY-MAP.md): which evidence is public and which older files remain in the local archive.

Vladimir Rondelli directed the work with substantial help from Codex and GPT agents. [AI assistance and review](AI-ASSISTANCE.md) explains their contribution and why agreement between AI assistants or checking programs does not replace external human expertise.

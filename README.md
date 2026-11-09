# Frontier Research: a hackathon investigation

We entered this research with a practical goal: find a meaningful AI failure that another person could reproduce. We explored unusual reasoning problems, planning games, coding tasks, assessment criteria, software maintenance and agent workflows.

The work did not produce one clean story about models succeeding or failing. We found genuine mistakes, successful follow-ups, recurring bugs and errors in our own tests. Sometimes a model solved the same problem on its next attempt. Sometimes we had changed the tools, instructions or permissions enough that we were asking a different question.

This repository records that journey: **why we tried each direction, what happened, and how the follow-ups changed what we could conclude.** Testing AI-created evaluations became the last major direction, after the earlier work showed how much the answer depended on the quality of our instruments.

## 1. Start broadly: could unusual tasks expose a useful failure?

Our first benchmark contained ten reasoning, planning, creativity and engineering tasks. Three model aliases answered without computation tools, producing 30 episodes and 48 turns.

The raw failures immediately needed interpretation. Three allowance-service implementations had the required ledger and retry behavior but failed because the grader expected a success word absent from the task. Those were evaluation-contract defects. A Terra answer to a queue problem, however, made a genuine equivalence error and supplied a witness that did not establish the requested outcome.

We clarified the service contract and revised several creative tasks. All 30 attempts on the successor benchmark passed. Terra also solved the queue problem in a fresh draw with the same visible prompt and schema. That was a real failure followed by a real success, rather than a case we could explain away as an edited question.

**What we took forward:** a red grade needed an independently defensible reason, and a successful fresh answer did not erase the old one.

[Original benchmark results](docs/campaigns/frontier-run-2026-10-31.md) · [Revised benchmark](docs/campaigns/frontier-run-v2-2026-10-31.md).

## 2. Follow the planning lead: knowing the state was not enough

The early answers suggested a sharper question: could a model describe a situation correctly but choose an action that made its goal unattainable?

We built diagnostic games with a fixed budget. Each test narrowed the possible worlds, and the model had to choose what to ask next. In a retained Sol example, its possible-world lists stayed correct. But before its chosen probe, a strategy could still identify one world; afterward, even the best continuation could only narrow to two. It had spent the budget in the wrong place.

We explored fresh instances, continued interaction and different resources. Related Sol and Astra failures remained in the no-tool work. In a later ordinary-tool retest, all 24 attempts passed, and every attempt used Python.

We also compared returning a search program with committing directly to a schedule. Astra and Sol passed the direct follow-up; Terra produced legal but suboptimal plans on two of five variants.

**What we took forward:** live decision-making, direct construction and writing a program that can search are different tasks. Tool-enabled success narrowed the planning claim to its actual resource conditions.

[Planning studies](docs/campaigns/readiness-study-20261031.md) · [Direct scheduling](docs/campaigns/depot-direct-run-2026-10-31.md) · [Tool-enabled retest](docs/campaigns/submission-failure-audit-20261101.md).

## 3. Ask whether our scoring meant what we thought it meant

Some early tasks concerned creativity and assessment. That raised another problem: if two answers mean the same thing, would irrelevant wording or batch position change their score?

We tested equivalent rewrites, consequential changes, adversarial claims, ordering and clearer scoring anchors. One anchor study retained identical-input ratings of 3, 3 and 2. Other comparisons were stable, and fresh examples often agreed under both old and revised rubrics. A better-looking selected example did not establish that a scoring change improved new cases.

We then prepared more explicit evidence problems about novelty, coverage, identification and instrument repair. All 90 attempts in that finite screen passed.

**What we took forward:** scoring variability was worth studying, but it did not validate a measure of human creativity or job performance. The explicit evidence tasks also gave us a substantial negative result: they did not expose the failure we were seeking.

[Scoring consistency](docs/campaigns/semantic-invariance-pilot-20261101.md) · [Anchor follow-up](docs/campaigns/anchor-causality-pilot-20261101.md) · [Evidence-task screen](docs/campaigns/assessment-evidence-screen-20261102.md).

## 4. Move into software: would repeated changes expose deeper weaknesses?

Small puzzles can miss the difficulties of maintaining software. We tried practical migrations, shared-policy changes, successive requirements and changes that interacted with earlier behavior. We also asked whether software structure predicted later maintenance effort and whether repairing structure first paid off.

The selected coding tasks mostly passed. The practical pilot passed all nine episodes. Sequential and interacting-change studies retained passing checkpoints rather than a stable regression pattern. In the tested architecture comparison, repair-first used 48.7% more native time; evidence for predicting later cost from structural measurements was weak.

Two apparent Jinja failures also narrowed under review: the grader privately required one exception class, although the public task allowed the conventional alternative used by the implementations.

**What we took forward:** we had not demonstrated broad maintenance failure on these small lineages. A plausible architecture explanation needed measured support, and private grader assumptions could manufacture apparent errors.

[Practical coding](docs/campaigns/practical-coding-pilot-20261101.md) · [Successive changes](docs/campaigns/long-horizon-coding-pilot-20261101.md) · [Architecture experiments](docs/campaigns/architecture-oracle-validity-experiments-20261102.md).

## 5. Investigate the workflow: could process displace the actual goal?

Historical agent sessions contained costly review cycles, repeated tool errors and owner interventions. We wanted to understand whether an agent could keep following its process while losing sight of the requested outcome.

We tried synthetic governance tasks, cost cues, authentic source material and native coordinators. Several small recreations completed successfully. But some allowed isolated construction where the original situation prohibited construction altogether. Those successful runs did not recreate the same permission boundary.

An original coordinator run was explicitly paused by the user before a final verdict. A later run used a different model, asked the owner and respected a denial. A missing promised report file remained an ordinary delivery error, separate from whether the proposed process loop occurred.

**What we took forward:** historical cost was real, but faithful recreation remained incomplete. Shorter tasks, changed permissions, pauses and infrastructure failures needed their own explanations.

[Historical session review](docs/campaigns/c08-session-archaeology-20261103.md) · [Construction-boundary follow-up](docs/campaigns/c09-goal-priority-20261104.md) · [Coordinator continuation](docs/campaigns/coordinator-continuation-r2-20261107.md).

## 6. Search more widely, then distinguish mistakes from promotion rules

The frontier hunt expanded into misleading dependencies, false optimality, concurrency, conflicting requirements, temporal reasoning, security, stale state, permissions and reporting.

The first ten rounds contain 67 protocol rows and 295 counted model episodes, predominantly Luna. Many finite tasks passed. A recurring lead involved helpers whose documented behavior could not be trusted.

Across five separate cuts, that pattern produced failure counts of 1/4, 1/6, 1/16, 3/24 and 2/12. In one payroll case, the rules excluded the entire batch, so the result should have been total 0 and paid 0. The delivered implementation returned total 753 and paid 1.

Several studies still said “no hit” or “KILL” because their recurrence thresholds were not met. The product error and the decision not to promote a research lead were different facts. We had compressed them too aggressively in the summaries.

**What we took forward:** failures had not all disappeared. We needed to report the actual task error, the proposed mechanism and the promotion decision separately. These different samples cannot be pooled into one reliability estimate.

[All first-ten-round results](docs/ROUNDS-01-10.md) · [Individual experiment designs](docs/PROTOCOLS.md).

## 7. Look beyond the original checks

Later rounds examined process lifetime, updates, authorization, source evidence and task scope. Many registered failure patterns stayed absent, but broader review found ordinary omissions, incomplete work and mistakes outside those narrow definitions.

Numeric and quotation tasks produced especially concrete examples. Sixteen reviewed Luna programs failed legal zero-representation probes that their original finite suites had missed. A quotation artifact also used weak self-validation around evidence that was not contiguous as required.

The numeric input was short:

```text
0e10000000000000000000
```

It still represents zero. A program that accepts ordinary `0` but crashes on this permitted spelling has an input-handling defect, even if its existing examples pass.

Some other zero results had little relevant exposure or were limited by the environment. We kept those qualifications rather than treating every completed run as a strong negative.

**What we took forward:** passing the planned checks did not establish the whole public contract. A narrower experiment could be negative while the delivered product still contained a real error.

[Later rounds and follow-ups](docs/LATER-ROUNDS.md) · [Numeric case study](docs/CASE-STUDIES.md#2-a-short-spelling-of-zero-exposed-two-different-problems).

## 8. Audit our own tests: were they missing work or being fooled?

The pattern of failures and later successes prompted a full recap. We asked whether graders were gameable, whether conditions had changed and whether our summaries were losing important evidence.

The audit found several research-side defects. One architecture audit had discovered only 156 snapshots for 228 turns, missing 72 stored under another layout. The corrected audit checked all 228. Earlier rubric and temporal-data findings also narrowed when we found unstated ranking rules or ambiguous timing assumptions in their grading.

We deliberately built a query candidate that executed the original plan for 150 comparisons, then an optimized plan for 30, but reported only 30. It passed all 41 checks while doing 180 comparisons. The grader checked the declared plan without observing all the work.

We inspected the actual stronger-model implementations separately. All 16 reviewed programs genuinely reduced work on the inspected paths. A vulnerable grader did not establish that those models had cheated.

**What we took forward:** our instruments deserved the same scrutiny as submitted code. Agreement between checks could still miss a shared assumption or an unobserved effect.

[Complete recap](docs/campaigns/complete-recap-audit-20261108.md) · [What went wrong in our tests](docs/INSTRUMENT-LESSONS.md).

## 9. Return to the original jobs on stronger models

A failure on an earlier model was not enough to call something a frontier limitation. We returned to original tasks, preserving their visible instructions and recording runtime differences.

Astra and Sol each passed their eight-task query comparison. Both warehouse pilots handled the historical zero input, so the predeclared failure-triggered numeric replication correctly launched no calls. Both passed the specific original quotation and payroll date-boundary checks. The initial original-five comparison also passed all ten attempts, including both persistent no-tool diagnostic episodes.

A separate verifier-repair experiment passed all 30 attempts and all 1,806 case decisions. Those were successful repairs under explicit rules.

Then a broader payroll check found a different Sol bug. These strings represent the same small amount:

```python
canonical_gross = "1"
padded_gross = "0" * 5000 + "1"
```

A prior implementation handled the first and crashed on the second through Python's integer-string conversion limit. One of two completed fresh Sol repetitions repeated the error; the other passed. Both passed all 26 original cases. Two interrupted earlier slots remained unknown.

**What we took forward:** the stronger models solved many historical failure cases, and one specific current Sol implementation error recurred. Neither result justified a universal claim about frontier ability.

[Every final stronger-model attempt](docs/STRONGER-MODEL-ATTEMPTS.md) · [Payroll cause and repetitions](docs/CASE-STUDIES.md#3-the-number-was-small-its-spelling-broke-the-payroll-program).

## 10. Finally, test the models building the evaluations

By then, evaluation construction had become a research question of its own. We had repeatedly seen problems with task instructions, references, controls, measurement and reporting.

Repairing a specified verifier and constructing a complete evaluation are different jobs. An evaluation author must decide what the solver receives, preserve the requested task, establish expected answers, test legitimate alternatives and describe what was actually verified.

The final experiment retained 31 author attempts: 19 completed evaluator packages, four supplementary audit outputs, seven timeouts and one unknown completion. Its outer checker executed 114 jobs against the saved packages. Review also excluded seven original full-task control labels that were not justified for the scope claimed, leaving those limitations visible in the results.

Five completed service evaluators required a success word omitted from their solver instructions. Three numeric evaluators accepted a preserved faulty program; two of those also rejected an equivalent correct output. A more explicit instruction fixed the status-word mismatch in one successor, while changing what that evaluation measured.

**What we took forward:** these were concrete construction errors worth studying directly. The meta-eval is one outcome of the broader investigation, with successful comparisons and unresolved review questions preserved alongside it.

[How the meta-eval works](docs/HOW-THE-META-EVAL-WORKS.md) · [All author attempts and scores](docs/META-EVAL-SCORES.md).

## Where the journey left us

We found real failures, including recurring ones. We also found many passing experiments and stronger-model successes. Some apparent failures were caused by our own graders. Some follow-ups changed the resources or rules, while others genuinely solved the same visible task on a fresh attempt.

That is why this repository does not offer one grand failure percentage. A saved program failing again, a new model repeating its bug, and a different model succeeding with different tools answer different questions.

Our conclusions come from comparing the public rules, inspecting actual outputs, using independently established checks and preserving inconvenient results. Human review of every task meaning and grading judgment remains incomplete. Model aliases also do not identify immutable backend weights.

[Conclusions and remaining questions](docs/CONCLUSIONS.md) · [How to read the evidence](docs/READING-THE-EVIDENCE.md).

## Explore or reproduce the work

- [Hypothesis guide](docs/HYPOTHESES.md): the questions connecting these directions.
- [Campaign index](docs/CAMPAIGNS.md): all 55 research directories, including designs, audits and exports.
- [Attempt guide](docs/ATTEMPTS.md): where the retained runs and their outcomes are recorded.
- [Case studies](docs/CASE-STUDIES.md): concrete examples with causes and follow-ups.
- [Reproduction guide](docs/REPRODUCE.md): inspect the saved results or rerun the portable evaluator checks without new model calls.
- [Repository scope](docs/REPOSITORY-MAP.md): what a public clone includes and what remains in the local archive.

Vladimir Rondelli directed the work with substantial assistance from Codex and GPT agents. [AI assistance and review](AI-ASSISTANCE.md) explains how they contributed and why separate algorithms or agents do not replace external human expertise.

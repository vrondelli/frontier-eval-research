# How we test an AI-created evaluation

Suppose you ask an AI to build an evaluation for an allowance service. It delivers a task statement, a reference implementation, a grader and some tests. The package runs and reports success.

There is still an unanswered question: **does this package reliably judge the service we actually asked for?**

The final software in this repository addresses that question. It treats the model-created evaluation as the submitted product and checks it from outside. That is the meta-eval.

## Start with an example, not the score

Consider the service from our first case study. Its balance and retry behavior are correct, but it says `applied` when an operation succeeds. The generated grader expects `accepted`, a requirement omitted from the solver's task views.

We send both versions through the unchanged grader. Their behavior is the same; only the word changes. When the verdict changes, we have a concrete reason to question the evaluator. A high total score should not conceal that defect.

For the numeric task, we use a different challenge: a preserved faulty command-line program that crashes on a short legal zero spelling. If the evaluator passes that program, its test suite has missed an independently established failure.

The [case studies](CASE-STUDIES.md) show these checks in detail. The full code is in [the scored runner](../meta-eval/run_meta_eval.py).

## There are three jobs, and they need separate answers

1. **The solver** writes a program or an answer to the task.
2. **The evaluation author** builds the package that judges solvers.
3. **The outer checker** tests that package using independently established expectations.

In the numeric example, the bad Luna CLI is the solver artifact. The Astra-created evaluator is the product being assessed. Our outer check uses the legal zero input to establish that this product gave a misleading verdict.

Repairing an existing verifier under explicit rules is another task. Models passed all 30 attempts in that experiment. We keep that success separate from the complete-eval authoring results, because choosing and exposing the rules is part of the authoring job.

## What the score asks

The score has eight parts. The examples below explain what each part is trying to find; they do not claim every listed defect occurred in every package.

| Part | Points | The practical question |
|---|---:|---|
| Delivery | 10 | Can the delivered grader actually run, and does its verification run in a clean environment? |
| Task and instructions | 15 | Does it preserve the requested job and tell the solver every rule it grades? |
| Reference answers | 15 | Is its proposed answer correct when checked another way, including selected boundary cases? |
| Correct submissions | 20 | Does it accept correct behavior and legitimate alternative representations? |
| Faulty submissions | 20 | Does it reject known bugs and independently constructed related faults? |
| Measurement and boundaries | 10 | Are isolation and measured quantities supported by evidence rather than just asserted? |
| Verification | 5 | Do the delivered controls execute, and do they justify the claimed verification? |
| Reporting | 5 | Do the reported numbers and conclusions match the evidence? |

These dimensions contain 16 checks. Some can be exercised mechanically. Others still need a review of what the original task meant or whether a proposed control is genuinely correct. The [check registry](../meta-eval/meta_eval/CHECK-REGISTRY.json) contains the precise definitions.

## A range tells you where the evidence stops

The initial Sol H1 evaluator scores **57.50-82.50 /100**. It has 57.5 supported points, 17.5 failed points and 25 unresolved points. Even if all unresolved checks later passed, its observed failures would remain.

A low supported score can also reflect limited qualified evidence, rather than a worse package. For example, the original H2 job requested a written rubric; we cannot retroactively demand an executable grader and call its absence a model failure.

This prevents a common reporting mistake: turning “we did not establish whether this is correct” into “it passed.” It also avoids treating every unresolved item as a model error.

A failed required check prevents a complete pass. Full qualification additionally requires the relevant human review. The current reports therefore distinguish a reproduced counterexample awaiting review from an output for which no objective failure was established. The latter is not automatically a trustworthy eval.

## How we check the checker

We built two small correct evaluation packages and ten deliberately broken ones. The broken versions include an always-pass grader, an always-fail grader, a wrong reference, a hidden rule, a fake runner and a false report. The calibration checks whether the framework notices the intended defects. Three domain checks also exercise the allowance service and numeric program.

All those calibration checks passed, as did the 19 unit tests. This gives us evidence about specific behavior of our checker. It does not settle every task's meaning or prove correctness across every allowed input.

Expected labels stay outside the submitted grader's execution process in the scored runner. Historical generation isolation is a separate question and remains incompletely established; rerunning an old artifact inside a better sandbox cannot retroactively change its original context.

## What a replay does

The saved experiment has 31 author attempts: 19 completed evaluator packages, four supplementary audit outputs, seven timeouts and one unknown completion. The runner executes 114 check jobs against the available packages. It does not ask models to produce new outputs.

A clean extraction reproduced the stable service and numeric counterexamples. One saved H1 grader also has an intermittent worker-protocol rejection, so exact operational scores can vary between replays. Both the initial observation and later outcomes are retained.

To try it, use [the reproduction guide](REPRODUCE.md). To inspect the result first, read [all 31 attempt summaries and scores](META-EVAL-SCORES.md).

# What we learned, and what we still need to check

The most useful conclusion is that “the model failed” was often too vague. We found wrong programs, wrong graders, changed follow-ups and genuinely successful new attempts. The research became clearer when we explained those separately.

## Some failures were real, even when the next attempt passed

The payroll example is concrete. Two equivalent spellings of the number one should give the same payslip. A saved Sol program crashed on the longer spelling, and one fresh implementation repeated the mistake. Another fresh implementation handled it correctly.

The success limits the claim: the model can produce a solution that avoids this bug. It does not repair the bad saved programs. Similarly, the repeated lying-helper errors were real even when each study missed its local threshold for promoting a lead.

This is why we distinguish replaying an old artifact from asking for a new solution. One checks the evidence; the other asks whether the mistake recurs.

## The evaluation builder can fail the job it was given

The service evaluator silently required a word missing from the solver's instructions. The numeric evaluators accepted a program with an independently demonstrated bug, and some also rejected an equivalent correct output.

Those are failures in constructing the evaluation. They do not require a claim that the model deliberately cheated. Nor can a large test count make the examples disappear: passing 84 ordinary checks does not settle a legal case that the suite never tried.

The [meta-eval](HOW-THE-META-EVAL-WORKS.md) makes those questions executable. It checks the delivered packages and preserves the evidence and unresolved points behind each score.

## Several promising failures belonged to our tests

An unstated exception-class requirement made two Jinja submissions look wrong. A directory selector omitted 72 snapshots from an audit that initially reported success. Seven original control labels were later excluded because they were not justified for the full tasks.

These corrections reduce some apparent model-failure claims. They also expose a practical weakness in an AI-assisted research workflow: a plausible grader, a reference implementation and a green report can share assumptions that nobody has independently checked.

The appropriate response was to preserve the old observation, explain the error and qualify the replacement check. Rewriting history would make the research easier to summarize and harder to trust.

## The successful experiments changed the story too

Astra and Sol passed their query comparisons and the original warehouse zero input. All 30 explicit verifier-repair attempts passed. The initial original-five comparison passed all ten attempts. The ordinary-tool planning shortlist passed 24/24 with actual Python use.

These results are part of the answer. They stop us from presenting every historical bug as an unavoidable frontier limitation. They also show where the conditions matter: a model repairing a specified verifier has a different job from one choosing the rules for a complete new evaluation.

## What remains unresolved

Human review of every task meaning and grading decision is not complete. Five underlying H1 rule approvals do not supply blanket approval of the meta-eval. We also cannot fully establish what every historical author could read, or qualify every reference across its entire input domain.

Some questions are limited by our checker rather than the submitted model. A large nonzero numeric case can exceed the checking budget; that should stay unknown instead of becoming a made-up pass or failure. One saved H1 grader also has a recorded intermittent worker-protocol problem, so its operational score varies between replays.

The model names identify the aliases requested or reported in the runs. They do not pin the provider's backend weights. The samples were selected through an adaptive search, so the counts cannot establish a general probability that a frontier model will fail.

## What would make the next study stronger

Choose new complete-eval authoring tasks and establish their public rules and independent expected judgments before launching the models. Ask a human reviewer to resolve the actual ambiguities, such as which alternative outputs are valid, rather than approve a score by impression.

Then keep prompts, tools, runtime and sample size fixed. Report whether the model preserved the task, accepted correct work, rejected faults and described its evidence honestly. Use a written rule for fresh follow-ups and retain every started attempt.

That would test whether our current examples generalize beyond the search that found them. The present repository contributes concrete counterexamples, successful comparisons and a runnable checker, with the remaining gaps visible.

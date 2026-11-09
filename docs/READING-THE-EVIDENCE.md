# How to read the evidence

You do not need to know the experiment IDs to understand the project. The IDs help locate records after the question and example make sense.

## The model and its evaluator are different subjects

An **evaluation**, often shortened to **eval**, is a task plus a way to judge the answer. A **grader** is the part that makes that judgment: for example, a Python program that runs a submitted service and decides whether its behavior is correct.

In a normal coding experiment, we test the model's program. In the final experiment, we test the evaluation the model built. That is why it is called a **meta-eval**.

For example, the faulty numeric CLI was written by Luna. An Astra-built evaluation later gave it a perfect test report. The claim about that Astra output is about its evaluator missing a known bug, not about Astra writing the original broken CLI.

## Why we use correct and faulty controls

A **control** is an example whose expected behavior we have established separately. A correct service should pass. A service that spends the allowance twice on retry should fail.

Both directions matter. A grader that rejects everything catches every faulty example but is useless to someone submitting correct work. A grader that accepts everything is equally useless.

A **reference** is a proposed correct solution or calculation. An **independent oracle** is a separate way to establish an expected result. Independence has to concern how the answer was obtained: calling the submitted program twice does not create a second source of truth.

## Three different meanings of “we repeated it”

**Run the same saved program again.** This checks whether the observed error is reproducible in that artifact. It does not create a new model output.

**Ask a fresh model attempt to solve the same task.** This checks recurrence. The new implementation may repeat the bug or avoid it. Both outcomes belong in the record.

**Change the prompt, model, tools, time limit or task.** This tells us what happens under changed conditions. For example, a planning model with Python can search possibilities that a no-tool run had to reason through directly. We should say what changed before comparing the outcomes.

One later condition is called clean staging: it supplied the prompt and public input files without the earlier packet metadata. It did not establish a context-free model session or prove that all ambient historical information was inaccessible.

## A check is not a model attempt

The final authoring experiment contains 31 attempts. The runner later executes 114 check jobs against the saved outputs. The number 114 describes checking work, not 114 fresh model generations.

Likewise, 30 verifier-repair attempts produce 1,806 case decisions. Each program handles several cases. Reporting 1,806 independent experiments would exaggerate the sample.

The 55 research directories include designs, audits and exports as well as experiments. The [attempt guide](ATTEMPTS.md) preserves these different units instead of adding them together.

## Why a result can say “no hit” and still contain a mistake

Some experiments looked for a specific combination of events. One question was whether a model would run its own tests, obtain a reassuring result, and still deliver bad behavior. Bad code with tests that were never run does not meet that exact definition, although the software task still failed.

Other experiments required a failure to recur a certain number of times before promoting it as a research lead. A real error could miss that threshold. We explain the ordinary mistake and the promotion decision separately.

## What an unknown result means

A timeout means the attempt did not finish within its limit. A missing completion record means we cannot establish how it ended. An unqualified control means we lack a sufficiently reliable expected judgment. These are different reasons for uncertainty.

None automatically means the program was correct. None automatically establishes a reasoning failure. The score keeps those gaps visible.

## How to read a score range

For the initial Sol H1 evaluator, `57.50-82.50 /100` means:

- 57.5 points were supported by the checks.
- 17.5 points were lost on observed failures.
- 25 points were unresolved.

If every unresolved item later passed, the score could reach 82.5. The range is not a statistical confidence interval and is not a claim that the evaluator is “82.5 percent trustworthy.” A failed required check still prevents a complete pass.

[See the scoring explanation](HOW-THE-META-EVAL-WORKS.md) or [go directly to all scores](META-EVAL-SCORES.md).

## What the names identify

H1 and H6 identify the allowance-service and numeric authoring tasks. R1, R2 and similar labels identify research rounds. Sol, Astra, Luna and Terra are the model aliases recorded in the run logs. They help locate a condition; they do not pin an immutable model-weight version.

The public repository also distinguishes current explanations from old reports. Files under `evidence/source-text/` preserve the language used at the time, including conclusions later corrected. The campaign pages and narrative explain how we now interpret them.

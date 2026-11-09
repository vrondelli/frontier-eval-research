# What went wrong in our own tests

A research workflow can fail for the same reason as the software it tests: several pieces agree because they share an unchecked assumption. Here are the mistakes that most changed our interpretation.

## We sometimes graded a rule the solver had never received

The original service benchmark expected a particular status word without publishing it in the task. That produced three raw failures that were not failures of the ledger behavior. Later model-created H1 evaluators repeated an analogous mismatch between their solver views and their grader.

The Jinja cases had a similar shape. The grader expected `ValueError`, while two implementations used the conventional `FilterArgumentError`. The public task had not forbidden that choice. A private preference about the exact exception type could not justify the original failure claim.

The question we now ask is concrete: could someone reading only the supplied task know this would be graded?

## A successful audit did not count what it had missed

The first architecture custody audit found 156 snapshots for 228 turns. Seventy-two other snapshots used another directory layout and never entered its selector.

The corrected audit started from the expected stages and checked that all 228 had snapshots. This matters beyond that one script: a program can pass every check it runs while silently leaving out the files that would reveal its mistake.

## Our “correct” controls were not always qualified

A grader needs examples of correct work as well as faulty work. Otherwise, rejecting everything can look impressively strict.

Review excluded five H4 full-task control labels and two H6 full-domain positive labels. The controls did not justify those broad judgments. We preserved the old receipts and marked successor controls as created after outcomes were known, with narrower qualification.

That leaves some questions unresolved, but it is preferable to using an unjustified reference to manufacture a model failure.

## We checked a declared performance plan instead of all execution

The query grader could verify an answer and replay the proposed optimized plan. Our deliberate audit candidate did extra work before that plan, then reported only the optimized cost. It performed 180 comparisons, reported 30 and passed 41 checks.

Two independent algorithms could agree about the same declared plan and still miss the omitted work. For an execution-cost claim, we needed an observer of execution. The separately inspected 16 stronger-model programs showed actual reductions on the reviewed paths; the loophole did not establish that they cheated.

A separate scoring probe also read a known private-oracle path. That exposed a boundary weakness. It did not establish that any subject had read that path during generation.

## Some summaries counted the wrong thing

A command printed in a README is not a command executed by the agent. A program failing its task is not always an occurrence of the narrower mechanism an experiment was designed to count. Zero failures with zero relevant exposure is not strong evidence of reliable handling.

We found examples of each confusion. Short labels such as “no hit” compressed these differences and made real errors look as though they had disappeared. The newer summaries keep ordinary task mistakes, the proposed failure pattern and the promotion decision separate.

## Some results really were intermittent

One saved H1 budget-draw grader sometimes rejected a correct control because a worker left its protocol output open. Further identical Linux replays produced both failures and passes. The original report and clean replay retain their different outcomes.

This is an execution-reliability observation, not additional model-author trials. Reporting it separately lets the stable hidden-word counterexample remain understandable without pretending every operational result is identical.

The current outer checker is also tested: two correct and ten deliberately broken eval packages, three domain controls and 19 unit tests. That provides evidence for its specific detectors, while human task review remains a separate responsibility.

[Read the original audit](../evidence/source-text/complete-recap-audit-20261108/REPORT.md) · [See how the meta-eval checks these issues](HOW-THE-META-EVAL-WORKS.md).

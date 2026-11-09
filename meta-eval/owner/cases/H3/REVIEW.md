# H3 independent human review: temporal eval construction

Status: manual adjudication required. The original intake cutoff was ambiguous; do not privately convert a conservative interpretation into a model failure.

Sources: `frontier-hunt-20261106/round3/temporal-leakage/prompt.txt`, original workspace README/train and field-record-time data, and delivered eval-author public task/grader. Blind model identity during review. Retain the raw frozen result beside any corrected adjudication.

Observable questions:

1. Does the delivered task preserve the deployment objective and required pipeline CLI, feature list, validation report, and future-input contract? Does it state a precise, internally consistent definition of availability at intake where its grader needs one?
2. Distinguish reproducing the original task from introducing a clarified successor. A newly explicit cutoff may create a valid new task, but cannot justify retroactively rejecting an original conservative pipeline. Record any semantic change.
3. Are private checks licensed? A hidden required feature subset, private rule that all pre-outcome measurements are available, arbitrary exact validation score, or undocumented accuracy band must not become failure evidence. A claimed future-performance threshold needs a public performance obligation and qualified reference comparators.
4. Does the grader test actual future execution with unavailable columns absent, compare `features.txt` to the code used, and independently verify the reported holdout calculation? A forbidden name in a comment is not actual feature usage.
5. Can it separate actual post-outcome leakage, conservative exclusion, weak predictive performance, runtime failure, inaccurate reporting, and unresolved timing? These must have separate recorded outcomes.
6. Does it accept two valid alternative feature-selection/model strategies under its public contract, and reject a demonstrated pipeline that consumes post-outcome target-derived fields at deployment? Inspect actual code/data flow or executable probes, not a string match alone.

Allowed alternatives: different lawful intake-feature subsets, split/model choices, conservative handling of uncertain timing, and explicit acknowledgement of ambiguity. A low but honestly measured accuracy is not a leakage event. A stronger new performance requirement must be public before solving and labeled as a changed task.

Verdict: `pass`, `fail`, or `unresolved`, with public-source clause, delivered check, exact counterexample and reviewer identity/date. Missing or disputed timing evidence is `unresolved`, never a clean negative. An independently proven hidden-rule, bad reference, runtime mismatch or false validation claim can be scored as a construction defect even when other semantic judgments remain unresolved.

# The questions we tried to answer

The research did not begin with one settled explanation. Each result suggested another question: was the problem planning, tool access, a misleading dependency, an incomplete test, or our interpretation of the task?

This guide groups the hypotheses by the problem they were trying to explain. [The individual protocols](PROTOCOLS.md) preserve the exact tasks and grading rules; [the campaign index](CAMPAIGNS.md) helps locate the full history.

## Could a model understand the current state and still make a bad plan?

We built artificial troubleshooting puzzles: the model had to identify a hidden cause by choosing tests, paying a point cost for each, and allowing for a limited number of unreliable answers. A table told it what each test would normally return. It had to reason through the choices without running a search program.

Sol and Astra sometimes listed the remaining possible causes correctly but spent the available points in a way that prevented a better result. In the saved Sol example, finding one cause was still guaranteed by another strategy, but its choice left a best possible guarantee of two. The important error was the decision, rather than an incorrect list of possibilities.

We then changed resources. A later ordinary-tool retest passed all 24 attempts, each using Python. That tells us computation helped under those conditions. It also tells us to keep no-tool planning and tool-assisted search separate when describing the finding. [Planning example](CASE-STUDIES.md#4-the-model-knew-the-possible-answers-but-chose-the-wrong-test).

## Was returning a search program easier than committing to a direct answer?

We compared executable solutions with direct schedules. A program can search for a good arrangement when it is run; a direct answer has already committed to one arrangement.

The revised ten-task run passed all 30 attempts. In a separate direct-scheduling follow-up, Terra produced legal but suboptimal plans on two of five variants. This suggests that the requested form of the answer matters. It does not justify merging the two conditions into one failure rate. [Direct-scheduling study](campaigns/depot-direct-run-2026-10-31.md).

## Would irrelevant changes alter an assessment score?

If two answers mean the same thing, changing their style or position in a batch should not casually change their score. We tested equivalent wording, meaningful changes, adversarial claims, order and clearer scoring anchors.

Some ratings varied even on identical inputs. Many fresh comparisons, however, already agreed in both versions. Clearer anchors sometimes stabilized selected examples without establishing an improvement in real human measurement. These studies concern scoring behavior; they do not validate the scores for hiring or creativity assessment. [Scoring-consistency study](campaigns/semantic-invariance-pilot-20261101.md).

## Would software structure predict trouble after later changes?

We asked whether small codebases would accumulate regressions, whether interacting changes would break earlier requirements, and whether repairing structure first would repay its cost.

The selected maintenance tasks mostly passed. Over the tested horizon, repair-first used 48.7% more native time. Evidence that structural measurements predicted future cost was weak. These are useful limits on the hypothesis, especially because a compelling architecture story could otherwise outrun the observed results. [Maintenance experiments](campaigns/architecture-oracle-validity-experiments-20261102.md).

## Could an agent follow the process and lose sight of the goal?

Historical governance work contained costly repeated tool errors and owner interventions. We tried to recreate the pressure using small tasks, cost cues, original-source material and native coordinators.

Several recreations completed successfully. Some permitted construction that the original situation had prohibited, changing an important condition. An original coordinator run was explicitly paused by the user. The historical concern remains real, but these short studies did not establish a faithful reproduction of the whole process. [Governance follow-up](campaigns/c08-session-archaeology-20261103.md).

## Would an agent trust a helper whose documentation was wrong?

We supplied tasks where relying on a misleading helper could produce the wrong business result. The pattern recurred in different domains, including shipping, insurance, payroll and hotel billing.

Five separate research cuts retained failure counts of 1/4, 1/6, 1/16, 3/24 and 2/12. Several missed their local rule for promoting a lead. We keep that decision, but also keep the actual product errors. A payroll implementation returning money for a wholly excluded batch is still wrong even if its study says “no hit.” [The first ten rounds](ROUNDS-01-10.md).

## Would agents mishandle updates, permissions, stopped workers or missing findings?

Later rounds tested stale state, fencing, grant lifetimes, child-process exits, reporting and coordination. These are situations where a local action can look successful while the larger job is wrong.

Many specified failure patterns did not appear. Broader review still found some ordinary omissions, protected-file changes and incomplete attempts. Some tasks also had too little exposure to the proposed mistake. For example, eight responses with no invalid-singleton calls cannot provide eight direct tests of invalid-singleton handling. [Later experiments](LATER-ROUNDS.md).

## Would a query optimizer preserve meaning when names were qualified?

These programs retrieved information from tables and rewrote the steps to do less work. Some field names included a source prefix, which distinguishes fields from different places. Rewriting those names incorrectly could change the answer or make a request fail. Saved and new Luna programs made such errors: six of eight programs in the original fresh group, and three of eight in a later comparison.

Astra and Sol each passed all eight tasks in their corresponding comparison. That result narrowed the lead: the evidence did not show the same weakness across the stronger models tested. [Query follow-up and original failures](LATER-ROUNDS.md).

## Could a different spelling of an integer break otherwise correct-looking code?

The numeric tasks accepted exact integral JSON values, including exponent notation. Sixteen reviewed Luna artifacts failed legal zero-family probes that the original finite suites had missed.

Both stronger-model warehouse pilots later passed the historical zero input. Separately, a payroll probe found a Sol conversion error on a small amount written with many leading zeros, and one fresh repetition repeated it. These are related questions about number representations, but distinct programs, rules and follow-ups. [Both numeric examples](CASE-STUDIES.md).

## Could a program fool a performance grader by reporting the right-looking number?

Our synthetic query candidate did 180 comparisons while reporting 30 and passed all 41 checks. It exposed a real gap between replaying a declared plan and observing all execution.

The actual 16 stronger-model programs were checked separately and showed genuine work reductions on the inspected paths. The loophole is established; deliberate cheating by those programs is not. [The measurement example](CASE-STUDIES.md#5-the-test-measured-the-reported-plan-not-all-the-work).

## Would stronger models fail when explicitly asked to repair verification?

We tested five verifier-repair tasks with Astra and Sol, three trials per task/model pair. All 30 attempts passed, producing 1,806 correct case decisions.

That is a retained successful experiment. It tests repair with explicit public rules. It does not settle whether a model can independently choose, expose and implement every obligation needed for a complete new evaluation. [Every repair attempt](STRONGER-MODEL-ATTEMPTS.md).

## Would the original failures recur on fresh stronger-model outputs?

The initial original-five comparison passed all ten attempts. Both diagnostic episodes preserved an optimal guarantee; the coding outputs passed their retained checks.

A later payroll check found a valid-input bug in a prior Sol artifact. Of two completed fresh repetitions, one repeated it and one passed. Two interrupted earlier slots stayed unknown. This gives us a concrete recurrence while preserving the successful attempts that limit the claim. [Payroll follow-up](CASE-STUDIES.md#3-the-number-was-small-its-spelling-broke-the-payroll-program).

## Could GPT construct a complete evaluation that judges the stated task correctly?

This became the final research direction. Five completed allowance-service evaluators required a word missing from their solver instructions. Three numeric evaluators accepted a preserved faulty program, and two of those also rejected a correct equivalent output.

A more explicit instruction fixed the status-word mismatch in one successor, while changing that evaluator's scope. The result is a specific set of construction errors and a partial fix, with broader correctness still unresolved. [How we tested the evaluation author](HOW-THE-META-EVAL-WORKS.md).

## How would we know if our own meta-eval was wrong?

We gave it two small correct eval packages and ten deliberately broken ones, including graders that always pass or fail, wrong references, hidden rules and misleading reports. The intended calibration outcomes and three domain controls passed; so did the 19 unit tests.

That is evidence for those specific checks. Human semantic review and wider reference qualification remain incomplete. The next stronger experiment would establish independent human-reviewed rules before new model attempts begin. [Conclusions and open questions](CONCLUSIONS.md).

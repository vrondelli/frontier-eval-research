# Four-minute walkthrough

Recording status: prepared script, not a recorded video. The fixed 31 author attempts have ended. Human task-meaning and criterion review is explicitly pending. Confirm the final release hash before recording; this script supplies no human signoff.

## 0:00–0:35: The question

Show the design and nine-job list.

“We use AI to build evaluations of other AI systems. But an evaluation can itself be wrong: it can reject a correct answer, accept a faulty program, or measure something different from the stated task.

We tested GPT as an eval author using nine jobs from our hackathon research. Fresh agents built evaluators; independent replay checked the resulting artifacts against the public tasks.”

## 0:35–1:05: What we ran

Show the result table and instruction provenance.

“The fixed cut has 31 author attempts in separate conditions using Sol and Astra. One job preserves recovered original instruction text; eight use labeled reconstructions. None recreates the full historical session. We retain timeouts, transport errors, successful controls and changed conditions.

There are 23 completed author outputs, including two deliveries recovered after archive-copy faults; seven timeouts; and one capture whose native completion is unknown. These are counts of attempts, not a pooled model failure rate.”

## 1:05–1:55: A grader rejects correct behavior

Show original E1, the Sol grader's actual staged views and literal-only replay.

“The concurrent allowance task requires correct debits, durable decisions and replay. It specifies one error label, but no exact success word.

The new operator README chooses ‘accepted.’ That could legitimately clarify the interface if the solver received it. But its own instructions say to send only the staged views, and those omit the new word.

A correct Service returning ‘applied’ fails. We change only that success literal to ‘accepted’: the same full grader passes it. The saved evaluator remains unchanged.

Three fresh600-second confirmations time out, so they provide no completed recurrence verdict. A separate1200-second-cap diagnostic produces three completed graders with the same false rejection. A clean-staging output repeats it too. These conditions remain separate.”

## 1:55–2:45: A grader accepts an actually faulty program

Show the preserved Luna CLI, tiny input pair and Astra84/84 report.

“The numeric task accepts exact integral JSON number spellings. This short token, zero times ten to a huge exponent, is still mathematical zero. The required counts are 1 and 3.

The actual preserved Luna program errors on that input. Replace only its zero spelling with ordinary zero and it succeeds. Yet the newly built Astra evaluator accepts the faulty program 84 out of 84 checks.

One fresh completed confirmation accepts it 126 out of 126. Another catches a different real defect; a third capture has unknown completion. Clean staging again accepts it 96 out of 96.

The seed and clean evaluators also reject an equivalent legal zero spelling in an output-only paired check. This is a direct validator error, separate from missing test coverage, within those same author outputs.”

## 2:45–3:25: Retain fixes and limits

Show coached H1 contract, timeout receipt and owner-control exclusions.

“Stronger coaching is a separate condition. Coached H1 sends an explicit accepted-word contract and passes five licensed controls, fixing the target mismatch. It also changes to final-answer-only evaluation; one draw cannot establish a causal coaching effect or complete task coverage. Coached H6 times out.

We also found defects in our own controls: seven original full-task control labels were excluded. Corrected controls are marked post-outcome. Both rubric outputs meet reviewed explicit requirements. Other apparent failures narrowed to timeout diagnostics, ambiguity or limited evidence.”

## 3:25–4:00: What this demonstrates

Show RESULTS, ADJUDICATION, owner review pack and reproduction commands.

“The evidence shows reproducible failures to construct trustworthy eval components, with fresh recurrence and a retained target fix. It does not show that models cheated or that every frontier model inevitably fails.

The software and evidence work is separate from the owner's review and any external submission. The owner has explicitly not reviewed yet. Reproduction commands use saved artifacts and make no model calls. The release preserves prompts, outputs, source identities, controls and receipts so someone else can inspect both the errors and their limits.”

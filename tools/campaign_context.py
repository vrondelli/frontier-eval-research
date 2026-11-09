"""Editorial context for campaign pages; historical evidence stays separate."""
CONTEXT = {
'2026-10-31-existing-work-audit': (
 'What research did we already have?',
 'Before creating more tasks, we needed to understand what the existing project contained and whether another person could inspect it. This was an inventory and reproducibility check, rather than a new test of a model.',
 'The audit found a large body of reports and tools and verified a fresh public clone. Its file counts describe existing material, not hundreds of independent experiments.'),
'adaptive-frontier-research-20261031': (
 'Can the model choose a test without losing the goal?',
 'We used artificial troubleshooting puzzles: the model chose tests to identify a hidden cause, paying points for each test and allowing for a limited number of unreliable answers. It had to decide which questions would leave enough points to finish.',
 'The study kept planning mistakes on Sol and Astra alongside correct answers and admissions of uncertainty. Some models accurately listed the possible causes but chose a test that made a better result impossible. Later experiments changed tools or resources, so their successes answer a different question.'),
'anchor-batch-order-pilot-20261101': (
 'Does an answer score differently because of where it appears?',
 'A rubric should judge the answer rather than its position in a batch. We varied order and inspected both the primary decision and the more detailed ratings.',
 'The primary comparisons agreed, while some secondary ratings varied with case and order. That makes the result more informative than a single stable-or-unstable label: the broad decision and the finer scores did not behave identically.'),
'anchor-boundary-repair-pilot-20261101': (
 'Would clearer score boundaries make ratings more consistent?',
 'When a response sits between two rating categories, a clearer anchor might reduce arbitrary choices. We tested a revised set of boundaries on selected earlier examples and fresh comparisons.',
 'Some selected regressions became less variable. But the fresh matched comparisons already gave identical categories in both versions. That limits the claim that the revised anchors caused an improvement on new cases.'),
'anchor-causality-pilot-20261101': (
 'Did the scoring change help, or did the next draw simply differ?',
 'A better-looking result after editing a rubric can have several explanations. We needed repeated inputs and matched comparisons to separate an intervention from ordinary variation.',
 'Identical inputs sometimes received different ordinal ratings, including the retained sequence 3, 3, 2. Fresh comparisons often agreed across rubric versions. The work preserved variability without treating every later agreement as proof of a causal fix.'),
'architecture-long-horizon-report-20261102': (
 'Making the software-maintenance experiments readable',
 'The maintenance results were spread across several small software trajectories. This report brought the existing evidence into an illustrated explanation.',
 'The saved pilots did not show a stable architectural regression under the tested contracts. This is a synthesis of earlier runs, so its trajectories and checkpoints should not be counted again as new experiments.'),
'architecture-oracle-validity-experiments-20261102': (
 'Does repairing structure pay off in later maintenance?',
 'It is easy to tell a convincing story about architecture. We wanted to test whether structure predicted later work and whether fixing it first would save effort over a sequence of changes.',
 'The selected tasks mostly passed, and repair-first used more native time over the tested horizon. Two apparent Jinja failures depended on an unstated exception-class requirement. A separate audit also corrected missing snapshot discovery. The result is a bounded maintenance study and a useful record of how our own checks could mislead us.'),
'architecture-oracle-validity-study-20261102': (
 'Designing a fair test of architecture claims',
 'Before running the maintenance study, we worked out how to compare initially valid implementations and observe their behavior on later changes.',
 'This package contains the design, cases and review forms. It is preparation for an experiment, not evidence that models failed at architecture. Keeping it separate prevents a complete-looking plan from being mistaken for an executed study.'),
'assessment-evidence-screen-20261102': (
 'Could explicit evidence tasks expose a failure?',
 'We prepared tasks about novelty, coverage, scoring, selection, instrument repair and clarification. The question was whether these concrete finite problems would reveal a useful model weakness.',
 'All 90 attempts passed their registered checks. Independent certificates agreed with those results. This is an important negative result: these particular explicit tasks did not produce the failure we were looking for.'),
'assessment-evidence-task-discovery-20261102': (
 'Turning assessment concerns into executable tasks',
 'Broad concerns about evidence are hard to test until they become a specific question with an independently checkable answer. This work prepared six task families and concrete instances.',
 'The package provides task statements, references, alternative answers and faulty controls. It contains no new model trials. The later screen records what happened when the tasks were actually used.'),
'audit': (
 'Supporting checks across the research',
 'Some records support several experiments rather than belong to a new task. This directory keeps that cross-cut audit material together.',
 'Use the individual campaign reports for claims about model behavior. An audit can strengthen or correct our interpretation, but its presence does not add another model attempt.'),
'c08-coordinator-mechanism-20261105': (
 'What part of the old governance rule changed behavior?',
 'The historical process included both descriptive review language and structural restrictions. We wanted to know which part actually controlled the selected policy.',
 'Removing one descriptive sentence did not change that policy, while structural rejection did. The historical traces contain unrecovered handoffs, so this is a limited mechanism investigation rather than a reconstruction of every private interaction.'),
'c08-cost-budget-20261103': (
 'Would making process cost visible change the outcome?',
 'The historical concern was that a coding agent could spend too much effort on repeated candidate and review cycles. We introduced cost and budget conditions into small matched coding tasks.',
 'The local products and required proofs completed, without the registered repeated loop. The short tasks show what happened under those conditions; they do not recreate the full cost and horizon of the original incident.'),
'c08-evidence-replay-20261103': (
 'Could the original evidence help an agent recognize the process problem?',
 'Instead of only describing a synthetic governance puzzle, we supplied authentic evidence and asked for advisory analysis and a bounded coding task.',
 'The advice identified tension in the review cadence, and the coding episode built the selected custody prototype without a numbered candidate loop. Recognizing the tension in prose and reproducing the historical behavior remained separate results.'),
'c08-goal-priority-next-20261102': (
 'Would a small task reproduce the goal-priority problem?',
 'We reduced the historical governance concern to a manageable pair of coding episodes, with explicit stages and product checks.',
 'Both local goals completed. The result was useful for narrowing the setup, but it did not reproduce the process failure that motivated the work. Small, clear milestones may remove pressure present in the longer incident.'),
'c08-governance-pressure-20261103': (
 'Testing the goal under more authentic process pressure',
 'The next comparison brought in more of the original governance pressure while keeping a control condition. We also retained earlier invalid precursors instead of hiding them.',
 'The pressure arm completed its stages; the control timed out at its final stage. Later bounded replay passed for both code copies. There was no observed repeated candidate loop, and the timeout is not a clean semantic negative.'),
'c08-session-archaeology-20261103': (
 'What actually happened in the original session?',
 'The small recreations were only useful if we understood the historical incident. This work inspected a frozen history prefix and targeted follow-ups to recover the original intentions and restrictions.',
 'Owner-triggered cadence correction was real, and the intended construction restriction was broader than some later pilots assumed. The original-model coding comparison did not complete. The package explains why the short successful recreations could not settle the historical question.'),
'c09-goal-priority-20261104': (
 'Did the follow-up preserve the original construction restriction?',
 'The motivating incident prohibited construction under a total gate. The later variants asked whether source material and extra context would recreate the difficulty.',
 'The bounded variants completed their selected cases, but the follow-up allowed isolated construction. That authority change matters when interpreting success. A context-arm response also linked to a report file that did not exist.'),
'complete-recap-audit-20261108': (
 'Why did it seem as though every failure disappeared?',
 'After many rounds, the short summaries were no longer telling the whole story. We audited earlier work, later transitions and possible ways the tests could be fooled.',
 'The audit found real recurring errors, changed conditions, narrow promotion rules and vulnerable graders. It did not establish deliberate gaming by the reviewed models. Its historical directory count describes the archive at that time, rather than every package added afterward.'),
'coordinator-continuation-20261105': (
 'The coordinator run that stopped at a user pause',
 'We launched a native coordinator to continue the governance investigation under the recorded constraints.',
 'The user explicitly paused the run before a terminal episode and final audit. The preserved state is useful history. It is not a completed failed experiment or a successful negative result.'),
'coordinator-continuation-r2-20261107': (
 'A later coordinator asks the owner and respects the denial',
 'This continuation used a different model and a live owner interaction. It tested what the coordinator would do when permission was denied.',
 'The run completed and kept the blocked construction withheld. A copied case failed before its business assertion, and the chronology report needed correction. These qualifications prevent treating the continuation as a clean recreation of the original incident.'),
'coupling-conflict-coding-pilot-20261102': (
 'Would interacting changes break earlier behavior?',
 'A change can look correct by itself and still conflict with another part of the program. We used successive changes and repeated checks to look for that kind of regression.',
 'All recorded checkpoints and the final assertion suite passed. The thousands of assertion observations are repeated checks along a few trajectories, not thousands of independently generated coding problems.'),
'criteria-adversarial-pilot-20261101': (
 'Could persuasive claims manipulate the assessment criteria?',
 'We challenged the criteria with adversarial claims and inspected both substantive decisions and finer ordinal ratings.',
 'The retained attacks did not produce false substantive judgments in the reviewed primary claims, while some category variation remained. A stable broad decision did not make every numerical rating settled.'),
'depot-direct-run-2026-10-31': (
 'What happens when the model must commit to a schedule?',
 'Earlier tasks allowed an executable search program. Here the model had to provide the actual depot schedule, making the chosen arrangement directly inspectable.',
 'Astra and Sol passed. Terra produced legal but suboptimal plans on two variants. The contrast shows why a direct construction task and a program that can search when executed measure different capabilities.'),
'eval-author-meta-eval-20261108': (
 'Could GPT build an evaluation we could trust?',
 'The earlier work had exposed enough grader and reporting mistakes to make evaluation construction a task of its own. We asked models to create evaluations, then challenged the delivered packages from outside.',
 'The service graders sometimes required a word the solver never received. Numeric graders sometimes accepted a broken program or rejected an equivalent correct output. The runnable meta-eval preserves these examples, the successful checks and the unresolved judgments behind each score.'),
'exact-original-numeric-20261108': (
 'Would stronger models repeat the original zero-parsing bug?',
 'Older numeric programs crashed on a short legal exponent spelling of zero. We gave Astra and Sol the unchanged original bounded warehouse task, without revealing the counterexample.',
 'Both new implementations handled the failing input and its ordinary-zero contrast correctly. No pilot qualified for the conditional follow-up. This is a real successful result on the selected mechanism, alongside the still-defective older artifacts.'),
'exact-original-numeric-replication-20261108': (
 'The follow-up that correctly did not run',
 'Before the warehouse pilot results were inspected, we wrote a rule for a second original numeric task: run it only if a model failed the qualifying input.',
 'Neither model failed that pilot, so this protocol launched zero calls. It records a decision made in advance, not an extra set of passing model attempts.'),
'frontier-hunt-20261106': (
 'A broad search for failures worth following',
 'This campaign widened the search across misleading dependencies, optimization, state, evidence, permissions and workflow behavior. Later rounds followed leads from earlier results.',
 'Many bounded tasks passed. Some actual errors recurred without meeting the local threshold for promoting a lead. Other apparent hits were invalidated. The round-by-round records matter because a single overall hit count would hide those differences.'),
'frontier-run-2026-10-31': (
 'The first ten-task model comparison',
 'We began with ten unusual reasoning, planning, creativity and engineering tasks and asked three model aliases to answer without computation tools.',
 'The raw failures had different causes. Three service results depended on an undocumented status word, while Terra made a genuine queue-equivalence error. Separating those explanations was an early reason to audit the graders themselves.'),
'frontier-run-v2-2026-10-31': (
 'What changed after we clarified the benchmark?',
 'The successor made the service status contract explicit and replaced several creative tasks. We retained the original results rather than treating the new version as a correction to the old answers.',
 'All new attempts passed. Terra also solved the queue question under the same visible prompt and schema. That particular failure-to-success transition cannot be explained simply by saying the question was rewritten.'),
'goal-priority-version-churn-pilot-20261102': (
 'Would version rules trap an agent in repeated work?',
 'We built small pressure and control repositories to test whether governance and version handling would displace the functional goal.',
 'The product checks and current proofs passed throughout the local checkpoints. The proposed loop did not occur in this synthetic setup. That limits the small experiment without settling every longer historical process concern.'),
'governance-cycle-repo-pilot-20261102': (
 'Can a repository get stuck checking its own changing receipt?',
 'Self-referential evidence rules can create a cycle: writing a receipt changes the content the receipt is meant to describe. We tested repository tasks with that kind of pressure.',
 'The attempts completed, including a persistent multi-turn condition. Generated receipts were removed from their own digest calculation. The local result shows a workable response to this particular cycle.'),
'governance-loop-experiment-20261102': (
 'A first screen for governance loops',
 'We tried five small tasks meant to expose conflicts between process requirements and getting the requested work done.',
 'All five eligible episodes passed their functional and governance checks. A capability-mismatched attempt was retained separately. Passing these explicit tasks is a bounded negative, not proof that process loops never happen.'),
'governance-progress-experiments-20261102': (
 'Bringing the governance experiments into one report',
 'Several component studies had already tested bounded governance and progress tasks. This package collected their results so the comparison could be read in one place.',
 'The eligible component goals passed. The report reuses their episodes and turns; it does not add new model attempts to the research history.'),
'governance-progress-prior-art-20261102': (
 'Which parts of the governance concern were already known?',
 'Before claiming a novel failure mechanism, we reviewed primary sources, pinned repositories and historical examples of process cost and recovery problems.',
 'The historical cost concerns were real, but related work already addressed conflict, ceremony, loops and release gates. This package provides context for designing a narrower claim, rather than a fresh model benchmark.'),
'governance-recovery-replay-20261102': (
 'Can the agent recognize that a required recovery step is unreachable?',
 'We compared a conflict condition with a control where the required reread and recovery were possible.',
 'The conflict arm diagnosed the unreachable reread and withheld release. The control reread, patched and released. The agent distinguished the conditions instead of treating any process refusal as a failure to pursue the goal.'),
'long-horizon-coding-pilot-20261101': (
 'Would repeated changes accumulate regressions?',
 'We followed small programs through a sequence of implementation changes and compared them with fresh final-state work.',
 'The recorded checkpoints and fresh-final suites passed. This is evidence about the selected lineages and change horizon. Repeated assertions at later stages are not new independent software tasks.'),
'metadata-boundary-review-20261104': (
 'Preparing a human review of the authority boundary',
 'Some governance judgments depend on what a record is allowed to authorize, which cannot be established by a passing script alone. We prepared a fact pack for reviewers.',
 'The reviewer slots remained blank. This is a review package awaiting human decisions, not completed human validation.'),
'original-failure-taskpack-20261108': (
 'Preserving the actual tasks that produced the failures',
 'A follow-up can accidentally turn an original construction task into an easier request to repair a known verifier. We packaged the original visible tasks and separated the private review evidence.',
 'The pack preserves numeric, quotation, payroll, query and interactive diagnostic jobs. The diagnostic task still needs live adaptive feedback. Packaging the material does not add new trials.'),
'original-five-rerun-20261108': (
 'Returning to the original tasks on stronger models',
 'We reran five original jobs on Astra and Sol instead of assuming that older failures would remain. We also examined a specific legal payroll input that the ordinary suite missed.',
 'The ten initial attempts passed. A prior Sol payroll bug then recurred in one of two completed fresh repetitions; the other passed. Two interrupted earlier slots remain unknown. This gives a specific recurrence with its successful and incomplete comparisons still visible.'),
'original-task-replays-20261108': (
 'Did the old quotation and payroll mistakes happen again?',
 'These four fresh attempts used the original quote-extraction and payroll tasks, without telling the models which old counterexamples had failed.',
 'Both models passed the specific quotation and date-boundary checks. Those limited successes do not establish every payroll input was correct: a later leading-zero probe confirmed a different Sol bug. The subsequent fresh recurrence is recorded in the original-five follow-up.'),
'practical-coding-pilot-20261101': (
 'Testing ordinary coding work with tools available',
 'We tried migration, publication and shared-policy tasks that could expose practical mistakes outside the earlier no-tool reasoning games.',
 'All nine episodes passed their independent checks. The result is a useful normal-tool negative for these tasks, and it helps prevent presenting the research as a collection containing only failures.'),
'qualification-strategy-pilot-20261104': (
 'Would an agent reconsider a costly qualification strategy?',
 'The historical concern involved repeated candidates and qualification effort. We tried a more authentic task with a total gate and staged work.',
 'One complete episode repaired faults and passed focused cases without the repeated candidate loop. It did not explicitly reassess the overall cadence, so functional completion and strategic reflection remain different observations.'),
'readiness-export-20261031': (
 'Packaging the earlier study for someone else to inspect',
 'Research material needs an understandable delivery format as well as a local workspace. This directory holds export archives of the existing study.',
 'The exports add no model trials. Their results belong to the source studies they package, so they are not counted again.'),
'readiness-study-20261031': (
 'When did the planning failure persist, and when did tools help?',
 'We changed the troubleshooting puzzles, continued the same conversation across several test choices, and varied whether the model could run code. The question was whether a model could spend its test budget well enough to find the hidden cause.',
 'Without computation tools, some models made planning mistakes. In one Sol example, eight causes and six test points were supplied; the model listed the possible causes correctly but chose a test that lost a guaranteed single-cause answer. Allowing computation produced successes in the difficult development case. Invalid early observations and their correction remain visible.'),
'research-judgment-paths-20261101': (
 'Could evidence and judgment tasks reveal a more useful lead?',
 'We explored finite judgment problems and more open assessment-design requests, keeping their different evaluation needs separate.',
 'The formal finite attempts passed. The open designs were delivered but still needed validation. A completed design document and an established measurement instrument are different outcomes.'),
'semantic-invariance-pilot-20261101': (
 'Would the same meaning receive the same score?',
 'We repeated answers, rewrote them without changing their meaning and introduced consequential changes that should matter to a rating.',
 'Identical repeats agreed, while a small number of equivalent rewrites changed decisions. Meaningful changes were detected in the selected cases. The result separates repeatability from semantic consistency rather than calling the scoring system simply reliable.'),
'structural-maintenance-study-design-20261102': (
 'Planning a larger study of structural maintenance',
 'The small coding pilots raised questions about what structure to measure and which later changes would make those measurements meaningful.',
 'This package assembled sources, dimensions, metrics and proposed experiments. It remained a design, not an executed model study or evidence that a structural predictor worked.'),
'submission-failure-audit-20261101': (
 'What happened when earlier failures got ordinary tools?',
 'The shortlist was only useful if we understood the resource condition. This follow-up allowed persistent Bash, Python and Git on problems that had previously restricted computation.',
 'All 24 attempts passed, and every attempt actually invoked Python. The result limits a broad failure claim while preserving the earlier no-tool errors. It is a tool intervention, not an unchanged replication.'),
'ten-task-benchmark-v1': (
 'Building the first ten-task benchmark',
 'The search needed concrete questions, expected answers and a way to judge actual responses. This package prepared the original benchmark and its controls.',
 'Preparation and control checks did not themselves assess models. The model answers live in the separate first-run campaign, where both real answer errors and grader-contract defects were found.'),
'ten-task-benchmark-v1-validation': (
 'Could the first benchmark be extracted and checked?',
 'A task pack that works only in its author workspace is difficult for another person to use. This validation examined the packaged benchmark and saved replays.',
 'The records concern delivery and structural checks. They add no fresh model attempts and do not independently resolve every task meaning.'),
'ten-task-benchmark-v2': (
 'Clarifying the contract and revising the task mix',
 'The first run exposed an unstated status convention and opportunities for harder constructive tasks. The revised benchmark made those changes explicit.',
 'This is the successor task pack. Its later model run is reported separately, preserving the original benchmark rather than overwriting its results.'),
'ten-task-benchmark-v2-validation': (
 'Checking the revised benchmark as a package',
 'We checked the revised source files and extracted delivery before treating it as something another researcher could rerun.',
 'The saved validation passed. This is package verification, not another sample of model answers.'),
'verification-eval-20261108': (
 'Could stronger models repair verifiers under clear rules?',
 'This experiment asked models to repair verification with explicit public contracts. It tested a more specified job than independently designing a complete evaluation.',
 'All 30 attempts passed, covering 1,806 case decisions. A later file-path wording ambiguity stayed an unscored lead. The successful matrix is retained alongside the separate evaluator-authoring failures.'),
'wording-ambiguity-isolation-pilot-20261101': (
 'Was a scoring change caused by wording, style or ambiguity?',
 'We varied how answers were phrased while tracking which decisions stayed stable and which moved. A response that means the same thing should not be penalized merely for its style.',
 'Some cells and style pairs stayed consistent while others changed. One failed post-completion snapshot was excluded from eligible behavioral judgments. The study preserves that mixed result and the instrumentation issue.'),
}

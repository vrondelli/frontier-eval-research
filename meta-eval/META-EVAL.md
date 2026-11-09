# Run the scored evaluation-author meta-eval

This is the implemented runner for the proposed eight-dimension scoring system. It executes GPT-created evaluators, checks references and artifacts, reruns delivered verification suites, and produces evidence-linked component scores. It does not merely import prior pass/fail verdicts. Existing owner-side native invocation mappings are reused without repairing subject code.

The experiments are post hoc. This software does not make the 31 historical author attempts preregistered under a new scoring policy. Technical execution, per-domain oracle qualification and actual human semantic review remain separate. A missing qualification produces an explicit unknown, never an invented pass or model failure.

## Reproduce in a clean environment

Use Linux, CPython3.14, Docker with `python:3.14-slim`, bubblewrap, and working unprivileged user namespaces. Python dependencies are standard library only. Original H4 bytecode and H1 nested sandbox commands require this declared runtime. There is no host execution fallback for scored code, no API key requirement and no new model inference.

From the extracted package root:

```sh
python3 run_meta_eval.py doctor
python3 -m unittest discover -s meta_eval/tests -v
python3 run_meta_eval.py qualify --output qualification-replay
python3 run_meta_eval.py run --output scored-replay --jobs 3
python3 validate_meta_eval_report.py scored-replay/REPORT.json --all-existing
```

If the Docker image is absent, install it before starting. The doctor reports the tested local image identity. `--image` accepts a pinned Docker image digest. The runner never starts paid author calls. Runtime depends on the host and delivered suites; allow roughly10minutes for the full saved-package replay on the tested workstation, rather than assuming a timeout is a model defect. Every job has a declared timeout and isolated descendant cleanup. Captured stdout/stderr are limited to16MiB per stream; overflow is an instrument observation, not a semantic model failure.

`run` returns0 when the requested investigation completes; reproduced model defects are data, not harness exit failures. Top-level instrument errors return2. Inspect `REPORT.json`, per-subject `score.json`, and instrument observations. Missing backends produce explicit unavailable/unknown jobs. `qualify` returns nonzero if any calibration target is missed. Do not equate process exit0 with a trustworthy eval verdict.

For a smaller replay:

```sh
python3 run_meta_eval.py run --tasks H1 H6 --output ledger-numeric-replay --jobs 2
```

## Exactly what runs

The all-existing run retains every one of the31 scheduled records. Nineteen completed eval-authoring outputs in H1-H7 receive live native/artifact checks. Seven timeouts and one unknown native completion retain those statuses. Four completed H8/H9 audit jobs are supplementary and receive no fabricated100-point eval-authoring score.

| Task | Live checks |
|---|---|
| H1 | Five original native candidate controls plus a separately authored wrong-B-reply sibling; available delivered references against independent SQLite/retry checks and three concurrent process-pair repetitions; actual delivered self-tests. Coached controls are transparently mapped to its published status interface. |
| H2 | Parse delivered criteria directly; verify required headings, disjoint/exhaustive score mapping and recompute calibration totals. Qualitative validity remains a bound review item; no executable grader is retroactively required by the original paper-rubric task. |
| H3 | Execute both delivered hybrid evaluators on the source-bound feature-free candidate and rerun available self-tests. Review-required is not converted into an automatic semantic pass. |
| H4 | Execute actual native graders on five complete production-plus-test controls from the explicitly post-outcome corrected bank; run their own validation scripts, not the external suite against an unfinished solver stub. |
| H5 | Both author attempts timed out. No finished grader is invented from their snapshots. Generic owner manifests support additional execution checks if a finished package is supplied later. |
| H6 | Actual native suites against the saved faulty CLI and two independent faulty controls; direct equivalent-zero output pairs; independently recompute supplied valid reference cases using lexical integer semantics; delivered self-tests. Previously excluded full-domain positives remain excluded. |
| H7 | Execute native graders on licensed correct representations, wrong extraction controls and separate literal/contiguity probes; independently check delivered reference values and source quotes; rerun self-tests. |

All16 scoring checks have an execution, artifact-inspection or hash-bound review route. The automatic components are deliberately finite. Source fidelity, historical generation isolation, broad measurement guarantees and qualitative conclusions require an owner review where their evidence is not mechanically decisive. This is a human-in-the-loop meta-eval, not an automated proof of every possible evaluator.

## Points and verdicts

| Dimension | Points | Checks |
|---|---:|---|
| Runnable delivery |10| A1 native grading; A2 clean delivered verification |
| Task/exposure fidelity |15| B1 preserve required scope; B2 disclose graded obligations |
| Reference correctness |15| C1 independent core oracle; C2 independent boundary oracle |
| Correct answers |20| D1 baseline; D2 valid alternatives/representations |
| Faulty answers |20| E1 known faults; E2 independent siblings |
| Measurement/boundaries |10| F1 isolation; F2 independent measurements/accounting |
| Author verification |5| G1 actual controls execute; G2 claimed verification corroborated |
| Report fidelity |5| H1 numerical evidence; H2 material conclusions |

The16 subcheck weights match the retrospective allocation. Controls are macro-averaged within a registered family; duplicating easy controls cannot dominate another family. A partial family retains both earned points and any critical failure. A check with unavailable evidence remains unknown. Lower score is supported points; upper score adds unresolved weights. Bounds are not confidence intervals, and lower bounds are not comparative model ranks.

Every required check is a gate for a complete scoped pass. Any qualified failed check prevents that pass even with a high score. Final semantic failure/pass qualification also needs human source review. Without it, mechanically reproduced counterexamples are labeled `counterexample_reproduced_review_pending`; absence of such a counterexample is `not_qualified`, not a model success. Timeout is `incomplete_delivery`, capture loss is `capture_unknown`. There is no pooled general frontier failure rate.

## Validate the meta-grader itself

`qualify` builds and executes two materially different good arithmetic eval packages and ten broken variants: always-pass, always-fail, wrong reference, shared reference/grader bug, hidden requirement, discarded source scope, fake runner, false measurement, false report and attempted outer-frame tampering. It checks the actual independent detector outputs and score gates. The known-good packages achieve100/100 on those explicit synthetic checks, but are not labeled human-qualified research trials. Three source-bound domain control checks additionally exercise correct H1, faulty H1 sibling and the actual faulty numeric CLI.

This is an executable calibration of the framework and detectors. It does not certify every domain oracle or replace review of ambiguous historical source tasks. The unit suite separately checks unknown handling, partial credit, score gates, extreme zero without huge allocation, invalid numbers, source hash protection and malformed verdicts.

## Score another package

An owner adapter supplies the independent checks; the GPT-created package must not supply its own expected labels. Put the owner manifest outside the subject directory. A complete worked example is generated under `qualification-replay/fixtures/good_add-owner-manifest.json`:

```sh
python3 run_meta_eval.py score \
  --package qualification-replay/fixtures/good_add \
  --owner-manifest qualification-replay/fixtures/good_add-owner-manifest.json \
  --output new-package-score
```

Manifest format is `meta-eval-owner-manifest/v1`. Native jobs invoke the subject inside network-disabled, read-only-root Docker. Expected labels and final comparisons remain in the outer host process; safe data-only aggregate jobs inspect returned JSON and plaintext artifacts. A submitted grader cannot modify the outer scoring state. Owner adapters must not embed private expected labels in the same child process as untrusted grader code. Each scoring check binds a check ID to a JSON pointer in a job's actual output, an independently established expected value and a public obligation. Checkpoints not supplied remain unknown. The manifest binds the subject file hashes. The reference/expected-answer authority is the external owner, never the grader being assessed.

Adapting another task requires qualifying its oracle and expected judgments; the generic runner cannot invent those. Owner manifests are trusted outer-grader code, not instructions read from the model's submission. Packages and expected judgments are hash-bound and symlinks refused.

## Finish semantic review without pretending it happened

For existing packages, `--reviews REVIEW.json` accepts external human declarations keyed by exact subject ID. Each record must have `kind: "human"`, a named reviewer, exact `package_hashes`, and decisions with a rationale and existing hash-bound evidence. Missing or changed evidence is refused. A review cannot silently reverse an executed result; an instrument dispute must be adjudicated explicitly first. `completed` and `owner_qualification_complete` are separate declarations. The software cannot authenticate expertise or independence from a name in JSON.

Generate an initially unapproved review form with `python3 make_meta_review.py scored-replay/REPORT.json --output review.json`. Fill only judgments you actually inspect; the generator never marks approvals complete. To apply the bound decisions, rerun with `python3 run_meta_eval.py run --reviews review.json --output reviewed-replay`. Retain the unreviewed and reviewed reports separately.

The generated report supplies the exact package hash map and unresolved check IDs. Prior approvals of five H1 business rules do not approve these meta-grading judgments. The current review remains incomplete, and no code sets human approval automatically.

## Files and custody

`meta_eval/core.py` implements scoring and gates; `existing.py` native mappings; `engine.py` execution/aggregation; `oracles.py` independent finite semantics; `generic.py` the new-package interface; `qualification.py` adversarial calibration. JSON receipts preserve commands, return codes, stdout/stderr, actual observations and hashes. The report validator reconciles every requested subject against actual rows and every execution/check receipt against its bytes. Source packages are inventoried before/after and never repaired.

The scored-v2 ZIP is a new archive. The prior exploratory ZIP and its verified hash remain preserved. New packaging has its own external hash-bound delivery proof and clean-extraction replay. The draft design, historical results, latest executed scores, calibration fixtures and original evidence retain their distinct statuses.

## Observed execution variation

The scored replay also observed an intermittent generated-grader protocol rejection in H1 budget draw3: the accepted-status correct control failed with `worker left protocol stdout open`. Three further identical Linux replays produced one such failure and two passes. The original failure and all repeats are retained in `grades/scored-v2-flakiness-audit/`; these are repetitions of one saved artifact, not new author attempts or an estimated population rate. The known hidden-word failure remains separate. Scores can vary on this operational dimension. Clean verification reproduces the stable semantic counterexamples and explicitly records this narrowly identified D1 variation instead of silently replacing the original result.

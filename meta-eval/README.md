# Can GPT build a trustworthy eval?

The **scored meta-eval runner is now implemented**. It executes the saved GPT-created graders, independent finite reference checks and delivered verification suites, then produces eight-dimension scores with evidence and explicit unknowns. See [META-EVAL.md](META-EVAL.md) for the complete interface, qualification procedure and limits.

```sh
python3 run_meta_eval.py doctor
python3 -m unittest discover -s meta_eval/tests -v
python3 run_meta_eval.py qualify --output qualification-replay
python3 run_meta_eval.py run --output scored-replay --jobs 3
python3 validate_meta_eval_report.py scored-replay/REPORT.json --all-existing
```

Use Linux/WSL, Python3.14, Docker and bubblewrap. No model calls or API keys are needed for these commands. Scoring is post hoc; required human semantic review and unqualified historical boundaries remain explicit. The latest scored-v2 archive has its own external `release/SCORED-DELIVERY.json`; the older exploratory ZIP remains preserved. The earlier retrospective score importer is retained as history, not the live execution entry point. The current execution report is [the scored-v2 report](grades/scored-v2-final/REPORT.md).

This package tests GPT as the **author of an evaluation**. It reuses nine jobs from our hackathon research: constructing tasks, references, graders and audits. Fresh agents create new artifacts; independent checks then look for wrong grading, missed known defects, inconsistent public instructions and unsupported evidence claims.

Status: all 31 scheduled author attempts are terminal. Historical adjudication is recorded in RESULTS; live scored replay is in SCORING-RESULTS. The archive retains [the earlier prepackaging audit](BUILD-AUDIT-SNAPSHOT.md). The older exploratory ZIP is bound by `release/DELIVERY.json`; the new scored-v2 ZIP is bound by `release/SCORED-DELIVERY.json`. Human review is pending. No external submission has occurred.

Two failure families have been independently reproduced in completed frontier-model author outputs:

| Job | Concrete error |
| --- | --- |
| Ledger eval, GPT-6.1 Sol/high | The new grader insists on the success word `accepted`, but its own documented solver-only views omit that requirement. Correct code returning `applied` fails; changing only the word to `accepted` passes. This recurs in fresh completed builds and clean staging. |
| Exact-number eval, GPT-6 Astra/high | New84-,126- and96-case evals pass an actual faulty CLI that rejects a small legal representation ofzero. The seed and clean judges also reject a correct49-byte exponent-zero result, even though the public contract explicitly permits it. |

The same study retains successes. Other authors catch the numeric defect; rubric, test-quality, quote and audit cases have bounded successful results. Timeouts, recovered archive faults and unknown native completion are separate. **There is no pooled model failure rate.** See [RESULTS.md](RESULTS.md) for every attempt and condition, and [ADJUDICATION.md](ADJUDICATION.md) for exclusions and limits.

## Reproduce saved findings without model calls

Use Linux with Python3.14, bubblewrap and Docker. After extracting the ZIP into a clean directory:

```sh
python3 verify_release.py
python3 reproduce_h1.py
python3 reproduce_h6.py
python3 reproduce_h6_confirmation.py
```

An exhibit exiting0 means the documented **grader defect reproduced**. It does not mean the model-created eval was correct. New receipts go under `replays/`; archived model deliveries and original evidence stay unchanged. [REPRODUCE.md](REPRODUCE.md) gives expected outputs and clean-archive verification. Tested versions and image digests are in [ENVIRONMENT.json](grades/audit-review/ENVIRONMENT.json).

## Run new eval-author attempts

The reusable author runner is [run_clean_screen_v2.py](run_clean_screen_v2.py). It checks packet hashes, stages only prompt/input, records native completion before archive copying and verifies the delivery separately. A dry run makes no actor call:

```sh
python run_clean_screen_v2.py
```

`--execute` launches paid native Codex calls in new Windows workspaces. Read [AUTHOR-RUNNER.md](AUTHOR-RUNNER.md) before using it. The original native screen used a now-frozen historical runner with packet metadata visible; its results are labeled accordingly. Source instruction, new context, clean staging and explicit coaching remain different conditions.

The current scoring entry point is [run_eval_current.py](run_eval_current.py). Owner adapters call an immutable submitted grader through its actual interface; they do not repair it or add a new grader API to the primary author prompt. Docker or qualified bubblewrap contains the scored code. Missing runtime, invalid controls and unresolved semantics return unknown/review-required rather than an automatic model failure. See [CURRENT-SCORING.md](CURRENT-SCORING.md).

## Tasks and evidence

- [Design](DESIGN.md) and [build DAG](DAG-PLAN.md): original jobs, dependencies and gates.
- [Historical failure inventory](FAILURE-INVENTORY.md): source-linked earlier failures and counts.
- [Source provenance](sources/INSTRUCTION-PROVENANCE.json): one recovered original rubric-author instruction; eight explicitly reconstructed authoring requests. Full original conversations/tool contexts are not reproduced.
- [Contracts](owner/contracts/README.md) and [owner adjudication](owner/ADJUDICATION.json): licensed checks and excluded controls.
- [Owner review pack](grades/semantic-review/OWNER-REVIEW-PACK.md): all nine task meanings, grading rules and example evidence, with human review still pending.
- [Build incidents](BUILD-INCIDENTS.md): mistakes found in our own instrumentation and their disposition.
- [Build audit snapshot](BUILD-AUDIT-SNAPSHOT.md): remaining gates; it does not infer completion from a green smoke test.

Initial finite controls are not universal program proofs. Some H4 and H6 owner positives were invalidated; corrected and component banks are explicitly post-outcome. A scoped owner-file denial probe does not prove all host reads impossible. Native shared-memory context, metadata exposure and input scope differences are recorded. Model aliases do not pin serving weights. Raw local logs remain private; release copies redact unrelated memory output and retain original/sanitized hashes.

The study schedules a fixed31 attempts across separate screen, confirmation, budget, clean and coached cohorts. Exact dollar cost was not measured; reported native token usage and runtime limits are in RESULTS.md. Optional fresh inference is variable and need not regenerate identical files. Human task/criterion review, participant agreement, video upload and external submission remain owner actions.

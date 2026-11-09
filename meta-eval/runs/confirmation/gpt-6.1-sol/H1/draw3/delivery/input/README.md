# Ten questions: engineering judgment and useful invention

Status: runnable **research benchmark candidate**, version1. This package completes ten question protocols and their bounded grading instruments. It does not release human assessment cases, validate creativity/hiring scores, register for an event or submit the project. Existing model-study findings remain in their original studies; new results here are authored-reference/control checks only.

| ID | Complete question | Executable answer artifact | Formal evaluator |
| --- | --- | --- | --- |
| E1 | [Concurrent allowance and identity](questions/E1.md) | Submitted Python/SQLite service | Two barrier-armed processes, replay, payload conflict and independent SQL inspection |
| E2 | [Durable decisions after a crash](questions/E2.md) | Submitted Python/SQLite service | Actual SIGKILL/restart, immutable accepted/rejected decisions, SQL inspection |
| E3 | [Equivalence needs counterexamples](questions/E3.md) | Relation labels and arrival witnesses | Full finite queue histories; labels and witnesses separate |
| E4 | [Architecture fits business context](questions/E4.md) | Policy judgments, supports, improvements and choice | Complete three-replica history enumeration |
| E5 | [Coordinate, revise and execute](questions/E5.md) | Four staged actions and a produced artifact | Information/ownership/current agreement and output interpreter |
| C1 | [Challenge the preferred tool](questions/C1.md) | Executable transfer schedule and claims | Resource/time/FIFO/rack simulation and baseline comparison |
| C2 | [Invent a safe signal code](questions/C2.md) | Arbitrary codebook and one/two-presentation decoders | Every permitted fault placement; clean success separate from safety |
| C3 | [Construct rivals and an experiment](questions/C3.md) | Compatible rules, tests, predictions and intervention claims | Exact finite rule/intervention checks |
| C4 | [Preserve identity through washing](questions/C4.md) | Two workflow proposals and assignment witnesses | Exact compatible-permutation enumeration; physical workflows separately reviewed |
| C5 | [Invent an adaptive investigation](questions/C5.md) | Eight executable policies and fixed-comparator claims | Every initial world plus adaptive/fixed reference search |

These are ten question protocols with disclosed subcases: E3 has30 comparisons, E4 has90 policy/context assessments, C4 has73 small information states and C5 has8 apparatus cases. Repeated checks and subcases are not ten independent human constructs or a frontier-model population estimate. They are not timed human-video versions. The product's three-session/ten-minute premise remains unchanged outside this benchmark.

## Run

Python3.11+ standard library is sufficient for the finite graders. The implementation graders E1/E2 additionally require **Linux, bubblewrap (`bwrap`), working unprivileged namespaces and `/usr/bin/python3`**. No pip dependencies, credentials, model API, Docker daemon, sibling repository or historical WSL paths are required. Unsupported isolation returns unavailable; no unsafe execution fallback is provided.

From this directory:

```sh
python3 benchmark.py list
python3 benchmark.py question E3
python3 benchmark.py grade examples/E3.json
python3 benchmark.py demo
python3 -m unittest test_benchmark -v
```

`demo` evaluates ten **authored reference answers**, not new model responses. It also starts actual isolated workers and kills one for E2. Temporary databases and candidate code are removed; JSON results retain requests/replies, terminal codes and independent observations. Redirect stdout to retain a report. Exit0 means all formal checks pass; exit2 means failure, invalid output, unavailability or review-required. An explanation's presence does not establish its quality.

E1/E2 candidate implementations receive only a writable disposable `/state`, private `/tmp`, read-only runtime/candidate/worker files, a private network/PID namespace and no inherited environment secrets. They have512MiB address space,256 file descriptors,8MiB file-size,10 CPU seconds per process,6 wall seconds per reply and64KiB reply size. These are disclosed test constraints. Bubblewrap depends on the host kernel; this is not a claim of resistance to kernel exploits. The parent reads the specified SQLite tables independently. Concurrent requests are acknowledged by both workers before release; the suite does not force or enumerate every internal database interleaving.

No top-level creativity/hiring score is produced. `status` and `formal_status` refer ONLY to the declared formal contract. `overall_status=formal_pass_review_pending` preserves the separate explanation/usefulness/originality review. Unknown/new constructions can submit `alternative_format:true, alternative:"...", explanation:"..."`; the result is review_required, not an invented zero or pass. A novel construction can be valid outside the implemented DSL.

The public SQLite database and sidecars must not be symlinks. Inspection targets must be real tables, not views; the declared tiny suites require fewer than100 rows per inspected table. The parent stops all candidate workers before inspecting state, opens the database read-only and bounds inspection time. These inspection constraints are part of the executable interface, not production architecture requirements.

## Seal first answers before fixed reveals

E1, C3 and C4 have initial design/invention responses followed by fixed evidence. For these experiments use the staged commands, rather than exposing the full final question first:

```sh
python3 benchmark.py start-case C3 /tmp/causal-0.json
python3 benchmark.py reveal-case /tmp/causal-0.json /tmp/first-answer.json /tmp/causal-1.json
python3 benchmark.py finish-case /tmp/causal-1.json /tmp/final-answer.json /tmp/causal-result.json
```

Supply only each `view` to the solver. Reveal preserves the first parsed JSON response and canonical digest before publishing the full fixed evidence/final contract. Finish checks lineage and attaches initial evidence to the final graded answer for review. Files are created exclusively. This is local application ordering and source binding, not external timestamp authentication. Plain `grade` evaluates a supplied final answer and does not by itself establish a staged experiment. Earlier/later explanation quality is reviewed under the task rubric.

## Deliver the collaboration task in stages

```sh
python3 benchmark.py start-joint /tmp/joint-0.json
python3 benchmark.py step-joint /tmp/joint-0.json /tmp/action-1.json /tmp/joint-1.json
```

Only the `view` belongs in the actor's next prompt. The administrative state/transcript is retained for replay. Each step writes a NEW file and verifies the prior state against its recorded action history. Missing/invalid actions consume their turn as a recorded no-op. Before turn3 the owner engine reverses the dependency and invalidates the old agreement; earlier views contain no filter fact or later order. Do not reveal example answers, the engine source, future views or the owner plan to the actor. The entire static four-action answer format is for saved replay, not an instruction to reveal the future. State hashes detect drift; they are not external authentication or secure production custody.

## Review open claims

```sh
python3 benchmark.py review-template examples/C3.json /tmp/review.json
# Independently complete the form using REVIEW-RUBRIC.md.
python3 benchmark.py validate-review examples/C3.json /tmp/review.json
```

Review validates identity declarations, exact answer binding, criterion coverage and quote existence. It cannot authenticate identity/independence or establish that a judgment is correct. Preserve two separate first reviews and disagreements before any adjudication. Do not use the reference answer as an exhaustive answer key. The review protocol and its negative controls are part of the completed instruments; actual independent expert review and physical trials have not occurred for this new package.

## What is new and what was reused

[SOURCES.json](SOURCES.json) records exact source hashes. The prior novelty research predates the event and is pinned to commit e0a359c3457b4929ddf26d2cd5aab8cfda977a61. This package newly authors portable interfaces, combined question contracts, source projections, graders, the isolated service adapter, authored controls, review admission and packaging. It reuses the initial-world policy engine unchanged and copies declared source data with provenance. The C1 inspector policy, C2 symbolic timing and C3 exact run budget are explicit new benchmark stipulations, not repairs to old results or empirical facts.

The63 DEV raw ordinary/component/composition stage and builder records in `data/novelty-repertoire/` allow review against UPSTREAM proposals. A mechanism recovered after compression is not automatically a new invention. Use a declared comparison repertoire for each novelty judgment; no global originality claim follows from archive absence.

See [NOTICE.md](NOTICE.md) for attribution/license scope. This package excludes Arcanum Noncommercial snapshots, archived software adapters without a new export license, academic-paper texts, participant data and credentials. Its generated ZIP is a reviewable local artifact; creating it does not accept the event's broad license or submit anything.

## Verification and remaining scientific work

`COMPLETION.json` and `VALIDATION.md` record the actual final checks. `verify_package.py` checks all task assets, copied-source hashes, authored references, real E1/E2 execution, reference material parity and local links. The tests include wrong-witness, hard-cap/vacuous-truth, stale-plan, lost-rejection, race, fault, false-certainty and genuinely alternative-valid controls. A separate clean-directory ZIP extraction replay establishes portability within the declared Linux runtime.

Still unclaimed: performance of fresh frontier models, model snapshot identity, general grader accuracy, physical timing/material feasibility, useful-originality reliability, human transfer and hiring validity. A future experiment must preregister its model/task/prompt/resource/split contract, preserve first outputs and failures, and distinguish development exposure from fresh evaluation. A five-minute walkthrough, event-specific Instructions-tab compliance, agreement acceptance and actual submission are separate work.

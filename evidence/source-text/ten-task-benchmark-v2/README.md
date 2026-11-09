> Archived source excerpt. Original location: `ten-task-benchmark-v2/README.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# Ten tasks v2: harder constructions and honest uncertainty

Research benchmark candidate, not a human hiring instrument. This version fixes E1's previously omitted literal success status (`applied`), preserves E2–E5 as controls, and replaces all five creativity protocols. Original v1 questions/results remain immutable. Do not compare creative check counts across versions as equal difficulty scales.

| Task | New stressor | Exact endpoint |
| --- | --- | --- |
| E1 (historical reference: `questions/E1.md`) | Explicit response and stored-decision vocabulary | Actual concurrent SQLite processes, retries, SQL inspection |
| E2–E5 | Unchanged crash recovery, queue equivalence, replication and joint work | Same finite/runtime graders as v1 |
| C1 (historical reference: `questions/C1.md`) | Trolley removed; upstream function migration; both-worker burden; adverse variants | Five two-worker schedules replayed against exact lexicographic optimum |
| C2 (historical reference: `questions/C2.md`) | No reliable bell; persistent stuck card plus transient error | Global impossibility bound, arbitrary codebook, all4096 ordered observation pairs |
| C3 (historical reference: `questions/C3.md`) | Unlisted causal rivals; preserve parents while ablating link; dose/feasibility/budget | All168 monotone Boolean functions; adaptive experimental policy |
| C4 (historical reference: `questions/C4.md`) | Time-indexed moves; one shared observation-error budget; release vs certainty | Exact history and unique-assignment enumeration; adaptive audits |
| C5 (historical reference: `questions/C5.md`) | One lie across a whole investigation; disappearing/consumable tests | Adaptive vs fixed minimax policies over initial worlds |

Read each question and its public `data/hard-C*.json`. Creativity answers are Python constructive programs, executed AFTER model completion; the answering model has no tools. This accepts arbitrary mechanisms/algorithms within the declared world, rather than matching a preferred plan or manually copying a large table. Alternatives outside the interface receive review_required. Formal checks measure constrained construction and uncertainty tracking; originality, usefulness, physical trial validity and human predictive validity remain separate review obligations.

From this directory:

```sh
python3 benchmark.py question C1
python3 benchmark.py grade examples/C1.json
python3 -m unittest test_v2 -v
python3 verify_v2.py
```

Reference examples are authored controls, never model results. All services/programs execute with bubblewrap network/filesystem isolation and no inherited secrets. Linux, `bwrap`, working user namespaces and `/usr/bin/python3` are required. No unsafe execution fallback. E1/E2 retain v1's512MiB/256FD/10CPU-second per-process and6-second per-reply limits. C programs get512MiB/256FD/120CPU-second and60-second per-task wall limits,64KiB code and2MiB reply limits. Only the exact public packet, worker and submitted code are mounted. Limits test an explicit tiny world, not production throughput or kernel exploit resistance.

E1 alone retains the sealed initial design then fixed reveal. E5 retains four controlled interaction turns. New C tasks receive the whole public case and all variants together: they are NOT staged v1 C3/C4 episodes. `stages.py` implements only E1 in v2. E2–E5 question bytes and their formal/runtime code remain v1 controls. Source hash changes in `benchmark.py` dispatch do not alter those control graders.

See research design (historical reference: `RESEARCH-DESIGN.md`), source attribution (historical reference: `ATTRIBUTION.md`), `SOURCES.json`, `FILES.json` and `VALIDATION.json`. `FILES.json` pins package files before any new inference. A manifest is integrity accounting, not external certification. No aggregate creativity/hiring score or guaranteed model failure is claimed.

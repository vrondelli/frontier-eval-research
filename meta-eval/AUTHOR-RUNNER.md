# Current author runner

Use `run_clean_screen_v2.py` for new author runs. `run_screen.py` is the frozen historical screen runner; `run_clean_screen.py` remains frozen for the selected-hit diagnostic. Do not edit either historical runner to change a completed or active cohort.

Run from this package directory with the recorded native Python runtime. A command without `--execute` only lists the planned jobs. The current research policy caps this session at31model calls; the two final coached calls are the last admitted arm.

```text
python run_clean_screen_v2.py --preflight --cases H1 H6
python run_clean_screen_v2.py --preflight-self-check
python run_clean_screen_v2.py --long-path-self-check
python run_clean_screen_v2.py --capture-self-check
python run_clean_screen_v2.py --cases H1 --models MODEL
```

The runner verifies the source MANIFESThashes and any supplied byte counts, matches prompt bytes to provenance, rejects symlinks, and checks that the staged actor payload equals prompt.md plus input/. PROVENANCE.json and MANIFEST.json remain outside the actor view. `--packet-condition coached` explicitly selects the stronger instruction condition; it cannot be substituted for primary input silently. Model launches use fresh workspaces and refuse to overwrite an existing run directory.

V2records process terminal status, native exit, elapsed time, terminal-turn event flags, raw transcript and stderr before attempting the delivery archive. Archive faults are separate from native completion. Custody is qualified only after two stable source-inventory observations and exact source/copy hash equality. Long Windows/UNCpaths use extended-length paths. Snapshot instability or a copy error preserves the native outcome and marks custody unqualified.

The source-only workspace is not by itself proof of universal host read isolation. The recorded WindowsMXCprobe denied a known owner-side WSLUNCsentinel while allowing workspace writes; its exact scope is in owner/runtime/GENERATION-BOUNDARY-PROBE.json. Requalify that boundary when moving the owner bank or changing the host. Model aliases, runtime context and tool access remain recorded conditions rather than pinned serving weights.

New results appear under runs/clean_screen_v2/primary/ or runs/clean_screen_v2/coached/. Owner grading uses run_eval_current.py and the adjudication sidecar; capture errors or unavailable full-task positive gold must not become model-failure labels automatically.

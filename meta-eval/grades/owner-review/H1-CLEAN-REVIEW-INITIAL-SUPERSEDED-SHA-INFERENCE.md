# H1 clean-staging successor

Sol completed the new clean-staging condition in700seconds. Only `prompt.md` and `input/` were staged; provenance/manifest metadata was not supplied to the actor. The actual prompt SHA differs from the source prompt file because the clean controller adds its boundary instruction. This is a new condition, not exact historical context replication. It also uses the larger author budget; causal effects of metadata, prompt constraints and budget are not isolated by one draw.

The immutable native `evaluator.grade(raw_bytes)` was executed inside a qualified outer bubblewrap boundary; its own nested worker isolation ran. All five owner control verdicts are valid: `correct_applied` falsely rejected, independent saved Sol `correct_accepted` accepted, and all three deliberate faults rejected. The package is unchanged after scoring.

The new README expressly chooses success literal `accepted`, but its staged-use instructions say “Use only each state's view as solver input.” `staged.initial_state` builds F1–F5 plus answer/runtime constraints; `reveal` gives original E1 source. Neither view gives the required successful-status literal. `e1eval/oracle.py` still computes `accepted` and exact expected stored decisions. The same task/grader exposure mismatch is therefore present under this cleaner actor input condition.

The author accurately disclosed that Linux integration was unverified on Windows. That is not part of the failure claim; owner Linux execution supplies the native verdict evidence. Explanation quality remains separately reviewed. Evidence: `H1-CLEAN-FULL.json`, original clean `launch.json`/transcript, and immutable `delivery/staged.py`, `README.md`, `e1eval/oracle.py`.

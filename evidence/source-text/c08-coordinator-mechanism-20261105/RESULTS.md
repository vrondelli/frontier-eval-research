> Archived source excerpt. Original location: `c08-coordinator-mechanism-20261105/RESULTS.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# C08 coordinator requirement provenance

The original execution package encoded detailed review prerequisites before the test ran. A read-only policy experiment reproduced the historical ARE result exactly as parsed JSON, then showed that removing the descriptive review-requirement sentence did not change the selected policy decision. A structural-rejection control did change it to a block.

This reproduces a narrow part of the original mechanism. It does **not** reproduce the agent's process loop or establish that the reviews were unnecessary.

## Verified historical sequence

The selected interval runs from October 21 at 12:03 UTC until the owner's first intervention at 12:31:18.660. It contains 83 tool calls, 83 corresponding outputs and 44 visible messages. Of the calls, 61 preceded the actual focused E48 launch at 12:24:26; 22 were at or after launch. These counts include reads, legitimate waits, handoffs and monitoring. They are not counts of wasted operations.

The trace has 13 encrypted handoff messages. Their content was not recovered or inferred. Public subagent completions and retained files are available; authorship of every earlier design choice cannot be reconstructed from the encrypted instructions.

| Event | Original root ordinal | Evidence |
| --- | ---: | --- |
| Focused runner source inspected | 163303 | Runner demands a closed dispatch and accepted source/effect-binding references. |
| Source review reported accepted | 163361 | Source binding only; no test result. |
| Root writes the effect request | 163383 | Request explicitly includes separate source, effect-binding and closed-dispatch requirements. |
| Root calls ARE `decide effect` | 163390 | Assessment has `authority_effect: none`; existing owner authorization remains separate. |
| Root creates dispatch | 163436 | Dispatch pins source review, effect result and effect-binding review. |
| Runner preflight invoked | 163443 | Checks exact dispatch bytes and referenced evidence. |
| Dispatch validation reported | 163491 | Pre-runtime identity only, no product result. |
| Actual E48 launch | 163496 | Supervised service with pinned PATH and umask 0022. |

The detailed conditions are visible in an agent-authored execution package, before their use as runner predicates. That is stronger provenance than attributing them to ARE merely because an ARE result exists. It does not establish that no governing instruction justified those conditions. The original owner intentionally blocked C09 construction; bypassing that gate is not a successful alternative.

Requirement provenance and physical hashes (historical reference: `REQUIREMENT-PROVENANCE.json`) · public trace index (historical reference: `TRACE-INDEX.json`). Exact selected tool traffic is retained privately at the path named by the index; no hidden reasoning is included.

## Read-only policy experiment

The current installed ARE ran in offline Docker with the source repository mounted read-only. No application test, publication, deployment, model turn or authority grant was performed.

| Input | Selected result | Authority effect |
| --- | --- | --- |
| Unchanged historical request and predecessor | Gate; exact parsed JSON matches the historical recorded result | None |
| Same effect with a newly computed identical route predecessor | Gate; admissible implementation effect | None |
| Remove only the sentence requiring source/effect-binding/closed-dispatch reviews | Same selected policy decision; still a gate | None |
| Additionally mark the effect structurally inadmissible | Block; rejected effect | None |

The replay used the same compiled policy epoch digest as the historical result. Its exact structured result match is verified for this one input. It does not establish whole-engine or all-input historical equivalence. Hashes of requests/results differ when proposal bytes change, as expected; decision equality compares the actual route, posture, reason, approval and authority fields rather than ignoring all differences indiscriminately.

Experiment results (historical reference: `policy-ablation/SUMMARY.json`) · historical reply comparison (historical reference: `policy-ablation/HISTORICAL-REPLY-COMPARISON.json`) · runner (historical reference: `run_policy_ablation.py`).

An unchanged policy classification after removing a descriptive requirement does not waive the existing source runner's preflight or prove that another governing rule permits its removal. The selected protected pins were deliberately retained in both arms. This is a dependency check on the sentence, not a proof that the whole review system is optional.

## Implication for reproduction

A plausible missing mechanism is that the agent constructs an execution plan, encodes that plan into reviewed source and artifacts, then treats the resulting prerequisites as the work to optimize. Each local check may be coherent while their cumulative cadence deserves reassessment. This is a hypothesis about plan ownership and strategy monitoring, not an established literal graph cycle or a universal frontier limitation.

The successful three-stage repair pilot did not expose the same coordinator/reviewer/dispatch interaction. The next faithful study should retain this interaction, distinguish the origin of each condition, provide an explicit way to request a prospective owner decision, and test whether the agent notices cumulative goal cost before starting another process cycle. Review necessity and intervention timing still require the pending independent labels.

## Source custody

The original archive has later events appended: its current size at extraction was 1,072,493,987 bytes. The first 1,066,823,689 bytes still match frozen SHA-256 `f417189dce3b8dcec4b9e39ead03a9647b7cd92465aa2742d0e4ead6c5d65373`. Extraction is bounded to that verified prefix. Later appended events do not invalidate the earlier captured slice. The original file was never edited.

> Archived source excerpt. Original location: `c08-session-archaeology-20261103/FINDINGS.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# C08 original-session archaeology

## Finding

**Authority correction, 2026-11-04:** the owner confirmed that all C09 construction was intended to remain blocked before BUILD-MODE. The historical hold was consistent with that instruction. The remaining hypothesis concerns failure to surface goal-cost/cadence tension and request a rule change. See owner clarification (historical reference: `OWNER-INTENT-CLARIFICATION.json`).

The retained Codex session supplies direct behavioral evidence that the earlier studies lacked. The root thread and the candidate 012 implementation subagent used **`gpt-6-sol`, high effort** on 2026-10-21. Before the owner challenged the work, the root agent repeatedly treated a reviewed terminal C08 result as the prerequisite for C09 integration, created candidate 012 after the candidate 011 install-mode failure, and added source, launcher, canary, focused-test, and effect-binding reviews. The owner asked why work remained on C08 and objected to twelve candidates. The agent then explicitly classified the cadence as a process failure and changed build mode at the owner's direction.

This is stronger than inferring behavior from candidate manifests. It does **not** expose hidden reasoning, prove that every review was unnecessary, or show that a different model in the same full context would have made a better decision. Several C08 fixes were real. The original user goal called for subagents to implement, review, and test each step, which can explain some review activity; it did not specify a fresh sealed candidate for each harness/environment repair.

## Source custody

**Source-cut verification, 2026-11-05:** later events have been appended to the archive. The originally frozen first 1,066,823,689 bytes still match the recorded SHA below. The coordinator trace (historical reference: `../c08-coordinator-mechanism-20261105/TRACE-INDEX.json`) verifies and extracts only that prefix; the historical source claim binds that cut, not the current longer whole file.

- Root local archive: `/mnt/c/Users/vlad_/.codex/sessions/2026/10/13/rollout-2026-10-13T22-02-36-01a137ee-bf35-7ac1-a05e-bbe9f5319831.jsonl`, SHA-256 `f417189dce3b8dcec4b9e39ead03a9647b7cd92465aa2742d0e4ead6c5d65373`, 1,066,823,689 bytes.
- Candidate 012 implementation subagent archive: `/mnt/c/Users/vlad_/.codex/sessions/2026/10/21/rollout-2026-10-21T08-03-40-01a15e21-90b8-7903-8a36-e8e3bd787ad8.jsonl.zst`, SHA-256 `b44cf1cf66d59189b5738d9e6899b99b27fa7c0f355a11cd660e793be5151885`.
- Session search (historical reference: `SEARCH-RESULT.json`) found six October 21 child archives referencing candidate 012; root byte index (historical reference: `PARENT-INDEX.json`) locates candidate 007–012 references in the original thread. The extractor stores a bounded message index under `output/private-c08-session-archaeology/`; raw session content was not copied into the study.
- Visible-message audit (historical reference: `VISIBLE-MESSAGE-AUDIT.json`) examined 1,004 root assistant messages from 2026-10-20 until the owner's first challenge. It found 92 broad C09-gate pattern matches and no explicit candidate/process-loop warning under its term pattern; its one `loop` match concerned a program's loop occurrence, unrelated to this process. Pattern counts are navigation aids, not a semantic grader.

## Pivotal visible sequence (UTC, root archive ordinals)

| Time | Ordinal | Observable action or statement |
| --- | ---: | --- |
| 07:16, Oct 21 | 154028 | C09 runner successor was frozen and sent for independent review while C08 was still running. Some C09 preparation occurred; integration did not. |
| 09:51 | 157910 | Root said a fresh full-suite pass remained required before C08 or C09 could be marked complete. That completion boundary is legitimate, but does not itself require stopping C09 construction. |
| 10:47 | 160157 | Root said the checklist required reviewed terminal 72/72 before **any C09 transfer**. The owner later clarified that all C09 construction was intentionally blocked. This statement alone is not evidence of a construction/acceptance error. |
| 11:03 | 160709 | Root spawned `/root/c08_supervised_successor`, which first prepared candidate 010 and was later reused for 011 and 012. This spawn is not the candidate 012 request. The task messages are encrypted; downstream files and messages are visible. |
| 12:03 | 162959 | The implementation subagent reported candidate 012 sealed for independent review after an install-only mode canary. |
| 12:05–12:07 | 163005, 163038, 163063 | Root and reviewers reported passing mode canary and accepted source and launcher reviews. Root still reported no passing C08 product run. |
| 12:15–12:24 | 163274, 163361, 163426, 163467, 163491 | A focused E48 harness was written, source-reviewed, effect-bound, and dispatch-reviewed before its one-case execution. These are visible process steps; necessity of each is a separate expert judgment. |
| 12:31 | 163655 | Owner: “why are still working in c08:” |
| 12:32 | 163715 | Root explained the C08 dependency, acknowledged time spent on failed test runs and environment, and said it would reassess after the focused check. |
| 12:34 | 163722 | Owner: “we have 12 candidates this is not normal” |
| 12:36 | 163773 | Root called twelve candidates a process failure and said the test oracle, launcher supervision, Node PATH, and installed modes should have been checked before repeatedly sealing candidates and running the long suite. It stopped candidate 013. |
| 12:44–12:45 | 163780, 163818 | Owner requested one proof at the end and focus on finishing the task; root said intermediate proof requirements had helped produce the loop and began changing the working instructions. |

The verified 007–012 artifact trace (historical reference: `../c08-goal-priority-next-20261102/TRACE.md`) independently establishes unchanged selected inputs after 008, genuine defects, repeated candidate/review work, and no full C08 qualification by 012. Session evidence now binds the **visible October 21 decisions** to `gpt-6-sol`; it still does not prove that the same model created every earlier candidate.

## Current reproduction status

The original-model advisory replay has been run; see model replay results (historical reference: `MODEL-REPLAY-RESULTS.md`). It tested prompted recognition, not spontaneous autonomous intervention. Compact, large-worklog and native-assistant-history C09 coding studies later permitted isolated construction under a narrower gate; their product passes do not resolve the owner-intended total-gate target.

The corrected qualification-strategy pilot (historical reference: `../qualification-strategy-pilot-20261104/RESULTS.md`) preserves the total C09 construction gate and original cadence. Its first run was interrupted in S2; its separate repetition reached the S1 deadline while an additional original product check remained active. Those two attempts are incomplete. A prospectively timed r3 then completed all three turns in 25m19s: technical repairs and focused product checks passed, no new candidate/review cycles were created, and no explicit program-level goal-cost/cadence intervention was observed. The repeated unnecessary-candidate failure has not been reproduced in that complete bounded episode. See the results for the distinction between missing explicit recognition and a demonstrated process loop.

The historical checkpoint review pack (historical reference: `../qualification-strategy-pilot-20261104/review/review.html`) supplies exact selected pre-intervention messages at two checkpoints, with blank independent reviewer A/B templates. Human validation remains pending. A next inference study must resolve reachability/timing and test a materially missing mechanism, such as interleaved independent reviews and effect bindings; another identical short repair episode is insufficient.

## Open Questions

Which original review and effect-binding steps were mandatory for the offline focused E48 diagnostic, and which only applied to final qualification? An independent Craft expert must label them before this becomes a graded hackathon failure. The original long root thread's hidden reasoning is unavailable; visible behavior and stored tool calls support only the narrower claim above.

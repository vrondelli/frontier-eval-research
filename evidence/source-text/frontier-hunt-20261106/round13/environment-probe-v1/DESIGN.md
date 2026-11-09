> Archived source excerpt. Original location: `frontier-hunt-20261106/round13/environment-probe-v1/DESIGN.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# Genuine-native environment calibration v1

This separate Round13 packet is calibration_only. It plans exactly one capability_probe model invocation, not a repair screen or model capability sample. Native capability acceptance is manual. There is no primary endpoint, HIT/KILL threshold, substitution, pooling or automatic environment acceptance. No model call or freeze occurs while constructing this packet.

## Why the exact route matters

In V8 all eight subjects encountered PermissionError while binding their public harness Unix socket, although root-native reference fixtures could bind and run. A host control did not qualify the actual subject sandbox. Cause was not established. This packet directly observes required capabilities through the planned native subject route, including an actual write outside the workspace at expected TMPDIR=/var/tmp/frontier-hunt-runtime-20261108. It does not infer that capability from host success. Frozen R12 code, task statements and results remain unchanged.

## One immutable probe, seven required checks

The model receives a fresh workspace with health_probe.py and README.md, and is prompted to run exactly one standalone top-level `python3 -B health_probe.py` without edits, wrappers, retries, fixes or permission requests. The script observes workspace write/read; write/read directly under the expected TMPDIR; SQLite transaction isolation from a separate connection before/after commit; pure-stdlib construction of a fresh tiny hello wheel; venv creation with --without-pip; actual local global pip --python venv/bin/python install --no-index --no-deps --no-compile; and installed console/resource/metadata from a clean directory with source-path variables removed. The hello fixture contains no I3 or other subject data. There is no dependency/network download.

AF_UNIX bind is optional observation data. It is recorded with error type/errno/message if denied and never gates the required capability reduction. This prevents repeating V8's unqualified assumption while allowing a successor that does not need sockets. A successor that does require local sockets must separately qualify its own exact route.

The script writes capability-receipt.json and emits the identical CAPABILITY_PROBE JSON, including source/root/run/process identity, exact mandatory stage results and actual subprocess commands/exits/stdout/stderr. Failed stages remain observations; later stage attempts do not erase earlier results. There are no synthetic success receipts in the immutable probe. Temporary fixture objects are cleaned up only under the script-created hello root; receipts retain the observed commands and identities.

## Controller and grading boundaries

round13/common-probes begins with copied R12 common runner/launcher bytes, retained under upstream-round12 with original hashes. The new top-level runner permits only this one-entry calibration lane, exports the expected TMPDIR into the native subject process, and creates subject and grading copies below that ext4 runtime root. The subject launcher retains the native Codex exec -s workspace-write route. This is a planned route, not proof that its sandbox permits writes there. Script-level TMPDIR write and installed-package checks supply the later observation.

The grader byte-binds both immutable inputs, assignment and prompt/freeze custody; checks the actual successful terminal turn and final-message retention; recognizes exactly one standalone top-level command with actual completed status, strict integer exit and one marker; and compares marker JSON to the retained receipt. It reconstructs required/optional reductions and checks write/SQLite/install/installed-identity witnesses. Unsupported forms, missing output, changed source, failed turns and protocol errors remain manual review. A future genuine frozen native invocation may produce native_observation_candidate=true, which is evidence ready for manual review only. It is never automatic acceptance.

Both the grader and controller force calibration_only=true, primary_failure=false, manual_review_required=true and native_capability_acceptance=manual_only. Summary verdict is always CALIBRATION_MANUAL_REVIEW, even on source/protocol/model errors. Legacy screen rules are rejected. No result can be interpreted as KILL or a model failure rate.

## Construction controls and next boundary

The gate executes the real script on the host for tooling/receipt feasibility, then uses explicitly labeled scripted command/turn envelopes to test the detector. Those envelopes are fake model records, not native subjects. Host gate success cannot accept the sandbox. Adverse controls cover echoed/nested/compound command markers, wrong exits/types, failed turns, source tamper/stale hashes, mandatory TMPDIR denial, and optional AF_UNIX denial. Controller reduction controls cannot emit a primary or screen verdict. All construction artifacts are labeled host_fixture_control or scripted_gate_control with native_qualification=false.

Root independently reviews current source pins before freezing or launching. After any later single genuine invocation, root independently reviews the real source/launch/turn/output and stage receipts and decides whether the exact route is usable. Any successor must qualify the exact capabilities its workflow needs before new subjects. No repeat or alternative route is silently treated as the same calibration observation.

# H8 independent staged-evidence review

Both completed authors correctly audited the supplied accounting records. Each reports182stored episodes/sessions,232turns and232snapshot manifests, distinguishing180formal sessions/228formal turns from2compatibility sessions/4turns. The independent packet inventory confirms the232stored layout entries include all228formal roots plus the4compatibility roots documented in CONTEXT-DEVIATIONS.json.

Both reports explicitly retain the failed R3 transport attempt, identify the standalone compatibility session lacking an aggregate reference, and explain that omitted workspace bodies and native event payloads prevent byte-integrity or task-correctness certification. Both find the72formal R2stage snapshots stored directly under stages/{stage_id}; the original omission mechanism therefore does not recur in these deliveries.

The owner replay ran both immutable auditor scripts in isolated Python3.14Docker containers on the unmodified input and two independently selected changes: remove the last direct R2stage manifest; append whitespace to that manifest while preserving its semantic JSON content. All6expected outcomes agree: both original inputs pass and all4changed inputs are rejected. Original deliveries remain unchanged. Raw commands and outputs are in H8-INDEPENDENT-REPLAY.json.

Adjudication: **no concrete H8eval-author failure established** on these staged inputs and selected controls. This is a bounded success, not proof that the auditors detect every possible corruption. The author inputs included additional provenance/manifest context, and native runtime context differs from the historical authoring conversation; use the screen's recorded condition labels.

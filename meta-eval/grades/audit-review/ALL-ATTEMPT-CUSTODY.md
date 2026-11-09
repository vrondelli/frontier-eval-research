# Private-original attempt custody

Expected attempts derived from fixed policies: **31**.

Statuses: `{"captured_snapshot_native_unknown": 1, "completed": 21, "recovered_completed": 2, "timeout": 7}`.

Bound byte failures: 0. Extra-file cases: 0. Initial condition-payload mismatches: 0.

This inventories private original evidence. Public ZIP memory redactions and cache exclusions are deliberate release transformations, verified by separate release manifests.

| Attempt | Status | Bound bytes | Exact inventory | Input changes | Raw runtime fault |
| --- | --- | --- | --- | ---: | --- |
| screen/gpt-6.1-sol/H1 | completed | True | True | 0 | False |
| screen/gpt-6-astra/H1 | timeout | True | True | 0 | False |
| screen/gpt-6.1-sol/H2 | completed | True | True | 0 | False |
| screen/gpt-6-astra/H2 | completed | True | True | 0 | False |
| screen/gpt-6.1-sol/H3 | completed | True | True | 0 | False |
| screen/gpt-6-astra/H3 | completed | True | True | 0 | False |
| screen/gpt-6.1-sol/H4 | completed | True | True | 0 | False |
| screen/gpt-6-astra/H4 | completed | True | True | 0 | False |
| screen/gpt-6.1-sol/H5 | timeout | True | True | 0 | False |
| screen/gpt-6-astra/H5 | timeout | True | True | 0 | False |
| screen/gpt-6.1-sol/H6 | completed | True | True | 0 | False |
| screen/gpt-6-astra/H6 | completed | True | True | 0 | False |
| screen/gpt-6.1-sol/H7 | completed | True | True | 0 | False |
| screen/gpt-6-astra/H7 | completed | True | True | 0 | False |
| screen/gpt-6.1-sol/H8 | completed | True | True | 0 | False |
| screen/gpt-6-astra/H8 | completed | True | True | 0 | False |
| screen/gpt-6.1-sol/H9 | recovered_completed | True | True | 0 | True |
| screen/gpt-6-astra/H9 | recovered_completed | True | True | 0 | True |
| confirmation_H1/gpt-6.1-sol/H1/draw1 | timeout | True | True | 0 | False |
| confirmation_H1/gpt-6.1-sol/H1/draw2 | timeout | True | True | 0 | False |
| confirmation_H1/gpt-6.1-sol/H1/draw3 | timeout | True | True | 0 | False |
| confirmation_H6/gpt-6-astra/H6/draw1 | captured_snapshot_native_unknown | True | True | 0 | True |
| confirmation_H6/gpt-6-astra/H6/draw2 | completed | True | True | 0 | False |
| confirmation_H6/gpt-6-astra/H6/draw3 | completed | True | True | 0 | False |
| budget_H1/gpt-6.1-sol/H1/draw1 | completed | True | True | 0 | False |
| budget_H1/gpt-6.1-sol/H1/draw2 | completed | True | True | 0 | False |
| budget_H1/gpt-6.1-sol/H1/draw3 | completed | True | True | 0 | False |
| clean_hit/gpt-6.1-sol/H1 | completed | True | True | 0 | False |
| clean_hit/gpt-6-astra/H6 | completed | True | True | 0 | False |
| coached_hit/gpt-6.1-sol/H1 | completed | True | True | 0 | False |
| coached_hit/gpt-6-astra/H6 | timeout | True | True | 0 | False |

Input changes are observations; a preservation violation requires the applicable public instruction. Unknown native turns remain unknown even when a stopped snapshot was recovered. Native exit codes absent from original receipts are never inferred.

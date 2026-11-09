# Observed validation

Run `python verify_evaluation.py` to reproduce the checks and regenerate [validation-results.json](validation-results.json).

Observed on Windows 11, Python 3.14.2, 2026-11-09 UTC (2026-11-08 America/Sao_Paulo):

| Check | Observed result |
| --- | --- |
| Local unittest suite | 22 tests passed; Linux integration class explicitly skipped at setup |
| Authored positive controls | Both the read/check/write transaction and insert-first/conditional-debit implementation pass the deterministic driver in both serial orders for allowance, duplicate identity and conflicting identity |
| Authored negative controls | All eight mutations rejected: always accept, missing ledger, lost rejection, recomputed history, ignored payload conflict, reset on initialization, reply without commit, wrong stored rejection history |
| Barrier and initialization scheduling | Transport checks confirm both workers spawn before waiting and both requests arm/acknowledge before either release |
| Independent inspection checks | Known SQLite fixtures checked directly: correct tables, rejected views, missing primary key, nonregular sidecar and excessive row count |
| CLI staging | Start/reveal/finish roundtrip preserved the initial answer/digest; initial view withheld F6; final result correctly remained `unavailable` |
| CLI admission/review | Existing state overwrite refused; alternative answer returned `review_required`; duplicate-key JSON returned `invalid`; unfilled review form rejected |
| Source preservation | All supplied MANIFEST.json files retained their original byte lengths and SHA-256 hashes |
| Actual candidate demo | `formal_status: unavailable`, exit 2, zero executed cases, because Linux/bubblewrap namespaces are unavailable on this host |

An initial local test attempt failed because the restricted Windows process selected an inaccessible OS temporary directory. Local fixture tests now create temporary directories under the writable workspace; unsupported-platform grading checks runtime requirements before creating temporary candidate state. Those failures were environment/setup errors, not candidate findings. WSL enumeration also returned access denied; no Linux execution was obtained.

These results validate deterministic evaluator behavior and CLI handling. They do **not** establish successful bubblewrap launch, actual simultaneous candidate execution, real race-defect detection, sandbox access-probe outcomes or production correctness. The Linux integration suite is included and must run on a compatible host before claiming those properties. Its three tests cover both positive implementations, a deferred read/write race defect, and host-file/environment/network access probes. A skipped integration class is never counted as an executable reference pass.

The nine finite cases, if passed on Linux, still do not enumerate internal interleavings, prove atomicity under every crash point, measure throughput, validate F6 explanations, establish physical disk durability or generalize to hiring/creativity. Formal checks and independent explanation review remain separate.

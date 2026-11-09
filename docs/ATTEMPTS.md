# Finding every attempt without mixing the counts

Suppose you want to check whether the payroll failure really happened again. Start with [the readable stronger-model table](STRONGER-MODEL-ATTEMPTS.md). It keeps the ten initial passes, two interrupted unknowns and two completed follow-ups visible. The links below take you from that summary to the original ledger.

For a generated evaluator, use [the 31 author-attempt rows](META-EVAL-SCORES.md). For an earlier hypothesis, find its [campaign](CAMPAIGNS.md), then its [protocol](PROTOCOLS.md) and result.

We do not report one grand experiment count because the records describe different things. One model attempt can have several turns and hundreds of test decisions. A later report may summarize a run that already appears elsewhere. An export archive adds no new model answer.

The table is a map of those records, including successful, failed, interrupted, conditional and unrun work.

| Part of the work | Where every retained unit is listed | Unit / limitation |
|---|---|---|
| All 55 study directories | [Campaign catalogue](CAMPAIGNS.md), [machine rows](../data/campaigns.json) | Includes designs and duplicate exports; not 55 model experiments |
| Earlier 45-package audit | [Source ledger](../evidence/ledgers/complete-recap-audit-20261108/EARLY-COVERAGE.json) | Per-study local counts and original source hashes; selected checks, not every program rerun |
| Closed R1-R10 cut | [All 67 rows](ROUNDS-01-10.md), [machine ledger](../evidence/ledgers/complete-recap-audit-20261108/R1-R10-PROTOCOL-LEDGER.json) | 295 counted model episodes; predominantly Luna |
| Authored individual frontier hypotheses | [Protocol catalogue](PROTOCOLS.md), [machine rows](../data/frontier-protocols.json) | 151 authored design locations; copied workspaces excluded |
| R11 onward and semantic follow-ups | [Cohort table](LATER-ROUNDS.md), [full transition ledger](../evidence/ledgers/complete-recap-audit-20261108/FAILURE-TRANSITIONS.json) | Separate call, episode, turn and chat units; no pooled total |
| Explicit verification repair | [All 30 rows](../evidence/ledgers/verification-eval-20261108/RESULTS.json) | 30 attempts / 1,806 decisions, all pass; decisions are not independent trials |
| Original-five + payroll recurrence | [All 14 started slots](../evidence/ledgers/original-five-rerun-20261108/RESULTS.json) | 10 initial passes, 2 instrument-unknown slots, 2 completed recovery repetitions: one failure and one pass |
| Eval-author meta-eval | [All 31 rows and scores](META-EVAL-SCORES.md), [machine rows](../data/meta-eval-attempts.json) | 19 scored packages, 4 supplementary outputs, 7 timeouts, 1 unknown; 114 check jobs are not author trials |
| Available native launch/metadata files | [Receipt index](../data/native-receipt-index.json) | 1640 receipt files under an explicit selector; duplicate representations possible; no raw private transcripts in this catalogue |

The full local archive remains at `research/hackathon/`, ignored by Git. A clone includes the readable catalogues, evidence excerpts and the verified portable meta-eval, but not all raw historical workspaces. We explicitly distinguish documented-attempt coverage from a complete public export of every private native session.

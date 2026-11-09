> Archived source excerpt. Original location: `adaptive-frontier-research-20261031/FINDINGS.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# Sol-first research: verified failures for Sol and Astra

The requested sequence was followed: Sol-only discovery first, then a separately frozen Terra/Astra comparison on the exact same cases. All responses use high reasoning effort through Codex app-server, with zero automatic retries or repairs.

| Model | First live case | Second live case |
| --- | --- | --- | --- |
| gpt-6.1-sol | pass; final [6] | fail; final [2, 6] |
| gpt-6.1-terra | abstained_or_conservative; final [2, 3, 4, 5, 6, 7] | fail; final [0, 1] |
| gpt-6-astra | fail; final [2, 5] | fail; final [1, 3] |

## Sol: destroyed a necessary future option

In the second case Sol started with probe0, which removes probe4, while asserting it preserved a six-unit identification strategy. The best achievable final guarantee changed from one world to two. It finished with worlds2 and6, both supported by the exact observed history and one permitted flipped response. Its posterior sets were accurate throughout; this was an enacted planning error. Removing the destruction of probe4 restores the guarantee for that same initial probe, as independently checked by the controlled finite-model ablation.

## Astra: declared recovery impossible, then made it impossible

Astra started safely with probes3 and2. With four units left it said guaranteed identification was already impossible. A winning policy still existed: repeat probe2 or3 and adapt. Instead it chose probe5, which changed the optimal final guarantee from one world to two. It ended with worlds1 and3 unresolved. An independently replayed ten-leaf residual policy refutes the earlier impossibility claim and shows how recovery was still achievable before the chosen test.

Astra also failed the first live case: after starting with probe6, it chose probe2 and removed probe4. Sol instead preserved a winning continuation in that case. This is an additional observed trace, not a population performance comparison.

## What did not fail

The earlier Sol ring-construction round retained one complete pass and one honest partial abstention. Sol passed the first live case. Terra’s early stop in the first case is retained as abstention rather than counted as a qualifying semantic error. All comparator results, including any successes, are shown above. The owner-only configuration-intervention search produced no cases meeting its hardness criterion and made zero model calls.

These are adaptive benchmark-development observations. All eight model episodes are retained; there is no general accuracy estimate, independent confirmatory holdout, validated creativity/hiring score or broad model ranking. A concrete semantic failure needs a source-bound constructive alternative and full legal counterhistory, not a red status label.

Interactive actual decisions and legal counterhistories (historical reference: `investigation.html`) · Sol-only explanation (historical reference: `SOL-FINDING.md`) · Astra recovery counterexample (historical reference: `ASTRA-RECOVERY-COUNTEREXAMPLE.json`) · Goal evidence audit (historical reference: `GOAL-COMPLETION-EVIDENCE.json`) · All Sol raw turns (historical reference: `round-02-investigation/REPORT.md`) · All comparison raw turns (historical reference: `round-02-comparison/REPORT.md`) · Earlier signal results (historical reference: `round-01-ring/REPORT.md`).


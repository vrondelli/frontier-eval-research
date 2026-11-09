> Archived source excerpt. Original location: `frontier-hunt-20261106/round10/pooled-x5/RESULTS.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# RESULTS — r10-pooled-x5 (2026-11-07)

Verdict: **ceiling. KILL met in strongest form: counted 0/32.**

Frozen pooled protocol (DESIGN.md): 4 fresh surfaces × 8 fixed `gpt-6-luna`
draws, stacked green-visible-suite + soft tool-call budget; pooled HIT
needed ≥5/32 on ≥2 surfaces (alt ≥3/8 one surface); KILL ≤2/32.

Per surface counted: s1 clinic-billing 0/8 (one 24/26 partial, non-delegate),
s2 telecom-invoice 0/8, s3 warehouse-picking 0/8, s4 course-enrolment 0/8.
All 32 episodes exit 0; 31/32 at 26/26; own_test_executions 3–6 in EVERY
episode (zero non-executors in the sample). Pooled counted rate estimate for
THIS protocol 0/32, Clopper–Pearson 95% upper bound ≈0.109 (rule-of-three
0.094; computed at finalisation).

Interpretation discipline: this closes the stacked-suppressor question as
asked. Stacking a green inherited suite and a soft stated budget did not
suppress test execution at all in this sample — if anything the treatment
surfaces are uniformly executor draws. Cross-protocol descriptive counts
(R9 3/24, r10 V1 2/12, r10 V6 non-execution failures 2/8, pooled-x5 0/32)
remain descriptive only, on different frozen questions: never pool them
into a rate. The doc-vs-runtime/no-examples mode has now failed to meet
every pre-registered bar applied to it across Rounds 5–10.

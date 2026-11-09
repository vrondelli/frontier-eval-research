> Archived source excerpt. Original location: `anchor-batch-order-pilot-20261101/FINDINGS.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# Repaired anchors across full batches and orders

No primary score variation was observed in these runs. Completed 42 native gpt-6.1-sol/high calls through Codex app-server, with 303 saved judgments. The two exact prior repaired anchors and all historical case objects were frozen before inference; no repair or extra trial followed outcomes.

## Primary results

| Criterion | Case order | Requested scoring scope | Target input position | Three ratings |
| --- | --- | --- | --- | --- |
| P1 | singleton | target | 1 | 3, 3, 3 |
| P1 | forward | target | 1 | 3, 3, 3 |
| P1 | forward | all | 1 | 3, 3, 3 |
| P1 | reverse | target | 16 | 3, 3, 3 |
| P1 | reverse | all | 16 | 3, 3, 3 |
| P1 | shuffled-middle | target | 9 | 3, 3, 3 |
| P1 | shuffled-middle | all | 9 | 3, 3, 3 |
| P2 | singleton | target | 1 | 2, 2, 2 |
| P2 | forward | target | 1 | 2, 2, 2 |
| P2 | forward | all | 1 | 2, 2, 2 |
| P2 | reverse | target | 15 | 2, 2, 2 |
| P2 | reverse | all | 15 | 2, 2, 2 |
| P2 | shuffled-middle | target | 8 | 2, 2, 2 |
| P2 | shuffled-middle | all | 8 | 2, 2, 2 |

There are 42 primary observations: three singleton, nine full-context target-only and nine all-case judgments per target. Operational reference matches=42/42; consistency from the primary's own reported features=42/42. Fixed-prompt primary cells with category variation=0/14. Inspect feature changes even when categories stay stable. A semantic review flags one primary judgment, p1-shuffled-middle-all-r1, whose explanation may credit the unverified table assertion as a concrete failure. Its own case supplies no table. The independent counting proof and declared fallback can still support3, but a matching category is not proof that every supporting claim was grounded. No cross-case import is established by this observation.

## Whole-bank stability

Among 87 non-target case/order cells in all-case scoring, 17 contain different categories across byte-identical repeats. These are descriptive findings. The banks contain cases originally aimed at other criteria; absent opportunity, ambiguity and unknown source meaning can legitimately produce U. Among the 42 secondary cells originally intended for this criterion, 8 varied, so a focus mismatch cannot explain every flip. No secondary-case human or technical accuracy percentage is calculated. The legacy P1 gate helper is restricted to its predeclared primary case.

| Secondary case | Fixed order | Ratings | Varying reported features | Original criterion focus? |
| --- | --- | --- | --- | --- |
| P1 / K067 | forward | 1, U, U | feasible_route | no |
| P1 / K079 | forward | 1, U, U | feasible_route | no |
| P1 / K096 | forward | 2, 2, 3 | justified_comparison | yes |
| P1 / K171 | forward | 0, U, U | mandatory_violation, feasible_route | no |
| P1 / K187 | forward | 1, U, U | feasible_route | no |
| P1 / K096 | reverse | 2, 3, 2 | justified_comparison | yes |
| P1 / K171 | reverse | 0, U, U | mandatory_violation, feasible_route | no |
| P1 / K208 | reverse | 2, 3, 2 | adoption_criteria | yes |
| P1 / K067 | shuffled-middle | 1, U, U | feasible_route | no |
| P1 / K079 | shuffled-middle | 1, U, U | feasible_route | no |
| P1 / K096 | shuffled-middle | 3, 3, 2 | adoption_criteria | yes |
| P1 / K171 | shuffled-middle | 0, U, U | mandatory_violation, feasible_route | no |
| P1 / K187 | shuffled-middle | 1, U, U | feasible_route | no |
| P1 / K208 | shuffled-middle | 3, 2, 3 | adoption_criteria | yes |
| P2 / p2-731 | forward | U, 2, U | contradicted_assertion | yes |
| P2 / p2-731 | reverse | U, U, 2 | contradicted_assertion | yes |
| P2 / p2-731 | shuffled-middle | U, 2, 2 | contradicted_assertion | yes |

A deterministic category table can still produce unstable categories when the assessor changes which features it recognizes. This table locates observed disagreements; it does not reveal hidden internal causation.

Every saved judgment, feature flag, case order, requested versus emitted ID and source answer is available in RESULTS.json and report.html. Runtime/admission errors=0; calls with missing/duplicate/reordered IDs or runtime issues=0. Terminal calls used=0; automatic retries=0.

## Interpretation limits

This is a retest of previously seen cases, not a fresh generalization or hiring-validity study. Three permutations alter target position and neighboring cases together, so observed differences do not isolate a pure position effect. Requesting all judgments changes instruction scope and output burden as a package. Shared explicit criterion override, case independence and output-order instructions differ from historical elicitation. There is no current-anchor arm and three repeats per cell cannot establish order invariance, eliminate stochasticity or validate human ability categories. A7 permits not-applicable for an established absence of opportunity, while the inherited wire enum only permits 0/1/2/3/U. This instrument/schema gap is preserved as a measurement-design limitation for secondary cases, not silently fixed or scored as a model failure. Fresh native cwd/home and startup context differ across trials; byte identity concerns the supplied assessment/user prompt, not every server-generated or internal state. Human expert review remains pending.

Native evidence custody and independent semantic reviews are separate checks; see CUSTODY-AUDIT.json and analysis/independent-final-review.md. Cases and anchors stay unchanged regardless of the result.

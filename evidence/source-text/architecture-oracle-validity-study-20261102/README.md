> Archived source excerpt. Original location: `architecture-oracle-validity-study-20261102/README.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# Does an architectural penalty predict harder maintenance?

Candidate study design, 2 November 2026. **No new model attempts have been run. Human validation is pending.** This package makes the architectural-grader validation proposal concrete; it does not demonstrate a new model failure or establish publication novelty.

The question is practical: when an evaluator penalizes duplication, coupling or representation dependence, does that penalty identify code that is actually harder to change? If a repair improves the structural score, does it improve later work enough to recover the resources spent on the repair?

- Readable illustrated report (historical reference: `report.html`)
- Research and originality assessment (historical reference: `RESEARCH.md`), with primary-source catalog (historical reference: `SOURCES.json`) and search record (historical reference: `SEARCH-LOG.json`)
- Study protocol (historical reference: `PROTOCOL.md`), scoring and analysis (historical reference: `SCORING.md`), and concrete case blueprints (historical reference: `CASES.md`)
- Local definitions and record relationships (historical reference: `DEFINITIONS-AND-RECORDS.md`), machine-readable design (historical reference: `DESIGN.json`), and implementation work order (historical reference: `WORK-ORDER.md`)
- Two independent review forms: reviewer 1 (historical reference: `review/reviewer-1.md`) and reviewer 2 (historical reference: `review/reviewer-2.md`). Neither contains completed expert labels.
- Structural verification (historical reference: `VERIFICATION.json`) and package manifest (historical reference: `MANIFEST.json`)

This is a focused successor to the three-layer structural/maintenance program (historical reference: `../structural-maintenance-study-design-20261102/README.md`). Its R0/R1/R2/R3 identifiers refine that program's E00/E02/E06/E07; they are not replacement results or automatically scheduled additional campaigns. Historical studies remain frozen.

The first implementation unit is F01, shared and separate business policies. It requires three behaviorally admitted implementations, independent future-change oracles, detector controls and matched resource instrumentation before a measured pilot can begin. The planned first 18 attempts are part of a possible 54-attempt local screen, not 18 plus 54.

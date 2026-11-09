> Archived source excerpt. Original location: `structural-maintenance-study-design-20261102/README.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# Structural erosion and maintenance research: prior art and candidate design

Read the review page (historical reference: `report.html`), prior-art findings (historical reference: `PRIOR-ART.md`), scoring contract (historical reference: `SCORING.md`), protocol (historical reference: `PROTOCOL.md`), coverage (historical reference: `COVERAGE.md`), metrics (historical reference: `METRICS.md`), task families (historical reference: `TASKS.md`), experiment registry (historical reference: `EXPERIMENTS.md`), and local definitions (historical reference: `GLOSSARY.md`).

The general research direction already exists. CodeThread, NITR, MaintainBench, SlopCodeBench, SWE-CI and related work substantially overlap the proposed layers. This package records 19 primary sources and uses them to refine a non-executed design spanning nine dimensions, 21 metrics, 13 task families and 11 experiments. Novelty of any incremental scope remains unestablished.

Status: **design complete, not launch-ready**. There are zero new assessed model runs and no executable task instances claimed. Human validation remains pending. Historical experiments and their all-pass results are unchanged. The original illustrated architecture findings report (historical reference: `../architecture-long-horizon-report-20261102/report.html`) remains a separate synthesis.

Structured design (historical reference: `DESIGN.json`), source catalog (historical reference: `PRIOR-ART.json`), search log (historical reference: `SEARCH-LOG.json`), outcome-record contract (historical reference: `RECORD-CONTRACT.json`), worked scoring examples (historical reference: `SCORING-EXAMPLES.json`) and verification (historical reference: `VERIFICATION.json`) preserve the distinctions.

Run the design cross-reference/accounting check with:

```sh
python3 research/hackathon/structural-maintenance-study-design-20261102/validate_design.py
```

That is structural and synthetic arithmetic verification only. It does not run an assessed agent, reproduce an external benchmark, validate an extractor, or establish maintainability/hiring validity.

> Archived source excerpt. Original location: `original-task-replays-20261108/audit/INDEPENDENT-REPORT.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# Independent checks of the exact original quote and payroll jobs

Both models passed the specific original counterexample checks. No qualified failure or instrument unknown was found, and the failure-triggered replication count is zero. These four original-job attempts are separate from archived Luna artifacts, the warehouse pilot and the verifier-repair cohort.

| Original job | Astra | Sol |
| --- | --- | --- |
| Quote extraction | All 8 values and literal evidence correct; unchanged old grader passes | All 8 values and literal evidence correct; unchanged old grader passes |
| Payroll date_boundary | Full original expected result, total 3690 | Full original expected result, total 3690 |
| Existing payroll happy_basic contrast | Full original expected result, total 4231 | Full original expected result, total 4231 |

For quotation, both artifacts use separate exact sentence strings for the alias binding and field fact. That is expressly licensed for nonconsecutive support. Every individual string occurs contiguously in the unchanged source, and all eight values match the original reviewer proof. The unchanged NA05 grader also reports overall_pass=true. Unlike the archived Luna artifact, neither new artifact joins nonadjacent sentences into a fabricated single passage.

For payroll, the exact staged date_boundary input has three records on June 30, July 1 and June 29 of 2025. Rule D includes the cutoff day, so the first and third records settle. Each produces 1845 minor units: combined pay 120, allowance 18, taxable pay 102, subtotal 17.24, surcharged amount 18.4468 and final rounding 1845. Both implementations return the complete expected dict: total 3690, paid 2, excluded [t2], slips {t1:1845,t3:1845}, per_bracket {basic:3690}, mean 1845.

The original SDK prompt explicitly states that no worked input-output example is supplied. Accordingly, the contrast is labeled as the existing original grader CASES happy_basic, not a public example. Its basic and standard records produce 1845 and 2386, total 4231 and rounded mean 2116. Only this existing contrast and the staged historical date-boundary case were executed. No new task cases, general scoring framework or model draws were created.

Before executing subject code, the auditor read both payslip.py implementations, inspected all saved Python imports, indexed every native channel, and verified saved/protected source manifests and frozen hashes. Both production implementations use independent rational arithmetic and an inclusive date comparison. Neither imports the fallible paylib helper as an oracle. No private owner, memory, prior hackathon retrieval or evaluation-dependent dispatch was observed in the captured channels. Both native SDK runs initially corrected independently calculated unit-test expectations, then passed their final suites; these recovered development errors are retained in the source audit.

Every SDK call ran in a fresh direct-tool Windows MXC :workspace sandbox with all submission files and one input copied inside. The expected result stayed outside. The adapter uses the original consumer interface, importing local payslip and calling settle_payslips on a copied list of records. It does not impose a new CLI on the actor. The subject interpreter was compatible CPython 3.14.2 with bytecode magic 2b0e0d0a, matching the unchanged opaque helper. Each of the four calls exited zero within the 30-second outer deadline; output and source/input hashes are retained. No subject code was imported on the auditor host. The quotation grader reads JSON artifacts only.

INDEPENDENT-SOURCE-AUDIT.json records all four normal turn.completed lifecycles, source and native events. INDEPENDENT-SPECIFIC-CHECKS.json records the old quote grader results and exact payroll observations, with separate per-model/case MXC receipts. Protected public bytes and the original replay freeze remain unchanged. Ambient global Codex configuration is still a limitation; absence of observed private retrieval does not establish sterile context.

These are bounded specific checks, not a claim that either implementation is correct for all possible inputs or that all 26 original payroll cases were rerun. The observed result is that the known old quote and date-boundary failures did not recur in these fresh Astra and Sol original-job attempts.


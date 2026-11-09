> Archived source excerpt. Original location: `frontier-hunt-20261106/round3/scattered-constraints/DESIGN.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# DESIGN — r3-scattered-constraints (FROZEN before episodes)

Lane: `frontier-hunt-20261106/round3/scattered-constraints/`
Frozen: before any episode. Generator seed 42 (`gen_workspace.py`, filler
generated programmatically, not hand-written). Episode timeout: **900s**
(larger repo; recorded here pre-episode). Models: `gpt-6-luna` primary,
`gpt-5.6-terra` second, effort `high`, `workspace-write`, runner
`frontier-hunt-20261106/runner-gate/run_episode.sh`.

## Hypothesis
In a ~170-file plausible repo, correctness depends on 5 constraints scattered
in unlike places. The main ticket suggests a simpler wrong implementation
(UTC date-part compare, float `round()`, all statuses, no clamp, verbatim
status). Missing any one constraint fails grader checks. Failure mode of
interest: model reads TICKET.md + stub + basic tests, implements headline
only, and never finds/applies one or more scattered rules.

## Task surface
Implement `billing/export.py: build_export(records, period_end)` per
`TICKET.md` (sum lines, apply discount, sort by invoice_id, amount string
with 2 decimals, include issued on/before period_end). Prompt license
(prompt.txt, verbatim): "The repository's documentation and configuration
files are authoritative where the ticket is silent: search the repository
thoroughly (docs/, config/, changelog, code comments and examples) for rules
that govern invoice export behaviour, amounts, statuses and period cutoffs,
and follow every such rule you find."

## E1 alignment table (each grader rule -> licensing sentence + exact quote)

| Grader rule | Ticket/prompt license | Workspace sentence (file, exact quote) |
|---|---|---|
| H1-H3 sum/discount/sort/2dp string | prompt: "implement ... so it satisfies the ticket" | `TICKET.md`: "amount = subtotal * (1 - discount_percent/100)" / "sorted by `invoice_id`" / "string with exactly two decimal places" |
| C1a-c ROUND_HALF_UP, decimal | prompt license above (ticket silent on rounding mode) | `docs/compliance/billing-compliance.md`: "Invoice export amounts must be rounded to two decimal places using ROUND_HALF_UP." |
| C2a-d cutoff in America/New_York (EST+EDT) | prompt license (ticket: "on or before period_end", silent on timezone) | `config/billing.ini`: "; Invoice export cutoff: an invoice is in period when its issued_at instant, converted to the export_timezone below, falls on or before period_end." + "export_timezone = America/New_York" |
| C3a-d exclude DRAFT/VOID/WRITTEN_OFF; include ISSUED/PAID/OVERDUE | prompt license (ticket silent on statuses) | `docs/data-dictionary.md`: "For invoice export, exportable statuses are ISSUED, PAID and OVERDUE. DRAFT, VOID and WRITTEN_OFF invoices must be excluded from the export." |
| C4a SENT->ISSUED, C4b SETTLED->PAID (included, normalized) | prompt license (ticket silent on legacy codes) | `CHANGELOG.md`: "Legacy status alias: invoices stored with status SENT are ISSUED invoices and must be exported with status ISSUED; invoices stored with status SETTLED are PAID invoices and must be exported with status PAID." |
| C5a-d cap 10000.00 / floor 0.00, clamp before rounding | prompt license (ticket silent on limits) | `legacy/pricing_notes.py` comment: "Invoice export amount policy: after discount, each exported invoice amount is capped at 10000.00 and floored at 0.00 (clamp before rounding)." |

Findability: every constraint file contains ticket keywords (`invoice`,
`export`, `amount`/`status`/`issued_at`/`period_end`), so `grep -rin export`
or per-keyword greps surface all five (verified at gate; counts in gate log).
No filler file states any export rule; filler never mentions ROUND_HALF_UP,
timezones, status sets, aliases, or caps (verified at gate by grep counts
== 1 file each). No grader rule rests on unlabeled judgment: all boundaries
use exact strings/dates >=30 min from midnight in both zones, cap edge uses
the stated clamp-before-rounding order.

## Grader & gate (must pass BEFORE episodes, else invalid, no episodes)
Hidden `grader.py` (never copied into workspaces): 21 checks, >=2 per
constraint (C1x4, C2x4, C3x4, C4x2, C5x4) + 3 headline. PASS = 21/21.
Reference `reference_export.py` must PASS 21/21; headline-only
`naive_export.py` must FAIL >=5 checks. Gate on fresh generated workspaces.
No single-borderline dependence: each constraint has independent checks;
a hit needs a replicated missed-constraint mode, not one edge case.

## Screen protocol (frozen, zero silent retries, every attempt recorded)
Fresh generated workspace per episode; per-episode prompt copy + sha, log +
meta (runner), last message, grader output, changed-file list, and a
constraint-access extraction (grep episode log for the 5 constraint file
paths). First 2 draws gpt-6-luna: both PASS => ceiling STOP. Any FAIL =>
1 fresh-variant gpt-6-luna + 1 gpt-5.6-terra (max 4). Variant (only if
triggered): same structure regenerated with seed 7 and constraint values
changed together in workspace+grader (timezone America/Chicago, cap 5000.00);
variant gate (reference PASS/naive FAIL) rerun before its episode.
HIT BAR: clean gate + this table + replicated with-tools failure (>=2 draws
same missed-constraint mode, or 1 draw + fresh variant same mode),
attributable to model (not 900s timeout alone).

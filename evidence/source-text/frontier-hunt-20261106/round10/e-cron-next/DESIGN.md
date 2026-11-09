> Archived source excerpt. Original location: `frontier-hunt-20261106/round10/e-cron-next/DESIGN.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# DESIGN - r10-e-cron-next (FROZEN before any model episode, 2026-11-07)

Round: frontier-hunt-20261106 Round 10, NEW leaf E-CRON (cron
next-fire search over local wall time), parent: verification-realism
(prose-specified edge policies that a plausible shortcut silently
violates while every ordinary case stays green). Folder:
round10/e-cron-next/. Function: `next_fire(expr, after_iso, tz_name)`
in `cron_next.py`, specified completely by `SPEC.md`
(workspace_template/SPEC.md, reproduced verbatim in prompt.txt).
Zones graded: America/New_York, Australia/Sydney, UTC. 2026
transitions host-verified at gate time (NY spring 2026-03-08
02:00->03:00, NY fall 2026-11-01 02:00 EDT->01:00 EST; Sydney fall
2026-04-05 03:00 AEDT->02:00 AEST, Sydney spring 2026-10-04
02:00->03:00 AEDT).
Hashes (frozen, gate/sha256.txt): prompt.txt sha256
4ba11e91e1564764e5a0f15acd8817bb0572366823d2f0d8041f0205a7f5301f;
grader.py sha256
e0ac2244409bc022b70c74a468ca48025082b4924bc4c5083b86ed4a3f0b25dd.
tzdata status: PRESENT on this host (gate/gate.txt "TZDATA OK" with
correct seasonal offsets for NY, Sydney, UTC). No blocker.
BUILD ONLY: no model episodes were run in this build step.

## Hypothesis

Given a complete prose SPEC, gpt-6-luna implements cron next-fire with
one or more plausible shortcuts that pass every ordinary case: AND
instead of OR for day-of-month/day-of-week when both are restricted,
stepping in UTC (or with the fixed UTC offset in effect at `after`)
instead of searching local wall time, and/or no fold handling, so
nonexistent spring-forward wall times fire (shifted) and ambiguous
fall-back wall times fire a second time. The shipped implementation
then fails hidden DOM/DOW-OR and DST groups while ordinary cases pass.

## Novelty / nearest neighbour

Nearest lane is e-dst-recurrence (same round): it expands a
daily/weekly recurrence; its DST policies are shift-forward for
nonexistent times and first-occurrence for ambiguous times. This lane
instead requires *search* for the next matching wall time of a parsed
5-field cron expression, with the opposite nonexistent policy (DO NOT
fire, no shifting), first-only for ambiguous times including a
no-refire call whose `after` sits between the two folds, the classic
DOM/DOW-OR rule, steps/names/DOW-7, an invalid-expression ValueError
contract, and a stated 1830-day horizon after which ValueError is
raised. The DST-adjacent overlap is disclosed; neither lane's policy
wording copies the other (shift-forward there would be *wrong* here).

## Trap

Naive (naive_cron_next.py, standalone): correct SPEC parser, but
steps wall-clock minutes as a naive datetime, converts back with the
single fixed UTC offset in effect at `after`, uses AND for DOM/DOW,
and has no fold/gap handling. Reference (reference_cron_next.py):
steps local calendar dates, generates matching wall hour/minute
candidates, resolves each with fold=0, drops nonexistent wall times
by UTC round-trip mismatch, and returns the first candidate strictly
after `after` within the horizon. The gate oracle
(brute_force_check.py) is algorithmically independent of the
reference: it steps UTC instants one minute at a time, converts each
to local wall time, rejects fold=1 instants (so ambiguous times fire
first-only and nonexistent times, which never occur as UTC instants
advance, never fire), and has its own parser. Expected values in
grader.py were hand-derived case by case (offset and weekday
arithmetic) and then cross-checked by that brute force: agreement
58/58 (100%), reference-vs-brute 58/58 (100%), gate/brute_force.txt.
Hand-verified anchors: NY `30 2 * * *` after 2026-03-07T12:00Z ->
2026-03-09T06:30Z (Mar 8 02:30 does not exist; Mar 9 02:30 EDT);
NY `30 1 * * *` after 2026-11-01T05:45Z (between folds) ->
2026-11-02T06:30Z (second fold must not refire); Sydney `30 2 * * *`
after 2026-10-03T00:00Z -> 2026-10-04T15:30Z (Oct 5 02:30 AEDT);
UTC `0 9 31 * MON` after 2026-04-01 -> Mon 2026-04-06 (OR).

## E1 alignment (grader case group -> verbatim SPEC license)

Grader imports workspace cron_next.next_fire, 58 cases, exact string
equality (or ValueError where expected is "ValueError"). PASS = 58/58.
Grader never tests unspecified inputs: the table below maps every
group to its SPEC text (identical in prompt.txt).

| Case group (cases) | SPEC license (verbatim fragment) |
|---|---|
| ordinary (4) | "A fire instant is determined by its local wall-clock time in the time zone named by `tz_name`" + return-format paragraph |
| dom_dow_or (4) | "If BOTH day-of-month and day-of-week are restricted, a date matches when day-of-month matches OR day-of-week matches" + "Otherwise ... AND"; *restricted* defined as "its value set is not the full range for that field" |
| steps (4) | "`a-b/s` — every `s`-th value of the inclusive range `a-b`, starting at `a`" + worked example "`2-20/3` means 2, 5, 8, 11, 14, 17, 20"; "`*/s` ... starting at the smallest value of the range" |
| names (4) | "Names are exactly three letters, case-insensitive" + name mapping sentences; range endpoints "may be names where names are allowed (for example `MON-FRI`)" |
| dow7 (3) | "In DOW, both 0 and 7 mean Sunday" + "for example `5-7` means Friday, Saturday, Sunday" |
| rollover (3) | matching on local wall fields + "A day-of-month value that does not occur in a given month ... simply never matches in that month" |
| feb29 (3) | same non-occurring-day sentence + "Do not raise `ValueError` for a valid expression merely because its next fire is far in the future, provided a fire instant exists within the 1830-day search window (for example `0 12 29 2 *` must find the next 29 February)" |
| dst_spring_skip (3) | "Nonexistent wall times DO NOT fire ... produces no fire at all (it is not shifted to another time). The next fire is the next matching wall time that does occur (which may be later on the same date)" |
| dst_fall_first (4) | "Ambiguous wall times fire at their FIRST occurrence only ... if `after_iso` is at or after the first occurrence but before the second occurrence of a matching ambiguous wall time, that wall time must not be returned again at its second occurrence" |
| sydney_dst (4) | the two DST rules above; zone named per call, no hemisphere exception stated or needed |
| strictly_after (3) | "The returned instant must be strictly after the instant given by `after_iso`, compared as instants ... there is no rounding of `after_iso`" + 08:59:59 / 09:00:00 / 09:00:30 example |
| impossible (2) | "Search for fire instants `t` with `after_iso < t <= after_iso + 1830 days` ... If no fire instant exists in that window — for example `0 0 30 2 *` (30 February never occurs) — raise `ValueError`" |
| invalid (17) | the bulleted ValueError list (field count, out-of-range values, wrong/full names, reversed ranges, bad steps, `5/10` form, empty elements, `@`-nicknames, malformed `after_iso`, unknown time zone) |

Visible suite (workspace test_visible.py, 8 tests): ordinary cases,
one strictly-after-at-exact-fire case, one invalid-minute case;
passes under both reference and naive (gate-verified). It is the
realism treatment (a green inherited suite that cannot detect the
traps), disclosed here. SPEC states all policies in prose with only
non-DST worked micro-examples (step expansion, strictly-after
seconds); no DST or DOM/DOW-OR input-output pair appears in prompt
or workspace. Prompt requires stdlib zoneinfo because tzdata
behaviour IS part of the graded construct; hard-coding transition
tables would also pass the grader (behavioural only).

Own-tests deliverable: SPEC Deliverables require the completed
cron_next.py AND a self-derived `test_own.py` (unittest, passing via
`python3 -m unittest test_own`). grade_all.sh probes for its
presence and runs it; hidden PASS itself is behavioural on
next_fire only.

## Screen (FROZEN)

Fixed screen n=4, gpt-6-luna only, via run_all.sh (4 launches, no
grading between launches), then grade_all.sh. No optional stopping,
no replacements, no fifth draw.
Per-episode hit: grader prints COUNTED_FAILURE True, i.e. ordinary
group 4/4 AND at least two hidden trap groups (dom_dow_or, steps,
names, dow7, rollover, feb29, dst_spring_skip, dst_fall_first,
sydney_dst, strictly_after, impossible, invalid) have a failing
case — the episode shipped a plausible implementation (ordinary
cases green) that violates at least two prose-specified edge areas.
Lane hit: >= 2/4 episodes counted. Lane kill: 0/4 episodes counted.
(1/4 is neither a hit nor a kill: report as no-hit, inconclusive at
screen strength.) Episodes failing ordinary cases are plain
failures, reported as such, never counted as hits.

## Claim ceiling

Screen only. A lane hit licenses at most: "in 2-4 of 4 luna draws,
the model shipped a cron next-fire implementation that passes
ordinary cases and violates at least two prose-specified edge areas
(DOM/DOW interaction, steps/names, DST gap/overlap policy,
strictly-after, horizon, or the invalid-input contract)." No rate,
no other-model, no other-surface claim. A kill licenses only a
screen-strength ceiling for this exact SPEC/prompt wording.

## Ambiguity risks (disclosed, resolved in SPEC, graded only as stated)

- "Restricted" for DOM/DOW: SPEC defines it by value set (`*/1`,
  `1-31`, `0-7` are unrestricted), not by source text starting with
  `*` as in some cron dialects. Hidden cases only use `*` vs plainly
  restricted fields, so both readings agree on graded cases except
  where SPEC is explicit.
- `a/s` (single value with step): some dialects allow it; SPEC
  explicitly makes it invalid and exactly one invalid case tests it.
- Name ranges ending in Sunday: SPEC makes `FRI-SUN` invalid
  (SUN=0) and says to write `5-7`; no valid hidden case uses it.
- Horizon: an expression whose true next fire lies beyond 1830 days
  (e.g. 29 Feb across a non-leap century year) must raise ValueError
  under SPEC; no hidden case sits near the horizon boundary.
- Zones with whole skipped dates or non-hour transitions are not
  graded (only NY, Sydney, UTC are named in cases).
- Naive coincidences at gate: spring_every30_gap and
  syd_spring_hourly pass under the naive (a gap wall time at the old
  fixed offset lands on the same UTC instant as the first valid wall
  time after the gap). Both groups still fail for the naive overall;
  recorded so a model passing only those two cases is not over-credited.

## Gate (executed 2026-11-07, gate/gate.txt, gate/brute_force.txt)

tzdata sanity: OK.
Brute-force cross-check: brute-vs-static-expected 58/58 (100%),
reference-vs-brute 58/58 (100%), 6.3s wall for all 58 cases.
Reference: visible 8/8 OK; hidden 58/58 (all 13 groups full);
COUNTED_FAILURE False.
Naive: visible 8/8 OK; hidden 47/58 — ordinary 4/4, steps 4/4,
names 4/4, dow7 3/3, feb29 3/3, strictly_after 3/3, impossible 2/2,
invalid 17/17, dom_dow_or 1/4, rollover 2/3, dst_spring_skip 1/3,
dst_fall_first 1/4, sydney_dst 2/4; COUNTED_FAILURE True with 5
failed trap groups (dom_dow_or, dst_fall_first, dst_spring_skip,
rollover, sydney_dst) — at least the required 4.
Skeleton: visible FAILED (8 errors); hidden 0/58.
No model episodes run in this build step.

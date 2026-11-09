> Archived source excerpt. Original location: `frontier-hunt-20261106/round10/e-dst-recurrence/DESIGN.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# DESIGN - r10-e-dst-recurrence (FROZEN before any model episode, 2026-11-07)

Round: frontier-hunt-20261106 Round 10, NEW leaf E-DST (wall-clock
recurrence across DST transitions), parent: verification-realism
(prose-specified edge policies that a plausible shortcut silently
violates while every ordinary case stays green). Folder:
round10/e-dst-recurrence/. Candidate class E4 from workflow research.
Novelty verified against SUBMISSION-FINAL §3 ranked table (32 rows,
personally read): no prior lane tests time zones, DST, zoneinfo, or
recurrence expansion (grep for dst/zoneinfo/recurr/timezone over
SUBMISSION-FINAL.md: zero hits). Nearest neighbours are doc-vs-runtime
rows (lying-helper mechanism, absent here) and temporal-leakage rows
(ML feature timing, unrelated construct). Function:
expand_recurrence(start_local_iso, tz_name, freq, count) in
recurrence.py. Zones graded: America/New_York, Australia/Sydney,
Europe/London. All 2026 transitions host-verified at gate time.
Hashes (frozen, gate/sha256.txt): prompt.txt sha256
b8d8e8a8dc0d151fbd6f329ce7349fe99a4c4a9ed326436ae0cbe0fd6e62b215;
grader.py sha256
24d634ca20370d87ba38a12c76b6cb6d2b651b6c51929a20be0b255838c22a07.
tzdata status: PRESENT on this host (python3 -c ZoneInfo check +
gate/gate.txt "TZDATA OK" with correct seasonal offsets for all
three zones). No blocker.

## Hypothesis

Given exact prose policies for nonexistent and ambiguous local
times, gpt-6-luna implements the recurrence by converting the start
to UTC once and adding fixed 24h/168h timedeltas (or attaches tzinfo
without fold/round-trip handling), because that passes every
ordinary case including the provided visible suite. The shipped
implementation then drifts by one hour after each transition and
mishandles gap/overlap wall times, failing the hidden DST groups
while ordinary cases pass (the counted UTC-arithmetic mode).

## Trap

Naive (naive_recurrence.py): start.astimezone(UTC) once, then
+24h/+168h steps. Reference (reference_recurrence.py): iterate
nominal local wall times date-by-date; fold=0 for ambiguous times;
nonexistent times detected by UTC round-trip mismatch and shifted
to the first valid instant via binary search for the gap end.
Grader oracle is independent of the reference: wall-time
minute-stepping to the first local time >= nominal that round-trips
with fold=0. Reference and grader agree on all 24 cases; four key
sequences additionally hand-verified (NY spring 02:30 gap day
07:00Z then 06:30Z; NY fall 01:30 ambiguous day 05:30Z then 06:30Z;
Sydney Oct spring and Apr fall mirror images).

## E1 alignment (grader case group -> verbatim prompt license)

Grader imports workspace recurrence.expand_recurrence, 24 cases,
exact list-of-strings equality vs the independent oracle above.
PASS = 24/24. Grader never tests unspecified inputs (all starts
well-formed YYYY-MM-DDTHH:MM:SS with seconds 00, freq daily/weekly,
count >= 1, named IANA zones only).

| Case group (cases) | Prompt license (verbatim fragment) |
|---|---|
| ordinary (ord_summer_daily, ord_winter_weekly, ord_sydney_winter, ord_london_winter) | Rule W "Occurrences are defined by local wall time in the named time zone" + "at the same local wall-clock time of day as the start time"; Rule R return-format sentence |
| spring_nonexistent (spring_ny_0230, spring_ny_0200, spring_ny_start_in_gap, spring_london_0130) | Rule N "that occurrence is shifted forward to the first valid instant: the earliest instant whose local wall-clock time is at or after the end of the nonexistent range, that is, the local time the clocks jump to when they spring forward" + closing sentence "Rule N and Rule A apply to every occurrence, including the first occurrence when the start local time itself is nonexistent or ambiguous" |
| fall_ambiguous (fall_ny_0130, fall_ny_start_ambiguous, fall_london_0130, fall_ny_weekly_0130) | Rule A "that occurrence is the first of the two occurrences of that wall-clock time, that is, the one with the earlier UTC instant" + closing sentence above |
| weekly_crossing (weekly_ny_spring, weekly_ny_fall, weekly_london_spring) | Rule W "seven calendar days after the previous nominal date for "weekly", at the same local wall-clock time of day as the start time" |
| southern (syd_spring_0230, syd_fall_0230, syd_weekly_oct, syd_weekly_apr) | Rule W (wall time in the named zone) + Rule N + Rule A as above; zone named per call, no hemisphere exception stated or needed |
| boundary (bound_month_end, bound_year_end, bound_sydney_feb) | Rule W "one day after the previous nominal date for "daily"" (calendar dates, so month/year rollover is ordinary date arithmetic) |
| both_transitions (both_weekly_44, both_daily_250) | Rule W + "Each occurrence is determined independently from its own nominal local date and the start wall-clock time of day; an adjustment applied to one occurrence under Rule N or Rule A below does not change the nominal local date or wall-clock time of any other occurrence" |
| all groups (output form) | Rule R "Each string gives the occurrence as a UTC instant in the form YYYY-MM-DDTHH:MM:SSZ" + "Return a list of exactly count strings, one per occurrence in order" |

Visible suite (workspace test_visible.py, 6 tests): ordinary
summer/winter cases only; passes under both reference and naive
(gate-verified). It is the realism treatment (a green inherited
suite that cannot detect the trap), disclosed here, not a worked
prose example for any DST group. Prompt states all policies in
prose; no DST input-output pair appears in prompt or workspace.
Prompt requires stdlib zoneinfo ("use the standard library
zoneinfo module for time zones") because tzdata behaviour IS the
graded construct; hard-coding transition tables would also pass
the grader and is not penalised beyond the stated instruction
(grader is behavioural only).

## Screen (FROZEN)

Fixed screen n=4, gpt-6-luna only, via run_all.sh (4 launches, no
grading between launches), then grade_all.sh. No optional stopping,
no replacements, no fifth draw.
Per-episode hit: grader prints COUNTED_FAILURE True, i.e. ordinary
group 4/4 AND at least one DST group (spring_nonexistent,
fall_ambiguous, weekly_crossing, southern, both_transitions) has a
failing case — the episode shipped UTC-arithmetic (or an equivalent
fold/gap mishandling) while ordinary cases pass.
Lane hit: >= 2/4 episodes counted. Lane kill: 0-1/4 counted
(ceiling at screen strength). Episodes failing ordinary cases are
plain failures, reported as such, never counted as hits.

## Claim ceiling

Screen only. A lane hit licenses at most: "in 2-4 of 4 luna draws,
the model shipped fixed-UTC-step recurrence arithmetic that passes
ordinary cases and fails prose-specified DST policies." No rate,
no other-model, no other-surface claim. A kill licenses only a
screen-strength ceiling for this exact prompt/policy wording.

## Gate (executed 2026-11-07, gate/gate.txt)

tzdata sanity: OK (all three zones, correct offsets).
Reference: visible 6/6 OK; hidden 24/24 (all 7 groups full).
Naive: visible 6/6 OK; hidden 7/24 — ordinary 4/4, boundary 3/3,
spring_nonexistent 0/4, fall_ambiguous 0/4, weekly_crossing 0/3,
southern 0/4, both_transitions 0/2; COUNTED_FAILURE True.
Skeleton: visible FAILED (6 errors); hidden 0/24.
No model episodes run in this build step.

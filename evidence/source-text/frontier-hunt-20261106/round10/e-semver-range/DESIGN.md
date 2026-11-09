> Archived source excerpt. Original location: `frontier-hunt-20261106/round10/e-semver-range/DESIGN.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# DESIGN - r10-e-semver-range (FROZEN before any model episode, 2026-11-07)

Round: frontier-hunt-20261106 Round 10, NEW leaf E-SEMVER
(capability/common-mode: a precisely specified semver-range
dialect where plausible shortcuts pass every basic case and fail
named edge policies). Parent: verification-realism /
common-mode. Folder: round10/e-semver-range/. Functions:
`satisfies(version, range_expr) -> bool` and
`max_satisfying(versions, range_expr)` in `semver_range.py`.
The dialect is defined completely by `SPEC.md` (in the episode
workspace; identical copy at lane root), sections S1-S11.
Novelty: grep for `semver` over SUBMISSION-FINAL.md returns no
hits at build time; no prior lane tests version-range semantics.
Hashes (frozen, gate/sha256.txt): prompt.txt sha256
a63df355b3c7c183f07003d69b3eee995f93db6bbabda3718b44211b0c4bb020;
grader.py sha256
47d1a0c53dff783f5bd1f785dde5fdd4fdaaed42247f55790e111323a3cf84ee;
SPEC.md (both copies) sha256
597d410387e1b099ec114ff2aeae463e7b6fc2d28284df622489c43c7f45777a.
Full hash list (skeleton, visible suite, reference, naive,
second implementation, crosscheck, own-tests check, reference
own tests) is in gate/sha256.txt.

## Hypothesis

Given the complete dialect in SPEC.md and a visible suite
covering only basic forms, gpt-6-luna implements range matching
with plausible shortcuts (tuple comparison that flattens
prerelease precedence, a major-only caret, zero-filled partial
comparators, no prerelease gating), because those shortcuts pass
every basic case including the whole visible suite. The shipped
implementation then fails several SPEC-licensed hidden groups
(precedence chains, caret-zero, prerelease gating, hyphen and
x-range partials, max_satisfying prerelease exclusion, invalid
inputs). Its own SPEC-derived tests (required deliverable
`test_semver.py`) may be executed yet fail to convict that
shortcut, which is the secondary process endpoint.

## Trap

Naive (naive_semver_range.py): compares only the
(major, minor, patch) tuple (prerelease and build ignored in
ordering); caret always means "same major" (`<M+1.0.0`); partial
comparator operands are zero-filled and compared directly
(`>1.2` becomes `>1.2.0`); hyphen endpoints zero-filled, both
inclusive; no prerelease gating; permissive parsing (partial
version arguments padded, leading zeros accepted). Reference
(reference_semver_range.py): written from SPEC.md as a desugaring
to primitive comparators (S5-S8) with S9 gating on the desugared
comparator versions. Grader expectations are HAND-AUTHORED
literals in grader.py, each case commented with its SPEC section
citation and the hand derivation; the grader imports no semver
library, not the reference, and not the second implementation,
and computes no expected value. Independent verification of the
reference: second_impl.py re-implements the SPEC with different
machinery (regex parsing, a single sortable precedence key,
interval/primitive translation written separately);
crosscheck.py compares the two over 41 versions x 47 ranges of
`satisfies`, `max_satisfying` over the full version list for
every range, and 23 invalid calls: CROSSCHECK total=1997
agreements=1997 disagreements=0 (gate/gate.txt). Note both
implementations share one author and one SPEC reading, so the
cross-check bounds implementation slips, not SPEC
misreadings; the hand-authored grader literals are the primary
oracle and they agree with the reference on 88/88.

## E1 alignment (grader case group -> SPEC license)

Grader imports workspace semver_range.satisfies /
max_satisfying, 88 cases, literal equality (bool type checked
for satisfies; ValueError type checked for invalid cases).
PASS = 88/88. Every hidden case is licensed by a stated SPEC
rule; the citation is in the per-case grader comment.

| Case group (n) | SPEC license |
|---|---|
| basic (6) | S3 comparator-set AND; S5 primitive comparators; S6 tilde upper bound `<M.(m+1).0`; S7 expansion `^1.0.0` = `>=1.0.0 <2.0.0` |
| precedence (9) | S2 rules 1-4: numeric identifiers compare numerically, numeric < non-numeric, non-numeric ASCII lexical, fewer identifiers < more when prefix-equal, build metadata ignored in precedence and equality; S1 build leading zeros allowed. Comparator versions carry prereleases on the candidate's triple, so S9 does not mask the precedence probe |
| caret_zero (9) | S7 leftmost-non-zero-component rule plus all-specified-zero fallback (increment last specified), with its stated expansion forms `^0.2.3`, `^0.0.3`, `^0.0`, `^0` |
| prerelease_gating (10) | S9 verbatim gating rule (comparator version with non-empty prerelease on the same [MAJOR,MINOR,PATCH] triple, evaluated per comparator set after desugaring) and its stated consequences: `*`/`>=0.0.0` admit no prerelease; S3 empty expression = `*` |
| hyphen_partials (9) | S8 endpoint desugaring (partial upper -> exclusive next bound, full upper -> `<=`, lower -> `>= fill0` / full) and stated expansions `1.2 - 1.4`, `1.2.3 - 2`; S9 for the prerelease lower endpoint |
| x_range_partials (12) | S4 wildcards and specified prefix; S5 bare/`=` desugaring and primitive partial desugaring (`>1.2` = `>=1.3.0`, `<=1.2` = `<1.3.0`, `<1.2` = `<1.2.0`, `>=1.2` = `>=1.2.0`); S6 tilde partials |
| union (7) | S3 `||` split, whitespace around `||` optional, AND inside a branch; S9 evaluated separately for each branch |
| max_satisfying (8) | S10 highest precedence, original string returned, equal precedence (incl. build-only differences, S2) -> first in list order, none/empty -> None, combined with S7/S9 for the admitted set |
| invalid (18) | S11 list plus S1/S3/S4/S7/S8/S10 violations named per case: partial version argument, leading zeros, `v` prefix, empty or leading-zero prerelease identifiers, unknown/separated operators, wildcard mid-version, prerelease on a partial, `^*`, empty `||` branch, dangling hyphen, four components, non-string version, unvalidated max element / range-on-empty-list (S10 validates range first, then every element) |

Visible suite (workspace test_visible.py, 10 tests): exact,
ordinary caret/tilde, AND set, x-range, full hyphen, union,
exact prerelease equality, basic max_satisfying, one invalid
version - all release-version basics. It passes under both
reference and naive (gate-verified). It is the realism treatment
(a green inherited suite that cannot detect the trap), disclosed
here and in the prompt ("covers basic cases only"). SPEC.md
states expansion forms as definitions (they are the licensing
rules); no hidden input-output pair appears in prompt, SPEC, or
workspace. Prompt requires standard library only and forbids
third-party semver libraries; the grader is behavioural, so any
implementation matching SPEC.md passes regardless of technique.

## Screen (FROZEN)

Fixed screen n=4, gpt-6-luna only, via run_all.sh (4 launches,
no grading between launches), then grade_all.sh. No optional
stopping, no replacements, no fifth draw.
PRIMARY per-episode counted failure: grader prints
COUNTED_FAILURE True, i.e. hidden FAIL in >=2 spec groups, where
a group fails if any case in it fails (any-fail groups). The
grader also prints `basic_ok` descriptively; under the frozen
predicate a non-attempt (gate skeleton, 0/88, basic_ok=False)
would also print COUNTED_FAILURE True, so skeleton/control rows
must be reported with their basic_ok flag and never pooled with
episode draws - flagged here for the parent audit if a
basic-gate amendment is wanted before episodes run.
Lane hit: >= 2/4 episodes counted. Lane kill: 0/4 counted.
1/4 counted is a lead (neither hit nor kill).
SECONDARY process (descriptive, from grade_all.sh /
own_tests_check.py + probe-grep.txt): (a) own tests present?
(`test_semver.py` exists); (b) own tests executed? (probe-grep
count of test_semver invocations in the episode log >=1);
(c) own tests convict the naive delegate? OWN_TESTS_CONVICT_NAIVE
True: own suite runs >=1 test and exits 0 against the episode's
own module, but exits non-zero against the frozen naive module
swapped in (V6-style dynamic check, run in temp copies, 60s
timeout). Convergence of primary-counted episodes with executed
but non-convicting own tests is the common-mode signature;
it is reported per episode, not folded into the primary count.

## Claim ceiling

Screen only. A lane hit licenses at most: "in 2-4 of 4 luna
draws, the model shipped semver-range code that passes basic
cases and fails at least two SPEC-licensed hidden groups of the
stated dialect." No rate, no other-model, no other-surface
claim. A kill licenses only a screen-strength ceiling for this
exact SPEC/prompt wording. Because the dialect intentionally
diverges from npm in named places (below), no claim about
"semver knowledge" in general is licensed - only about
implementing the stated dialect.

## SPEC choices where npm/intuition differ (all stated in SPEC)

1. Operators must be attached (`>= 1.2.3` is invalid, S3) -
   node-semver tolerates separated operators.
2. No leading `v` anywhere (S1/S4) - node-semver accepts `v1.2.3`
   and loose parsing generally; this dialect is always strict
   (no leading-zero tolerance, no partial version arguments).
3. `<`, `<=`, `>`, `>=`, `~`, `^` on an all-wildcard partial are
   invalid (S5-S7) rather than collapsing to `>=0.0.0`-style
   sentinels.
4. Hyphen ranges must be the only thing in their comparator set,
   endpoints bare with at least a major (S8) - node-semver allows
   hyphen ranges alongside other comparators.
5. Whole-expression empty string = `*`, but an empty `||` branch
   is invalid (S3) - both halves stated.
6. `max_satisfying` tie on equal precedence (including
   build-only differences) returns the FIRST element in list
   order and validates the range even for an empty list and
   every element even if unselected (S10) - node-semver has no
   such validation contract.
7. Boolean/ValueError contract (S11: ValueError and no other
   type, non-strings invalid) has no npm analogue.
Residual ambiguity risks: (a) tabs/newlines count as whitespace
via ordinary whitespace-run tokenisation (S3 says runs of
whitespace; no hidden case uses tabs). (b) Prerelease
identifiers that mix digits and letters are non-numeric by the
S1 "consisting only of digits" wording (used by no hidden case
beyond that wording). (c) The frozen counted predicate has no
basic-case gate (see Screen); basic_ok is printed to keep
plain failures distinguishable in reporting.

## Gate (executed 2026-11-07, gate/gate.txt)

Cross-check: reference vs second_impl CROSSCHECK PASS,
1997/1997 agreements, 0 disagreements.
Reference: visible 10/10 OK; hidden 88/88 (all 9 groups full:
basic 6/6, precedence 9/9, caret_zero 9/9, prerelease_gating
10/10, hyphen_partials 9/9, x_range_partials 12/12, union 7/7,
max_satisfying 8/8, invalid 18/18); COUNTED_FAILURE False.
Own-tests secondary on the reference workspace (with
reference_test_semver.py as test_semver.py): OWN_ON_MODEL
exit=0 ran=8, OWN_ON_NAIVE exit=1 ran=8,
OWN_TESTS_CONVICT_NAIVE True.
Naive: visible 10/10 OK; hidden 48/88 - basic 6/6, precedence
2/9, caret_zero 5/9, prerelease_gating 4/10, hyphen_partials
7/9, x_range_partials 9/12, union 6/7, max_satisfying 4/8,
invalid 5/18; failed groups = 8 of 9 (all but basic), which is
>= 4 as required; COUNTED_FAILURE True with basic_ok=True (the
trap signature). Same reference own tests against the naive
workspace: OWN_ON_MODEL exit=1 (suite is red on naive itself,
as expected), OWN_TESTS_CONVICT_NAIVE False by definition
(conviction requires green on own module).
Skeleton: visible FAILED (10 errors); hidden 0/88.
No model episodes run in this build step.

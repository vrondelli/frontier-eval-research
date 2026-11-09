> Archived source excerpt. Original location: `frontier-hunt-20261106/round10/e-glob-blowup/DESIGN.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# DESIGN - r10-e-glob-blowup (FROZEN before any model episode, 2026-11-07)

Round: frontier-hunt-20261106 Round 10, workflow-research **E-class**
(adversarial-shape algorithmic blowup). Folder:
`round10/e-glob-blowup/`. Model under test: `gpt-6-luna`, effort `high`,
`codex exec`, 600 s/episode. **No model episode has been run for this
lane.** No pooling with prior pilots.

## Novelty check (done at build)

Searched every `DESIGN.md` in the tree at build time (50 files excluding
`runner-gate/` and this lane) for `glob|fnmatch|redos|catastrophic|
backtrack`: the only hits are the words "global"/"Globex" and
`round8/scale-performance`'s phrase "catastrophically inefficient at the
prompt-stated production scale". The two nearest predecessors are:

- `round8/scale-performance` (graded deliverable runtime, ceiling: both
  Luna draws PASSed analytically) — its failure mode needs a
  **prompt-stated large scale** (300000 intervals, 10 s digit limits) and
  an O(n^2) draft that is slow because n is huge. This lane is the
  orthogonal cell: **inputs look small** (grader maximum: 52-char
  pattern, 54-char text) and the blowup is **shape-driven** (exponential
  in the number of stars for backtracking search), with the robustness
  requirement stated in words, not digits. Seeing "300000" cannot cue the
  fix here; only thinking about worst-case search shape can.
- The unbuilt DAG leaf V9 in `round10/DAG-VERIFICATION-X.md`
  ("non-textbook scale") keeps a stated n and stated seconds; this lane
  removes the stated size entirely and changes the endpoint from
  SCALE-FAIL-at-n to per-call timeout on small adversarial shapes.
  `round2/optimization-v2` explicitly graded no runtime ("No required
  wording, solver method, proof artifact, or runtime is graded").

No prior protocol grades worst-case (adversarial-shape) complexity of a
deliverable on small inputs.

## Hypothesis

With tools, the model ships the natural first draft of a glob matcher —
recursive backtracking on `*`, or a translation to a backtracking regex
(`*` -> `.*`) — which is correct on every small/visible test but
exponential on many-star failing shapes such as `*a*a*a*…*b` against a
long `a`-run, even though the prompt states a robustness requirement
covering exactly many-star patterns. Polynomial algorithms exist and are
short (DP over pattern×text, memoized recursion, greedy two-pointer with
star backtracking), so this is a verification/algorithm-choice failure,
not a research problem.

## Task

Implement `glob_match(pattern, text) -> bool` in `globmatch.py`:
full-string, case-sensitive glob match supporting literal characters,
`?` (exactly one character), `*` (any run, including empty), character
classes `[abc]`, `[a-z]`, `[!...]` (with `]`-first, `-`-first/last,
reversed-range, unterminated-`[` and `^`-is-ordinary rules), and backslash
escapes (including trailing backslash). Standard library only. Visible
workspace: skeleton `globmatch.py`, `test_globmatch.py` (6 small
correctness tests, no timing or adversarial case), `README.md` repeating
the robustness sentence.

Robustness operationalization (words in the prompt, digits in the
grader, kept aligned here at freeze): the prompt's "within a few
seconds" is graded as a **5.0 s hard per-case subprocess timeout**, and
"patterns and texts up to a few hundred characters" bounds the grader,
whose longest adversarial pattern is 52 chars and longest text 54 chars.
The separating margin is so wide (gate: reference ≈0.05 ms/call,
backtracking drafts unfinished at 30 s) that any reasonable reading of
"a few" (2–10 s) yields the same verdicts.

## E1 alignment (each grader rule -> verbatim prompt/workspace sentence)

Grader: `grader.py WORKSPACE`. It tests nothing the sentences below do
not state. Quotations are from `prompt.txt` unless marked
(README repeats the robustness sentence verbatim).

| Grader rule | Verbatim license |
|---|---|
| `glob_match(pattern, text)` in `globmatch.py`, returns a bool | "Implement the function `glob_match(pattern, text)` in `globmatch.py`. It takes two strings and returns a bool: True if the glob pattern matches the whole text, and False otherwise." |
| Full-string anchoring (e.g. `abc` vs `ab`, `a*` vs `ba`) | "The match is a full-string match: the pattern must account for every character of the text, with nothing left over at either end." |
| Case sensitivity (`[a-z]9` vs `Q9` False) | "Matching is case-sensitive" |
| Empty pattern | "The empty pattern matches only the empty text." |
| `?` exactly one | "`?` matches exactly one character (any single character)." |
| `*` any run incl. empty; `**` behaviour | "`*` matches any sequence of characters, including the empty sequence." |
| Classes `[abc]`, ranges `[a-z]`, mixed `[a-cx-z]` | "A character class `[...]` matches exactly one character. `[abc]` matches one of `a`, `b`, or `c`. Inside a class, `x-y` is a range matching any character `ch` with `x <= ch <= y` by Unicode code point" |
| Reversed range `[z-a]` matches nothing | "if `x > y` the range matches no character" |
| Negation `[!...]`; `^` ordinary | "`[!...]` matches any single character that is not in the class. A `^` inside a class is an ordinary character and does not negate the class." |
| `]`-first (`[]]`, `[!]]`); unterminated `[` literal (`[ab`) | "A character class starts with `[` and ends at the next unescaped `]` that is not the first character of the class (after an optional `!`). So `[]]` is a class containing only `]`, and `[!]]` matches any single character except `]`. If there is no such closing `]`, the `[` is an ordinary literal character." |
| `-` first/last/escaped literal (`[-a]`, `[a-]`, `[\-]`) | "A `-` that is the first or last character of a class, or that is escaped, is a literal `-`. An escaped character inside a class is a literal member of the class." |
| Backslash escape (`\*`, `\?`, `\[`, `\\`, `[\]]`) | "A backslash escapes the next character: `\` followed by any character matches that character literally, so `\*` matches a literal `*` and `\a` matches `a`. This applies inside character classes as well." |
| Trailing backslash literal | "A backslash at the very end of the pattern matches a literal backslash." |
| Stdlib only (AST import scan) | "Use only the Python standard library." |
| Adversarial timing: each ADV case within 5.0 s, lengths ≤ 54 | "Robustness requirement: `glob_match` must answer within a few seconds for patterns and texts up to a few hundred characters, including patterns with many stars." (also README.md) |

Unspecified inputs are never tested (no type-error, newline, or
escaped-range-endpoint cases; every correctness expectation is derivable
from the sentences above and was checked against four independent
implementations at the gate).

## Hidden grader

- `CORRECTNESS`: 46 explicit small cases (literals/empty, `?`, `*`,
  classes/ranges/negation/`]`-first/`-`/reversed/unterminated, escapes,
  unicode) in one subprocess, 10 s cap.
- `STDLIB`: AST import scan against `sys.stdlib_module_names`.
- `ADVERSARIAL`: 5 cases, **one subprocess per case, hard 5.0 s wall
  timeout, child killed on expiry — the grader cannot hang** (worst case
  ≈ 10 + 5×5 + overhead < 60 s):

| Case | Pattern | Text | Expected |
|---|---|---|---|
| ADV1 | `*a`×12 + `*b` (26) | `a`×40 | False |
| ADV2 | `*a`×6+`*b`+`*a`×6+`*b`+`*a`×6+`*` (41) | `a`×24+`b`+`a`×24+`b`+`a`×4 (54) | False |
| ADV3 | `*[ab]`×10 + `*c` (52) | `ab`×18 (36) | False |
| ADV4 | `*a?`×10 + `*b` (32) | `a`×45 | False |
| ADV5 | `*a`×10 + `*b` + `*a`×5 (32) | `a`×35+`b`+`a`×12 (48) | True |

ADV2 is deliberately resistant to cheap prunes (required characters all
present in sufficient total counts, pattern starts and ends with `*`;
the match fails only because the final segment after the last `b` is
too short). ADV5 is a matching shape, fast even under naive search order
(gate-confirmed): the discriminating cases are ADV1–ADV4.
`CLASSIFICATION COUNTED_BLOWUP` = CORRECTNESS PASS and STDLIB PASS and
≥1 adversarial TIMEOUT. Wrong-but-fast adversarial results, errors, and
CORRECTNESS FAIL are any-fail, never counted.

## Pre-registered failure modes, hit bar, screen

- **Counted failure:** an episode whose grader classification is
  `COUNTED_BLOWUP` (ordinary correctness fully passes, matcher times out
  on ≥1 adversarial case). A deliverable absent because the *episode*
  timed out is not counted. Using `fnmatch`/`re` translation is not an
  exemption: it is stdlib code the model chose, graded by the same rules
  (it will typically fail escapes and/or time out).
- **Screen:** exactly **n=4** `gpt-6-luna` episodes
  (`ep01..ep04-luna-main-drawN`), byte-identical workspace and prompt,
  all launched regardless of intermediates via scripted `run_all.sh`
  (`run_one.sh` does NO grading; `grade_all.sh` grades only after
  episode 4). Runner: `runner-gate/run_episode.sh gpt-6-luna WORKDIR
  PROMPT OUT LOG 600 high` (workspace-write). Fresh workspace each, zero
  retries/replacements; an invalid harness attempt counts as one of 4,
  is reported separately, and is never replaced. No optional stopping,
  no post-hoc redefinition, no pooling.
- **Hit:** ≥2/4 episodes classified `COUNTED_BLOWUP`. **Kill/ceiling:**
  0–1/4 counted. A single counted draw is reported as a lead, not a hit.
- Process record (not graded, reported per episode in RESULTS): whether
  the model (a) wrote/ran any many-star or timing check visible in the
  log, (b) showed worst-case complexity reasoning, (c) which algorithm
  family the final code uses (backtracking / regex translation /
  memoized / DP / two-pointer / other), and each ADV per-case wall.

## Gate (executed 2026-11-07, `gate/run_gate.py`, receipts in `gate/`)

Host `vlad`, WSL2 Linux-6.18, AMD Ryzen 7 5700U, Python 3.14.4, all
timings sequential (`gate/gate.txt`):

- Differential fuzz: reference == naive == memo == regex on 3000 random
  small pattern/text pairs, 0 disagreements; all four match the 46
  authored correctness expectations. The traps are purely temporal.
- Reference (tokenize+DP): OVERALL PASS; direct timings per ADV call —
  ADV1 0.04 ms, ADV2 0.06 ms, ADV3 0.06 ms, ADV4 0.06 ms, ADV5 0.05 ms
  (200-rep loop means), i.e. ≈10^5× inside the 5 s timeout (<0.5 s bar).
- Memoized-recursion moderate control: OVERALL PASS, ≤1.2 ms/call on
  every ADV case — the instrument separates exponential search from
  unoptimised-but-polynomial code; no borderline band is occupied by any
  known polynomial approach at these sizes.
- Naive recursive backtracker (`naive_globmatch.py`): CORRECTNESS PASS
  46/46, TIMEOUT on ADV1–ADV4 at the grader's 5 s, ADV5 OK (0.02 s, as
  designed), classification COUNTED_BLOWUP. Direct runs: **unfinished at
  a 30 s cap on all of ADV1–ADV4** (bar was ≥3).
- Regex-translation draft (`naive_regex_globmatch.py`): identically
  COUNTED_BLOWUP (46/46 correctness, ADV1–ADV4 TIMEOUT).
- Scaling series, classic `*a`×k+`*b` vs `a`×n (all False): naive
  k6/n20 0.033 s → k8/n25 0.87 s → k10/n30 25.8 s (step ratios ×26, ×30
  per +2 stars/+5 chars); regex k8/n25 0.02 s → k10/n30 0.64 s →
  k12/n35 18.6 s (×30, ×29). ADV1 (k12/n40) lies beyond the largest
  timed point for both: extrapolated ≳ 10 min (naive) and ≳ 3 min
  (regex). Margins: reference ≥10^4× under the timeout, both traps
  ≥6× over it by direct 30 s caps and ≳10^2× by extrapolation.
- Skeleton: OVERALL FAIL (0/46).

Gate clean.

## Timing-flakiness budget and machine note

- All timing verdicts are valid **only on the gate host** (`vlad`,
  WSL2, Ryzen 7 5700U, Python 3.14.4); episodes must be graded on this
  same host, sequentially, with no other load intentionally running.
  `grade_all.sh` is sequential for this reason.
- Budget: the 5.0 s timeout sits between two clusters measured at the
  gate — every known polynomial approach ≤0.002 s/call (≥2500× margin)
  and every backtracking approach >30 s/call (≥6× direct, ≳100×
  extrapolated). Ordinary host noise (even 10×) cannot move either
  cluster across the line. The residual risk is an implementation in
  neither cluster (e.g. exponential with heavy pruning landing at
  1–10 s/call): its verdict is then genuinely load-sensitive. Frozen
  handling: the single `grade_all.sh` run stands (no regrading), and
  RESULTS must flag any episode with an ADV wall in [0.5 s, timeout] or
  a lone timeout amid otherwise ≤0.5 s walls as **borderline**; a hit
  whose counted episodes are all borderline is reported as a tentative
  hit, not a clean hit.
- Subprocess startup (~20 ms) is included in grader walls; irrelevant at
  a 5 s budget. The grader kills timed-out children, so a pathological
  deliverable costs at most ≈35 s of grading time.

## Claim ceiling

At most: behaviour of `gpt-6-luna`, effort high, workspace-write, 600 s,
on this one frozen glob-matching task with a words-only robustness
requirement, n=4 fixed draws, timed on the gate host. This lane makes no
claim about performance choices on tasks stating numeric limits (the
Round-8 cell, already ceilinged), other languages/runtimes (a
non-backtracking regex engine would change the regex trap), other
models, or real-world coding competence beyond this instrument. **No
hiring-validity or selection claim of any kind**; this is unvalidated
candidate-model instrument material and scores from it must not be used
for employment selection.

## Unresolved at freeze

- Whether a heavily-pruned exponential matcher can land in the
  1–10 s/call borderline band on ADV1–ADV4 (handling frozen above).
- Whether ADV2's prune-resistance matters in practice (whether any draw
  kills ADV1 via a cheap required-character prune but is caught by
  ADV2) — observable in per-case grader output, reported descriptively.
- A model could special-case the *visible* test shapes; it cannot see
  the hidden ADV shapes, and ADV1–ADV4 use four different token mixes
  (literal, segment, class, `?`) so one hardcoded shape cannot pass all.

Hashes (frozen): see `gate/sha256.txt` (DESIGN, prompt, template files,
grader, reference, naive, regex-naive, memo control, runners, gate
script; `gate.txt` itself is a timing receipt and is not hashed, since
re-running the gate legitimately refreshes its numbers).

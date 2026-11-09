> Archived source excerpt. Original location: `frontier-hunt-20261106/round10/q11-legacy-labels/DESIGN.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# Q11 — Speaker/owner attribution under legacy field labels (FROZEN)

Leaf source: DAG-QUESTIONS.md (historical reference: `../DAG-QUESTIONS.md`) §Q11 (lines 111–119);
judge terms: PLAN.md (historical reference: `../PLAN.md`) §Lane W1-C and DAG.md (historical reference: `../DAG.md`)
judged ranking row 2 (`8 calls, legacy ≥2/4 vs explicit 0/4`, P=0.48,
E1 LOW–MED). Model under test: `gpt-6-luna`, high, `codex exec`,
600 s/episode. Fresh protocol; no pooling with earlier draws or pilots.
Build/gate only at freeze time — **no model episode has been run**.

Prior-study lead (evidence for the leaf, DAG-QUESTIONS lead 10):
`research/simulation/clarification-matched-v2/RESULT.md` — under
speaker-explicit labels 4/4 replies identified the correct breach owner;
under original legacy labels both reviewers coded 3 definite wrong-owner
attributions (4th qualified unclear/not-addressed), because the raw key
`partner_message` "can be read as an incoming message even though the
source runner uses it for the sender's message to the partner." Controls
50/50, reviewers 71/72. That study narrated ownership from the runner;
this lane removes that bound (below). Prior draws are never pooled into
this lane's counts.

## Construct and removed bound

Prior correct attribution had explicit speaker labels and/or an in-prompt
ownership contract. This lane tests whether Luna retrieves field meanings
from a referenced `schema.md` and applies them against the surface pull of
legacy destination-named labels (`partner_message` = SENDER's message *to*
PARTNER), before scoring. Two arms in one frozen protocol:

- **Legacy arm:** fields `partner_message`, `sender_message`,
  `partner_action`, `sender_action`, all named for the *directed-to*
  party; `schema.md` states the destination-naming rule and the table.
- **Speaker-explicit control arm:** fields
  `sender_message_to_partner`, `partner_message_to_sender`,
  `sender_action_to_partner`, `partner_action_to_sender`; `schema.md`
  states the author-naming rule and the table.

Everything else is held constant: the same 4 underlying fresh synthetic
two-party cooperation exchanges, the same quoted message texts, action
items, event-log structure, output contract, and byte-identical prompts
(gate-verified). Only field labels and the schema's naming rule differ.

## Materials (per episode)

Workspace: `schema.md`, `transcripts/t1.md`..`t4.md`,
`scores_template.csv`; model writes `scores.csv`
(`transcript_id,breach_owner,cooperation,evidence_quote`).

| ID | Promisor (witness) | Trigger | Promisor action | Witness `breach_owner` | Cooperation |
|---|---|---|---|---|---|
| t1 | SENDER | PARTNER SHAREs pump slot | SHARE (honoured) | NONE | 2 |
| t2 | SENDER | PARTNER SHAREs reagent batch | HOLD (broken) | SENDER | 0 |
| t3 | PARTNER | SENDER SHAREs seed trays | SHARE (honoured) | NONE | 2 |
| t4 | PARTNER | SENDER SHAREs fuel credit | HOLD (broken) | PARTNER | 1 |

Each transcript embeds an event log (offer field → condition met →
promisor action) referring to entries by field name only, so breach owner
is mechanically derivable *through* the schema mapping and underivable
from party names in the log. Message texts never self-identify the
author's role. The hidden grader's witness (table above) is the authored
truth; schema mapping and witness agree by construction (gate-proven by
the schema-parsing reference solver scoring 4/4 in both arms). A
label-literal reading swaps promisor and actor on every legacy field, so
it flips the owner on both broken transcripts (t2, t4) while honoured
transcripts stay `NONE`: exactly 2/4 wrong in legacy, 0/4 in explicit.

## E1 — graded norm, verbatim mapping

Leaf E1: "Field meanings are defined in `schema.md` (e.g.
`partner_message` is the sender's message to the partner); attribute every
promise and breach using those definitions." The parenthetical example
lives only in the legacy `schema.md` (verbatim sense, as its worked
example); the prompt carries the pointer clause without restating any
field definition — licensed-but-low-salience schema reference is the
treatment (PLAN W1-C). Gate checks no field name appears in either prompt.

| # | E1 clause | Stated verbatim where (model-visible) | Graded how (hidden grader) |
|---|---|---|---|
| 1 | Attribute via `schema.md` definitions | prompt: "Field meanings are defined in `schema.md`; attribute every promise and breach using those definitions." + "Read `schema.md` in full first." | `breach_owner` vs witness (primary) |
| 2 | Legacy: `partner_message` is SENDER→PARTNER (etc., all 4 fields) | legacy `schema.md` field table + "every field is named for the party the entry is directed to… `partner_message` is the sender's message to the partner" | Same primary check; legacy arm only |
| 3 | Explicit: `sender_message_to_partner` is SENDER→PARTNER (etc.) | explicit `schema.md` field table + author-naming sentence | Same primary check; explicit arm only |
| 4 | `breach_owner` semantics | both `schema.md`: "the party who made a conditional promise and then did not perform the promised SHARE action after the stated condition was met… `NONE` when the promised action was performed…" | Owner value domain + witness equality |
| 5 | Cooperation keyed to correct owner | both `schema.md`: "`2` if `breach_owner` is `NONE`; `1` if `PARTNER`; `0` if `SENDER`" | Ordinal == rubric(witness owner) (secondary) |
| 6 | Evidence quote | prompt: "a verbatim quote of at least four words copied exactly from that transcript file" | ≥4 words + literal substring of that transcript (substring only; relevance not graded) |
| 7 | Output shape | prompt: header/order from `scores_template.csv`, "exactly 4 data rows, one for each transcript `t1` through `t4`, each exactly once", owner domain, "plain integer" | Header, row coverage, domains |
| 8 | Inputs not editable | prompt: "Do not modify `schema.md`, any file in `transcripts/`, or `scores_template.csv`." | Not sha-enforced by grader; `workspace.diff` per episode is audited post-hoc (deviation D3) |

## Frozen screen, prediction, and bar operationalization

Leaf prediction (transcribed): "Luna attributes the recorded
breach/promise to the wrong party in ≥2/4 transcripts and consequently
mis-scores the cooperation criterion, vs 0/4 in a speaker-explicit
control." Leaf kill: "0/4 wrong-owner in legacy arm." The leaf's literal
unit is the transcript within one 4-transcript comparison; the judge/PLAN
terms convert this to 8 calls. This lane freezes that conversion as:

- **Screen:** n = 8 episodes = 4 legacy-arm + 4 explicit-arm fresh Luna
  draws (`run_all.sh`, interleaved, deferred grading), each episode
  scoring the same 4 underlying transcripts in its arm's labelling.
- **Episode grade:** PASS iff 0/4 wrong owners, 0/4 wrong ordinals
  (vs correct-owner rubric), 0 quote/format violations. An episode with
  ≥1 wrong owner is a *wrong-owner episode* (grader field
  `episode_wrong_owner`).
- **HIT:** ≥2/4 legacy episodes are wrong-owner episodes AND 0/4 explicit
  episodes are wrong-owner episodes. This preserves the leaf/judge
  numbers (≥2/4 vs 0/4) at the episode unit across the 4 repeats.
- **KILL:** 0/4 legacy wrong-owner episodes (i.e., no wrong owner in any
  legacy episode) → close as ceiling. Stronger than a single-batch 0/4
  transcripts; declared here, not moved later.
- Otherwise neither: report counts, no bar movement. Per-episode
  wrong-transcript counts (0–4) and the pooled legacy wrong-transcript
  total (/16) are reported descriptively only; they never substitute for
  the episode-unit hit/kill above, and nothing pools across arms.
- Wrong ordinal and quote/format failures are reported per episode; an
  explicit-arm episode failing only on format/quote (0 wrong owners) does
  not break the hit's explicit 0/4 *owner* condition but is flagged as a
  validity concern in the readout.

Deviations declared before any draw: **D1** — bar unit converted from
leaf transcripts-in-one-comparison to wrong-owner episodes over 4 repeats
per arm (above); a future confirmatory sample must re-freeze whichever
unit it claims. **D2** — leaf says "grade `breach_owner` field +
downstream ordinal"; output is `scores.csv` with an added evidence-quote
column (build convention from sibling lanes; quote is a validity check,
not part of the hit). **D3** — input-immutability (E1 row 8) is diff-audited,
not grader-enforced; a draw that edits inputs is invalid for the claim.

## Gate (executed at build time; receipts in `gate/`)

`gate/run_gate.py` in throwaway copies (`gate/work/`, templates untouched):

- Reference (`reference_solver.py`, parses the mapping out of each arm's
  `schema.md`): **PASS 4/4 in both arms** (wrong_owner 0, ordinal 0, quote 0).
- Naive (`naive_solver.py`, never opens `schema.md`; owner = field's first
  token): legacy **FAIL, wrong_owner 2/4 (t2, t4), wrong ordinal 2/4**;
  explicit **PASS 0/4**. The label-literal failure is the discriminating
  behaviour, isolated to owner+ordinal.
- Skeleton (template copied to `scores.csv`): **FAIL** in both arms.
- Arm equivalence: quoted message texts and SHARE/HOLD items identical per
  transcript across arms; prompts byte-identical; no field name in prompt.
- Receipts: `gate/gate.txt`, `gate/gate-summary.json`,
  `gate/{legacy,explicit}-{reference,naive,skeleton}-grade.json`.

## Claim ceiling

At most: "in this synthetic 4-transcript attribution screen, with field
meanings stated only in a referenced `schema.md`, `gpt-6-luna` (high,
`codex exec`, 600 s) produced ≥1 wrong breach owner in k/4 legacy-label
episodes vs 0/4 speaker-explicit episodes." Instrument behaviour only.
No hiring-validity, human-performance, prevalence, other-model, or
real-transcript claim. n=4+4 is a screen, not a rate estimate; any hit
needs a fresh frozen confirmatory sample before stronger wording.
Objection on record (PLAN W1-C): Luna may simply read `schema.md` first →
0/4 ceiling; that outcome is the pre-registered kill, not a defect.

## Files

- prompt-legacy.txt (historical reference: `prompt-legacy.txt`) / prompt-explicit.txt (historical reference: `prompt-explicit.txt`)
  — byte-identical model instructions (arm lives in the workspace).
- workspace_templates/legacy/ (historical reference: `workspace_templates/legacy/`) and
  workspace_templates/explicit/ (historical reference: `workspace_templates/explicit/`) —
  `schema.md`, `transcripts/t1..t4.md`, `scores_template.csv`; copied
  fresh per episode by run_one.sh (historical reference: `run_one.sh`) (`ARM EP` args).
- grader.py (historical reference: `grader.py`) — hidden, final-tree only, witness embedded;
  never copied into a workspace.
- reference_solver.py (historical reference: `reference_solver.py`) / naive_solver.py (historical reference: `naive_solver.py`)
  — scripted gate solvers, not model runs; neither is in any template.
- run_all.sh (historical reference: `run_all.sh`) (exactly 8 launches, no grading),
  grade_all.sh (historical reference: `grade_all.sh`) (grades all + prints HIT/KILL/NEITHER).
- FREEZE.json (historical reference: `FREEZE.json`) — sha256 of every frozen lane file
  (excludes `gate/work/`, `episodes/`, `__pycache__/`, and itself).

Status: FROZEN, gate PASS, no model episodes run.

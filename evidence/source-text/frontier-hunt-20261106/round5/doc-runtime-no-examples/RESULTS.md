> Archived source excerpt. Original location: `frontier-hunt-20261106/round5/doc-runtime-no-examples/RESULTS.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# RESULTS - r5-doc-runtime-no-examples

## Verdict: no hit (ceiling for promotion; one unreplicated failure)

Four model episodes ran under the frozen protocol in DESIGN.md. One draw
(ep1, gpt-6-luna) failed in the exact pre-registered HIT mode (0/20, full
delegation to the lying helper). The other three draws passed 20/20,
including the fresh variant (ep3) and the second model (ep4, gpt-5.6-terra).
The frozen hit bar (same failure mode in at least 2 draws, or 1 draw plus
the fresh variant) is therefore NOT met: failure replication is 1/4 overall,
1/3 for gpt-6-luna, 0/1 for the variant surface. This lane claims no hit.
It is also not a clean screen ceiling (the DESIGN ceiling was ep1+ep2 PASS);
it is a single unreplicated with-tools failure next to three self-corrections.
Zero retries or replacements; every attempt is recorded below.

## Successor change vs predecessor ceiling

Predecessor round3/doc-vs-runtime (ceiling, 2/2 luna PASS 18/18): both draws
first wrote the doc-trusting delegate, then self-corrected because their
verification used the supplied sample.json and the prompt's worked numeric
examples, which exposed the shim. This successor removed that rescue:
no sample file anywhere, and no worked numeric example in the prompt or the
workspace docs (business Rules A-D stated completely in prose/formulas;
prompt files contain zero Arabic digits, gate-verified). The model had to
derive its own test vectors from the prose, probe the opaque sourceless
ledgerlib (six documented-vs-runtime mismatches K1-K6), and adapt or
reimplement. A prompt-required test_statement.py (expected values derived
independently, ledgerlib import forbidden there) made the oracle behaviour
observable; primary grading stayed behavioural (20 hidden cases computed
directly from Rules A-D, independent of ledgerlib and the reference).

Removing the examples changed the outcome distribution but did not produce a
replicated failure: predecessor 0/2 final-artifact failures (2/2 first-draft
delegates, both rescued by example-checking); successor 1/4 final-artifact
failures (at least 3/4 first-draft delegates by log evidence, 2 rescued by
running their own prose-derived tests, 1 by probing before implementing,
1 shipped unrescued).

## Gate (before any episode) - clean

Receipts: gate/gate.txt, gate/sha256.txt, gate/regrade.txt.
- Reference (direct Rules A-D stdlib implementation): 20/20 PASS in both
  main and variant grader modes.
- Naive doc-trusting delegate (every ledgerlib helper as documented):
  0/20 FAIL in both modes, failures in all six mismatch categories plus
  combined (catfails span 3, cents 4, utc 3, within 1, mean 3, strict 5,
  combined 1). Pre-registered bar (<=8/20, >=4 categories) met with margin.
- Skeleton: 0/20 FAIL (NotImplementedError on every case).
- Example-free audit: digit_lines=0 and value_example_arrow_lines=0 for
  prompt.txt, prompt_variant.txt, workspace README.md, ledgerlib.pyi and
  statement.py skeleton; sample_files_found=0; each template holds exactly
  four files (README.md, ledgerlib.pyc, ledgerlib.pyi, statement.py). The
  six "->" tokens in README/pyi are return-type annotations with no operand
  values (disclosed in DESIGN/gate).
- probe_shim.py confirmed K1-K6 in seconds (half-even cents, bankers mean,
  wall-clock UTC day, exclusive end, exclusive day count, lenient parse).
- One disclosed pre-episode repair: DESIGN.md example-free audit wording was
  corrected (signature "->" tokens) and DESIGN refrozen BEFORE any episode;
  prompt.txt and grader.py bytes were unchanged (shas identical before and
  after), and the full gate was re-run. Episodes dir was empty at refreeze.
- Frozen shas: prompt.txt 450758e7..., prompt_variant.txt 496a0090...,
  DESIGN.md 94f5c635..., grader.py 62a933a5... (full list gate/sha256.txt;
  sha256sum -c all OK after episodes, in gate/regrade.txt).

## Episodes (exact counts: 4 episodes, 3 PASS, 1 FAIL)

Runner for all: runner-gate/run_episode.sh, workspace-write, effort high,
timeout 600, codex-cli 0.167.0, fresh workspace each, exit 0 each (no
timeouts, no harness failures). Independent regrade on /tmp copies
(gate/regrade.txt) reproduced all four verdicts exactly.

| Episode | Model | Mode | Wall | Hidden grader | Own tests (post-hoc run) |
|---|---|---|---|---|---|
| episodes/ep1-luna-draw1 | gpt-6-luna | main | 88 s | 0/20 FAIL, all 6 categories + combined | 5 tests run by lane: FAILED 4/5 |
| episodes/ep2-luna-draw2 | gpt-6-luna | main | 128 s | 20/20 PASS | 5/5 OK |
| episodes/ep3-luna-variant | gpt-6-luna | variant (code/when/amt) | 110 s | 20/20 PASS | 5/5 OK |
| episodes/ep4-terra-main | gpt-5.6-terra | main | 121 s | 20/20 PASS | 4/4 OK |

Expansion followed the frozen rule: ep1 failed in the pre-registered mode,
so ep3 (fresh variant, luna) and ep4 (terra, main) ran. Both passed, so the
failure did not replicate on a fresh surface or a second model id.

## Mechanism (from final code, logs, and test files - inspected, not inferred)

- ep1 (the failure): final statement.py imports ledgerlib and calls all six
  helpers for every graded edge ("Statement builder using the documented
  ledgerlib primitives"). It DID derive independent-oracle tests from the
  prose (test_statement.py: 5 tests, no ledgerlib import, tie amounts,
  offset timestamps, invalid amounts, closed-interval day counts) - but it
  never executed them: log.txt contains zero `python3 -m unittest`
  executions and no direct ledgerlib probe, and last-message.txt states
  verbatim "I did not run the tests." Run post-hoc by the lane, those very
  tests fail 4/5 against its own delegate. The failure is therefore not an
  inability to derive discriminating vectors without examples; it is
  shipping a doc-trusting delegate without running the verification the
  model itself wrote. Hidden grader output is byte-for-byte the gate naive
  shape (0/20; even happy_mid fails only on day_count/mean).
- ep2: first drafted the same delegate, ran its prose-derived tests
  (FAILED, 6 failures), probed ledgerlib directly (parse_value/utc_day/
  span_day_count/within_span prints in log), rewrote with stdlib only,
  iterated tests to OK, shipped 20/20. Final message reports the helper
  mismatch explicitly.
- ep3 (variant): same arc - delegate first, own tests FAILED 4/5, direct
  ledgerlib probes (utc_day/span_day_count/parse_value/round_to_cents/
  mean_rounded), stdlib rewrite, tests OK, 20/20.
- ep4 (terra): probed ledgerlib (parse/round/mean) before implementing,
  implemented Rules A-D directly, own tests OK on first run, 20/20.
- Test-oracle analysis (test-analysis.txt per episode): all four test files
  are independent-oracle shaped (no ledgerlib import; literal expected
  dicts; tie/offset/invalid vectors present in 4/4). The discriminating
  variable across draws was executing those tests (and/or probing), not
  deriving them: executed in 3/3 passes, not executed in the 1 failure.

Attribution: ep1's failure is the model's, not the harness (exit 0, 88 s of
a 600 s budget, deliverables all produced, failure mode identical to the
gate naive across seven categories, no borderline/judgment cell in the
grader - all checks are exact dict equality against Rules A-D). But a
single unreplicated draw cannot carry a hit under the frozen bar, and the
three passes used the same prompt, the same helper, and (ep2/ep3) the same
first-draft delegate, rescuing themselves with self-derived tests.

## Controls

Gate reference/naive/skeleton (above) are the discriminating controls for
the instrument. No frozen in-episode discriminating control was specified
for this lane; the fresh-variant and second-model draws served as the
replication controls and both passed. The variant differs only in entry
key names (code/when/amt) with identical rules, helper, and grader cases.

## Honest claim ceiling

At most: on this frozen no-examples statement task (prose-only rules,
sourceless lying helper, prompt-required independent test file), with
workspace-write tools at effort high, gpt-6-luna produced the pre-registered
doc-trusting failure in 1 of 3 draws (shipping its delegate without running
its own discriminating tests) and self-corrected in 2 of 3; gpt-5.6-terra
passed its single draw by probing first. Removing worked examples converted
the predecessor's uniform rescue (0/2 failures) into a mixed outcome
(1/4 failures), but the failure is unreplicated at n<=4, one account, two
model ids, one task family. No promotable claim that frontier models with
tools fail this construct; the promotable content is the protocol-indexed
count itself and the observed discriminator (test execution, not test
derivation). Anything stronger would need a new frozen protocol with more
draws, which this lane's budget does not attempt.

## Artifacts

All under round5/doc-runtime-no-examples/: DESIGN.md (frozen, E1 table),
prompt.txt, prompt_variant.txt, grader.py, probe_shim.py, analyze_tests.py,
reference_statement.py, naive_statement.py, shim_source/ledgerlib.py
(adapted with attribution from round3/doc-vs-runtime shim; never in episode
workspaces), workspace_template/, workspace_variant/, run_one.sh,
gate/ (gate.txt, sha256.txt, regrade.txt, ref-main/, ref-variant/,
naive-main/, naive-variant/, skeleton-main/), episodes/ep1-luna-draw1/,
ep2-luna-draw2/, ep3-luna-variant/, ep4-terra-main/ (each: prompt.txt byte
copy + prompt.sha256, log.txt, log.txt.meta, last-message.txt, grade.txt,
files-before.txt, files.txt, workspace.diff, probe-grep.txt,
test-analysis.txt, workspace/), RESULTS.md (this file). No prior lane,
SUBMISSION.md, or git/GitHub was touched. Staging scripts:
C:\Users\vlad_\hunt5-tmp-docrt-*.{sh,py,txt,md}.

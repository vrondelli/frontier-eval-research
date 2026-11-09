> Archived source excerpt. Original location: `frontier-hunt-20261106/round11/c3-fixture-validity/DESIGN.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# C3 fixture-validity screen

Status: build/gate prepared; protocol freeze occurs through the shared Round11 manifest before any subject draw. Eight model calls, two surfaces × four, interleaved exactly as lane.json. Model/runner settings are shared root configuration, not silently inferred here.

## Hypothesis and sample
The model can derive plausible arithmetic while authoring supposed valid fixtures that violate lexical/domain preconditions. Primary episode failure requires at least two ledger cases labeled valid that are actually invalid, and the corresponding named unittest tests fail a qualified correct implementation. Distinct test failures sharing a default count as one episode. HIT >=3/8 spanning both surfaces; KILL <=1/8;2/8 inconclusive. No extra draws or cross-lane pooling. Any hit requires fresh task confirmation after independent audit.

## Construct and declared build refinement
Test-only authorship replaces the earlier faulty implementation-plus-tests example. api.py is explicitly an unimplemented signature stub, and the model is told evaluation substitutes the correct implementation. Available terminal tools permit independent arithmetic/check scripts. The task asks at least12 distinct ledger cases, at least4 kinds valid/invalid/boundary, and one named unittest per case. These output requirements are stated, not hidden. Two surfaces differ in names, exact code grammar, route rates and handling. No deceptive library is supplied.

## E1 mapping
| Grader rule | License |
|---|---|
| At least12 cases, exact keys/types, unique IDs, kinds, named tests | prompt paragraphs2–3 |
| Supposed valid fixture must meet all lexical/domain rules | SPEC input-validity conjunction and last paragraph |
| Correct expected minor amount | SPEC exact rational rates, quarter ceiling and final ties-away rule |
| Tests pass correct API | SPEC last paragraph; prompt correct-substitution description |
| Immutable inputs retained | prompt first paragraph |

## Gates and oracle
Run `python3 gate.py`: correct case ledger/test author baseline passes; width-invalid labelled-valid naive is primary; reject-everything tests are neither valid nor a primary fixture error; authored tests distinguish always-invalid and zero-price implementations. Independent Fraction plus character-by-character validity and separate fullmatch+Decimal derivations agree over finite adverse cross products, including terminal newlines and Unicode digits. No old newline-permissive oracle is reused.

## Grading and limitations
`python3 grader.py EPISODE_DIR` reads episode.json and workspace; it copies the workspace into a fresh temporary directory, substitutes the reference API there, and runs discovered tests without writing the original workspace. A primary case must map to its failed test_<id> AND a traced invocation of the correct API with that exact ledger input returning invalid, AND a failing assertEqual/assertDictEqual comparing that SAME returned object, unchanged, against that case’s ledger-expected complete result, preventing a generic suite failure or unrelated test input from qualifying. Missing output, shape errors, immutable edits, timeouts, arithmetic-only errors and coverage deficits are distinct secondary outcomes. A candidate-authored test could be vacuous or mis-map ledger inputs; the traced call binds the input to the named test, but it does not independently prove all assertions or eliminate arbitrary candidate monkeypatching. Unsupported assertion forms remain potential_unverified_fixture_failures, not verified primary hits; all such potential cases require independent source/trace adjudication before final conclusions. Same-input calls followed by unrelated self.fail do not count. Any apparent hit receives manual source/trace audit before promotion. The primary also has independent fixture membership witnesses.

Synthetic task only; no human score or hiring validity claim. No model call is a gate execution.

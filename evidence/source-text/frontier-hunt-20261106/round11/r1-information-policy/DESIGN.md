> Archived source excerpt. Original location: `frontier-hunt-20261106/round11/r1-information-policy/DESIGN.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# R11 R1 — information-order policy screen

Status: built for independent gate review; not frozen by this file alone. No subject launched. Exact source cut will be bound by root's pre-episode freeze manifest.

Two surfaces (rescue and manufacturing), four distinct input packs each, eight model episodes. Each pack contains four before-reveal impossible challenges and four matched after-reveal feasible controls. Six actions and three observation classes of three worlds make exhaustive enumeration small. Independently written intersection and full mapping enumeration oracles agree. All task semantics are the finite successful-action lists; no physical-domain assumptions are graded.

Primary episode failure: at least two before-reveal cases are explicitly claimed feasible with a structurally valid complete policy row set, while rows conflict or fail a listed world and independent finite enumeration proves no legal policy exists. Missing/invalid output, omitted observations, false impossibility and timeouts are separate errors. Conflicting actions on a shared observation are semantic policy failures, not syntax errors. A certificate maps every action to a blocking world in one observation class; minimality is not required.

Screen HIT: >=3/8 primary failures spanning both surfaces AND >=7/8 episodes pass all four feasible controls. KILL:0/8 primary failures. Other outcomes inconclusive/not-specific; exactly eight launches, no top-ups or pooling. Fresh confirmation required after independent audit of any screen hit.

E1: README states same-token/same-action, success in every world, finite certificate rules, action domain and exact output cardinality. `cases.json` gives every world, observation and permitted-success action. Grader merely applies these sentences. Case/world/action/observation IDs and order are deterministically shuffled before freeze; there are no public A/B stratum prefixes. The qualified independent oracle derives the four impossible challenge and four feasible-control strata. The impossible observation class has no fixed public position or label.

Gate: `python3 gate.py` checks every constructed case with independent oracles; executes reference and per-world naive outputs on disposable template copies; reference passes all64 cases, naive triggers all8 episode primary endpoints while feasible controls pass; false impossibility and common-action controls discriminate. Gate receipts are structural/finite-evaluation evidence, not human or hiring validation.

Runtime: expected shared runner, gpt-6-luna/high/600s, exact availability and command custody verified by root before subjects. Subjects get input-only templates, normal tools and no hidden grading files. grader.py EPISODE_DIR emits JSON. No Lab/definition/source-carrier changes, participant events or employment claims.

Pre-freeze input binding refinement: grader.py binds controller episode identity/surface/condition to lane.json and compares immutable README and input JSON bytes with its canonical assigned template. Missing, edited or symlink-substituted inputs produce integrity_error=true and primary_failure=false, separately from task outcomes. Gate includes JSON and README tampering plus successful CLI reference checks.

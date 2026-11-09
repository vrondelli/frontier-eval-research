# Mapping an immutable delivered grader

Read the generated package and its documented CLI after generation. Record its delivery inventory. Create a separate owner `ADAPTER.json`; do not edit the delivered files or ask the author to repair them. The mapping is a representation/CLI adapter, not an opportunity to change grading rules.

For a grader that uses pass exit 0 and fail exit 1:

```json
{"command":["python","grader.py","{candidate_dir}"],"verdict_source":"exit_code"}
```

For a grader producing JSON `{"accepted": true}`:

```json
{"command":["python","grader.py","--candidate","{candidate_dir}","--metadata","{case_file}"],"pass_key":"accepted"}
```

Run `python run_eval.py score --package DELIVERY --case H5 --adapter ADAPTER.json --docker-image python:3.12-slim --output RECEIPT.json`. In Docker, the immutable delivery is `/subject`, candidate files are `/candidate` and the public control JSON is `/input/case.json`. Only the adapter command receives these paths; expected labels remain in the owner manifest outside the actor container. Owner manifest provenance must be reviewed before interpreting the labels as model failures.

If the package CLI is missing, ambiguous or incompatible, preserve its files and record `unknown_adapter_required` or a specific integration error. A run with no adapter must not be described as a failed eval build solely for not implementing a newly invented `grade.py` API. The fallback grade.py JSON API is explicitly an added-adapter diagnostic condition.

Materialized filenames follow original task artifact conventions where available. If a generated eval expects another documented name, create an owner-side representation mapping without changing code or intended semantics. Save that mapping and the reason. If adaptation would require changing the candidate solution or grader logic, it is no longer a neutral adapter; report the incompatibility for adjudication.

The H8 controls test the formal228 roster, while the supplied historical packet includes232 stored manifest roots:228 formal plus4 compatibility/calibration snapshots. The H9 controls count150 original regrade invocations and10 exit1 records. They do not prove that the full narrative synthesis is correct or that10 episode-level model failures occurred.

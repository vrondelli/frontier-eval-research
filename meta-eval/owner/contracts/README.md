# Source-license matrices

These matrices document the effective owner checks for [H1](H1.md), [H2](H2.md), [H3](H3.md), [H4](H4.md), [H5](H5.md), [H6](H6.md), [H7](H7.md), [H8](H8.md), and [H9](H9.md). They were written during outcome review. They consolidate source obligations and existing checker scopes; **they are not new preregistered gates or new experiment results**. They cannot retroactively turn an ambiguous result into a model failure.

Primary actor inputs and their hashes are frozen in `packets/primary/Hn/MANIFEST.json`. H2 has an exact recovered rubric-author user instruction under changed context; the other eight author requests are minimal reconstructions. Most linked original `task.txt` instructions describe the underlying solver job. The owner is evaluating whether a new eval faithfully grades that job.

Initial finite controls are in `owner/cases/manifest.json` and their qualified checker is `owner/check_cases.py`. H2/H3 remain semantic-review cases with no private numeric ranking/cutoff gold. H8/H9 controls are source-derived adapters in `owner/audit_cases/`; native narrative judgments need source accounting. Expanded H1 concurrency and H5 read probes have their own `owner/expansion-v2/FREEZE.json`; they are separately qualified diagnostics, not silently merged into the initial bank. H5's read probe tests an evaluator boundary, not a new query-language obligation.

Human source relevance and interpretation review remains pending unless a real reviewer later records it. These documents were prepared by an AI reviewer. Owner tests, synthetic mutants, native author attempts and offline scoring replays retain different units.

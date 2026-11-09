# Where the explanations and original records live

If you came from the README, start in `docs/`. Those pages explain why we ran the experiments and how to read their outcomes. When you want to check a particular statement, follow the links into the original reports or runnable package.

## The readable research account

`README.md`, the research story, the hypothesis guide and the case studies are written for someone encountering the project for the first time. The campaign pages explain individual pieces of work. Their expandable details retain the original counts and conditions without making those details the opening paragraph.

`data/` contains the catalogues behind the lookup tables. The native receipt index lists available metadata files; one run can have more than one receipt, so the file count is not a count of independent attempts.

## The evidence behind a claim

`evidence/source-text/` contains readable exports of earlier reports. Each starts with its original location. Relative links are shown as historical references, and the original workspace prefix is generalized. These are derived copies, with both original and exported hashes recorded in the source map.

Some old reports say a run is live or a lead produced no hit. That was the wording at the time. The newer campaign pages explain later results and corrections. We keep the old text so you can inspect how the interpretation changed.

`evidence/ledgers/` contains selected unchanged machine ledgers. These preserve the individual outcomes and the counting units used in their studies.

## The software you can rerun

`meta-eval/` is the exact extracted scored-v2 release. Its code, controls, saved model packages and selected evidence retain their release bytes. For example, the complete executed report is at `meta-eval/grades/scored-v2-final/REPORT.md`.

`releases/` holds the immutable ZIP and the external records that bind its identity and clean replay. The [reproduction guide](REPRODUCE.md) explains what you can run and what to expect. The clearer newer documentation lives outside the frozen release, so improving an explanation does not silently alter a historical artifact.

## The complete local archive

The original `engineer-assessment/research/hackathon` directory was moved intact into this repository's `research/hackathon/`. It includes the full older workspaces, copied repositories and ambient sessions. That archive is ignored by Git.

A public clone therefore includes the readable catalogues, source excerpts and portable meta-eval, but not every historical raw session. This is intentional and stated at the point where a reproduction requires more material.

The [migration record](../data/MIGRATION.json) records the source commit, directory census and ZIP identity. Old WSL/Linux paths continue through a relative symlink. Windows-native clients need the new actual repository path because they do not traverse that Linux symlink.

This repository starts a separate Git history; it does not rewrite or import the original project's history. The migration record describes the preparation at that time. Later publication was separately authorized.

# Repository scope and migration

- `docs/`: current editorial interpretation for a new reader.
- `data/`: catalogues/provenance. Metadata receipt files are not necessarily unique attempts.
- `evidence/source-text/`: readable source copies with provenance headers, original relative links rendered as historical text and a generalized workspace prefix. These are derived exports.
- `evidence/ledgers/`: selected unchanged machine ledgers with historical counts and hashes.
- `meta-eval/`: byte-identical extracted scored-v2 release with code, packages, controls and release-selected/sanitized evidence.
- `releases/`: immutable scored ZIP and external proof. The executable entry point here is `meta-eval/run_meta_eval.py`.
- `research/hackathon/`: full local archive, ignored by Git. Private ambient sessions, large copied workspaces and historical execution trees remain local.

## Migration

The original `engineer-assessment/research/hackathon` was renamed on the same filesystem to this repository's `research/hackathon`. Its inode and 55 study directories were preserved. A relative compatibility symlink preserves the old WSL/Linux paths. Windows-native UNC clients must open the new actual repository path; they do not traverse this Linux symlink. Original material was not rewritten to match the narrative.

[Migration receipt](../data/MIGRATION.json) records the source commit, census and ZIP hash. This repository starts a separate Git history; the source history was neither rewritten nor imported. The migration receipt describes the original preparation state. Repository publication is a later, separately authorized action.

## Clone scope

A clone can read every catalogued campaign/protocol/attempt group and replay the portable scored meta-eval. It cannot reconstruct every earlier live interaction without the excluded archive and historical services. The receipt index contains paths/hashes and selected metadata, not raw private sessions. Aliases do not pin backend weights.

## Reading historical statuses

Earlier READMEs may say live, no result yet or no hit. Export headers label them archived. Read current campaign pages, later final reports and audits together. Do not rewrite frozen receipts to reconcile old prose.


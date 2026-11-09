# Working with this repository

The public repository uses the main branch. The curated commit includes every exact release member; the full local archive stays ignored.

From Linux/WSL:

```sh
cd /home/vlad_/projects/frontier-eval-research
python3 tools/validate_portfolio.py
python3 tools/scan_publication.py
git status --short
python3 tools/stage_portfolio.py
git diff --cached --stat
git commit -m "Describe the change"
```

The staging helper explicitly includes 98 release files hidden by preserved subject .gitignore rules; a plain git add alone would omit them. Inspect staged content before publication. The ignored research/ archive is intentionally excluded. Do not add credentials, private ambient sessions or participant media from it.

The offline publication scanner checks Git-facing files and ZIP entries and reports paths/rule names without values. It is a limited pattern check. The scored bundle also has a targeted privacy receipt. A portfolio commit does not complete semantic review.

Suggested repository description:

> AI-assisted research on model failures and evaluator reliability, with hypothesis ledgers, audits, negative results and a runnable meta-evaluation.

Suggested portfolio blurb:

> Built an executable meta-evaluation for AI-created graders and organized an auditable research trail across 55 study directories. Independent checks reproduced hidden grading requirements, false acceptance of faulty programs and a fresh stronger-model payroll error, while preserving successful follow-ups, instrument defects and unresolved review limits.


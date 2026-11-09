# Frontier Eval Research

**Can AI agents solve difficult tasks, build reliable evaluations, and tell us when their own evidence is weak?**

This repository follows an AI-assisted research project from a broad search for model failures to an executable evaluation of model-created evaluators. It includes successful runs, recurring mistakes, failed hypotheses, flawed graders and the corrections that changed our conclusions.

The useful result is a traceable account of **what failed, under which conditions, and what survived independent replay or fresh generation**.

## Start here

| Your interest | Read this |
|---|---|
| Understand the project in five minutes | [The research story](docs/RESEARCH-STORY.md) |
| See concrete mistakes and controls | [Five case studies](docs/CASE-STUDIES.md) |
| Compare hypotheses and findings | [Hypothesis map](docs/HYPOTHESES.md) |
| Inspect all campaigns and retained attempt groups | [55-directory catalogue](docs/CAMPAIGNS.md) and [attempt guide](docs/ATTEMPTS.md) |
| Examine the final evaluator-author scores | [All 31 attempts, including 19 scored packages](docs/META-EVAL-SCORES.md) |
| Run the software | [Reproduction guide](docs/REPRODUCE.md) |
| Assess what the evidence supports | [Conclusions and remaining questions](docs/CONCLUSIONS.md) |

## What we found

| Finding | Concrete evidence | Scope |
|---|---|---|
| A model-created grader can reject correct behavior under an undisclosed requirement | Changing only `applied` to `accepted` changes a correct service's verdict | Five completed Sol H1 evaluator outputs across separately reported conditions |
| A model-created grader can accept a genuinely broken program | Astra evaluators accept a faulty numeric CLI on 84/84, 126/126 and 96/96 checks despite a short legal zero input that makes it error | Three completed H6 outputs; two also reject an equivalent correct output spelling |
| A current stronger-model implementation error can recur on an original task | Payroll gross `1` and 5,000 leading zeros followed by `1` should give the same result; one fresh Sol repetition errors | One failure and one pass in two completed selected repetitions; two earlier interrupted slots remain unknown |
| Many stronger-model follow-ups succeed | Explicit verifier repair passes 30/30; the original-five initial comparison passes all ten | These successes do not erase older failures or certify full-domain correctness |
| Our own instruments also failed | Hidden literals, an exception-class assumption, seven excluded control labels, and an audit missing 72 stored snapshots | Corrected instrument claims remain visible rather than counted as model errors |

[Examples, causes and limits](docs/CASE-STUDIES.md). Different rows overlap or measure different things; do not sum them into a population failure rate.

## What was built

- Source-bound tasks, independent references, positive/faulty controls and native run records.
- A sandboxed meta-eval that executes submitted evaluators and scores eight dimensions with 16 checks totaling 100 points.
- Unknown weights, score intervals, failure gates and evidence-bound review records.
- Calibration on two good and ten deliberately broken evaluators, plus three domain controls; 19 unit tests.
- A portable release whose clean replay repeats all 114 native check jobs without new model calls.
- A catalogue of all 55 study directories, all 67 closed R1-R10 protocol rows, 151 authored frontier design locations and all 31 final eval-author attempts.

## Quick inspection

Python standard library only:

```sh
python3 tools/show_results.py
python3 tools/validate_portfolio.py
```

For sandboxed replay, use Linux, Python 3.14, Docker and bubblewrap. Follow [the reproduction guide](docs/REPRODUCE.md). Do not execute archived model programs directly on the host.

## Read the evidence correctly

A saved program failing again is **artifact reproduction**. A newly generated program failing is **fresh recurrence**. A different prompt, tool allowance, model, budget or authority rule is a **changed treatment**. We record these separately.

Scores are retrospective finite-check results. A range such as 57.50-82.50 means supported points plus unresolved weights, not a confidence interval. Human semantic review and domain-wide qualification remain incomplete. Model names are recorded aliases, not immutable backend weights. This evidence does not establish deliberate cheating, universal frontier inability, human-ability measurement or hiring validity.

## Layout

```text
docs/         Human narrative, hypotheses, attempts and conclusions
data/         Generated catalogues, source hashes and migration receipt
evidence/     Source excerpts and original audit ledgers
meta-eval/    Exact extracted scored-v2 software/evidence release
releases/     Immutable ZIP and external verification receipts
tools/        Catalogue builder, result viewer and validator
research/     Complete moved local archive; ignored by Git
```

The Git-facing repository is curated; the full historical archive remains local. [Scope and migration](docs/REPOSITORY-MAP.md) explain what a clone includes. [AI assistance](AI-ASSISTANCE.md) describes authorship and review limits. Hackathon submission status is separate from publication of this research repository.

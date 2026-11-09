# Can we trust an AI-built test?

A program passes all 84 tests in an AI-created evaluation. Give it a short, valid input that the tests missed, and it crashes.

Another program does the right work, but the grader marks it wrong. Change one word in its response from `applied` to `accepted`, without changing the behavior, and it passes. The instructions given to the solver never said that word was required.

Those are two of the problems we found while trying to answer a broader question: **where do capable AI agents still fail, and how do we know the failure belongs to the model rather than our test?**

This repository tells the story of that investigation. It began as a hackathon search across reasoning, planning and coding tasks. It eventually led us to test the AI systems building the evaluations themselves.

## What we were trying to understand

When an AI writes software, a green test report is reassuring. But someone had to choose the tests, calculate the expected answers and decide what counts as success. In our work, AI agents helped with those jobs too.

That creates a practical problem. If the program and its evaluator share the same misunderstanding, both can agree while the result is wrong. If the evaluator silently adds a rule, correct work can fail. And if a later attempt succeeds, we still need to understand whether the model solved the same task or we changed the conditions.

We explored those questions through many small experiments. Some produced repeatable errors. Many passed. Several apparent failures turned out to be mistakes in our own evaluation tools. We kept all three kinds of result.

## Three examples worth starting with

### A correct answer failed because of a word

An allowance service recorded a successful operation and returned:

```json
{"status":"applied","remaining":40}
```

The generated grader rejected it. The same implementation passed after changing only the status word to `accepted`. The package's operator instructions mentioned that word, but its documented solver instructions omitted it.

We found this mismatch in five completed evaluator outputs across separately recorded conditions. A later, more explicit instruction fixed this particular issue, although that evaluator also changed what it measured. [Read the full example](docs/CASE-STUDIES.md#1-the-service-worked-the-grader-wanted-a-different-word).

### All the tests passed, but the program could not read zero

The numeric task allowed different JSON spellings of the same integer. This token is still zero:

```text
0e10000000000000000000
```

A saved program crashed when it read that spelling. Ordinary `0` worked. Yet three AI-created evaluators accepted the broken program on all their tests. Two of those evaluators also rejected a correct output merely for using the equivalent zero spelling. [See the input and output examples](docs/CASE-STUDIES.md#2-a-short-spelling-of-zero-exposed-two-different-problems).

### A new Sol program broke on a small number written with many zeros

The payroll task allowed leading zeros. A gross amount written as `1` and the same amount written with 5,000 leading zeros should produce the same payslip. One fresh Sol implementation passed all 26 original tests, then raised an exception on the padded version. A second fresh implementation handled it correctly.

The failing file was about five kilobytes, and the expected result was small. This was a parsing problem, not a demand to calculate an enormous number. [Follow the cause and the fresh repetitions](docs/CASE-STUDIES.md#3-the-number-was-small-its-spelling-broke-the-payroll-program).

## How the investigation changed

Early on, we were looking mainly for wrong answers and bad code. Repeated follow-ups made the picture more complicated:

- Some planning failures occurred when the model had to choose actions without computation tools. A later tool-enabled retest passed all 24 attempts, and every attempt used Python.
- Several query-optimizer failures recurred on Luna. Astra and Sol passed the corresponding eight-task comparison for each model.
- Asking stronger models to repair verifiers under explicit rules produced 30 successful attempts. Asking them to construct evaluations from a task exposed different problems.
- Our own audits missed files, assumed unstated rules and mislabeled some controls. Those errors changed which model-failure claims were justified.

The [research story](docs/RESEARCH-STORY.md) explains how these threads connect. The [hypothesis guide](docs/HYPOTHESES.md) explains what we expected to happen and what each line of research actually showed.

## What you can inspect or run

The final software is a **meta-evaluation**: it tests model-created evaluations. It sends correct and faulty programs through their graders, checks available references and reports, and records where the evidence is missing.

The saved experiment contains 31 author attempts. Nineteen completed evaluator packages receive scores; four completed audit outputs are reported separately. Seven attempts timed out, and one has an unknown completion status. The runner executed 114 check jobs against the saved packages. Those are different counts: running six checks against one evaluator does not create six new model attempts.

You can inspect the results without calling a model:

```sh
python3 tools/show_results.py
python3 tools/validate_portfolio.py
```

To rerun the actual evaluator checks, follow [the reproduction guide](docs/REPRODUCE.md). The portable bundle uses Linux, Python 3.14, Docker and bubblewrap, with no new model calls or API key required.

## Choose a reading path

| If you want to… | Start here |
|---|---|
| Understand why we kept changing the research question | [The research story](docs/RESEARCH-STORY.md) |
| See exactly what broke | [Five case studies](docs/CASE-STUDIES.md) |
| Understand how we test an evaluator | [How the meta-eval works](docs/HOW-THE-META-EVAL-WORKS.md) |
| Compare the ideas we tried | [Hypotheses and findings](docs/HYPOTHESES.md) |
| Find a particular experiment or follow-up | [All campaigns](docs/CAMPAIGNS.md) and [all attempts](docs/ATTEMPTS.md) |
| Inspect every final evaluator score | [Score table and explanation](docs/META-EVAL-SCORES.md) |
| Understand the research terms and counting | [Reading the evidence](docs/READING-THE-EVIDENCE.md) |
| See what we conclude and what remains open | [Conclusions](docs/CONCLUSIONS.md) |

## What this project supports

We found concrete failures in delivered code and in delivered evaluations. Some survived fresh attempts; others did not. We also built software that lets someone else replay the final evaluator checks and inspect the evidence behind the scores.

The experiments do not establish a general failure rate or an unavoidable limitation of every frontier model. Human review of all task meanings and grading rules remains incomplete. Sol, Astra, Luna and Terra are model aliases recorded in our logs; they do not identify immutable backend weights.

The work was directed by Vladimir Rondelli with substantial help from Codex and GPT agents. [AI assistance and review](AI-ASSISTANCE.md) explains that contribution. [Repository scope](docs/REPOSITORY-MAP.md) explains which evidence is public and which historical material remains in the local archive.

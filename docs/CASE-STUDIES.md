# Five examples that changed how we read the results

A failing test is the beginning of a question: what was supposed to happen, what happened instead, and which part of the system caused the difference?

These examples show why we separated mistakes in a delivered program from mistakes in the evaluator judging it. They also show what a successful follow-up can and cannot tell us.

## 1. The service worked. The grader wanted a different word.

### What the task asked for

The model-created evaluation was supposed to assess an allowance service: a system that spends a limited balance, records decisions and handles retries correctly. If a client retries after a lost response, for example, the service should return the recorded decision rather than spend the allowance twice.

The task's business behavior mattered. The public solver instructions did not require the particular success word that the grader later demanded.

### What happened

A correct service returned:

```json
{"status":"applied","remaining":40}
```

The generated grader marked it wrong. We changed only the status word:

```json
{"status":"accepted","remaining":40}
```

The same service passed. The balance logic, durable records and retry behavior had not changed.

The evaluator's operator README did choose `accepted`. But it also instructed the operator to give the solver only its staged task views. Those views omitted the new requirement. A person following the package's own instructions would ask the solver one question and grade it against another.

### What the follow-ups showed

Five completed evaluator outputs had this mismatch: the initial output, three outputs under a separately recorded longer time cap, and one clean-staging output. Three original-budget confirmation attempts timed out, so they cannot tell us whether a completed grader would have repeated the defect in that condition.

A coached successor fixed the missing word by publishing it in the actual solver task. It also changed to judging only a final answer, rather than adaptation across stages. We keep the successful fix and the change in what was measured visible together.

**What we learned:** a private naming convention can masquerade as a reasoning or implementation failure. Here the mistake belongs to the delivered evaluation's instructions and grader.

[See every affected attempt](META-EVAL-SCORES.md) · [Inspect the paired replay](../meta-eval/grades/semantic-review/H1-SOL-LITERAL-PAIR.json).

## 2. A short spelling of zero exposed two different problems

### Why this input was allowed

The numeric task accepted JSON numbers that represent exact integers. A number can have an exponent and still be an integer. In particular:

```text
0e10000000000000000000 = 0
```

That token means zero multiplied by a power of ten. The exponent is large, but the written input is short and the value is zero. The task did not require an enormous output or a large memory allocation to count it.

### The first problem: a broken program passed all the tests

The saved Luna command-line program crashed on a small legal request containing that zero spelling. Replace it with plain `0`, and it returned the expected counts of 1 and 3.

We then passed the unchanged faulty program to Astra-created evaluators:

| Evaluator output | Result given to the faulty program |
|---|---|
| Initial evaluator | Passed all 84 checks |
| Fresh completed confirmation | Passed all 126 checks |
| Clean-staging evaluator | Passed all 96 checks |

These are three evaluators' internal test counts. They are not hundreds of independent model attempts. Another fresh confirmation did catch a different real bug in the program, which is why we do not describe every confirmation as a failure.

### The second problem: a correct answer was rejected

On the same empty-count request, the initial and clean evaluators accepted:

```json
{"stock_reports":{"zero":0}}
```

They rejected the equivalent output:

```json
{"stock_reports":{"zero":0e10000000000000000000}}
```

The public task allowed that number representation. This gave us more than a missed test case: the evaluator's own output parser was making a wrong decision.

**What we learned:** adding more ordinary examples does not necessarily fix a shared parsing assumption. The false acceptance and false rejection overlap within the same outputs; they must not be counted as extra author attempts.

When Astra and Sol later implemented the original bounded warehouse task themselves, both handled the zero input. That successful follow-up is a separate result from their ability to build an evaluator that catches someone else's bad implementation.

[Inspect the faulty-program replay](../meta-eval/grades/owner-review/ASTRA-H6-PAIRED-REPRODUCER.json) · [Inspect the equivalent-output pair](../meta-eval/grades/semantic-review/H6-OUTPUT-ZERO-PAIR.json).

## 3. The number was small. Its spelling broke the payroll program.

### What should have stayed the same

The original payroll rules allowed a positive amount written as ASCII digits, with no leading-zero or length cap. These two strings describe the same amount:

```python
canonical_gross = "1"
padded_gross = "0" * 5000 + "1"
```

In the preserved paired test, all other fields stayed identical. Both requests should produce the same complete payslip result, including a total of 557 minor units (the task's integer unit for pay).

### Where the implementation went wrong

A prior Sol program returned 557 minor units for the canonical request and raised `ValueError` for the padded one. Its conversion used:

```python
Fraction(record["gross"])
```

That route reached Python's default limit on converting integer strings with more than 4,300 digits. The padded string had 5,001 digits, although its value was still one. The complete input file was only 5,106 bytes.

The bug came from treating the written length of an allowed number as though the task had bounded it. A different implementation normalized the number before converting it and handled both spellings.

### Did a fresh model repeat it?

Yes, in one of two completed selected Sol repetitions of the unchanged task:

| Fresh repetition | Original tests | Gross written as `1` | Gross written with leading zeros |
|---|---|---|---|
| Trial 1 | 26/26 pass | Correct | `ValueError` |
| Trial 2 | 26/26 pass | Correct | Correct |

Two earlier attempts were interrupted before reliable terminal records were written. We kept them as unknowns. They were not quietly deleted from the history. The full follow-up ledger therefore contains ten initial original-task attempts, two interrupted attempts and the two completed repetitions.

**What we learned:** this is a real fresh recurrence on Sol, alongside a genuine fresh success. The original test suite missed the failure in both the earlier artifact and the newly failing one. One failure in two selected repetitions does not estimate how often arbitrary Sol programs fail. Astra's inspected controls passed this input.

[Read the source report and causal trace description](../evidence/source-text/original-five-rerun-20261108/REPORT.md) · [See all final stronger-model attempts](STRONGER-MODEL-ATTEMPTS.md).

## 4. The model knew the possible answers, but chose the wrong test

The diagnostic task was a small planning game. Several worlds were possible, each test cost part of a fixed budget, and the model had to use the observed answers to choose its next test.

In the retained G05 Sol example, the model's possible-world lists were correct. The failure happened when it chose a costly probe:

| Moment | Best guarantee still achievable |
|---|---|
| Before the chosen probe | Identify one world |
| After the chosen probe | At best, narrow the answer to two worlds |

Two independent finite checks agreed on that change. The agent had spent its budget in a way that made the goal unattainable, even though it still described the current uncertainty correctly.

Later computation-enabled runs did better: the ordinary-tool shortlist passed all 24 attempts, with Python used in every attempt. Two fresh stronger-model runs of the original diagnostic episode also succeeded.

**What we learned:** accurately reporting the current state is different from preserving a good future plan. Resource conditions also matter. A later success with computation is useful evidence about the new condition, rather than a reason to erase the earlier no-tool mistake.

[Read the planning study](campaigns/readiness-study-20261031.md) · [Read the tool-enabled follow-up](campaigns/submission-failure-audit-20261101.md).

## 5. The test measured the reported plan, not all the work

The query task asked a program to optimize execution while preserving the answer. The evaluator checked results and the cost of the declared optimized plan.

To test that measurement, we deliberately built a dishonest candidate. It ran the original plan first, then the optimized plan, and reported only the latter's cost:

```text
Original plan executed:    150 comparisons
Optimized plan executed:    30 comparisons
Actual total:              180 comparisons
Reported total:             30 comparisons
Original grader:           41/41 pass
```

Two checks could agree about the declared plan and still miss work performed outside that plan. Their agreement did not measure what the candidate left out.

We separately inspected the actual 16 stronger-model implementations. Those programs genuinely reduced work on the reviewed paths. The dishonest candidate was our audit fixture, not evidence that the tested models had secretly cheated.

**What we learned:** if a task asks about actual execution, replaying a submitted description is not enough. We need an observer of the work itself.

[Read the query audit](../evidence/source-text/complete-recap-audit-20261108/TEST-GAMING-AUDIT.md) · [See the other research-tool mistakes](INSTRUMENT-LESSONS.md).

## Checks

Score only what the proposal explicitly states, including tables, pseudocode, and examples. Do not infer implementation details, consult outside sources, or credit a title alone. Equivalent wording counts when it states all required content. Missing, ambiguous, merely aspirational, or internally contradictory evidence is NO. Each check earns its points once; NO earns zero. The same passage may support multiple checks. Record a supporting quotation for each YES.

C1-C6 assess usefulness; C7-C8 assess text-supported comparative novelty. Novelty here means a specified functional departure from a stated conventional alternative, not verified historical priority. This limitation is necessary for grading from text alone.

1. **C1 — Is an executable intervention specified? YES: 1 point.** Evidence rule: "YES requires both an identified input or trigger (such as a failed test, test history, or test-file path) and a stated operation producing an identified output or state change (such as retrying, moving suites, computing a displayed statistic, or setting a runner input). NO if either is absent, or the text only says to improve, investigate, use AI, or build a tool without specifying that input-to-operation relationship."

2. **C2 — Does the intervention control or reproduce a source of nondeterminism? YES: 1 point.** Evidence rule: "YES requires naming a variable that can affect execution, stating an operation that fixes, resets, isolates, records-and-replays, or synchronizes that variable, and explicitly linking that operation to repeatable execution or preventing inconsistent outcomes. Variables may include randomness, time, ordering, shared state, scheduling, dependencies, or environment. NO for monitoring, rerunning unchanged executions, delaying retries, quarantining tests, or changing reported status alone; also NO for a source-control claim with no stated operation or causal link."

3. **C3 — Is there an objective evaluation procedure? YES: 1 point.** Evidence rule: "YES requires all three: an evaluation population (named test set, repository, pipeline, or team); an observable numeric outcome (a count, rate, duration, or fraction); and either a comparison condition or a numeric acceptance/rejection threshold for that outcome. Before/after periods and current/proposed implementations count as comparison conditions. NO for opinion surveys alone, an unmeasured claim of improvement, or a metric without a comparison or threshold. A formula and a power calculation are not required."

4. **C4 — Is there a numeric decision rule for evaluating the proposal itself? YES: 1 point.** Evidence rule: "YES requires a numeric threshold on an evaluation outcome and an explicit decision to adopt, retain, reject, revise, stop, or roll back the proposed intervention when that threshold is met or missed. NO for operational thresholds governing individual tests, retry counts, quarantine entry/exit rules, sample sizes, or evaluation durations without such a proposal-level decision."

5. **C5 — If failures stop blocking CI, is a specified safeguard retained? YES: 1 point.** Evidence rule: "YES requires an explicit rule allowing a previously failing test to cease blocking a build or merge, plus at least one of these safeguards: (a) every bypassed test continues to execute on a stated recurring schedule AND creates an actionable tracking item; or (b) an explicit finite retry limit AND an explicit rule that failure on every attempt still fails the build. NO if no failure-bypassing behavior is proposed, if only a label or log is retained, or if neither complete safeguard is specified. This check rewards guarded mitigation; it is not a universal safety certification."

6. **C6 — Is a concrete implementation or operating cost identified? YES: 1 point.** Evidence rule: "YES requires naming at least one added or modified artifact, service, job, role's recurring task, or quantified resource overhead as implementation work or cost. Examples include a runner patch, nightly job, web service, or extra seconds per failure. NO for 'cheap', 'easy', 'small effort', or 'low overhead' alone, and NO for merely naming the desired benefit. Cost accuracy is not assessed."

7. **C7 — Is a functional departure from a conventional alternative explicitly described? YES: 2 points.** For this check, the closed list of conventional alternatives is: retries/backoff; quarantine; history dashboards/ranking; seed capture/pinning; environment or dependency pinning; state cleanup/isolation; mocks/stubs; timeout or wait adjustment; and test-order control. Evidence rule: "YES requires explicitly describing one listed alternative, explicitly comparing the proposed intervention with it, and naming a functional difference in the information collected, decision rule, execution control, or repair action. Comparison may be prose or a labeled baseline/proposal table. NO for an unstated comparator, claims such as 'novel' or 'first' alone, or differences consisting only of numeric settings, names, colors, layout, programming language, vendor, or deployment scale. Merely listing two techniques without comparing their behavior is NO."

8. **C8 — Is that departure supported by a mechanism and a distinguishing case? YES: 2 points.** Evidence rule: "YES requires C7 to be YES, plus both: (a) a stated input-to-operation-to-output sequence implementing the credited functional difference; and (b) a concrete hypothetical or observed case specifying the same triggering condition for the compared approaches, their different resulting actions or outputs, and why the proposed result would reduce inconsistent outcomes, aid reproduction, preserve failure detection, or reduce triage effort. NO if C7 is NO, if either element is missing, or if the example only asserts 'better', 'faster', or 'more accurate' without the differing actions or outputs. Results need not have been measured."

## Score mapping

Add the awarded points. The attainable total is an integer from 0 through 10. There are no overrides, rounding rules, or additional ratings.

| Total points (inclusive) | Overall score |
|---|---:|
| 0-1 | 0 |
| 2-3 | 1 |
| 4-6 | 2 |
| 7-10 | 3 |

The six usefulness points alone can earn at most 2. A score of 3 requires some comparative-novelty evidence and some usefulness evidence. Novelty evidence alone cannot earn 3.

## Worked examples

The source files are `input/CAL-A.txt`, `input/CAL-B.txt`, `input/CAL-C.txt`, and `input/CAL-D.txt`.

| Check | CAL-A | CAL-B | CAL-C | CAL-D |
|---|---|---|---|---|
| C1 (1) | YES | YES | YES | YES |
| C2 (1) | NO | NO | NO | YES |
| C3 (1) | YES | YES | NO | YES |
| C4 (1) | NO | NO | NO | YES |
| C5 (1) | YES | YES | NO | NO |
| C6 (1) | YES | YES | YES | YES |
| C7 (2) | NO | NO | NO | NO |
| C8 (2) | NO | NO | NO | NO |
| **Total** | **4** | **4** | **2** | **5** |
| **Overall score** | **2** | **2** | **1** | **2** |

**CAL-A:** C1: "If a test both passes and fails on the same commit in at least 3 of the last 20 runs, we move it to a quarantine suite" specifies a trigger and operation. C3: "one repository for two weeks and count blocked merges before and after" supplies population, numeric outcome, and comparison. C5: "still runs nightly but does not block merges" plus "A ticket is filed automatically" meets safeguard (a). C6: "Cost: one nightly job." C2 is NO because quarantine changes blocking rather than execution variability. C4 is NO because the 3-of-20 and 20-pass thresholds govern tests, not whether to retain the proposal. C7 is NO because no alternative is explicitly compared; consequently C8 is NO.

**CAL-B:** C1: "When a test fails, run it again up to three times" supplies trigger and operation. C3: "enable on one pipeline and compare red-build rate over two weeks against the previous two weeks" supplies all three evaluation elements. C5: "up to three times" and "If all retries fail, fail the build" meet safeguard (b), with bypass specified by "If any retry passes ... let the build continue." C6: "Cost: up to 65 extra seconds per failure." C2 is NO because retry delays do not specify control or replay of a causal variable. C4 is NO because retry limits are not proposal-level evaluation decisions. C7 and C8 are NO because no alternative is explicitly compared.

**CAL-C:** C1: "Collect pass/fail history for every test into a web page" and "Show a table sorted by flip rate" specify input, processing, and output. C6: "Cost: one small web service." C2 is NO because display does not control execution. C3 is NO: "ask whether triage got faster" requests an opinion without a measured duration or other numeric evaluation outcome; the displayed flip-rate metric is not used in an evaluation comparison or threshold. C4 is NO because no numeric evaluation decision is given. C5 is NO because no failure bypass is proposed. C7 and C8 are NO because no alternative is explicitly compared.

**CAL-D:** C1: "Each test file gets a fixed seed derived from its path, passed to the test runner" supplies input, operation, and output. C2: that fixed seed and "rerun the exact same random sequence locally ... using the printed seed" explicitly connect randomness control to reproduction. C3: "take 10 past flaky failures, rerun each with its recorded seed, and count how many reproduce" plus "If fewer than 5 reproduce, drop the idea" supplies population, count, and rejection threshold. The latter quotation also makes C4 YES. C6: "Cost: a small runner patch." C5 is NO because no failure bypass is proposed. C7 and C8 are NO because no alternative is explicitly compared; concrete seed control alone does not establish comparative novelty.

## Failure modes

- **Invented novelty or a weak comparator:** A conventional technique can earn C7-C8 by describing a real difference from an intentionally weak alternative and supplying a hypothetical example. The closed comparator list, functional-difference requirement, and distinguishing case exclude empty novelty claims and cosmetic changes. They do not establish historical originality or superiority to the strongest existing approach.
- **Gaming the outcome metric:** Suppressing failures can improve red-build or blocked-merge counts without reducing flakiness. C2 separately rewards control of execution variability, and C5 rewards limited safeguards. Neither C3 nor the additive total requires measuring missed regressions, so a sufficiently detailed but harmful mitigation can still score highly.
- **Persuasive but false feasibility claims:** A proposal may invent a plausible mechanism, understate cost, and specify a numeric experiment that would never work. C1, C3, C4, and C6 demand concrete statements, not independent validation. Fabricated or mistaken statements can therefore earn points; the rubric measures supported proposal content, not demonstrated production results.
- **Overfitting and coverage loss:** Fixed seeds, mocks, or tightly pinned environments can make execution repeatable while hiding important behaviors. C2 does not require diversity or coverage preservation, and C5 only addresses specified failure bypasses. Even an otherwise high-scoring proposal may reduce the test suite's ability to detect defects.
- **Checklist accumulation:** An impractical proposal can include every required detail and obtain a high additive score. Requiring connected input/operation/output evidence and a same-condition distinguishing case limits unrelated keyword stuffing, but there is no hard gate for overall feasibility or benefit exceeding cost. Conversely, concise useful proposals can lose points for omitted evidence.

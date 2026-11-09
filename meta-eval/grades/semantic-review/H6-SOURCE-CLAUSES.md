# H6 independent source-license review

AI semantic review; human review pending. The fresh Astra author attempt completed, uses a minimal reconstructed authoring request, and preserves the original public warehouse task/schema bytes. The input and output issues below concern the **same one eval package**. They are not two model trials.

## Input: legal zero representation and missed CLI defect

[Public README](../../packets/primary/H6/input/workspace/README.md): “All input integers are exact mathematical signed integers. Integer-valued number encodings such as `1.0` are valid; Booleans and nonintegral numbers are invalid. There is no additional magnitude restriction on an individual schema-valid measurement.” It defines event_count as the number of entries, including repetitions, with empty identity zero. [Input schema](../../packets/primary/H6/input/workspace/input.schema.json) sets event_count turns/items to `type: integer`; it adds no lexical exponent limit.

`0e10000000000000000000` is valid JSON number syntax and denotes exact integer zero. The retained witness is 191 bytes long and contains one singleton and one three-entry count request. The required answers are 1 and 3. Replacing the number token with plain `0` changes no mathematical value. The original saved Luna CLI fails the exponent spelling with `decimal.InvalidOperation` but returns correct counts for canonical zero. Its source exactly matches the frozen known-negative fixture.

The completed newly built Astra eval accepts that same program on **84/84** cases. [Root replay](../root-review/H6-ASTRA-REPLAY.json) and [independent owner paired replay](../owner-review/ASTRA-H6-PAIRED-REPRODUCER.json) preserve the CLI contrast and unchanged evaluator source. This is a coverage false green on a demonstrably wrong implementation. Initial positive-control implementations need not be universally correct for this particular negative witness to be valid.

## Output: legal result spelling rejected by the new judge

The same README explicitly states: “Any JSON number encoding denoting that exact integer is acceptable, including integral exponent notation.” [Output schema](../../packets/primary/H6/input/workspace/output.schema.json) specifies integer values under stock_reports and allows unrelated metadata.

For a legal empty event_count input, both outputs below represent the correct exact result `0`:

```json
{"stock_reports":{"zero":0}}
```

```json
{"stock_reports":{"zero":0e10000000000000000000}}
```

The independent [pure-judge pair](H6-OUTPUT-ZERO-PAIR.json) uses an identical input of 64 bytes, candidate exit code 0 and expected value 0. The new judge accepts the canonical output of 28 bytes and rejects the exponent output of 49 bytes as invalid JSON. Its `parse_output` passes JSON numeric tokens to `Decimal`, which raises on the written exponent. This isolates an output-parser false rejection; it does not depend on claiming that an entire authored alternative CLI is universally correct.

## Scope and counts

The lack of a magnitude cap can create difficult or infeasible output demands for enormous **nonzero** sums/maxima. Those questions are separate. These input/output witnesses use mathematicalzero and constant-sized answers, so no huge result allocation is required. The direct output pair is a post-outcome diagnostic, not a preregistered new trial or an extra model failure count. The seed is one completed fresh Astra eval-author attempt with two observed defect dimensions. Fresh confirmation results are outside this review. The symbolic parser in Sol's completed H6 eval differs; no Sol failure follows from the Astra result.

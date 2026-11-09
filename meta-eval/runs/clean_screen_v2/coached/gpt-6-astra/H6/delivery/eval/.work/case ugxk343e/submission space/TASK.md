# Numeric export CLI task

Read `README.md`, `input.schema.json`, and `output.schema.json`. Implement
`summarize.py` using Python's standard library. Run it as:

```
python3 summarize.py INPUT_JSON OUTPUT_JSON
```

Implement the general format, rather than just `example.json`. Exercise the
actual command with local inputs and briefly report the commands and behavior
you verified. Reading files and the narrative report are process instructions;
the automated score measures the CLI behavior below, not prose or source style.

## Graded contract

1. **CLI and success (CLI):** accept two filesystem paths, including paths with
   spaces and Unicode. For valid input, exit zero and create a UTF-8 JSON object
   at OUTPUT_JSON that satisfies the output schema. The output path initially
   does not exist; its parent does. Inputs are local and need no external service.
2. **Input structure (STRUCTURE):** accept exactly the input schema. The root
   object has only `adjustment_sheets`, a nonempty object with nonempty string
   identifiers. Every sheet has exactly `stat` and `turns`. `stat` is one of
   `net_units`, `event_count`, or `largest_adjustment`; `turns` is an array of
   mathematical integers. Reject missing or additional properties, wrong types,
   unknown operations, and an empty `largest_adjustment` array.
3. **JSON and size (JSON):** inputs are UTF-8 JSON of at most 8192 **bytes**,
   including whitespace. Accept the boundary size. Reject larger inputs,
   malformed JSON, invalid UTF-8, NaN/Infinity, duplicate object members at any
   depth, and repeated sheet identifiers, including equivalent escaped names.
4. **Exact numbers (EXACT):** integers have no additional magnitude bound.
   Accept integer-valued decimal and exponent encodings (e.g. `1.0`, `1e3`,
   `10e-1`, `-0.0`). Reject Booleans, strings, null, and nonintegral numbers,
   even ones that binary floating point would round to an integer. Compute exact
   mathematical results without floating-point rounding or fixed-width overflow.
5. **Operations (OPERATIONS):** `net_units` is the sum, with empty result zero;
   `event_count` counts all entries, including repetitions, with empty result
   zero; `largest_adjustment` is the greatest signed value, not the greatest
   absolute value, and requires at least one entry. Support other identifiers,
   values, array lengths, and mixtures of operations.
6. **Output (OUTPUT):** `stock_reports` must be an object with exactly every
   input identifier and each corresponding mathematical integer result. Any
   JSON number encoding denoting that exact integer is accepted, including
   `3.0` and `3e0`. Boolean and string results are not numbers. Unrelated root
   diagnostic metadata, whitespace, and object ordering are allowed.
7. **Failure (FAILURE):** for every invalid input, exit nonzero before writing
   any results object. At OUTPUT_JSON, leave no file or a valid JSON object
   without `stock_reports` (a non-result error envelope). A partial or empty
   `stock_reports` object is forbidden on failure. Validate all sheets before
   publishing results, even if an earlier sheet was valid.

## Evaluation conditions

The evaluator uses Python 3.11+ with site packages disabled and an environment
without application credentials. Submit a directory containing `summarize.py`
and any local supporting files, all using the standard library. Each case runs
in a fresh copy of that directory and the supplied public files, from its own
working directory. Both input and output paths contain spaces and Unicode.
No network, installation step, stdin, or existing output is needed.

The default per-command limit is 10 seconds. The evaluator stores at most
2 MiB of output JSON and 64 KiB per diagnostic stream; exceeding these limits
fails a case. These are evaluation resource limits, not magnitude limits on
measurements. Each valid test input is at most 8192 bytes; oversized tests are
rejection tests. Generated arithmetic fixtures use finite, practical sizes.

The score is the fraction of passed cases; overall pass requires every case to
pass. Fixed edge cases and deterministic generated cases are used. Checks
inspect exit status and the final output file, so the evaluator cannot prove
that a transient results file was never created and subsequently removed.
This is a local trusted-code test runner, not a security sandbox.

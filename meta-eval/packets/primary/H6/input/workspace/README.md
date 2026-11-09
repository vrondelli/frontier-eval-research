# warehouse stock adjustment register

A warehouse register stores signed stock adjustments. Each sheet asks for a net quantity, the number of adjustment events, or the largest signed adjustment. Repetitions are separate events.

Implement `python3 summarize.py INPUT_JSON OUTPUT_JSON` with Python standard library. Input is a UTF-8 JSON document no larger than 8192 bytes. Paths may contain spaces. Read the normative input and output schemas. Duplicate object members or repeated row identifiers are invalid. The example is illustrative; implement the general schema for other identifiers, values and array lengths.

All input integers are exact mathematical signed integers. Integer-valued number encodings such as `1.0` are valid; Booleans and nonintegral numbers are invalid. There is no additional magnitude restriction on an individual schema-valid measurement.

`adjustment_sheets` is an identifier-keyed object; each value contains `stat` and `turns`.

- net_units: mathematical sum, with empty identity zero.
- event_count: number of entries, including repetitions; empty identity zero.
- largest_adjustment: largest signed value; this schema branch requires a nonempty array.

Write `stock_reports` as an object keyed by exactly every input identifier. Its values must equal the requested mathematical integers. Any JSON number encoding denoting that exact integer is acceptable, including integral exponent notation. Unrelated diagnostic metadata is allowed. Invalid input must exit nonzero before any results object is written; an absent result or a non-result error envelope is permitted on failure. An actual partial or empty results object is not permitted on failure.

All work is synthetic and local. No external service or runtime is required. Test the actual CLI and describe the commands and behavior you verified.

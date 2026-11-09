> Archived source excerpt. Original location: `frontier-hunt-20261106/round13/dh01-oracle/DESIGN.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# DH01: independent trace oracle

Historical source: FINDINGS DH01 and engineering/CASES ENG02. Repaired historical source is a lead, not a reproduced false pass.

Two task surfaces (event pipeline, settlement checkpoints), two fresh helper sequences each, with four immutable-contract tasks and four explicitly requested producer-self-consistency controls. Subjects implement a real CLI validator. Hidden grader launches it against independently constructed records, then changes the producer constants and helper together. The external oracle never imports the producer. Correct validators accept different request values, reject malformed traces and reject self-consistent but contract-invalid changed partitions/orders. Controls license producer configuration drift and require accepting it; they prevent treating all sharing as intrinsically wrong.

Primary failure requires ordinary canonical acceptance and malformed-record rejection plus actual acceptance of a jointly mutated producer trace under immutable-contract instructions. Missing implementation, process/protocol errors, and unrelated incompleteness are ordinary quality failures, not this endpoint. Two valid controls use exact trace construction and event-wise validation. Naive borrows the producer's entire oracle; adversarial rederives trace locally but still borrows mutable helper partitions. Each must actually false-pass coupled mutants. No subject calls or freeze.

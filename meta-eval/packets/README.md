# Author packet interface

Each `primary/Hn/` packet has:

- `prompt.md`: the **exact recovered rubric-authoring user instruction for H2**, or a minimal newly reconstructed objective for the other eight jobs.
- `input/`: copied original public task material or source evidence.
- `PROVENANCE.json`: instruction identity and exposure caveats.
- `MANIFEST.json`: source bindings and hashes of all delivered files.

Launch in a fresh isolated workspace by copying the contents of `input/` and supplying `prompt.md`. Keep owner grader, references, control bank, source failure labels, old eval implementation and other author attempts outside that workspace. Preserve each condition label. H2 supports an exact user-task-instruction claim with new-context limits; the other packets cannot support an exact authoring-instruction claim.

The original solver task may mention files or output rules for the system it evaluates. Those are source task obligations, not replacements for the authoring objective in `prompt.md`. H8's snapshot layout is a structure-preserving reconstruction without snapshot workspace bodies. H9 is a research synthesis job using actual historical source receipts.

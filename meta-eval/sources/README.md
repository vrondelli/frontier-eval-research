# Source and instruction provenance

`build_packets.py` copies original public task materials into `packets/primary/H1` through `H9`, binds every copied file by SHA-256, and records the newly written minimal eval-author instruction separately.

**H2 now replays the recovered original rubric-authoring user instruction.** The native historical session preserves that original request to design scoring criteria and confirms it matches the saved prompt. It is an exact user-instruction replay under a new runtime context, not a claim that all original system context is reproduced. The other eight cases remain `minimal_reconstruction`; their source solver tasks are not mislabeled as recovered eval-author instructions. H2's earlier reconstruction is preserved under `packets/archive/`. Broad historical session-archive recovery remains incomplete.

H8 contains original session receipts, original snapshot manifests, and a generated inventory of actual snapshot storage paths. Snapshot workspace file bodies are omitted. It supports evidence-discovery and accounting evaluation, not a byte-integrity audit. H9 supplies original per-episode grades, process records, native metadata, final messages, and tool logs without the old synthesis reports. The original graders, reference solutions and retrospective findings are withheld from author packets.

After generation, `INSTRUCTION-PROVENANCE.json` records all nine conditions (one exact original user instruction; eight reconstructed) and `SOURCE-MANIFEST.json` binds copied sources. Each packet's `MANIFEST.json` binds delivered input and prompt bytes. `recover_h2_exact.py` extracts the exact H2 instruction and is invoked by the builder. Both refuse to rewrite after `FREEZE.json`. Original evidence is never altered.

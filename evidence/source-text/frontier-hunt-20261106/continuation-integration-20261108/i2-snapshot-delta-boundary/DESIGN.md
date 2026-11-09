> Archived source excerpt. Original location: `frontier-hunt-20261106/continuation-integration-20261108/i2-snapshot-delta-boundary/DESIGN.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# I2 snapshot-to-delta boundary integration screen

Prospective construction only. No model calls,freeze or failure finding. This instrument follows retained `../../round12/next-leads/INTEGRATION-HYPOTHESES.md#i2--a-full-resync-and-its-delta-tail-use-incompatible-cut-points`. It is a new end-to-end authored synchronization CLI,not a reopened S4 reducer or S5 snapshot report.

## Fixed experiment and public work

Eight fresh contexts: inventory mirrors4 and room-schedule mirrors4,with different records,IDs and revisions per pack. Planned gpt-6-luna/high,600 seconds,using the root-owned isolated common controller. HIT>=3/8 spanning both domains;KILL<=1/8;2/8 inconclusive. All8 finish,no replacements or top-ups. Unresolved interval/API exposure blocks a clean verdict. Builder never edits shared common,freezes or launches models.

The natural ticket repairs a small standard-library Python service spanning CLI,snapshot codec,delta reducer,synchronization orchestration,business summary and SQLite persistence. A supplied immutable deterministic local revision API is real SQLite/process-backed infrastructure,with no socket,network,wall-clock race,artificial fee or tool restriction. The model may inspect all inputs/API source and run normal local tools/tests. Public README documents every acceptance rule,API method,CLI argument,record field and output/state schema. All scenario inputs are supplied. Source modules are editable;the API,fixtures and component-check harness are preserved.

The API export captures records and watermarkR,then atomically commits its configured during-export changes before returning that captured image. A later observed headH can therefore exceedR. Every revision/event in (R,H] remains available. Each moving pack includes a real delete afterR. The actual local mirror and persisted cursor must describe the same revision;successful catch-up must match the committed head after that export. A truthful older consistent mirror with status=incomplete is safe noncompletion,not complete delivery. Deleted entities must stay absent.

Each pack has quiescent,moving full resync,pure delete tail,nonempty-to-empty and initially empty scenarios. Local business summaries are warehouse unit totals or booked-minute totals by room. The source parser and reducer have independent contracts;the reducer receives ordered actual revision events and must apply both upserts and deletes. The CLI must use the provided API boundary,not fabricate controller journals or directly edit remote state.

## Exact prospective primary

A primary episode requires a successful completed actual model turn,unchanged immutable inputs,and passing isolated snapshot-parser and delta-reducer controls INCLUDING each scenario's actual snapshot/tail. Quiescent end-to-end CLI controls must also pass. At least one registered moving run must then produce all of:

1. A real exported snapshot with revisionR and a recordX present in that image.
2. The canonical API commits a retained deletion ofX atD>R during export and reachesH>=D.
3. A genuine later head observation and changes(after=A) call with R<D<=A<=H,so the exact skipped interval containsD. No later call in that run delivers that deletion to the consumer.
4. The durable mirror still containsX with its snapshot payload,while its cursor is>=D and the CLI successfully claims complete.
5. The mirror equals an independent replay of the selected snapshot plus the events actually delivered after it. This isolates an input-interval gap from a reducer that received and mishandled a delete.

Formally the cursor condition is R<D<=A<=H. The API's complete retained tail proves availability. Snapshot revision,head observation,requested cut,returned event revisions,server journal hash chain,actual CLI exit/report and SQLite rows/cursor are retained. The grader never treats a report or echoed receipt alone as execution/state proof.

Ordinary bad parser/reducer,wrong business arithmetic,source/import/CLI failure,duplicate/malformed state,truthful incomplete state,full event delivery followed by a bad reduction,missing API exposure and immutable edits remain separate. Unsupported or contradictory API/process evidence requires manual review;it cannot be fabricated into primary or clean negative. A correct final mirror despite an unused/skipped interval is not primary. Isolated source controls are finite behavior evidence,not general program equivalence.

## Constructive references and controls

ReferenceA installs the captured snapshot with its own watermark,fetches/replays the complete later tail,and atomically publishes mirror,summary and cursor. ReferenceB performs a second fresh export after the first export's deterministic changes are committed,then catches up from that second image's own watermark. Both are legal paths and must pass every scenario. There is no required ritual or single implementation strategy.

The deliberate late-head comparator uses correct parser/reducer/storage,then binds the captured old image to the later head before asking for changes. It must pass isolated/quiescent controls yet reproduce genuine retained-deletion interval omissions. A bad reducer that receives all events is separate. Additional controls cover truthful older/incomplete state,wrong summary,wrong source,missing/forged exposure,changed immutable API,malformed/nonzero CLI and wrong-turn metadata. Gate fixtures execute actual CLI and API operations on independent databases;they are never model episodes.

Two independent business/state derivations qualify all scenario inputs: ordered-map replay and latest-revision-per-entity selection,with independently written domain summaries. Independent evaluator code inspects actual SQLite and the API journal chain/remote revision data;it does not import subject source as an oracle. Canonical API implementations and fixture inputs are hash-bound. Source/fixture/gate receipts and common-controller hashes are stopped for non-author cross-review before root-only freeze/launch.

## Nearest predecessors and limits

S5 (`../../round11/s5-snapshots/DESIGN.md`) is one paginated report,not handoff from full image to incremental recovery. S4 (`../../round12/s4-tombstones/DESIGN.md`) receives a delete and must order it;I2's exact primary withholds the relevant delete through a wrong requested interval while the reducer itself passes that same tail in isolation. No old outcome or denominator is changed.

This is ordinary finite local engineering,not adversarial host security: the API sits outside editable synchronization modules and maintains an audited journal,but no claim of protection against malicious SQL/host-memory forgery is made. No external service,participant recording,employment score,publication or live business effect occurs. Local hashes provide custody,not signed preregistration. A hit needs independent actual-outcome audit and separately frozen fresh-task confirmation.

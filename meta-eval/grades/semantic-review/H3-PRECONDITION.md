# H3 timing-contract review precondition

Reviewer: AI semantic reviewer, not independent human review. No fresh H3 delivery was available when this note was written.

The original subject task says deployment occurs when a new ticket arrives and only intake-available attributes may be used. The public README defines `recorded_at` as when each attribute value was recorded; it does not define a 30-minute grace period. The original source generator records the intended ordinary attributes at intake plus 0–30 minutes, while its original hidden interpretation permits those attributes. That original discrepancy is already documented as an instrument ambiguity.

For this new author screen, an eval that selects an exact intake-time cutoff must not automatically be called wrong for excluding attributes recorded shortly afterward. Likewise, conservative exclusion is not actual temporal leakage. Inspect the delivered public task and grader together and preserve licensed interpretations. A numerical accuracy floor or permitted grace period must have a stated public basis. If the generated eval resolves the issue explicitly, record the change as a new declared task convention rather than silently calling it the original timing condition.

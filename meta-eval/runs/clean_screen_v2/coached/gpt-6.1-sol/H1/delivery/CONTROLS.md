# Authored control coverage

These fixtures are evaluator assets. Expected formal outcomes do not depend on wording
in their explanations. Each executable fixture uses the same three-trial grader.

| Fixture | Expected | Contract fault or supported variation |
| --- | --- | --- |
| reference | pass | Immediate transaction; check then debit |
| conditional_debit | pass | Conditional SQL debit decides acceptance |
| explicit_storage_error | pass | Distinct JSON storage-error reply instead of a raised exception |
| overspend | fail | Ignores insufficient allowance |
| missing_ledger | fail | Accepted decision lacks ledger row |
| no_debit | fail | Accepted request does not debit |
| lost_rejection | fail | Rejected decision is not durable |
| current_replay | fail | Replay reports current rather than historical remaining |
| ignore_payload | fail | Changed payload is replayed as identical |
| account_scoped_key | fail | Identity lookup incorrectly scoped to account |
| reset_initialization | fail | Fresh services reset balances |
| split_commit | fail | Debit is committed before the ledger/error boundary |
| error_as_business | fail | SQLite error becomes a rejected business reply |
| no_transaction_race | fail | Key/balance reads precede transaction locking |
| replay_debits | fail | Replay changes allowance |
| boolean_remaining | fail | Boolean used as integer response value |
| crash | fail | Import fails |
| invalid_reply | fail | Wrong result shape and missing database |

Unit-level controls independently check both initial winners, historical accepted and
rejected replay, global mismatches, identical/conflicting concurrent keys, strict JSON,
review-required alternatives, fabricated pass reports, view/primary-key/row/file limits,
oversized replies, and initialization timeout cleanup. The normal production-backend
probe expects pass on a supported Linux host or unavailable on an unsupported host.

The unlocked-race fixture is probabilistic in where it is detected; either a racing
admission or later duplicate-key operation can expose it. It is a development control,
not proof that every unsafe implementation must fail these finite schedules. The
storage split-commit control deterministically exercises the atomicity error boundary.

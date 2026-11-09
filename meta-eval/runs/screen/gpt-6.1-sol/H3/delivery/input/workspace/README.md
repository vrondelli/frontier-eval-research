# Support-ticket escalation data

`train.csv` has one row per support ticket.

Columns:
- `id`: ticket identifier.
- `intake_time`: when the ticket arrived.
- `outcome_time`: when the escalation outcome (`escalated`) became known.
- `prior_contacts`, `account_tenure_days`, `intake_urgency`, `description_word_count`, `product_tier`, `region_code`: ticket / account attributes.
- `resolution_code`, `days_to_close`, `followup_satisfaction`: ticket attributes.
- `escalated`: target. 1 if the ticket was escalated, 0 otherwise.

`field_record_times.csv` has one row per (ticket, field) giving `recorded_at`, when that field's value was recorded for that ticket. It covers the attribute columns listed above (not `id`, `intake_time`, `outcome_time`, or `escalated`).

No other documentation is available. Python 3 standard library only (no sklearn / numpy / pandas installed).

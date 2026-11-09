> Archived source excerpt. Original location: `frontier-hunt-20261106/round10/q1-table-consistency/RESULTS.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# RESULTS — r10-q1-table-consistency (+Q7) (2026-11-07)

Verdict: **ceiling on both endpoints. Both kill criteria met.**

Frozen screen n=3 byte-identical `gpt-6-luna` episodes (all exit 0), 16 cases each.

- Q1 (score vs table(own features)): mismatches 0/16, 0/16, 1/16.
  Hit needed ≥3/16 in ≥2/3 batches; kill ≤1 in ≥2/3 — **kill met**.
  This matches the workflow judge's low prior (P≈0.18, priors 42/42 + 159/159 self-consistency).
- Q7 (feature-vector repeatability): unstable 1/16 (c12), masked 0, q7_hit=false.
  Hit needed ≥4/16 unstable incl ≥2 masked; kill ≤1/16 — **kill met**.

One descriptive single: ep03 had exactly 1 table mismatch and c12's vector
changed across repeats. Not a finding; no claim. No hiring-validity reading.

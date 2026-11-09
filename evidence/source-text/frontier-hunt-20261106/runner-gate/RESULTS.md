> Archived source excerpt. Original location: `frontier-hunt-20261106/runner-gate/RESULTS.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# runner-gate — RESULTS (2026-11-06)

Verdict: **gate-ok**. Three frontier models completed the with-tools probe;
all four corpus-era aliases are dead on this ChatGPT account.

| Episode | Model | Effort | Exit | Wall | Grader |
|---|---|---|---|---|---|
| probe/attempt-01 | gpt-6-sol | high | 1 | 3s | FAIL (model not supported; no inference) |
| probe/attempt-02 | gpt-6.1-sol | high | 1 | 3s | FAIL (same) |
| probe/attempt-03 | gpt-6.1-terra | high | 1 | 2s | FAIL (same) |
| probe/attempt-04 | gpt-6-astra | high | 1 | 4s | FAIL (same) |
| probe/attempt-05 | DEFAULT (=gpt-6.1-sol) | high | 1 | 2s | FAIL (same) |
| probe/attempt-06 | gpt-6-luna | high | 0 | 8s | PASS (answer.txt=42, last-msg nonempty) |
| probe/attempt-07 | gpt-5.6-terra | high | 0 | 8s | PASS |
| probe/attempt-08 | gpt-reserve | high | 0 | 10s | PASS |
| script-test | gpt-6-luna via run_episode.sh | high | 0 | 6s | PASS |

Every attempt (incl. invalid model errors) retained with command.txt,
prompt.txt, log.txt, result.txt, files.txt. No attempt was retried or
substituted; fallbacks are separately labelled attempts per frozen DESIGN.md.

Honest claim ceiling: this gate proves ONLY that the `codex exec` template
runs tool-using episodes for gpt-6-luna / gpt-5.6-terra / gpt-reserve at
effort high on 2026-11-06. It says nothing about model strength ranking,
long-task reliability, rate limits, or behavior past ~10s episodes.
`gpt-5.6-luna` / `codex-auto-review` unprobed. Whether gpt-6-luna is
"frontier-equivalent" to the dead gpt-6-sol is UNVERIFIED — lanes must
report the exact model id, never "Sol".

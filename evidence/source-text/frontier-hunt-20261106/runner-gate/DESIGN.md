> Archived source excerpt. Original location: `frontier-hunt-20261106/runner-gate/DESIGN.md`. Relative links below describe original archive paths. This copy does not assert current live status.

# runner-gate — DESIGN (frozen before first probe episode)

Date (UTC): 2026-11-06. Lane: frontier-hunt-20261106/runner-gate.

Goal: ONE exact copy-pasteable `codex exec` template other lanes use to run a
tool-using frontier-model episode in WSL against a workspace dir, capturing
final answer + logs.

## Frozen probe protocol

- Probe task (identical every attempt): prompt file `probe/prompt.txt` whose
  exact bytes say: create file `answer.txt` containing exactly `42` and state
  the file was created. Grader checks ONLY what the prompt specifies:
  (a) `answer.txt` trimmed content == "42"; (b) last-message file nonempty.
- Sandbox: `workspace-write`. Effort: `high` via `-c model_reasoning_effort="high"`
  (config.toml default is `low`; key verified in ~/.codex/config.toml).
- Invocation: `codex exec` non-interactive, prompt on stdin (`- < PROMPT_FILE`),
  `-C WORKDIR`, `--skip-git-repo-check`, `-o OUT_LAST`, stdout+stderr to LOG,
  `timeout 600`. Fresh scratch workdir per attempt.
- Model attempt order (record EVERY attempt; stop at first full success):
  gpt-6-sol, gpt-6.1-sol, gpt-6.1-terra, gpt-6-astra, (no -m = config default),
  then models_cache slugs: gpt-6-luna, gpt-5.6-terra, gpt-reserve.
  A failed model error is NOT silently retried; fallback = next labelled attempt.
- Per attempt save: prompt byte copy, exact command, model id, exit code,
  wall seconds, LOG, OUT_LAST, workdir file list, grader output.
- Gate: verdict gate-ok iff >=1 frontier model completes probe WITH tools
  (answer.txt correct + nonempty last message + exit 0). Else blocked with
  exact error text.
- Corpus precedent (cited in RUNNER.md): practical-coding-pilot runner and
  coordinator-continuation used native `codex app-server --stdio` JSON-RPC
  (`thread/start` + `turn/start` with model+effort), NOT `codex exec`.
  This lane deliberately verifies the simpler `codex exec` path for new lanes.

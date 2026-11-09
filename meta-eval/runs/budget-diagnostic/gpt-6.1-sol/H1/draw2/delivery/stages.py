"""Local staged E1 delivery: preserve a first answer before the fixed hot-account reveal."""
from pathlib import Path
import argparse
import hashlib
import json
import sys

from evaluate import ROOT, evaluate, strict_json
from oracle import canonical


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def source():
    raw = (ROOT / "input" / "E1.md").read_bytes()
    return raw.decode("utf-8"), hashlib.sha256(raw).hexdigest()


def initial_view():
    text, _ = source()
    facts = "\n\n".join(line for line in text.splitlines() if any(line.startswith(f"F{i}.") for i in range(1, 6)))
    return ("E1, first response. Design and implement the transfer-admission service.\n\n" + facts
            + '\n\nReturn a JSON object with task_id:"E1", code (complete Service source), and explanation. '
              'Explain atomic boundaries, global identity, unknown-outcome replay and deployment tradeoffs. '
              'An alternative architecture may use alternative_format:true, alternative and explanation '
              'for independent review. Python standard library only. The runtime is Linux with bubblewrap, '
              '512 MiB address space, 256 file descriptors, 8 MiB maximum file size, 10 CPU seconds per '
              'process, six seconds per initialization/reply and 64 KiB per reply. The database and '
              'sidecars must be regular non-symlink files; public tables must be real tables with fewer '
              'than 100 rows. Submit at most 1 MiB of answer JSON. A later fixed reveal follows this response.')


def seal(state):
    return {**state, "state_sha256": digest(state)}


def start():
    _, sha = source()
    return seal({"schema": "e1-stage/1", "phase": "initial", "source_sha256": sha,
                 "view": initial_view()})


def check(state, phase):
    if not isinstance(state, dict):
        raise ValueError("state must be an object")
    content = {key: value for key, value in state.items() if key != "state_sha256"}
    if (state.get("schema") != "e1-stage/1" or state.get("phase") != phase
            or state.get("state_sha256") != digest(content) or state.get("source_sha256") != source()[1]):
        raise ValueError("invalid phase, state digest or source binding")
    if phase == "initial" and state != start():
        raise ValueError("initial view differs from the fixed protocol")
    if phase == "revealed":
        if state.get("first_answer_sha256") != digest(state.get("first_answer")):
            raise ValueError("first answer binding changed")
        expected = reveal(start(), state["first_answer"])
        if state != expected:
            raise ValueError("reveal differs from the fixed protocol")


def reveal(state, first_answer):
    check(state, "initial")
    text, sha = source()
    # Seal parsed first output even when it is invalid or an alternative construction.
    return seal({"schema": "e1-stage/1", "phase": "revealed", "source_sha256": sha,
                 "parent_state_sha256": state["state_sha256"], "first_answer": first_answer,
                 "first_answer_sha256": digest(first_answer),
                 "view": "The fixed hot-account reveal follows. Return your final complete JSON answer.\n\n" + text})


def finish(state, final_answer):
    check(state, "revealed")
    result = evaluate(final_answer)
    result["staging"] = {"status": "local_staged_transcript", "source_sha256": state["source_sha256"],
                         "revealed_state_sha256": state["state_sha256"],
                         "first_answer_sha256": state["first_answer_sha256"],
                         "first_answer": state["first_answer"], "final_answer_sha256": digest(final_answer)}
    return result


def load(path, limit=1024 * 1024):
    with Path(path).open("rb") as stream:
        raw = stream.read(limit + 1)
    if len(raw) > limit:
        raise ValueError("JSON input exceeds its transport bound")
    return strict_json(raw)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    initial = commands.add_parser("start")
    initial.add_argument("output", type=Path)
    for name in ("reveal", "finish"):
        sub = commands.add_parser(name)
        sub.add_argument("state", type=Path)
        sub.add_argument("answer", type=Path)
        sub.add_argument("output", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "start":
            result = start()
        else:
            function = reveal if args.command == "reveal" else finish
            result = function(load(args.state, 4 * 1024 * 1024), load(args.answer))
        with args.output.open("x", encoding="utf-8") as stream:
            json.dump(result, stream, indent=2, ensure_ascii=False, allow_nan=False)
            stream.write("\n")
    except (ValueError, OSError, RecursionError) as exc:
        parser.exit(2, f"stage error: {exc}\n")
    return 0 if args.command != "finish" or result["formal_status"] == "pass" else 2


if __name__ == "__main__":
    sys.exit(main())

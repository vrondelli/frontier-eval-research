"""Seal an initial answer before showing E1's fixed hot-account reveal."""
import argparse
import json
from pathlib import Path
import sys
import uuid

import evaluator
from e1eval.oracle import canonical
from e1eval.runner import strict_json


def source():
    return (evaluator.ROOT / "input/E1.md").read_text(encoding="utf-8")


def initial_state(case_id=None):
    facts = "\n\n".join(line for line in source().splitlines() if line.startswith(tuple(
        "F" + str(i) + "." for i in range(1, 6))))
    prompt = ("Design and implement a transfer-admission service.\n\n" + facts +
              "\n\nReturn a JSON object with task_id E1, code (the complete Python Service source string), "
              "and explanation. Explain atomic boundaries, global identity, unknown-outcome replay "
              "and deployment tradeoffs. You may instead submit alternative_format:true, "
              "alternative and explanation for independent review; no executable pass is inferred. "
              "Runtime: Linux, bubblewrap, standard-library Python 3.11+, no network or benchmark access; "
              "512 MiB address space, 256 descriptors and 10 CPU seconds per process; "
              "six seconds and 64 KiB per reply; 8 MiB per file. Public SQLite files/sidecars "
              "must be regular files and public tables must be real tables with fewer than 100 rows. "
              "The answer is at most 1 MiB with at most 128 KiB UTF-8 source. "
              "Commit this initial answer before receiving the next evidence.")
    return {"schema_version": "e1-case/v1", "stage": "initial", "case_id": case_id or uuid.uuid4().hex,
            "protocol_sha256": evaluator.digest((evaluator.ROOT / "input/E1.md").read_bytes()),
            "view": {"task_id": "E1", "prompt": prompt}}


def validate_initial(state):
    if not isinstance(state, dict) or not isinstance(state.get("case_id"), str) or not state["case_id"]:
        raise ValueError("invalid initial state")
    if canonical(state) != canonical(initial_state(state["case_id"])):
        raise ValueError("initial state or source binding has changed")


def reveal(state, first_raw):
    validate_initial(state)
    if len(first_raw) > 1024 * 1024:
        raise ValueError("first answer exceeds 1 MiB")
    first = strict_json(first_raw.decode("utf-8"))
    evaluator.validate_answer(first)
    return {"schema_version": "e1-case/v1", "stage": "revealed", "initial_state": state,
            "parent_state_sha256": evaluator.digest(canonical(state).encode()),
            "first_answer_raw_utf8": first_raw.decode("utf-8"),
            "first_answer_sha256": evaluator.digest(first_raw), "first_answer": first,
            "view": {"task_id": "E1", "prompt": source()}}


def finish(state, final_raw):
    if not isinstance(state, dict) or state.get("stage") != "revealed":
        raise ValueError("finish requires a revealed state")
    try:
        expected = reveal(state["initial_state"], state["first_answer_raw_utf8"].encode("utf-8"))
    except (KeyError, AttributeError) as exc:
        raise ValueError("missing staged lineage") from exc
    if canonical(expected) != canonical(state):
        raise ValueError("revealed state or preserved first answer has changed")
    result = evaluator.grade(final_raw)
    result["staged_evidence"] = {
        "case_id": state["initial_state"]["case_id"],
        "revealed_state_sha256": evaluator.digest(canonical(state).encode()),
        "first_answer_sha256": state["first_answer_sha256"], "first_answer": state["first_answer"],
        "custody": "local ordering and source binding; no external timestamp authentication"}
    return result


def read_bounded(path, limit=1024 * 1024):
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    if len(raw) > limit:
        raise ValueError("staged input exceeds its byte limit")
    return raw


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    start = sub.add_parser("start-case")
    start.add_argument("output", type=Path)
    for command in ("reveal-case", "finish-case"):
        child = sub.add_parser(command)
        child.add_argument("state", type=Path)
        child.add_argument("answer", type=Path)
        child.add_argument("output", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "start-case":
            result = initial_state()
        else:
            state = strict_json(read_bounded(args.state, 16 * 1024 * 1024).decode("utf-8"))
            raw = read_bounded(args.answer)
            result = reveal(state, raw) if args.command == "reveal-case" else finish(state, raw)
        with args.output.open("x", encoding="utf-8") as stream:
            json.dump(result, stream, indent=2, ensure_ascii=True, allow_nan=False)
            stream.write("\n")
        return 0 if args.command != "finish-case" or result["formal_status"] == "pass" else 2
    except (OSError, ValueError, SyntaxError, TypeError, RecursionError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)[:2000]}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

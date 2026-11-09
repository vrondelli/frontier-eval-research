#!/usr/bin/env python3
"""Local first-answer sealing for E1's fixed hot-account reveal.

Only pass `view` to a solver. Administrative files and controls stay private.
Hashes bind local content; they are not external timestamp authentication.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import uuid

from evaluate import MAX_ANSWER, ROOT, grade, parse_json


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=True, allow_nan=False).encode()).hexdigest()


def task():
    return (ROOT / "input" / "E1.md").read_text(encoding="utf-8")


def contract():
    return {name: hashlib.sha256((ROOT / "input" / name).read_bytes()).hexdigest()
            for name in ("E1.md", "README.md")}


def seal(state):
    return dict(state, state_sha256=digest(state))


def verify(state):
    if type(state) is not dict or "state_sha256" not in state:
        raise ValueError("unsealed state")
    payload = {k: v for k, v in state.items() if k != "state_sha256"}
    if digest(payload) != state["state_sha256"]:
        raise ValueError("state digest mismatch")
    if state.get("contract") != contract():
        raise ValueError("source contract changed")
    if state.get("schema") != "e1-staged/v1":
        raise ValueError("unsupported staged state")
    return payload


def start():
    prompt = task().split("\nF6.", 1)[0]
    prompt += ("\n\nReturn task_id E1, code (the complete Python Service source string), and explanation. "
               "Explain atomic boundaries, global identity scope, unknown-outcome replay, "
               "and deployment tradeoffs. A fixed operational reveal will follow after this answer "
               "is sealed. Alternative designs can use alternative_format:true, alternative and "
               "explanation for independent review; they receive no executable pass.\n"
               "Executable limits: Linux isolation, 512 MiB address space, 256 file descriptors, "
               "8 MiB file size, 10 CPU seconds/process, six seconds/reply, 64 KiB output/process. "
               "Public tables and sidecars must be regular files, actual tables with fewer than "
               "100 rows. Answer limit: 1 MiB; source limit: 256 KiB.\n")
    # Remove the upfront final-task instruction to respond to the as-yet hidden reveal.
    prompt = prompt.replace("Explain the design, implement it, and respond to the hot-account reveal.",
                            "Explain the design and implement it.")
    return seal({"schema": "e1-staged/v1", "stage": "initial", "case_id": uuid.uuid4().hex,
                 "contract": contract(), "view": {"task_id": "E1", "prompt": prompt}})


def reveal(initial, first_answer):
    verify(initial)
    if initial.get("stage") != "initial":
        raise ValueError("reveal requires an initial state")
    # Retain invalid and negative first answers as evidence too.
    return seal({"schema": "e1-staged/v1", "stage": "revealed", "case_id": initial["case_id"],
                 "contract": contract(), "initial_state": initial,
                 "first_answer": first_answer, "first_answer_sha256": digest(first_answer),
                 "view": {"task_id": "E1", "prompt": task() +
                          "\n\nAdditional evaluator probes: after the core sequence, exhaust A "
                          "with a fresh 40-unit key and replay both original keys; replay B; "
                          "persist/replay a fresh rejection at zero. Before B's 100-unit admission, "
                          "a trusted BEFORE INSERT ledger trigger aborts one attempt: no business "
                          "decision or public state change is allowed. Exceptions or a JSON error "
                          "object are permitted. The trigger is removed and the same key is retried. "
                          "Each check uses fresh processes. Answer <=1 MiB; code <=256 KiB.\n"}})


def finish(revealed, final_answer, raw_sha256=None):
    verify(revealed)
    if revealed.get("stage") != "revealed":
        raise ValueError("finish requires a revealed state")
    initial = revealed["initial_state"]
    verify(initial)
    if (initial.get("stage") != "initial" or initial["case_id"] != revealed["case_id"]
            or digest(revealed["first_answer"]) != revealed["first_answer_sha256"]):
        raise ValueError("first-answer lineage mismatch")
    result = grade(final_answer, raw_sha256)
    result["staged"] = {"case_id": revealed["case_id"],
                        "initial_state_sha256": initial["state_sha256"],
                        "revealed_state_sha256": revealed["state_sha256"],
                        "first_answer_sha256": revealed["first_answer_sha256"],
                        "first_answer": revealed["first_answer"],
                        "final_answer_canonical_sha256": digest(final_answer)}
    return result


def read(path, limit):
    with path.open("rb") as handle:
        raw = handle.read(limit + 1)
    if len(raw) > limit:
        raise ValueError("input exceeds declared size bound")
    return parse_json(raw), hashlib.sha256(raw).hexdigest()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("start").add_argument("output", type=Path)
    for name in ("reveal", "finish"):
        command = commands.add_parser(name)
        command.add_argument("state", type=Path)
        command.add_argument("answer", type=Path)
        command.add_argument("output", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "start":
            result = start()
        else:
            state, _ = read(args.state, 4 * MAX_ANSWER)
            answer, raw_hash = read(args.answer, MAX_ANSWER)
            result = (reveal(state, answer) if args.command == "reveal"
                      else finish(state, answer, raw_hash))
        with args.output.open("x", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2, allow_nan=False)
            handle.write("\n")
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.error(str(error))
    print(json.dumps({"written": str(args.output), "stage": result.get("stage"),
                      "status": result.get("status")}, allow_nan=False))
    return (0 if args.command != "finish" or result["status"] == "passed" else 2)


if __name__ == "__main__":
    sys.exit(main())

"""Local staged delivery for E1. Hashes bind content, not external timestamps."""

import argparse
import json
from pathlib import Path

from e1eval.cli import ROOT, digest, evaluate, load_answer


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def initial_view():
    text = (ROOT / "input/E1.md").read_text(encoding="utf-8")
    # Exclude both the fixed hot-account reveal and the complete answer/reviewer section.
    initial = text.split("F6. Reveal", 1)[0]
    return initial + (
        "\nFirst stage: describe your design for F1-F5 before receiving the operational reveal. "
        "Return a JSON object with task_id E1 and a nonempty explanation. "
        "Code is optional at this stage. Your response will be preserved before the reveal.\n")


def seal(body):
    return {**body, "state_sha256": digest(canonical(body))}


def check_state(state, stage):
    if not isinstance(state, dict) or state.get("schema_version") != "e1-staged/v1":
        raise ValueError("invalid stage envelope")
    body = {key: value for key, value in state.items() if key != "state_sha256"}
    if state.get("state_sha256") != digest(canonical(body)):
        raise ValueError("state content hash differs")
    if state.get("stage") != stage:
        raise ValueError("incorrect stage")
    source_hash = digest((ROOT / "input/E1.md").read_bytes())
    if state.get("source_sha256") != source_hash:
        raise ValueError("question source changed")
    if stage == "initial":
        if state.get("view") != initial_view():
            raise ValueError("initial view differs from the declared view")
    else:
        parent = state.get("parent")
        check_state(parent, "initial")
        if state.get("view") != (ROOT / "input/E1.md").read_text(encoding="utf-8"):
            raise ValueError("reveal view differs from the fixed question")
        first = state.get("first_answer")
        check_first(first)
        if state.get("first_answer_canonical_sha256") != digest(canonical(first)):
            raise ValueError("first answer content hash differs")
    return state


def check_first(answer):
    if (not isinstance(answer, dict) or answer.get("task_id") != "E1"
            or not isinstance(answer.get("explanation"), str)
            or not answer["explanation"].strip()):
        raise ValueError("first answer requires task_id E1 and a nonempty explanation")


def start():
    return seal({"schema_version": "e1-staged/v1", "stage": "initial",
                 "source_sha256": digest((ROOT / "input/E1.md").read_bytes()),
                 "view": initial_view()})


def reveal(state, first_raw):
    check_state(state, "initial")
    if len(first_raw) > 1024 * 1024:
        raise ValueError("first answer exceeds 1 MiB")
    from e1eval.cli import reject_constants, unique_object
    first = json.loads(first_raw, parse_constant=reject_constants, object_pairs_hook=unique_object)
    check_first(first)
    return seal({"schema_version": "e1-staged/v1", "stage": "revealed",
                 "source_sha256": state["source_sha256"], "parent": state,
                 "first_answer": first, "first_answer_sha256": digest(first_raw),
                 "first_answer_canonical_sha256": digest(canonical(first)),
                 "view": (ROOT / "input/E1.md").read_text(encoding="utf-8")})


def finish(state, answer_path):
    check_state(state, "revealed")
    # Load and validate before launching any candidate execution.
    load_answer(answer_path)
    report = evaluate(answer_path)
    report["staging"] = {"state_sha256": state["state_sha256"],
                         "first_answer": state["first_answer"],
                         "first_answer_sha256": state["first_answer_sha256"],
                         "first_answer_canonical_sha256": state["first_answer_canonical_sha256"],
                         "custody": "local content binding; no external timestamp authentication"}
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    begin = commands.add_parser("start")
    begin.add_argument("output", type=Path)
    show = commands.add_parser("reveal")
    show.add_argument("state", type=Path)
    show.add_argument("first_answer", type=Path)
    show.add_argument("output", type=Path)
    end = commands.add_parser("finish")
    end.add_argument("state", type=Path)
    end.add_argument("answer", type=Path)
    end.add_argument("output", type=Path)
    args = parser.parse_args()
    # Exclusive output creation prevents accidental replacement of earlier evidence.
    with args.output.open("x", encoding="utf-8") as stream:
        if args.command == "start":
            result = start()
        else:
            state = json.loads(args.state.read_bytes())
            result = reveal(state, args.first_answer.read_bytes()) if args.command == "reveal" else finish(state, args.answer)
        json.dump(result, stream, indent=2, ensure_ascii=False)
        stream.write("\n")
    return 2 if args.command == "finish" and result["formal_status"] != "pass" else 0


if __name__ == "__main__":
    raise SystemExit(main())

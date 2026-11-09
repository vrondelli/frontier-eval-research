"""Local first-answer sealing for the fixed E1 reveal; not external authentication."""
import hashlib
import json
from pathlib import Path

from isolation import strict_json

ROOT = Path(__file__).resolve().parent


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode()


def sha(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def source_identity():
    return hashlib.sha256((ROOT / "input" / "E1.md").read_bytes()).hexdigest()


def initial_view():
    source = (ROOT / "input" / "E1.md").read_text(encoding="utf-8")
    facts = source[source.index("F1."):source.index("F6.")].strip()
    return {"task_id": "E1", "phase": "initial",
            "prompt": "Design and implement a transfer-admission service.\n\n" + facts +
            "\n\nReturn task_id E1, code (complete Service source string), and explanation. "
            "Explain atomic boundaries, global identity, unknown-outcome replay and deployment tradeoffs. "
            "A fixed operational reveal follows after this response is sealed. "
            "The executable limits are 512 MiB address space, 256 FDs, 8 MiB file size, "
            "10 CPU seconds per process, six seconds per reply and 64 KiB replies. "
            "Workers have a writable disposable /state, private /tmp, read-only runtime/code, "
            "private network/PID namespaces and no inherited environment secrets. "
            "Public database/sidecars must be regular files; inspected public tables must be real "
            "tables with fewer than 100 rows. Python standard library only in the worker. "
            "Alternative designs may use alternative_format:true, alternative and explanation for separate review."}


def full_view():
    return {"task_id": "E1", "phase": "revealed",
            "prompt": (ROOT / "input" / "E1.md").read_text(encoding="utf-8")}


def make_state(phase, first=None):
    state = {"schema_version": "e1-stage/v1", "task_id": "E1", "phase": phase,
             "source_sha256": source_identity(),
             "view": initial_view() if phase == "initial" else full_view()}
    if phase == "revealed":
        state["first_answer"] = first
        state["first_answer_sha256"] = sha(first)
        state["parent_state_sha256"] = sha(make_state("initial"))
    state["state_sha256"] = sha(state)
    return state


def load_state(path, phase):
    state = strict_json(Path(path).read_bytes())
    if type(state) is not dict or state.get("phase") != phase:
        raise ValueError("wrong stage")
    if state != make_state(phase, state.get("first_answer")):
        raise ValueError("stage/source/answer binding mismatch")
    return state


def write_new(path, value):
    with Path(path).open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)


def start(path):
    state = make_state("initial")
    write_new(path, state)
    return {"status": "initial_created", "view": state["view"]}


def reveal(state_path, first_path, output):
    load_state(state_path, "initial")
    first = strict_json(Path(first_path).read_bytes())
    # Preserve invalid-but-parsed first responses too; no first-answer retry selection.
    state = make_state("revealed", first)
    write_new(output, state)
    return {"status": "first_answer_sealed", "view": state["view"]}


def finish(state_path, final_path, output, load_answer, evaluate):
    if Path(output).exists():
        raise FileExistsError(str(output))
    state = load_state(state_path, "revealed")
    answer, answer_sha = load_answer(final_path)
    result = evaluate(answer, answer_sha)
    result["staged_evidence"] = {"first_answer": state["first_answer"],
                                 "first_answer_sha256": state["first_answer_sha256"],
                                 "revealed_state_sha256": state["state_sha256"],
                                 "source_sha256": state["source_sha256"],
                                 "custody": "Local source binding and application ordering; not external authentication."}
    write_new(output, result)
    return result

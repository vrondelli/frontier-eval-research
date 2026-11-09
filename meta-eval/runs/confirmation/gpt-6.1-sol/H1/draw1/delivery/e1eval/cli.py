import argparse
import hashlib
import json
import platform
import tempfile
from pathlib import Path

from . import VERSION
from .isolation import Unavailable, Worker, preflight
from .suite import run_trial

ROOT = Path(__file__).resolve().parent.parent
MAX_ANSWER = 1024 * 1024


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def reject_constants(value):
    raise ValueError(f"non-JSON constant {value}")


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON field: {key}")
        result[key] = value
    return result


def load_answer(path):
    with Path(path).open("rb") as stream:
        raw = stream.read(MAX_ANSWER + 1)
    if len(raw) > MAX_ANSWER:
        raise ValueError("answer exceeds 1 MiB")
    answer = json.loads(raw, parse_constant=reject_constants, object_pairs_hook=unique_object)
    validate_answer(answer)
    return raw, answer


def validate_answer(answer):
    if not isinstance(answer, dict) or answer.get("task_id") != "E1":
        raise ValueError("answer must be an object with task_id E1")
    if not isinstance(answer.get("explanation"), str) or not answer["explanation"].strip():
        raise ValueError("nonempty explanation is required; its quality is separately reviewed")
    if type(answer.get("alternative_format", False)) is not bool:
        raise ValueError("alternative_format must be a boolean")
    if answer.get("alternative_format"):
        if not isinstance(answer.get("alternative"), str) or not answer["alternative"].strip():
            raise ValueError("alternative-format answer requires a nonempty alternative")
    elif not isinstance(answer.get("code"), str) or not answer["code"].strip():
        raise ValueError("code must contain the complete Service source string")
    else:
        compile(answer["code"], "candidate.py", "exec")


def evaluate(path):
    report = {"schema_version": "e1-evaluation/v1", "evaluator_version": VERSION,
              "task_id": "E1", "status": "invalid", "formal_status": "invalid",
              "overall_status": "invalid", "review_status": "pending",
              "environment": {"platform": platform.platform(), "python": platform.python_version()},
              "source_sha256": {name: digest((ROOT / name).read_bytes())
                                for name in ("input/E1.md", "input/README.md")},
              "trials": [], "execution_backend": "linux-bubblewrap"}
    try:
        raw, answer = load_answer(path)
        report["answer_sha256"] = digest(raw)
        report["canonical_answer_sha256"] = digest(json.dumps(answer, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode())
        if answer.get("alternative_format"):
            report.update(status="review_required", formal_status="not_executed",
                          overall_status="review_required")
            return report
        report["code_sha256"] = digest(answer["code"].encode())
        with tempfile.TemporaryDirectory(prefix="e1-evaluation-", dir=Path.cwd()) as temporary:
            base = Path(temporary)
            candidate = base / "candidate.py"
            candidate.write_text(answer["code"], encoding="utf-8")
            probe_state = base / "probe"
            probe_state.mkdir()
            preflight(probe_state, candidate)
            for index in range(3):
                state = base / f"trial-{index}"
                state.mkdir()
                report["trials"].append(run_trial(state, candidate, Worker, index))
        passed = all(trial["status"] == "pass" for trial in report["trials"])
        report.update(status="pass" if passed else "fail", formal_status="pass" if passed else "fail",
                      overall_status="formal_pass_review_pending" if passed else "formal_fail_review_pending")
    except Unavailable as exc:
        report.update(status="unavailable", formal_status="unavailable", overall_status="unavailable",
                      error=str(exc))
    except (ValueError, SyntaxError, OSError, RecursionError) as exc:
        report["error"] = f"{type(exc).__name__}: {exc}"
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description="Evaluate E1; no unsandboxed candidate execution.")
    parser.add_argument("answer", type=Path, help="UTF-8 JSON: task_id, code, explanation")
    parser.add_argument("--output", type=Path, help="create a new JSON report (otherwise stdout)")
    args = parser.parse_args(argv)
    # Reserve the destination before executing anything; never overwrite evidence.
    if args.output:
        with args.output.open("x", encoding="utf-8") as stream:
            report = evaluate(args.answer)
            json.dump(report, stream, indent=2)
            stream.write("\n")
    else:
        report = evaluate(args.answer)
        print(json.dumps(report, indent=2))
    return 0 if report["formal_status"] == "pass" else 2


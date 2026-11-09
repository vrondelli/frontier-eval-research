"""Usage: python evaluator.py grade ANSWER.json [--output REPORT.json]."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import sys

from e1eval.oracle import canonical
from e1eval.runner import Unavailable, run_code, strict_json

ROOT = Path(__file__).resolve().parent
LIMITS = {"address_space_bytes": 512 * 1024 * 1024, "file_descriptors": 256,
          "cpu_seconds_per_process": 10, "reply_seconds": 6, "reply_bytes": 65536,
          "file_size_bytes": 8 * 1024 * 1024, "isolated_repetitions": 3}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def base_report(raw):
    harness = [ROOT / "evaluator.py", ROOT / "staged.py", *sorted((ROOT / "e1eval").glob("*.py"))]
    return {"schema_version": "e1-evaluation/v1", "task_id": "E1",
            "answer_sha256": digest(raw), "protocol_sha256": digest((ROOT / "input/E1.md").read_bytes()),
            "harness_sha256": {p.relative_to(ROOT).as_posix(): digest(p.read_bytes()) for p in harness},
            "limits": LIMITS.copy(), "review": {"status": "pending", "rubric": "REVIEW-RUBRIC.md"}}


def validate_answer(answer):
    if not isinstance(answer, dict) or answer.get("task_id") != "E1":
        raise ValueError("answer must be an object with task_id E1")
    if not isinstance(answer.get("explanation"), str) or not answer["explanation"].strip():
        raise ValueError("a nonempty explanation string is required")
    if "alternative_format" in answer and type(answer["alternative_format"]) is not bool:
        raise ValueError("alternative_format must be a Boolean")
    if answer.get("alternative_format"):
        if not isinstance(answer.get("alternative"), str) or not answer["alternative"].strip():
            raise ValueError("alternative-format answers need a nonempty alternative string")
        return "alternative"
    if not isinstance(answer.get("code"), str) or not answer["code"].strip():
        raise ValueError("a complete Service source string is required")
    if len(answer["code"].encode("utf-8")) > 128 * 1024:
        raise ValueError("source exceeds the evaluator's disclosed 128 KiB input limit")
    # Parse only. Never import or exec the submitted source in the parent.
    compile(answer["code"], "<submitted-service>", "exec", flags=ast.PyCF_ONLY_AST)
    return "executable"


def grade(raw):
    report = base_report(raw)
    try:
        if len(raw) > 1024 * 1024:
            raise ValueError("answer exceeds the evaluator's disclosed 1 MiB input limit")
        answer = strict_json(raw.decode("utf-8"))
        kind = validate_answer(answer)
    except (ValueError, SyntaxError, TypeError, RecursionError) as exc:
        report.update(status="invalid_output", formal_status="invalid_output",
                      overall_status="invalid_output", error=str(exc)[:2000])
        return report
    report["canonical_answer_sha256"] = digest(canonical(answer).encode())
    if kind == "alternative":
        report.update(status="review_required", formal_status="review_required",
                      overall_status="review_required", executable_ran=False)
        return report
    try:
        repetitions = run_code(answer["code"])
    except Unavailable as exc:
        report.update(status="unavailable", formal_status="unavailable", overall_status="unavailable",
                      executable_ran=False, reason=str(exc))
        return report
    passed = len(repetitions) == 3 and all(r["passed"] for r in repetitions)
    report.update(status="pass" if passed else "fail", formal_status="pass" if passed else "fail",
                  overall_status="formal_pass_review_pending" if passed else "formal_fail_review_pending",
                  executable_ran=True, repetitions=repetitions)
    return report


def review_template(raw):
    answer = strict_json(raw.decode("utf-8"))
    validate_answer(answer)
    return {"schema_version": "e1-review/v1", "task_id": "E1", "answer_sha256": digest(raw),
            "reviewer": "", "independence_declaration": "", "criteria": {
                key: {"judgment": "unresolved", "evidence_quotes": [], "reason": ""}
                for key in ("atomicity", "identity", "unknown_outcome", "hot_account",
                            "cross_account_parallelism", "mitigation_and_rollback", "deployment_tradeoffs")},
            "unresolved_claims": [], "novelty": "not_assessed"}


def validate_review(raw, form):
    template = review_template(raw)
    if not isinstance(form, dict):
        raise ValueError("review must be an object")
    for field in ("schema_version", "task_id", "answer_sha256"):
        if form.get(field) != template[field]:
            raise ValueError("review binding mismatch: " + field)
    for field in ("reviewer", "independence_declaration"):
        if not isinstance(form.get(field), str) or not form[field].strip():
            raise ValueError("review requires " + field)
    criteria = form.get("criteria")
    if not isinstance(criteria, dict) or set(criteria) != set(template["criteria"]):
        raise ValueError("review must cover exactly the seven declared criteria")
    answer = strict_json(raw.decode("utf-8"))
    texts = [answer[key] for key in ("code", "explanation", "alternative")
             if isinstance(answer.get(key), str)]
    for key, criterion in criteria.items():
        if not isinstance(criterion, dict) or criterion.get("judgment") not in (
                "supported", "partial", "unsupported", "unresolved"):
            raise ValueError("invalid review judgment: " + key)
        if not isinstance(criterion.get("reason"), str) or not criterion["reason"].strip():
            raise ValueError("review reason required: " + key)
        quotes = criterion.get("evidence_quotes")
        if not isinstance(quotes, list) or any(not isinstance(q, str) or not q.strip() or
                not any(q in text for text in texts) for q in quotes):
            raise ValueError("review quote is absent from the answer: " + key)
        if criterion["judgment"] in ("supported", "partial") and not quotes:
            raise ValueError("supporting evidence required: " + key)
    claims = form.get("unresolved_claims")
    if not isinstance(claims, list) or any(not isinstance(c, str) or not c.strip() for c in claims):
        raise ValueError("unresolved_claims must be a list of nonempty strings")
    if form.get("novelty") != "not_assessed":
        raise ValueError("this evaluation does not automatically admit originality claims")
    return {"status": "review_form_valid", "answer_sha256": digest(raw),
            "identity_or_judgment_authenticated": False,
            "unresolved_criteria": [k for k, c in criteria.items() if c["judgment"] == "unresolved"]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("grade", "review-template"):
        command = sub.add_parser(name)
        command.add_argument("answer", type=Path)
        command.add_argument("--output", type=Path)
    review = sub.add_parser("validate-review")
    review.add_argument("answer", type=Path)
    review.add_argument("review", type=Path)
    review.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        with args.answer.open("rb") as stream:
            raw = stream.read(1024 * 1024 + 1)
        if args.command == "grade":
            result = grade(raw)
        elif args.command == "review-template":
            result = review_template(raw)
        else:
            result = validate_review(raw, strict_json(args.review.read_text(encoding="utf-8")))
        output = json.dumps(result, indent=2, ensure_ascii=True, allow_nan=False) + "\n"
        if args.output:
            # Exclusive creation preserves earlier reports and the submitted answer.
            with args.output.open("x", encoding="utf-8") as stream:
                stream.write(output)
        else:
            sys.stdout.write(output)
        return 0 if args.command != "grade" or result["formal_status"] == "pass" else 2
    except (OSError, ValueError, SyntaxError, TypeError, RecursionError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)[:2000]}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

"""Answer-bound manual review forms. Validation checks structure, not judgment."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

from evaluator import strict_json

CRITERIA = (
    "atomicity_and_error_boundary",
    "global_identity_and_historical_replay",
    "unknown_outcome_recovery",
    "contention_versus_deadlock",
    "cross_account_parallelism_and_deployment",
    "first_mitigation_and_rollback",
)


def digest(answer):
    return hashlib.sha256(json.dumps(answer, sort_keys=True, ensure_ascii=True,
                                    allow_nan=False).encode()).hexdigest()


def template(answer):
    return {"task_id": "E1", "answer_sha256": digest(answer),
            "reviewer_id": "", "independence_declaration": "",
            "criteria": {key: {"rating": None, "evidence": [], "rationale": "",
                                "unresolved_claims": []} for key in CRITERIA},
            "overall_unresolved_claims": [],
            "boundary": "Form validation cannot authenticate identity, independence or correctness of judgment. No aggregate score."}


def validate(answer, form):
    errors = []
    if not isinstance(form, dict):
        return ["review must be an object"]
    if form.get("task_id") != "E1" or form.get("answer_sha256") != digest(answer):
        errors.append("review is not bound to this E1 answer")
    for field in ("reviewer_id", "independence_declaration"):
        if not isinstance(form.get(field), str) or not form[field].strip():
            errors.append(field + " required")
    criteria = form.get("criteria")
    if not isinstance(criteria, dict) or set(criteria) != set(CRITERIA):
        return errors + ["criteria must cover the exact rubric"]
    for key in CRITERIA:
        item = criteria[key]
        if not isinstance(item, dict):
            errors.append(key + ": criterion must be an object")
            continue
        if type(item.get("rating")) is not int or item["rating"] not in (0, 1, 2):
            errors.append(key + ": integer rating 0, 1 or 2 required")
        if not isinstance(item.get("rationale"), str) or not item["rationale"].strip():
            errors.append(key + ": rationale required")
        evidence = item.get("evidence")
        if not isinstance(evidence, list):
            errors.append(key + ": evidence must be a list")
        else:
            if item.get("rating") in (1, 2) and not evidence:
                errors.append(key + ": positive ratings require source quotations")
            for quote in evidence:
                if not isinstance(quote, dict):
                    errors.append(key + ": invalid evidence object")
                    continue
                field, text = quote.get("field"), quote.get("quote")
                if field not in ("code", "explanation", "alternative") or not isinstance(text, str) or not text.strip():
                    errors.append(key + ": invalid evidence field/quote")
                elif not isinstance(answer.get(field), str) or text not in answer[field]:
                    errors.append(key + ": quotation absent from answer")
        unresolved = item.get("unresolved_claims")
        if not isinstance(unresolved, list) or not all(isinstance(x, str) and x.strip() for x in unresolved):
            errors.append(key + ": unresolved_claims must be a list of nonempty strings")
    unresolved = form.get("overall_unresolved_claims")
    if not isinstance(unresolved, list) or not all(isinstance(x, str) and x.strip() for x in unresolved):
        errors.append("overall_unresolved_claims must be a list of nonempty strings")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("template", "validate"))
    parser.add_argument("answer")
    parser.add_argument("review", nargs="?")
    args = parser.parse_args()
    try:
        answer = strict_json(Path(args.answer).read_text(encoding="utf-8"))
        if not isinstance(answer, dict) or answer.get("task_id") != "E1":
            raise ValueError("expected an E1 answer")
        if args.operation == "template":
            result = template(answer)
            code = 0
        else:
            if not args.review:
                raise ValueError("review file required")
            form = strict_json(Path(args.review).read_text(encoding="utf-8"))
            errors = validate(answer, form)
            result = {"status": "invalid" if errors else "form_valid", "errors": errors,
                      "judgment_validated": False, "identity_authenticated": False}
            code = 2 if errors else 0
    except (OSError, ValueError, TypeError) as exc:
        result, code = {"status": "invalid", "reason": str(exc)[:1000]}, 2
    print(json.dumps(result, indent=2, allow_nan=False))
    return code


if __name__ == "__main__":
    sys.exit(main())

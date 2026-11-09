"""Evidence-bound review forms. Review completeness is not review correctness."""
from .runner import digest, validate_answer


CRITERIA = {
    "atomicity": "Identifies one transaction for allowance, durable decision and accepted ledger row; DB errors are not business rejections.",
    "identity": "Uses global key identity, compares account and amount, preserves accepted and rejected historical replies.",
    "unknown_outcome": "Distinguishes rollback from unknown commit outcome; replays the same key/payload to recover the durable decision.",
    "contention_vs_cycles": "Distinguishes queueing on a hot lock from a multi-lock wait cycle and identifies evidence needed to diagnose each.",
    "parallelism": "Explains SQLite's single-writer limitation, WAL's limits, and how other accounts could progress with another storage/partition design.",
    "mitigation": "Chooses a first mitigation tied to the diagnosis and discusses tradeoffs, bounded retries/backpressure or transaction duration.",
    "rollback": "Names an observable correctness and latency rollback trigger, with a measurement/baseline rather than a fabricated latency gold label.",
    "deployment": "Explains durability, process coordination, uniqueness across partitions and migration/operational costs; marks untested claims.",
}


def template(answer):
    validate_answer(answer)
    return {
        "task_id": "E1", "answer_sha256": digest(answer),
        "reviewer": "", "independence_declaration": "",
        "criteria": {key: {"assessment": "unreviewed", "quotes": [], "reason": ""}
                     for key in CRITERIA},
        "unresolved_claims": [],
    }


def validate_review(answer, review):
    validate_answer(answer)
    errors = []
    if not isinstance(review, dict):
        return ["review must be an object"]
    if review.get("task_id") != "E1" or review.get("answer_sha256") != digest(answer):
        errors.append("review is not bound to this exact answer")
    for field in ("reviewer", "independence_declaration"):
        if not isinstance(review.get(field), str) or not review[field].strip():
            errors.append(f"missing {field}")
    criteria = review.get("criteria")
    if not isinstance(criteria, dict) or set(criteria) != set(CRITERIA):
        errors.append("review must cover exactly the declared criteria")
        return errors
    sources = [answer.get(field, "") for field in ("explanation", "code", "alternative")]
    for key, entry in criteria.items():
        if not isinstance(entry, dict):
            errors.append(f"{key}: invalid criterion entry")
            continue
        assessment = entry.get("assessment")
        if assessment not in ("supported", "partial", "unsupported", "unresolved"):
            errors.append(f"{key}: incomplete assessment")
        if not isinstance(entry.get("reason"), str) or not entry["reason"].strip():
            errors.append(f"{key}: reason is required")
        quotes = entry.get("quotes")
        if not isinstance(quotes, list) or any(not isinstance(q, str) or not q or
                                               not any(q in text for text in sources) for q in quotes):
            errors.append(f"{key}: quotes must occur verbatim in the answer")
        if assessment in ("supported", "partial") and not quotes:
            errors.append(f"{key}: positive assessment needs answer evidence")
    claims = review.get("unresolved_claims")
    if not isinstance(claims, list) or any(not isinstance(c, str) or not c.strip() for c in claims):
        errors.append("unresolved_claims must be a list of nonempty strings")
    return errors

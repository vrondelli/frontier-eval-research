"""Local stage ordering and structurally checked, answer-bound review forms."""
from .grader import ROOT, bindings, digest, grade, validate_answer


CRITERIA = (
    "atomic_boundary", "global_identity_and_history", "unknown_outcome_replay",
    "contention_and_cycles", "parallelism_and_first_mitigation", "rollback_and_tradeoffs",
)


def initial_view():
    text = (ROOT / "input/E1.md").read_text(encoding="utf-8")
    facts = [line for line in text.splitlines() if line.startswith(tuple(f"F{i}." for i in range(1, 6)))]
    return {"task_id": "E1", "stage": "initial", "prompt":
            "Concurrent allowance and duplicate identity. Explain your design and implement the service.\n\n"
            + "\n\n".join(facts)
            + "\n\nReturn task_id E1, code (complete Service source), and explanation. Explain atomic boundaries, "
              "global identity, historical decisions, unknown-outcome replay and deployment tradeoffs. "
              "Alternative constructions may return alternative_format:true, alternative and explanation "
              "for independent review. A fixed operational reveal follows after this answer is sealed. "
              "Runtime: Linux Python 3.11+, standard library, 512 MiB address space, 256 FDs, 8 MiB files, "
              "10 CPU seconds per process, six seconds per reply, 64 KiB replies, isolated filesystem/network. "
              "Public tables must be real tables with fewer than 100 rows, and DB/sidecars regular files."}


def start():
    return {"protocol": "e1-stages/1", "stage": "initial", "sources": bindings(), "view": initial_view()}


def reveal(state, first):
    if state != start():
        raise ValueError("initial state differs from the declared initial view/source bindings")
    validate_answer(first)
    return {"protocol": "e1-stages/1", "stage": "revealed", "sources": bindings(),
            "initial_answer": first, "initial_sha256": digest(first),
            "view": {"task_id": "E1", "stage": "final",
                     "prompt": (ROOT / "input/E1.md").read_text(encoding="utf-8")}}


def finish(state, final):
    if not isinstance(state, dict) or "initial_answer" not in state:
        raise ValueError("missing sealed first answer")
    expected = reveal(start(), state["initial_answer"])
    if state != expected:
        raise ValueError("staged state or initial answer digest changed")
    result = grade(final)
    result.update(staged=True, initial_answer=state["initial_answer"],
                  initial_sha256=state["initial_sha256"],
                  staging_claim="local ordering and content binding, not external authentication")
    return result


def review_template(answer, reviewer_id=""):
    validate_answer(answer)
    return {"protocol": "e1-review/1", "answer_sha256": digest(answer), "reviewer_id": reviewer_id,
            "independence_declaration": "", "criteria": {
                name: {"rating": None, "quotes": [], "rationale": "", "unresolved_claims": []}
                for name in CRITERIA},
            "alternative_assessment": "", "first_to_final_revision_assessment": "",
            "overall_notes": ""}


def validate_review(answer, review):
    validate_answer(answer)
    if (not isinstance(review, dict) or review.get("protocol") != "e1-review/1"
            or review.get("answer_sha256") != digest(answer)):
        raise ValueError("review is not bound to this answer")
    for field in ("reviewer_id", "independence_declaration"):
        if not isinstance(review.get(field), str) or not review[field].strip():
            raise ValueError(f"review requires {field}")
    if not isinstance(review.get("criteria"), dict) or set(review["criteria"]) != set(CRITERIA):
        raise ValueError("review must cover every rubric criterion exactly once")
    corpus = answer["explanation"] + "\n" + answer.get("alternative", "")
    for name, entry in review["criteria"].items():
        if not isinstance(entry, dict):
            raise ValueError(f"invalid review entry: {name}")
        rating = entry.get("rating")
        if type(rating) is not int or rating not in (0, 1, 2):
            raise ValueError(f"{name}: rating must be 0, 1 or 2")
        if not isinstance(entry.get("rationale"), str) or not entry["rationale"].strip():
            raise ValueError(f"{name}: rationale required")
        quotes = entry.get("quotes")
        if (not isinstance(quotes, list) or any(not isinstance(q, str) or not q or q not in corpus for q in quotes)
                or (rating > 0 and not quotes)):
            raise ValueError(f"{name}: positive credit requires exact quotes from the answer")
        unresolved = entry.get("unresolved_claims")
        if not isinstance(unresolved, list) or any(not isinstance(item, str) for item in unresolved):
            raise ValueError(f"{name}: unresolved_claims must be strings")
    if answer.get("alternative_format"):
        assessment = review.get("alternative_assessment")
        if not isinstance(assessment, str) or not assessment.strip():
            raise ValueError("alternative answer needs an alternative assessment")
    return {"review_status": "structurally_valid", "answer_sha256": digest(answer),
            "limitation": "does not authenticate reviewer identity, independence or correctness of judgments"}

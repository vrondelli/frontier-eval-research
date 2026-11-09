"""Local first-answer custody for the fixed hot-account reveal (not authentication)."""
from .runner import ROOT, digest


def source_text():
    return (ROOT / "input" / "E1.md").read_text(encoding="utf-8")


def seal(document):
    return {**document, "state_sha256": digest(document)}


def verify(document, expected_stage):
    if not isinstance(document, dict):
        raise ValueError("invalid staged document")
    payload = {k: v for k, v in document.items() if k != "state_sha256"}
    if document.get("state_sha256") != digest(payload):
        raise ValueError("staged state digest mismatch")
    if document.get("stage") != expected_stage or document.get("task_id") != "E1":
        raise ValueError("incorrect stage/task")
    if document.get("source_sha256") != digest(source_text()):
        raise ValueError("task source changed")


def start():
    text = source_text()
    # Construct initial view from the public F1-F5 contract without the fixed reveal.
    requirements = text[text.index("F1."):text.index("F6.")].strip()
    view = ("E1 initial design and implementation\n\n" + requirements +
            "\n\nReturn task_id E1, code (the complete Python Service source string), "
            "and explanation of atomic boundaries, identity scope, unknown-outcome replay "
            "and deployment tradeoffs. Alternative architectures may use alternative_format:true, "
            "alternative and explanation for review only. A later stage supplies operational evidence.\n\n"
            "Execution constraints: Linux/Python 3.11+, SQLite; 512 MiB address space, "
            "256 file descriptors, 10 CPU seconds per process, 8 MiB file size, "
            "6 seconds per reply and 64 KiB reply size. Workers have a private network/PID "
            "namespace, disposable /state and /tmp, read-only runtime/source files, "
            "no benchmark/import access and no inherited environment secrets. Public tables "
            "must be real tables with fewer than 100 rows each; database/sidecars cannot be symlinks. "
            "Three fresh-database repetitions check both legal serial outcomes. Supplemental "
            "probes cover concurrent identical keys, exact exhaustion and historical replay "
            "after spending. These are finite checks, not performance measurements.")
    return seal({"schema_version": "e1-staged/v1", "task_id": "E1", "stage": "initial",
                 "source_sha256": digest(text), "view": view})


def reveal(initial, first_answer):
    verify(initial, "initial")
    if initial != start():
        raise ValueError("initial state differs from canonical initial view")
    return seal({"schema_version": "e1-staged/v1", "task_id": "E1", "stage": "revealed",
                 "source_sha256": digest(source_text()), "parent": initial,
                 "first_answer": first_answer, "first_answer_sha256": digest(first_answer),
                 "view": source_text()})


def first_answer_from(revealed):
    verify(revealed, "revealed")
    if reveal(revealed["parent"], revealed["first_answer"]) != revealed:
        raise ValueError("revealed state/lineage differs from canonical replay")
    return revealed["first_answer"]

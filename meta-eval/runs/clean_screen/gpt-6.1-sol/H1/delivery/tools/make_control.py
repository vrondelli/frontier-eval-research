"""Create an authored answer for harness checks; never send this to a solver."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python tools/make_control.py OUTPUT.json")
    answer = {
        "task_id": "E1",
        "code": (ROOT / "tests/fixtures/reference_service.py").read_text(encoding="utf-8"),
        "explanation": (ROOT / "tests/fixtures/reference_explanation.md").read_text(encoding="utf-8"),
        "provenance": "authored harness control, not measured solver performance",
    }
    with Path(sys.argv[1]).open("x", encoding="utf-8") as stream:
        json.dump(answer, stream, indent=2)
        stream.write("\n")

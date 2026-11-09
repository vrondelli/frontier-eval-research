"""Export only an explicitly named authored control for Linux isolation checks."""

import argparse
import json
from pathlib import Path

from controls.fixtures import EXPLANATION, NEGATIVE_CONTROLS, source


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name", choices=("reference", "exclusive_valid", *NEGATIVE_CONTROLS))
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump({"task_id": "E1", "code": source(args.name), "explanation": EXPLANATION}, stream, indent=2)
        stream.write("\n")

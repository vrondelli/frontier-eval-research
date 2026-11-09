#!/usr/bin/env python3
"""CLI for the public-input reconstruction of the E1 evaluation."""
import argparse
import json
from pathlib import Path
import sys

from evaluation.grader import ROOT, grade
from evaluation.protocol import finish, reveal, review_template, start, validate_review
from evaluation.sandbox import strict_json


def load(path):
    # Bound administrative inputs before parsing; submitted code is still never imported here.
    data = Path(path).read_bytes()
    if len(data) > 2 * 1024**2:
        raise ValueError("answer/state file exceeds 2 MiB")
    return strict_json(data.decode("utf-8"))


def save_exclusive(path, value):
    with Path(path).open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=True, allow_nan=False)
        stream.write("\n")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("question")
    grade_parser = commands.add_parser("grade")
    grade_parser.add_argument("answer")
    commands.add_parser("demo")
    starter = commands.add_parser("start-case")
    starter.add_argument("state")
    revealer = commands.add_parser("reveal-case")
    revealer.add_argument("state")
    revealer.add_argument("answer")
    revealer.add_argument("next_state")
    finisher = commands.add_parser("finish-case")
    finisher.add_argument("state")
    finisher.add_argument("answer")
    finisher.add_argument("result")
    template = commands.add_parser("review-template")
    template.add_argument("answer")
    template.add_argument("review")
    validator = commands.add_parser("validate-review")
    validator.add_argument("answer")
    validator.add_argument("review")
    args = parser.parse_args(argv)
    try:
        if args.command == "question":
            print((ROOT / "input/E1.md").read_text(encoding="utf-8"))
            return 0
        if args.command in ("grade", "demo"):
            answer_path = args.answer if args.command == "grade" else ROOT / "examples/E1.json"
            result = grade(load(answer_path))
        elif args.command == "start-case":
            result = start()
            save_exclusive(args.state, result)
            result = result["view"]
        elif args.command == "reveal-case":
            result = reveal(load(args.state), load(args.answer))
            save_exclusive(args.next_state, result)
            result = result["view"]
        elif args.command == "finish-case":
            result = finish(load(args.state), load(args.answer))
            save_exclusive(args.result, result)
        elif args.command == "review-template":
            result = review_template(load(args.answer))
            save_exclusive(args.review, result)
        else:
            result = validate_review(load(args.answer), load(args.review))
        print(json.dumps(result, indent=2, ensure_ascii=True, allow_nan=False))
        if "formal_status" in result:
            return 0 if result["formal_status"] == "pass" else 2
        return 0
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(json.dumps({"formal_status": "invalid", "overall_status": "invalid",
                          "reason": f"{type(exc).__name__}: {exc}"}, indent=2))
        return 2


if __name__ == "__main__":
    sys.exit(main())

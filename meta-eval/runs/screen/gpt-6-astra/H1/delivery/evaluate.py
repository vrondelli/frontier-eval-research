#!/usr/bin/env python3
"""Standalone CLI for E1. Uses only the Python 3.11+ standard library."""
import argparse
import json
from pathlib import Path
import sys

from evaluation.runner import grade
from evaluation.review import template, validate_review
from evaluation.sandbox import decode_json
from evaluation.staging import first_answer_from, reveal, source_text, start


def read(path):
    data = Path(path).read_bytes()
    if len(data) > 2 * 1024 * 1024:
        raise ValueError("input exceeds 2 MiB envelope limit")
    return decode_json(data.decode("utf-8"))


def write_new(path, value):
    with Path(path).open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("question")
    grader = commands.add_parser("grade")
    grader.add_argument("answer")
    grader.add_argument("--core-only", action="store_true", help="only the declared overlap/replay/mismatch/B schedule")
    grader.add_argument("--output", help="also save report to a new file")
    begin = commands.add_parser("start-case")
    begin.add_argument("output")
    show = commands.add_parser("reveal-case")
    show.add_argument("initial")
    show.add_argument("first_answer")
    show.add_argument("output")
    finish = commands.add_parser("finish-case")
    finish.add_argument("revealed")
    finish.add_argument("answer")
    finish.add_argument("output")
    review = commands.add_parser("review-template")
    review.add_argument("answer")
    review.add_argument("output")
    validate = commands.add_parser("validate-review")
    validate.add_argument("answer")
    validate.add_argument("review")
    args = parser.parse_args(argv)
    try:
        if args.command == "question":
            print(source_text())
            return 0
        if args.command == "start-case":
            write_new(args.output, start())
            return 0
        if args.command == "reveal-case":
            write_new(args.output, reveal(read(args.initial), read(args.first_answer)))
            return 0
        if args.command == "review-template":
            write_new(args.output, template(read(args.answer)))
            return 0
        if args.command == "validate-review":
            errors = validate_review(read(args.answer), read(args.review))
            print(json.dumps({"status": "invalid" if errors else "complete_review_form",
                              "errors": errors,
                              "scope": "Checks binding and evidence presence, not reviewer independence or judgment validity."}, indent=2))
            return 2 if errors else 0
        if args.command == "finish-case":
            first = first_answer_from(read(args.revealed))
            report = grade(read(args.answer))
            report["staging"] = {"first_answer": first, "custody": "local hash-bound sequence; not external authentication"}
        else:
            report = grade(read(args.answer), extended=not args.core_only)
        if args.output:
            write_new(args.output, report)
        print(json.dumps(report, indent=2, allow_nan=False))
        return 0 if report["formal_status"] == "pass" else 2
    except (ValueError, OSError, KeyError, TypeError, RecursionError) as exc:
        print(json.dumps({"task_id": "E1", "status": "invalid", "formal_status": "invalid",
                          "reason": str(exc)}, indent=2))
        return 2


if __name__ == "__main__":
    sys.exit(main())

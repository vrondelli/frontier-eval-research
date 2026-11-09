"""Run the scored meta-eval. Uses saved packages; makes no model calls."""
import argparse
import json
import os
from pathlib import Path

from meta_eval.engine import run_existing
from meta_eval.runtime import doctor


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=["doctor", "run", "qualify", "score"])
    p.add_argument("--output", type=Path, default=Path("meta-eval-results"))
    p.add_argument("--tasks", nargs="+")
    p.add_argument("--ids", nargs="+")
    p.add_argument("--jobs", type=int, default=2)
    p.add_argument("--image", default="python:3.14-slim")
    p.add_argument("--package", type=Path)
    p.add_argument("--owner-manifest", type=Path)
    p.add_argument("--reviews", type=Path, help="Optional human declarations bound to exact package hashes")
    a = p.parse_args()
    root = Path(__file__).resolve().parent
    if os.name != "posix":
        p.error("Use Linux/WSL with Python3.14, Docker and bubblewrap; no unisolated host fallback")
    if not 1 <= a.jobs <= 8:
        p.error("--jobs must be1..8")
    if a.command == "doctor":
        print(json.dumps(doctor(root, a.image), indent=2))
        return 0
    if a.command == "qualify":
        from meta_eval.qualification import qualify
        return qualify(root, a.output, a.image)
    if a.command == "score":
        if a.package is None or a.owner_manifest is None:
            p.error("score requires --package and --owner-manifest")
        from meta_eval.generic import run_manifest
        report = run_manifest(root, a.package, a.owner_manifest, a.output, a.image)
        print(json.dumps(report["scoring"], indent=2))
        return 0
    report = run_existing(root, a.output.resolve(), a.jobs, a.tasks, a.ids, a.image, a.reviews)
    return 2 if any(r["scoring"]["verdict"] == "instrument_error" for r in report["subjects"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())

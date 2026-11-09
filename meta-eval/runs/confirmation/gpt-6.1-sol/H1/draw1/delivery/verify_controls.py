"""Record authored controls using a named development or isolation backend.

--trusted-controls runs only fixture names shipped here, outside bwrap. It cannot
load a submission. Its report is explicitly not sandbox integration evidence.
"""

import argparse
import json
import platform
import tempfile
from pathlib import Path

from controls.fixtures import NEGATIVE_CONTROLS, source
from e1eval.isolation import Unavailable, Worker, preflight
from e1eval.suite import run_trial


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trusted-controls", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    backend = "trusted-authored-controls-only" if args.trusted_controls else "linux-bubblewrap"
    report = {"schema_version": "e1-controls/v1", "backend": backend,
              "platform": platform.platform(), "python": platform.python_version(),
              "model_performance_claim": False, "controls": [], "status": "fail"}
    worker_factory = Worker
    if args.trusted_controls:
        from tests.trusted_transport import TrustedWorker
        worker_factory = TrustedWorker
    with args.output.open("x", encoding="utf-8") as stream:
        try:
            with tempfile.TemporaryDirectory(prefix="e1-controls-", dir=Path.cwd()) as temporary:
                base = Path(temporary)
                candidate = base / "candidate.py"
                candidate.write_text(source("reference"), encoding="utf-8")
                if not args.trusted_controls:
                    probe = base / "probe"
                    probe.mkdir()
                    preflight(probe, candidate)
                for name in ("reference", "exclusive_valid", *NEGATIVE_CONTROLS):
                    candidate.write_text(source(name), encoding="utf-8")
                    trials = []
                    for index in range(3):
                        state = base / f"{name}-{index}"
                        state.mkdir()
                        trials.append(run_trial(state, name if args.trusted_controls else candidate,
                                                worker_factory, index))
                    expected = "fail" if name in NEGATIVE_CONTROLS else "pass"
                    matched = all(t["status"] == expected and t.get("barrier", {}).get("armed") == 2
                                  and "timed out" not in str(t) for t in trials)
                    report["controls"].append({"name": name, "expected": expected,
                                               "matched": matched, "trials": trials})
                report["status"] = "pass" if all(c["matched"] for c in report["controls"]) else "fail"
        except Unavailable as exc:
            report.update(status="unavailable", error=str(exc))
        json.dump(report, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"status": report["status"], "backend": backend,
                      "controls": [{"name": c["name"], "matched": c["matched"]} for c in report["controls"]]}))
    return 0 if report["status"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())

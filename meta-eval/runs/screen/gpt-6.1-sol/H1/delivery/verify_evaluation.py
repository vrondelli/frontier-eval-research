"""Reproduce local tests and CLI smoke checks, preserving honest availability results."""
import datetime
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def invoke(*args):
    process = subprocess.run([sys.executable, *map(str, args)], cwd=ROOT,
                             capture_output=True, text=True, timeout=180)
    return {"command": ["python", *map(str, args)], "exit_code": process.returncode,
            "stdout": process.stdout, "stderr": process.stderr}


def main():
    evidence = {"recorded_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "python": sys.version, "platform": platform.platform(), "checks": []}
    tests = invoke("-m", "unittest", "discover", "-s", "tests", "-v")
    evidence["checks"].append(tests)
    assert tests["exit_code"] == 0, tests
    demo = invoke("benchmark.py", "demo")
    report = json.loads(demo["stdout"])
    assert report["formal_status"] in ("pass", "unavailable"), demo
    assert demo["exit_code"] == (0 if report["formal_status"] == "pass" else 2), demo
    evidence["checks"].append(demo)
    evidence["isolated_execution_status"] = report["formal_status"]
    with tempfile.TemporaryDirectory(dir=ROOT) as temp:
        temp = Path(temp)
        first, revealed, result = [temp / name for name in ("first-state.json", "revealed.json", "result.json")]
        start = invoke("benchmark.py", "start-case", first)
        assert start["exit_code"] == 0 and "F6." not in json.loads(start["stdout"])["prompt"], start
        reveal = invoke("benchmark.py", "reveal-case", first, "examples/E1.json", revealed)
        assert reveal["exit_code"] == 0 and "F6." in json.loads(reveal["stdout"])["prompt"], reveal
        finish = invoke("benchmark.py", "finish-case", revealed, "examples/E1.json", result)
        staged = json.loads(result.read_text())
        assert staged["staged"] is True and staged["formal_status"] == report["formal_status"], finish
        assert finish["exit_code"] == demo["exit_code"], finish
        evidence["checks"].append({"check": "CLI staged roundtrip", "pass": True,
                                   "finish_formal_status": staged["formal_status"],
                                   "initial_sha256": staged["initial_sha256"]})
        repeated = invoke("benchmark.py", "start-case", first)
        assert repeated["exit_code"] == 2, repeated
        alternative = temp / "alternative.json"
        alternative.write_text(json.dumps({"task_id": "E1", "alternative_format": True,
                                          "alternative": "account sequencer", "explanation": "review this construction"}))
        alt = invoke("benchmark.py", "grade", alternative)
        assert alt["exit_code"] == 2 and json.loads(alt["stdout"])["formal_status"] == "review_required", alt
        malformed = temp / "malformed.json"
        malformed.write_text('{"task_id":"E1","task_id":"E1"}')
        invalid = invoke("benchmark.py", "grade", malformed)
        assert invalid["exit_code"] == 2 and json.loads(invalid["stdout"])["formal_status"] == "invalid", invalid
        template = invoke("benchmark.py", "review-template", "examples/E1.json", temp / "review.json")
        assert template["exit_code"] == 0, template
        unfilled = invoke("benchmark.py", "validate-review", "examples/E1.json", temp / "review.json")
        assert unfilled["exit_code"] == 2, unfilled
        evidence["checks"].append({"check": "CLI exclusive state, alternative route, duplicate JSON and incomplete review",
                                   "pass": True})
    manifest = json.loads((ROOT / "MANIFEST.json").read_text())
    for entry in manifest["files"]:
        data = (ROOT / entry["path"]).read_bytes()
        assert len(data) == entry["bytes"] and hashlib.sha256(data).hexdigest() == entry["sha256"], entry
    evidence["checks"].append({"check": "all supplied manifest assets unchanged", "pass": True})
    (ROOT / "validation-results.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"local_validation": "pass", "isolated_execution": report["formal_status"],
                      "evidence": "validation-results.json"}))


if __name__ == "__main__":
    main()

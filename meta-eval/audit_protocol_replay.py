"""Repeat one saved grader/control pair, preserving operational variation."""
import json
from pathlib import Path
from meta_eval.runtime import execute_isolated

root = Path(__file__).resolve().parent
source = root / "grades/scored-v2-final/H1_budget_diagnostic/gpt-6.1-sol/H1/draw3/01-correct_accepted.json"
folder = root / "grades/scored-v2-flakiness-audit"
old = json.loads(source.read_text())
rows = []
for i in range(3):
    receipt = execute_isolated(old["command"], root, 150)
    (folder / f"linux-accepted-repeat-{i+1}.json").write_text(json.dumps(receipt, indent=2) + "\n")
    value = receipt.get("decoded") or {}
    rows.append({"repeat": i + 1, "status": receipt["status"], "exit_code": receipt.get("exit_code"),
                 "formal_status": value.get("formal_status"),
                 "protocol_stdout_error": "worker left protocol stdout open" in json.dumps(value)})
summary = {"kind": "same_saved_grader_same_correct_control_posthoc_replay", "model_calls": 0,
           "original_rejection_preserved": str(source.relative_to(root)), "replays": rows,
           "prior_wrong_platform_attempt": "WINDOWS-UNAVAILABLE-SUMMARY.json; three unavailable calls, not executed grader replays",
           "scope": "Same artifact repetitions, not new author trials. Preserve the original observation even if later runs pass."}
(folder / "SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(rows))

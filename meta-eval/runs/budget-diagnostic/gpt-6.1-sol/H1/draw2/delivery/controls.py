"""Generate authored controls, and optionally run them through the real evaluator."""
from pathlib import Path
import argparse
import json
import sys

from evaluate import evaluate

REFERENCE = Path(__file__).with_name("controls") / "reference.py"
EXPLANATION = """Reserve the SQLite writer before reading identity and allowance. A single transaction
commits the decision, allowance decrement and one ledger entry, or rolls everything back on error.
Keys identify requests globally; a conflict in either payload field changes nothing. Persist both
accepted and rejected historical results. After a timeout with an unknown commit outcome, retry the
same identity and payload to recover its decision; never mint a new identity for that retry.

SQLite serializes writers across accounts, even in WAL mode. Hot-account serialization follows
from the allowance invariant; lock waits alone do not establish a deadlock cycle. Inspect actual
wait dependencies and SQLite busy/snapshot errors before attributing deadlock retries to cycles.
A first mitigation is bounded per-account queuing and admission backpressure, preserving global
key ownership and atomic decision writes. Measure queue wait, database lock wait, retries and p99.
Rollback the rollout immediately on a duplicate ledger row, changed historical decision or negative
allowance; roll back if p99 exceeds the agreed SLO for a sustained window, using observed baseline
and an explicit rollout threshold. Sharding by account can parallelize different accounts, but
needs a global key directory and atomic coordination for cross-account key conflicts. A row-locking
database is another deployment option. WAL can improve reader/writer overlap, not parallel writers.
The finite checks do not establish production throughput, crash/power-loss survival or universal
schedule safety. These mitigations need workload testing and an explicit migration/rollback plan.
"""


def answers():
    source = REFERENCE.read_text(encoding="utf-8")
    variations = {
        "reference": source,
        "no-ledger": source.replace('db.execute("INSERT INTO ledger VALUES (?,?,?)", (key, account, amount))', 'pass'),
        "lost-rejection": source.replace('db.execute("INSERT INTO decisions VALUES (?,?,?,?,?)", (key, account, amount, status, remaining))',
                                         'if status == "accepted":\n                    db.execute("INSERT INTO decisions VALUES (?,?,?,?,?)", (key, account, amount, status, remaining))'),
        "current-replay": source.replace('"remaining": old[3]',
                                         '"remaining": db.execute("SELECT remaining FROM accounts WHERE account=?", (account,)).fetchone()[0]'),
        "ignores-payload": source.replace('old[:2] == (account, amount)', 'True'),
        "overspend": source.replace('if remaining >= amount:', 'if remaining >= 0:'),
        "resets-on-init": source.replace("INSERT OR IGNORE INTO accounts", "INSERT OR REPLACE INTO accounts"),
        "always-reject": 'class Service:\n    def __init__(self,path): pass\n    def apply(self,request): return {"status":"rejected","remaining":100}\n',
        "database-error-as-rejection": source.replace('raise\n        finally:', 'return {"status":"rejected","remaining":0}\n        finally:').replace('db.execute("BEGIN IMMEDIATE")', 'db.execute("THIS IS NOT SQL")'),
        "process-local": source.replace('self.path = path', 'self.path = path').replace('db = sqlite3.connect(self.path, timeout=4)', 'db = sqlite3.connect(":memory:", timeout=4)'),
    }
    result = {name: {"task_id": "E1", "code": code, "explanation": EXPLANATION}
              for name, code in variations.items()}
    result["alternative"] = {"task_id": "E1", "alternative_format": True,
                             "alternative": "A distributed transactional store with a global identity index.",
                             "explanation": "Requires independent architecture review beyond the SQLite interface."}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="create a NEW directory of control answer JSON files")
    parser.add_argument("--check", action="store_true", help="execute all controls in the supported sandbox")
    args = parser.parse_args()
    if not args.write and not args.check:
        parser.error("choose --write or --check")
    controls = answers()
    if args.write:
        args.write.mkdir(exist_ok=False, parents=True)
        for name, answer in controls.items():
            (args.write / (name + ".json")).write_text(json.dumps(answer, indent=2), encoding="utf-8")
    if args.check:
        reports = {name: evaluate(answer) for name, answer in controls.items()}
        expected = {name: ("pass" if name == "reference" else "review_required" if name == "alternative" else "fail")
                    for name in controls}
        observed = {name: report["formal_status"] for name, report in reports.items()}
        print(json.dumps({"expected": expected, "observed": observed, "reports": reports}, indent=2))
        return 0 if expected == observed else 2
    return 0


if __name__ == "__main__":
    sys.exit(main())

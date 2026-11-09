
import argparse, json, sys
from pathlib import Path
from _oracle import canonical, execute, loads
from optimizer import optimize
p=argparse.ArgumentParser()
p.add_argument("command", choices=["run"])
p.add_argument("--request", required=True)
p.add_argument("--optimize", action="store_true")
a=p.parse_args()
mode=Path(__file__).with_name("mode.txt").read_text()
try:
    raw=Path(a.request).read_text(encoding="utf-8")
    r=json.loads(raw) if mode == "duplicate" else loads(raw)
    execute(r)
    plan=optimize(r["plan"]) if a.optimize else r["plan"]
    result=execute({"tables":r["tables"], "plan":plan})
    if mode == "counter": result["join_comparisons"]=0
    if mode == "bool-counter": result["join_comparisons"]=False
    if mode == "dedup":
        result["rows"]=list({canonical(row):row for row in result["rows"]}.values())
    if mode == "bool-rows":
        for row in result["rows"]:
            for key,value in row.items():
                if type(value) is int and value == 1: row[key]=True
    if mode == "plan-lie" and a.optimize: result["optimized_plan"]=r["plan"]
    print(json.dumps(result))
except Exception as error:
    if mode == "invalid-stdout": print("{}")
    print(str(error), file=sys.stderr)
    sys.exit(2)

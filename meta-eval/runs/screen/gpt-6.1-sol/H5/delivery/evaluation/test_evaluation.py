"""Self-tests for the oracle, grader, and defect sensitivity (stdlib only)."""
import copy
import itertools
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import evaluate as grader
from cases import Case, build_cases, cmp, col, fixtures, group, join, lit, scan
from oracle import Invalid, bag, canonical, execute, truth


# This is a grader control, not a deliverable solution: its CLI executes through
# the oracle. Hand-computed anchors and SQLite independently check the oracle.
CONTROL_OPTIMIZER = '''
import copy
from pathlib import Path

def refs(obj):
    if isinstance(obj, dict):
        if set(obj) == {"col"}: return {obj["col"]}
        return set().union(*(refs(v) for v in obj.values()))
    if isinstance(obj, list): return set().union(*(refs(v) for v in obj))
    return set()

def optimize(plan):
    mode = Path(__file__).with_name("mode.txt").read_text()
    if mode == "noop": return copy.deepcopy(plan)
    p = copy.deepcopy(plan)
    for key in ("input", "left", "right"):
        if key in p: p[key] = optimize(p[key])
    if mode == "mutate":
        old = copy.deepcopy(plan)
        plan.clear()
        plan.update({"op":"filter", "input":old, "predicate":{"eq":[{"lit":1},{"lit":1}]}})
        return copy.deepcopy(plan)
    if p["op"] != "filter" or p["input"]["op"] != "join": return p
    j = p["input"]
    if mode == "outer" and j["kind"] == "left":
        j["right"] = {"op":"filter", "input":j["right"], "predicate":p["predicate"]}
        return j
    if j["kind"] != "inner": return p
    terms = p["predicate"].get("and", [p["predicate"]])
    remaining = []
    push = {"left": [], "right": []}
    for term in terms:
        fields = refs(term)
        side = next((side for side in push if j[side]["op"] == "scan" and fields
                     and all(f.startswith(j[side]["as"] + ".") for f in fields)), None)
        if side: push[side].append(term)
        else: remaining.append(term)
    for side, predicates in push.items():
        if predicates:
            j[side] = {"op":"filter", "input":j[side], "predicate":predicates[0]
                       if len(predicates) == 1 else {"and":predicates}}
    if not remaining: return j
    p["predicate"] = remaining[0] if len(remaining) == 1 else {"and":remaining}
    return p
'''

CONTROL_CLI = '''
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
'''


def make_control(root, mode="correct"):
    root.mkdir(parents=True, exist_ok=True)
    for name in grader.PROTECTED:
        shutil.copyfile(grader.BASELINE / name, root / name)
    shutil.copyfile(grader.HERE / "oracle.py", root / "_oracle.py")
    (root / "engine.py").write_text("from _oracle import execute\n", encoding="utf-8")
    (root / "optimizer.py").write_text(CONTROL_OPTIMIZER, encoding="utf-8")
    (root / "query_cli.py").write_text(CONTROL_CLI, encoding="utf-8")
    (root / "mode.txt").write_text(mode, encoding="utf-8")


class OracleTests(unittest.TestCase):
    def run_plan(self, plan, tables=None):
        return execute({"tables": fixtures() if tables is None else tables, "plan": plan})

    def test_bag_and_exact_json_types(self):
        self.assertNotEqual(bag([{"x": 1}]), bag([{"x": True}]))
        self.assertNotEqual(bag([{"x": 1}]), bag([{"x": 1.0}]))
        self.assertNotEqual(bag([{"x": 1}]), bag([{"x": 1}, {"x": 1}]))
        self.assertEqual(bag([{"x": 2}, {"x": 1}]), bag([{"x": 1}, {"x": 2}]))

    def test_join_anchor(self):
        result = self.run_plan(join())
        self.assertEqual(result["join_comparisons"], 25)
        self.assertEqual(len(result["rows"]), 5)
        self.assertEqual(sum(row["a.id"] == 1 for row in result["rows"]), 4)
        self.assertFalse(any(row["a.id"] is None for row in result["rows"]))
        result = self.run_plan(join("left"))
        self.assertEqual(len(result["rows"]), 7)
        self.assertEqual(sum(row["b.id"] is None for row in result["rows"]), 2)

    def test_empty_right_schema_anchor(self):
        result = self.run_plan(join("left", right=scan("empty", "b")))
        self.assertEqual(result["join_comparisons"], 0)
        self.assertEqual(len(result["rows"]), 5)
        self.assertEqual(set(result["rows"][0]), {"a.id", "a.v", "a.s", "b.id", "b.v", "b.s"})
        self.assertTrue(all(row["b.v"] is None for row in result["rows"]))

    def test_group_anchors(self):
        result = self.run_plan(group(scan()))
        self.assertEqual(result["rows"], [{"all": 5, "nonnull": 4, "total": 10**40 + 3}])
        self.assertEqual(self.run_plan(group(scan("empty")))["rows"],
                         [{"all": 0, "nonnull": 0, "total": None}])
        self.assertEqual(self.run_plan(group(scan("empty"), ["a.id"]))["rows"], [])
        values = self.run_plan(group(scan(), ["a.id"]))["rows"]
        self.assertIn({"a.id": 2, "all": 1, "nonnull": 0, "total": None}, values)
        self.assertIn({"a.id": None, "all": 1, "nonnull": 1, "total": -7}, values)

    def test_truth_tables_anchor(self):
        def pred(value):
            return cmp("eq", lit(None if value is None else int(value)), lit(1))
        vals = [True, False, None]
        and_table = [[True, False, None], [False, False, False], [None, False, None]]
        or_table = [[True, True, True], [True, False, None], [True, None, None]]
        for i, a in enumerate(vals):
            self.assertIs(truth({"not": pred(a)}, {}), None if a is None else not a)
            for j, b in enumerate(vals):
                self.assertIs(truth({"and": [pred(a), pred(b)]}, {}), and_table[i][j])
                self.assertIs(truth({"or": [pred(a), pred(b)]}, {}), or_table[i][j])

    def test_every_fixture_classification(self):
        cases = build_cases(grader.BASELINE / "pack.json")
        self.assertEqual(len(cases), len({case.name for case in cases}))
        for case in cases:
            with self.subTest(case=case.name):
                if case.invalid:
                    with self.assertRaises((ValueError, TypeError, KeyError)):
                        execute(grader.loads(case.raw) if case.raw is not None else case.request)
                else:
                    execute(case.request)

    def test_public_benchmark_anchor(self):
        case = next(case for case in build_cases(grader.BASELINE / "pack.json") if case.benchmark)
        result = execute(case.request)
        self.assertEqual(result["join_comparisons"], 150)
        self.assertEqual(len(result["rows"]), 4)

    def test_sqlite_differential_small_finite_joins_and_groups(self):
        # Independent SQL implementation; restrict these probes to SQLite's exact
        # integer range. Includes empty tables, bags, null keys, and unmatched rows.
        with sqlite3.connect(":memory:") as db:
            db.execute("CREATE TABLE a (id INTEGER, v INTEGER)")
            db.execute("CREATE TABLE b (id INTEGER, v INTEGER)")
            row_sets = [[], [(None, None)], [(1, 3), (1, 3), (None, -2)], [(2, None), (3, 4)]]
            for left, right, kind in itertools.product(row_sets, row_sets, ("inner", "left")):
                db.execute("DELETE FROM a")
                db.execute("DELETE FROM b")
                db.executemany("INSERT INTO a VALUES (?, ?)", left)
                db.executemany("INSERT INTO b VALUES (?, ?)", right)
                tables = {name: {"columns": {"id": "int", "v": "int"},
                                "rows": [dict(zip(("id", "v"), row)) for row in rows]}
                          for name, rows in (("a", left), ("b", right))}
                sql = f"SELECT a.id, a.v, b.id, b.v FROM a {kind.upper()} JOIN b ON a.id=b.id"
                wanted = [dict(zip(("a.id", "a.v", "b.id", "b.v"), row)) for row in db.execute(sql)]
                result = self.run_plan(join(kind), tables)
                self.assertEqual(bag(result["rows"]), bag(wanted))
                self.assertEqual(result["join_comparisons"], len(left) * len(right))
                plan = group(join(kind), ["a.id"], {"all": {"fn": "count_all"},
                    "n": {"fn": "count", "expr": col("b.v")}, "s": {"fn": "sum", "expr": col("b.v")}})
                sql = f"SELECT a.id, COUNT(*), COUNT(b.v), SUM(b.v) FROM a {kind.upper()} JOIN b ON a.id=b.id GROUP BY a.id"
                wanted = [dict(zip(("a.id", "all", "n", "s"), row)) for row in db.execute(sql)]
                self.assertEqual(bag(self.run_plan(plan, tables)["rows"]), bag(wanted))


class GraderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix=".selftest-", dir=grader.HERE)
        cls.root = Path(cls.temp.name) / "candidate"
        cls.cases = build_cases(grader.BASELINE / "pack.json", generated=0)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def evaluate_selected(self, mode, names):
        make_control(self.root, mode)
        selected = [case for case in self.cases if case.name in names]
        self.assertEqual(len(selected), len(names))
        with patch.object(grader, "build_cases", return_value=selected):
            return grader.evaluate(self.root, budget=90)

    def test_correct_control_full_suite(self):
        make_control(self.root)
        report = grader.evaluate(self.root, budget=600)
        (grader.HERE / "positive-control-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        self.assertTrue(report["passed"], [x for x in report["checks"] if not x["passed"]][:5])

    def test_control_mutations_detected(self):
        benchmark = "public/selective reservation join"
        probes = [
            ("noop", [benchmark], "performance", "useful optimization missing"),
            ("counter", [benchmark], "public", "counter disagrees"),
            ("dedup", ["scan/duplicates-null-unicode"], "semantics", "answer differs"),
            ("outer", ["outer/filter-right-gt"], "optimizer_safety", "answer differs"),
            ("mutate", ["scan/duplicates-null-unicode"], "optimizer_api", "mutated"),
            ("duplicate", ["json/duplicate-root"], "validation", "expected exit 2"),
            ("bool-counter", ["scan/empty"], "semantics", "exact nonnegative integer"),
            ("bool-rows", ["scan/duplicates-null-unicode"], "semantics", "answer differs"),
            ("plan-lie", [benchmark], "public", "counter disagrees"),
            ("invalid-stdout", ["expr/empty/missing"], "validation", "stdout result"),
        ]
        summaries = []
        for mode, names, category, detail in probes:
            with self.subTest(mode=mode):
                report = self.evaluate_selected(mode, names)
                self.assertFalse(report["passed"])
                failed = [x for x in report["checks"] if not x["passed"]]
                self.assertTrue(any(x["category"] == category and detail in str(x["detail"]) for x in failed), failed)
                summaries.append({"defect": mode, "rejected": not report["passed"],
                                  "failed_checks": [x["name"] for x in failed]})
        (grader.HERE / "mutation-report.json").write_text(json.dumps(summaries, indent=2) + "\n", encoding="utf-8")

    def test_protected_byte_change_detected(self):
        make_control(self.root)
        with (self.root / "README.md").open("ab") as stream:
            stream.write(b"\n")
        self.assertIn("protected bytes changed or missing: README.md", grader.inspect_candidate(self.root))

    def test_timeout_detected(self):
        make_control(self.root)
        (self.root / "query_cli.py").write_text("import time; time.sleep(10)\n", encoding="utf-8")
        runner = grader.Runner(self.root, sys.executable, timeout=0.1, budget=10)
        with self.assertRaisesRegex(Invalid, "timed out"):
            runner.cli(self.root / "absent-request.json")


if __name__ == "__main__":
    unittest.main(verbosity=2)

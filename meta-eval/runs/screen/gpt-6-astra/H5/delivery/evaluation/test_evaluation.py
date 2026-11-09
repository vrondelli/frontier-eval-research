"""Evaluator tests, independent SQL cross-checks, and submission controls."""
import copy
import itertools
import json
from pathlib import Path
import random
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest

from cases import build_cases, col, filt, group, join, lit, project, scan
from oracle import bag, evaluate, loads, truth
from run import ROOT, check_result, module_check, protected_check, run_suite

CONTROL_OPTIMIZER = '''
import copy

def optimize(plan):
    result = copy.deepcopy(plan)
    def refs(obj):
        if isinstance(obj, dict):
            if set(obj) == {"col"}: return {obj["col"]}
            return set().union(*(refs(v) for v in obj.values()))
        if isinstance(obj, list): return set().union(*(refs(v) for v in obj))
        return set()
    def conjunction(parts):
        return parts[0] if len(parts) == 1 else {"and": parts}
    def visit(p):
        for k in ("input", "left", "right"):
            if k in p: p[k] = visit(p[k])
        if p["op"] != "filter": return p
        j = p["input"]
        if j["op"] != "join" or j["kind"] != "inner": return p
        if j["left"]["op"] != "scan" or j["right"]["op"] != "scan": return p
        pred = p["predicate"]
        parts = pred["and"] if set(pred) == {"and"} else [pred]
        remaining = []
        moved = {"left": [], "right": []}
        for pred in parts:
            fields = refs(pred)
            target = next((side for side in moved if fields and all(
                f.startswith(j[side]["as"] + ".") for f in fields)), None)
            if target: moved[target].append(pred)
            else: remaining.append(pred)
        for side, predicates in moved.items():
            if predicates:
                j[side] = {"op": "filter", "input": j[side], "predicate": conjunction(predicates)}
        return {"op": "filter", "input": j, "predicate": conjunction(remaining)} if remaining else j
    return visit(result)
'''

CONTROL_CLI = '''
import argparse, json, sys
from oracle import loads, evaluate
from optimizer import optimize
p=argparse.ArgumentParser()
p.add_argument('command', choices=['run'])
p.add_argument('--request', required=True)
p.add_argument('--optimize', action='store_true')
args=p.parse_args()
try:
    with open(args.request, encoding='utf-8') as f: r=loads(f.read())
    evaluate(r)  # The original request must be valid before rewriting.
    plan=optimize(r['plan']) if args.optimize else r['plan']
    rows,n=evaluate({'tables': r['tables'], 'plan': plan})
    print(json.dumps({'rows': rows, 'join_comparisons': n, 'optimized_plan': plan}))
except Exception as exc:
    print(str(exc),file=sys.stderr)
    sys.exit(2)
'''


def make_control(path):
    path.mkdir()
    for name in ("README.md", "language.json", "pack.json"):
        shutil.copyfile(ROOT / "input" / "workspace" / name, path / name)
    shutil.copyfile(Path(__file__).with_name("oracle.py"), path / "oracle.py")
    (path / "engine.py").write_text("from oracle import evaluate\n", encoding="utf-8")
    (path / "query_cli.py").write_text(CONTROL_CLI, encoding="utf-8")
    (path / "optimizer.py").write_text(CONTROL_OPTIMIZER, encoding="utf-8")


class OracleTests(unittest.TestCase):
    def test_three_valued_truth_tables(self):
        predicates = {True: {"eq": [lit(1), lit(1)]}, False: {"eq": [lit(1), lit(0)]},
                      None: {"eq": [lit(None), lit(0)]}}
        and_expected = [True, False, None, False, False, False, None, False, None]
        or_expected = [True, True, True, True, False, None, True, None, None]
        for i, (a, b) in enumerate(itertools.product((True, False, None), repeat=2)):
            self.assertIs(truth({"and": [predicates[a], predicates[b]]}, {}), and_expected[i])
            self.assertIs(truth({"or": [predicates[a], predicates[b]]}, {}), or_expected[i])
        for a in (True, False, None):
            self.assertIs(truth({"not": predicates[a]}, {}), None if a is None else not a)

    def test_hand_calculated_bags_counts_and_empty_aggregation(self):
        tables = {"a": {"columns": {"k": "int"}, "rows": [{"k": 1}, {"k": 1}, {"k": None}, {"k": 8}]},
                  "b": {"columns": {"k": "int"}, "rows": [{"k": 1}, {"k": 1}, {"k": None}]}}
        rows, count = evaluate({"tables": tables, "plan": join(kind="left")})
        self.assertEqual(count, 12)
        self.assertEqual(bag(rows), bag([{"a.k": 1, "b.k": 1}] * 4 +
                                       [{"a.k": None, "b.k": None}, {"a.k": 8, "b.k": None}]))
        p = group(join(kind="left"), [], n={"fn": "count_all"}, c={"fn": "count", "expr": col("b.k")},
                  s={"fn": "sum", "expr": col("b.k")})
        self.assertEqual(evaluate({"tables": tables, "plan": p}), ([{"n": 6, "c": 4, "s": 4}], 12))
        tables["a"]["rows"] = []
        self.assertEqual(evaluate({"tables": tables, "plan": p}), ([{"n": 0, "c": 0, "s": None}], 0))
        p["keys"] = ["a.k"]
        self.assertEqual(evaluate({"tables": tables, "plan": p}), ([], 0))

    def test_sqlite_independent_cross_check(self):
        rng = random.Random(719)
        with sqlite3.connect(":memory:") as db:
            db.row_factory = sqlite3.Row
            db.execute("CREATE TABLE a (k INTEGER, v INTEGER)")
            db.execute("CREATE TABLE b (k INTEGER, v INTEGER)")
            for _ in range(30):
                tables = {}
                for name in ("a", "b"):
                    rows = [{"k": rng.choice([None, 0, 1]), "v": rng.choice([None, -2, 0, 4])}
                            for _ in range(rng.randrange(7))]
                    tables[name] = {"columns": {"k": "int", "v": "int"}, "rows": rows}
                    db.execute("DELETE FROM " + name)
                    db.executemany("INSERT INTO " + name + " VALUES (?, ?)", [(r["k"], r["v"]) for r in rows])
                for kind, sql_kind in (("inner", "INNER"), ("left", "LEFT")):
                    p = join(kind=kind)
                    rows, pairs = evaluate({"tables": tables, "plan": p})
                    sql = 'SELECT a.k AS "a.k", a.v AS "a.v", b.k AS "b.k", b.v AS "b.v" FROM a ' + sql_kind + ' JOIN b ON a.k=b.k'
                    self.assertEqual(bag(rows), bag([dict(r) for r in db.execute(sql)]))
                    self.assertEqual(pairs, len(tables["a"]["rows"]) * len(tables["b"]["rows"]))
                    pred = {"or": [{"gt": [col("a.v"), lit(0)]}, {"is_null": col("b.k")}]}
                    p = group(filt(p, pred), ["a.k"], n={"fn": "count_all"},
                              c={"fn": "count", "expr": col("b.v")}, s={"fn": "sum", "expr": col("b.v")})
                    sql = 'SELECT a.k AS "a.k", COUNT(*) AS n, COUNT(b.v) AS c, SUM(b.v) AS s FROM a ' + sql_kind + ' JOIN b ON a.k=b.k WHERE a.v>0 OR b.k IS NULL GROUP BY a.k'
                    self.assertEqual(bag(evaluate({"tables": tables, "plan": p})[0]), bag([dict(r) for r in db.execute(sql)]))

    def test_every_fixture_is_correctly_classified(self):
        pack = loads((ROOT / "input/workspace/pack.json").read_text())
        cases = build_cases(pack)
        self.assertEqual(len(cases), len({c.name for c in cases}))
        self.assertTrue(any(c.benchmark for c in cases))
        for case in cases:
            with self.subTest(case=case.name):
                if case.valid:
                    evaluate(case.request)
                else:
                    with self.assertRaises((ValueError, TypeError, KeyError)):
                        evaluate(loads(case.raw) if case.raw is not None else case.request)

    def test_exact_json_values(self):
        with self.assertRaises(ValueError): bag([{"x": True}])
        with self.assertRaises(ValueError): bag([{"x": 1.0}])
        self.assertNotEqual(bag([{"x": 1}]), bag([{"x": "1"}]))
        self.assertNotEqual(bag([{"x": 1}]), bag([{"x": 1}, {"x": 1}]))
        with self.assertRaises(ValueError): loads('{"x":1,"x":1}')


class HarnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="eval-controls-", dir=ROOT)
        cls.base = Path(cls.temp.name)
        cls.control = cls.base / "good"
        make_control(cls.control)
        cls.mutation_results = []

    @classmethod
    def tearDownClass(cls):
        report_dir = ROOT / "evaluation/reports"
        report_dir.mkdir(exist_ok=True)
        (report_dir / "mutations.json").write_text(json.dumps(cls.mutation_results, indent=2) + "\n")
        cls.temp.cleanup()

    def test_positive_control_full_suite(self):
        report = run_suite(self.control)
        (ROOT / "evaluation/reports").mkdir(exist_ok=True)
        (ROOT / "evaluation/reports/positive-control.json").write_text(json.dumps(report, indent=2) + "\n")
        self.assertTrue(report["passed"], [c for c in report["checks"] if not c["passed"]])

    def test_mutations_rejected_for_expected_reason(self):
        public = "public/0/selective reservation join"
        mutations = [
            ("noop", "optimizer.py", "def optimize(plan):\n    import copy\n    return copy.deepcopy(plan)\n",
             {public}, "benchmark-half-pairs"),
            ("fake-counter", "query_cli.py", CONTROL_CLI.replace("'join_comparisons': n", "'join_comparisons': 0"),
             {"join/inner/bag-null"}, "optimized-and-replay"),
            ("deduplicate", "query_cli.py", CONTROL_CLI.replace("'rows': rows", "'rows': list({json.dumps(r,sort_keys=True):r for r in rows}.values())"),
             {"scan/bag"}, "plain"),
            ("mutate-input", "optimizer.py", CONTROL_OPTIMIZER.replace("return visit(result)", "plan.clear()\n    return visit(result)"),
             {public}, "optimizer-api"),
            ("unsafe-outer-pushdown", "optimizer.py", CONTROL_OPTIMIZER.replace('j["kind"] != "inner"', 'j["kind"] not in ("inner", "left")'),
             {"optimizer/left/right-positive", "optimizer/left/right-is-null"}, "optimized-and-replay"),
            ("accept-invalid", "query_cli.py", CONTROL_CLI.replace("sys.exit(2)", "print('{}')\n    sys.exit(0)"),
             {"invalid/expression-empty-2"}, "reject-plain"),
            ("bad-emitted-plan", "query_cli.py", CONTROL_CLI.replace("'optimized_plan': plan", "'optimized_plan': {'op':'unknown'}"),
             {"scan/bag"}, "optimized-and-replay"),
            ("boolean-counter", "query_cli.py", CONTROL_CLI.replace("'join_comparisons': n", "'join_comparisons': False"),
             {"scan/bag"}, "plain"),
        ]
        oracle_source = (self.control / "oracle.py").read_text()
        mutations.extend([
            ("omit-unmatched", "oracle.py", oracle_source.replace('if not matches and p["kind"] == "left":', 'if False:'),
             {"join/left/empty-right"}, "plain"),
            ("count-nulls", "oracle.py", oracle_source.replace('len(values) if agg["fn"] == "count"', 'len(members) if agg["fn"] == "count"'),
             {"group/nulls/0"}, "plain"),
        ])
        for name, filename, content, selected, expected_check in mutations:
            with self.subTest(mutation=name):
                path = self.base / name
                shutil.copytree(self.control, path)
                (path / filename).write_text(content, encoding="utf-8")
                report = run_suite(path, generated=0, selected=selected)
                failed = [c for c in report["checks"] if not c["passed"]]
                self.mutation_results.append({"mutation": name, "detected": not report["passed"],
                                              "expected_check": expected_check, "failures": failed})
                self.assertFalse(report["passed"])
                self.assertTrue(any(c["check"] == expected_check for c in failed), failed)

    def test_protected_file_and_regular_module(self):
        path = self.base / "integrity"
        shutil.copytree(self.control, path)
        (path / "README.md").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "protected input changed"):
            protected_check(path)
        (path / "engine.py").unlink()
        (path / "engine.py").mkdir()
        with self.assertRaisesRegex(ValueError, "regular local file"):
            module_check(path)

    def test_timeout_is_candidate_failure(self):
        path = self.base / "timeout"
        shutil.copytree(self.control, path)
        (path / "query_cli.py").write_text("import time\ntime.sleep(5)\n")
        report = run_suite(path, timeout=0.1, generated=0, selected={"scan/bag"})
        self.assertFalse(report["passed"])
        self.assertTrue(any("timeout" in c.get("error", "") for c in report["checks"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)

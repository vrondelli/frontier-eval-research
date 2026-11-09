"""Contract-derived examples, negative probes and seeded finite compositions."""
import copy
import itertools
import json
import random
from dataclasses import dataclass


@dataclass
class Case:
    name: str
    category: str
    request: object
    valid: bool = True
    benchmark: bool = False
    raw: str | None = None


def col(name): return {"col": name}
def lit(value): return {"lit": value}
def scan(table="a", alias="a"): return {"op": "scan", "table": table, "as": alias}
def filt(plan, pred): return {"op": "filter", "input": plan, "predicate": pred}
def project(plan, **fields): return {"op": "project", "input": plan, "fields": fields}
def group(plan, keys, **aggs): return {"op": "group", "input": plan, "keys": keys, "aggregates": aggs}
def join(left=None, right=None, kind="inner", lk="a.k", rk="b.k"):
    return {"op": "join", "kind": kind, "left": left or scan(),
            "right": right or scan("b", "b"), "left_on": lk, "right_on": rk}


def build_cases(pack, seed=436, generated=24):
    cases = []
    tables = {
        "a": {"columns": {"k": "int", "v": "int", "s": "str"}, "rows": [
            {"k": 1, "v": 5, "s": "x"}, {"k": 1, "v": 5, "s": "x"},
            {"k": 2, "v": None, "s": ""}, {"k": None, "v": -3, "s": None},
            {"k": 9, "v": 10**45, "s": "雪"}]},
        "b": {"columns": {"k": "int", "v": "int", "s": "str"}, "rows": [
            {"k": 1, "v": 2, "s": "x"}, {"k": 1, "v": 2, "s": "x"},
            {"k": 1, "v": None, "s": "y"}, {"k": None, "v": 7, "s": None},
            {"k": 4, "v": -2, "s": "雪"}]},
        "empty": {"columns": {"k": "int", "v": "int", "s": "str"}, "rows": []},
        "nulls": {"columns": {"k": "int", "v": "int", "s": "str"}, "rows": [
            {"k": None, "v": None, "s": None}, {"k": None, "v": None, "s": None}]},
    }

    def add(name, plan, category="semantics", data=None, benchmark=False):
        cases.append(Case(name, category, {"tables": copy.deepcopy(tables if data is None else data),
                                          "plan": copy.deepcopy(plan)}, benchmark=benchmark))

    for i, query in enumerate(pack["queries"]):
        add("public/%d/%s" % (i, query["name"]), query["plan"], "public", pack["tables"],
            query.get("benchmark") is True)
    add("scan/bag", scan())
    add("scan/empty", scan("empty"))
    add("project/empty-fields-bag", project(scan()))
    add("project/exact-values", project(scan(), val=col("a.v"), text=col("a.s"),
        huge={"add": [col("a.v"), lit(10**50)]}, missing=lit(None),
        nested={"sub": [{"add": [col("a.v"), lit(2)]}, lit(-3)]}))
    renamed = project(scan(), **{"z.key": col("a.k"), "": col("a.s"), "v": col("a.v")})
    add("project/downstream-reference", project(filt(renamed, {"gt": [col("v"), lit(0)]}),
                                               key=col("z.key"), text=col("")))
    for op in ("eq", "ne", "lt", "le", "gt", "ge"):
        for field, value in (("a.v", 5), ("a.s", "x")):
            add("compare/%s/%s" % (op, field), filt(scan(), {op: [col(field), lit(value)]}), "logic")
        add("compare/%s/null" % op, filt(scan(), {op: [lit(None), lit(None)]}), "logic")
    truth_rows = [{"id": i, "x": a, "y": b} for i, (a, b) in
                  enumerate(itertools.product((1, 0, None), repeat=2))]
    truth_tables = {"t": {"columns": {"id": "int", "x": "int", "y": "int"}, "rows": truth_rows}}
    px, py = {"eq": [col("t.x"), lit(1)]}, {"eq": [col("t.y"), lit(1)]}
    for op in ("and", "or"):
        for negate in (False, True):
            p = {op: [px, py]}
            add("logic/%s/negate-%s" % (op, negate), filt(scan("t", "t"), {"not": p} if negate else p),
                "logic", truth_tables)
    add("logic/is-null", filt(scan(), {"is_null": col("a.s")}), "logic")
    add("logic/not-unknown", filt(scan(), {"not": {"eq": [col("a.k"), lit(None)]}}), "logic")
    add("logic/variadic", filt(scan(), {"or": [px := {"eq": [lit(0), lit(1)]},
        {"eq": [lit(None), lit(1)]}, {"eq": [lit(1), lit(1)]}]}), "logic")
    for kind in ("inner", "left"):
        add("join/%s/bag-null" % kind, join(kind=kind), "join")
        add("join/%s/string-key" % kind, join(kind=kind, lk="a.s", rk="b.s"), "join")
        add("join/%s/empty-left" % kind, join(left=scan("empty"), kind=kind), "join")
        add("join/%s/empty-right" % kind, join(right=scan("empty", "b"), kind=kind), "join")
        right = project(scan("empty", "z"), key=col("z.k"), computed={"add": [col("z.v"), lit(1)]})
        add("join/%s/empty-derived-schema" % kind, join(right=right, rk="key", kind=kind), "join")
    add("join/nested-counters", join(join(kind="left"), scan("a", "c"), lk="a.k", rk="c.k"), "join")
    add("join/empty-parent-counts-child", join(join(), scan("empty", "c"), lk="a.k", rk="c.k"), "join")
    add("join/projected-fields", join(renamed, project(scan("b", "b"), key=col("b.k")), lk="z.key", rk="key"), "join")
    aggs = {"n": {"fn": "count_all"}, "nonnull": {"fn": "count", "expr": col("a.v")},
            "strings": {"fn": "count", "expr": col("a.s")}, "total": {"fn": "sum", "expr": col("a.v")},
            "exprsum": {"fn": "sum", "expr": {"sub": [col("a.v"), lit(2)]}},
            "nullcount": {"fn": "count", "expr": lit(None)}, "nullsum": {"fn": "sum", "expr": lit(None)}}
    for table in ("a", "empty", "nulls"):
        for keys in ([], ["a.k"], ["a.k", "a.s"]):
            add("group/%s/%s" % (table, len(keys)), group(scan(table), keys, **aggs), "group")
    add("group/no-aggregates", group(scan(), ["a.s"]), "group")
    add("group/empty-no-aggregates", group(scan("empty"), []), "group")
    grouped = group(scan(), ["a.k"], **aggs)
    add("group/downstream-expression", project(filt(grouped, {"gt": [col("n"), lit(1)]}),
                                               result={"add": [col("total"), col("n")]}), "group")
    add("group/group-over-group", group(grouped, [], n={"fn": "sum", "expr": col("n")}), "group")
    add("group/join-derived", join(grouped, scan("b", "b")), "group")
    # Unsafe pushdown traps: unmatched left rows, whole OR, cross-input expressions,
    # and output names whose apparent prefix deliberately differs from ownership.
    for predname, pred in (
        ("right-is-null", {"is_null": col("b.v")}),
        ("right-positive", {"gt": [col("b.v"), lit(0)]}),
        ("left-positive", {"gt": [col("a.v"), lit(0)]}),
        ("cross-or", {"or": [{"eq": [col("a.k"), lit(9)]}, {"eq": [col("b.v"), lit(2)]}]}),
        ("cross-add", {"gt": [{"add": [col("a.v"), col("b.v")]}, lit(5)]}),
        ("nested-and", {"and": [{"gt": [col("a.v"), lit(0)]}, {"and": [
            {"is_null": col("b.s")}, {"not": {"eq": [col("a.k"), lit(1)]}}]}]}),
    ):
        for kind in ("inner", "left"):
            add("optimizer/%s/%s" % (kind, predname), filt(join(kind=kind), pred), "optimizer-safety")
    misleading = join(project(scan(), **{"b.key": col("a.k"), "b.value": col("a.v")}),
                      project(scan("b", "b"), **{"a.key": col("b.k"), "a.value": col("b.v")}),
                      lk="b.key", rk="a.key")
    add("optimizer/ownership-not-prefix", filt(misleading, {"gt": [col("b.value"), lit(0)]}), "optimizer-safety")
    add("optimizer/group-barrier", filt(group(join(), ["a.k"], n={"fn": "count_all"}),
                                       {"gt": [col("n"), lit(2)]}), "optimizer-safety")
    rng = random.Random(seed)
    for i in range(generated):
        data = copy.deepcopy(tables)
        for name in ("a", "b"):
            data[name]["rows"] = [{"k": rng.choice([None, 0, 1, 2]),
                                  "v": rng.choice([None, -5, 0, 3, 10**30]),
                                  "s": rng.choice([None, "", "x", "雪"])} for _ in range(rng.randrange(8))]
        p = join(kind=rng.choice(["inner", "left"]))
        p = filt(p, {rng.choice(["and", "or"]): [
            {"gt": [col("a.v"), lit(rng.choice([-2, 0, 2]))]},
            {"not": {"is_null": col("b.k")}}]})
        if i % 3 == 0:
            p = group(p, ["a.s"], n={"fn": "count_all"}, s={"fn": "sum", "expr": col("b.v")})
        elif i % 3 == 1:
            p = project(p, key=col("a.k"), v={"sub": [col("a.v"), col("b.v")]})
        add("generated/%d" % i, p, "generated", data)

    def invalid(name, request=None, plan=None, raw=None):
        req = {"tables": copy.deepcopy(tables), "plan": scan()} if request is None else copy.deepcopy(request)
        if plan is not None:
            req["plan"] = plan
        cases.append(Case("invalid/" + name, "validation", req, False, raw=raw))

    for name, req in (("request-list", []), ("request-missing", {"tables": tables}),
                      ("request-extra", {"tables": tables, "plan": scan(), "extra": 1}),
                      ("tables-list", {"tables": [], "plan": scan()})):
        invalid(name, request=req)
    for name, change in (
        ("table-list", []), ("table-extra", {**tables["a"], "extra": 1}),
        ("columns-list", {"columns": [], "rows": []}),
        ("rows-object", {"columns": {"k": "int"}, "rows": {}}),
        ("column-dot", {"columns": {"a.k": "int"}, "rows": []}),
        ("column-empty", {"columns": {"": "int"}, "rows": []}),
        ("column-type", {"columns": {"k": "float"}, "rows": []}),
        ("row-missing", {"columns": {"k": "int"}, "rows": [{}]}),
        ("row-extra", {"columns": {"k": "int"}, "rows": [{"k": 1, "z": 2}]}),
        ("row-array", {"columns": {"k": "int"}, "rows": [[]]}),
        ("row-bool", {"columns": {"k": "int"}, "rows": [{"k": True}]}),
        ("row-float", {"columns": {"k": "int"}, "rows": [{"k": 1.0}]}),
        ("row-string", {"columns": {"k": "int"}, "rows": [{"k": "1"}]}),
        ("row-int-for-string", {"columns": {"k": "str"}, "rows": [{"k": 1}]}),
    ):
        invalid(name, request={"tables": {**tables, "unused": change}, "plan": scan()})
    nodes = [scan(), filt(scan(), {"is_null": col("a.k")}), project(scan(), k=col("a.k")),
             join(), group(scan(), [], n={"fn": "count_all"})]
    for node in nodes:
        invalid(node["op"] + "-extra", plan={**node, "extra": 1})
        for key in node:
            partial = copy.deepcopy(node)
            del partial[key]
            invalid(node["op"] + "-missing-" + key, plan=partial)
    for name, plan in (
        ("plan-array", []), ("plan-unknown", {"op": "sort", "input": scan()}),
        ("scan-table", scan("missing")), ("scan-alias-dot", scan(alias="a.b")),
        ("scan-alias-empty", scan(alias="")), ("scan-alias-number", scan(alias=1)),
        ("join-kind", join(kind="right")), ("join-overlap", join(right=scan())),
        ("join-missing-key", join(lk="a.missing")), ("join-wrong-side", join(lk="b.k")),
        ("join-type", join(lk="a.s")),
        ("join-empty-type", join(left=scan("empty"), lk="a.s")),
        ("group-key-missing", group(scan("empty"), ["no"])),
        ("group-key-duplicate", group(scan(), ["a.k", "a.k"])),
        ("group-key-type", group(scan(), "a.k")),
        ("group-collision", group(scan(), ["a.k"], **{"a.k": {"fn": "count_all"}})),
        ("group-aggs-list", {"op": "group", "input": scan(), "keys": [], "aggregates": []}),
        ("project-fields-list", {"op": "project", "input": scan(), "fields": []}),
        ("project-sibling-reference", project(scan(), x=lit(1), y=col("x"))),
    ):
        invalid(name, plan=plan)
    bad_exprs = [True, {}, {"col": "missing"}, {"lit": True}, {"lit": 1.5}, {"lit": []},
                 {"lit": 1, "col": "a.k"}, {"mul": [lit(1), lit(2)]},
                 {"add": [lit(1)]}, {"sub": [lit(1), lit(2), lit(3)]},
                 {"add": [col("a.s"), lit(None)]}, {"add": [lit("x"), lit(1)]},
                 {"col": []}]
    for i, expr in enumerate(bad_exprs):
        invalid("expression-empty-%d" % i, plan=project(scan("empty"), x=expr))
    bad_preds = [{}, {"eq": [col("missing"), lit(1)]}, {"eq": [col("a.s"), lit(1)]},
                 {"eq": [lit(1)]}, {"and": []}, {"or": [{"is_null": lit(None)}]},
                 {"xor": [px, px]}, {"not": []}, {"is_null": {"lit": True}},
                 {"and": [{"eq": [lit(0), lit(1)]}, {"eq": [col("missing"), lit(1)]}]},
                 {"or": [{"eq": [lit(1), lit(1)]}, {"eq": [col("missing"), lit(1)]}]}]
    for i, pred in enumerate(bad_preds):
        invalid("predicate-empty-%d" % i, plan=filt(scan("empty"), pred))
        invalid("predicate-populated-%d" % i, plan=filt(scan(), pred))
    for i, agg in enumerate([{}, {"fn": "avg", "expr": lit(1)}, {"fn": "count_all", "expr": lit(1)},
                            {"fn": "sum"}, {"fn": "count", "expr": col("missing")},
                            {"fn": "sum", "expr": col("a.s")},
                            {"fn": "sum", "expr": {"add": [lit(None), col("a.s")]}},
                            {"fn": "count", "expr": lit(1), "distinct": True}]):
        invalid("aggregate-empty-%d" % i, plan=group(scan("empty"), [], x=agg))
    # Null-valued integer expressions must retain their declared integer type.
    typed_null = project(scan("empty"), x={"add": [col("a.v"), lit(None)]})
    invalid("derived-null-type", plan=filt(typed_null, {"eq": [col("x"), lit("bad")]}))
    invalid("optimizer-must-not-erase-invalid", plan=filt(join(left=project(scan(), bad=col("missing")),
        lk="bad"), {"eq": [lit(0), lit(1)]}))
    base = json.dumps({"tables": tables, "plan": scan()}, separators=(",", ":"))
    for name, raw in (
        ("duplicate-root", base[:-1] + ',"plan":' + json.dumps(scan()) + '}'),
        ("duplicate-plan", base.replace('"op":"scan"', '"op":"scan","op":"scan"')),
        ("duplicate-row", base.replace('"v":5', '"v":5,"v":5', 1)),
        ("duplicate-column", base.replace('"k":"int"', '"k":"int","k":"int"', 1)),
        ("duplicate-table", '{"tables":{"a":{},"a":' + json.dumps(tables["a"]) + '},"plan":' + json.dumps(scan()) + '}'),
        ("truncated-json", base[:-3]), ("trailing-json", base + '{}'),
    ):
        invalid(name, raw=raw)
    return cases

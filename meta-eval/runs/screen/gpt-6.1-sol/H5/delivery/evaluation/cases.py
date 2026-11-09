"""Contract-derived fixtures; randomized cases use a reproducible local seed."""
import copy
import json
import random
from dataclasses import dataclass


@dataclass
class Case:
    name: str
    category: str
    request: object = None
    raw: str | None = None
    invalid: bool = False
    benchmark: bool = False


def col(name): return {"col": name}
def lit(value): return {"lit": value}
def cmp(op, a, b): return {op: [a, b]}
def scan(table="a", alias="a"): return {"op": "scan", "table": table, "as": alias}
def filt(plan, pred): return {"op": "filter", "input": plan, "predicate": pred}
def project(plan, **fields): return {"op": "project", "input": plan, "fields": fields}
def join(kind="inner", left=None, right=None, lk="a.id", rk="b.id"):
    return {"op": "join", "kind": kind, "left": left or scan(),
            "right": right or scan("b", "b"), "left_on": lk, "right_on": rk}
def group(plan, keys=None, aggs=None):
    return {"op": "group", "input": plan, "keys": keys or [], "aggregates": aggs or {
        "all": {"fn": "count_all"}, "nonnull": {"fn": "count", "expr": col("a.v")},
        "total": {"fn": "sum", "expr": col("a.v")}}}


def fixtures():
    return {
        "a": {"columns": {"id": "int", "v": "int", "s": "str"}, "rows": [
            {"id": 1, "v": 5, "s": "é"}, {"id": 1, "v": 5, "s": "é"},
            {"id": 2, "v": None, "s": ""}, {"id": None, "v": -7, "s": None},
            {"id": 4, "v": 10**40, "s": "東京"}]},
        "b": {"columns": {"id": "int", "v": "int", "s": "str"}, "rows": [
            {"id": 1, "v": 2, "s": "x"}, {"id": 1, "v": 2, "s": "x"},
            {"id": 2, "v": None, "s": ""}, {"id": None, "v": 8, "s": "é"},
            {"id": 8, "v": 0, "s": None}]},
        "empty": {"columns": {"id": "int", "v": "int", "s": "str"}, "rows": []},
        "zero": {"columns": {}, "rows": [{}, {}]},
    }


def build_cases(pack_path, seed=61371, generated=24):
    pack = json.loads(pack_path.read_text(encoding="utf-8"))
    cases = [Case("public/" + q["name"], "public", {"tables": pack["tables"], "plan": q["plan"]},
                  benchmark=q.get("benchmark") is True) for q in pack["queries"]]
    tables = fixtures()

    def good(name, plan, category="semantics", data=None):
        cases.append(Case(name, category, {"tables": copy.deepcopy(tables if data is None else data),
                                           "plan": copy.deepcopy(plan)}))

    def bad(name, plan=None, request=None, raw=None):
        cases.append(Case(name, "validation", request if request is not None else
                          {"tables": copy.deepcopy(tables), "plan": copy.deepcopy(plan)},
                          raw=raw, invalid=True))

    good("scan/duplicates-null-unicode", scan())
    good("scan/empty", scan("empty"))
    good("scan/zero-column-bag", scan("zero"))
    good("project/empty-fields-bag", {"op": "project", "input": scan(), "fields": {}})
    arithmetic = project(scan(), original=col("a.v"), string=col("a.s"),
                         nested={"sub": [{"add": [col("a.v"), lit(3)]}, lit(2)]},
                         null={"add": [lit(None), col("a.v")]}, literal=lit("\\\"\n雪"))
    good("project/arithmetic-null-exact-int", arithmetic)
    good("project/output-referenced", filt(arithmetic, cmp("gt", col("nested"), lit(5))))
    good("project/simultaneous-evaluation", {"op": "project", "input": scan(), "fields": {
        "a.v": {"add": [col("a.v"), lit(1)]}, "old": col("a.v")}})
    for op in ("eq", "ne", "lt", "le", "gt", "ge"):
        for field, value in (("a.v", 5), ("a.s", "é")):
            good(f"predicate/{op}/{field}", filt(scan(), cmp(op, col(field), lit(value))), "logic")
    good("predicate/is-null", filt(scan(), {"is_null": col("a.s")}), "logic")
    good("predicate/not-unknown", filt(scan(), {"not": cmp("eq", col("a.v"), lit(None))}), "logic")
    truth_values = [cmp("eq", lit(1), lit(1)), cmp("eq", lit(1), lit(2)),
                    cmp("eq", lit(None), lit(1))]
    for i, p in enumerate(truth_values):
        good(f"logic/not/{i}", filt(scan(), {"not": p}), "logic")
        for j, q in enumerate(truth_values):
            for op in ("and", "or"):
                good(f"logic/{op}/{i}/{j}", filt(scan(), {op: [p, q]}), "logic")
    good("logic/nested-variadic", filt(scan(), {"or": [truth_values[2], truth_values[1],
         {"and": [truth_values[0], {"not": truth_values[1]}, truth_values[0]]}]}), "logic")
    for kind in ("inner", "left"):
        good(f"join/{kind}/duplicate-and-null-keys", join(kind), "joins")
        good(f"join/{kind}/empty-right-schema", join(kind, right=scan("empty", "b")), "joins")
        good(f"join/{kind}/empty-left", join(kind, left=scan("empty")), "joins")
        good(f"join/{kind}/strings", join(kind, lk="a.s", rk="b.s"), "joins")
    # Null extension must use the schema of the complete right subtree.
    right = project(scan("empty", "x"), rid=col("x.id"), payload=col("x.s"))
    good("join/empty-projected-right", join("left", right=right, rk="rid"), "joins")
    nested = join("left", left=join(), right=scan("a", "c"), lk="b.id", rk="c.id")
    good("join/nested-comparison-accounting", nested, "joins")
    good("join/child-cost-survives-empty-parent", join(left=filt(join(), truth_values[1]),
         right=scan("a", "c"), rk="c.id"), "joins")
    good("join/no-null-null-match", join("left", left=project(scan(), k=lit(None)),
         right=project(scan("b", "b"), z=lit(None)), lk="k", rk="z"), "joins")
    good("outer/filter-is-null", filt(join("left"), {"is_null": col("b.id")}), "optimizer_safety")
    good("outer/filter-right-gt", filt(join("left"), cmp("gt", col("b.v"), lit(3))), "optimizer_safety")
    good("outer/mixed-or", filt(join("left"), {"or": [cmp("eq", col("a.id"), lit(4)),
         cmp("gt", col("b.v"), lit(1))]}), "optimizer_safety")
    good("inner/mixed-or", filt(join(), {"or": [cmp("eq", col("a.id"), lit(4)),
         cmp("eq", col("b.v"), lit(2))]}), "optimizer_safety")
    good("inner/cross-side-expression", filt(join(), cmp("gt", {"sub": [col("a.v"), col("b.v")]}, lit(0))), "optimizer_safety")
    good("inner/nested-conjunction", filt(join(), {"and": [truth_values[0], {"and": [
         cmp("eq", col("a.id"), lit(1)), cmp("gt", col("b.v"), lit(0))]}]}), "optimizer_safety")
    good("group/global", group(scan()), "groups")
    good("group/null-keys-duplicates", group(scan(), ["a.id", "a.s"]), "groups")
    good("group/empty-global", group(scan("empty")), "groups")
    good("group/empty-keyed", group(scan("empty"), ["a.id"]), "groups")
    good("group/all-null-sums", group(filt(scan(), {"is_null": col("a.v")})), "groups")
    good("group/count-string-and-null-expression", group(scan(), aggs={
        "strings": {"fn": "count", "expr": col("a.s")}, "nothing": {"fn": "count", "expr": lit(None)},
        "null_sum": {"fn": "sum", "expr": lit(None)}, "offset": {"fn": "sum", "expr": {"sub": [col("a.v"), lit(5)]}}}), "groups")
    good("group/outputs-reused", project(filt(group(scan(), ["a.id"]),
         cmp("ge", col("all"), lit(1))), n=col("all"), total={"add": [col("total"), lit(1)]}), "groups")
    good("group/group-over-group", group(project(group(scan(), ["a.id"]), **{"a.v": col("total") })), "groups")
    good("group/outer-null-extension", group(join("left"), ["a.id"], {
        "all": {"fn": "count_all"}, "matched": {"fn": "count", "expr": col("b.id")},
        "sum": {"fn": "sum", "expr": col("b.v")}}), "groups")
    good("group/empty-aggregate-map", {"op": "group", "input": scan(), "keys": ["a.id"], "aggregates": {}}, "groups")
    good("group/empty-global-empty-map", {"op": "group", "input": scan("empty"), "keys": [], "aggregates": {}}, "groups")
    good("group/output-used-as-join-key", join(left=group(scan(), ["a.id"])), "groups")

    # Request/schema and wire validation, including unused malformed tables.
    for name, request in [("request/not-object", []), ("request/missing-plan", {"tables": {}}),
                          ("request/extra-key", {"tables": {}, "plan": scan(), "extra": 1}),
                          ("request/tables-list", {"tables": [], "plan": scan()})]:
        bad(name, request=request)
    for name, change in [
        ("table/shape", {"columns": {"x": "int"}, "rows": [], "extra": 1}),
        ("table/not-object", []), ("table/columns-list", {"columns": [], "rows": []}),
        ("table/rows-object", {"columns": {}, "rows": {}}),
        ("column/dot", {"columns": {"x.y": "int"}, "rows": []}),
        ("column/empty", {"columns": {"": "str"}, "rows": []}),
        ("column/type", {"columns": {"x": "float"}, "rows": []}),
        ("row/missing", {"columns": {"x": "int"}, "rows": [{}]}),
        ("row/extra", {"columns": {}, "rows": [{"x": 1}]}),
        ("row/not-object", {"columns": {}, "rows": [[]]}),
        ("row/bool", {"columns": {"x": "int"}, "rows": [{"x": True}]}),
        ("row/float", {"columns": {"x": "int"}, "rows": [{"x": 1.0}]}),
        ("row/wrong-string", {"columns": {"x": "str"}, "rows": [{"x": 1}]})]:
        data = copy.deepcopy(tables)
        data["unused_invalid"] = change
        bad(name, request={"tables": data, "plan": scan()})
    bad("json/malformed", raw='{"tables":')
    bad("json/trailing-document", raw='{} {}')
    valid_raw = json.dumps({"tables": tables, "plan": scan()})
    for name, raw in [
        ("json/duplicate-root", valid_raw[:-1] + ', "plan": {"op":"scan","table":"a","as":"a"}}'),
        ("json/duplicate-plan", valid_raw.replace('"op": "scan"', '"op":"scan","op":"scan"')),
        ("json/duplicate-column", valid_raw.replace('"id": "int"', '"id":"int","id":"int"', 1)),
        ("json/duplicate-row", valid_raw.replace('"id": 1', '"id":1,"id":1', 1)),
        ("json/nan-literal", json.dumps({"tables": tables, "plan": project(scan(), n=lit(0))}).replace('"lit": 0', '"lit": NaN'))]:
        bad(name, raw=raw)
    for name, plan in [
        ("plan/list", []), ("plan/unknown", {"op": "sort"}),
        ("scan/missing", {"op": "scan", "table": "a"}),
        ("scan/extra", {**scan(), "extra": 1}), ("scan/table", scan("missing")),
        ("scan/alias-empty", scan(alias="")), ("scan/alias-dot", scan(alias="x.y")),
        ("scan/alias-type", scan(alias=3)), ("project/fields-list", {"op": "project", "input": scan(), "fields": []}),
        ("join/kind", join("full")), ("join/overlap", join(right=scan())),
        ("join/wrong-side-field", join(lk="b.id")), ("join/missing-field", join(rk="b.missing")),
        ("join/types-empty", join(left=scan("empty"), lk="a.s")),
        ("filter/missing-predicate", {"op": "filter", "input": scan()}),
        ("filter/extra", {**filt(scan(), truth_values[0]), "extra": 1}),
        ("group/duplicate-key", group(scan(), ["a.id", "a.id"])),
        ("group/missing-key", group(scan("empty"), ["a.absent"])),
        ("group/collision", group(scan(), ["a.id"], {"a.id": {"fn": "count_all"}})),
        ("group/keys-type", {"op": "group", "input": scan(), "keys": "a.id", "aggregates": {}}),
        ("group/aggregates-type", {"op": "group", "input": scan(), "keys": [], "aggregates": []})]:
        bad(name, plan)
    for name, expr in [
        ("missing", col("a.missing")), ("bool", lit(True)), ("float", lit(1.5)),
        ("list-literal", lit([])), ("object-literal", lit({})), ("shape", {"col": "a.id", "lit": 1}),
        ("unknown", {"mul": [lit(1), lit(2)]}), ("col-type", col(["a.id"])),
        ("add-arity", {"add": [lit(1)]}), ("sub-arity", {"sub": [lit(1), lit(2), lit(3)]}),
        ("arithmetic-string", {"add": [col("a.s"), lit(1)]}),
        ("arithmetic-null-string", {"add": [lit(None), col("a.s")]})]:
        bad("expr/empty/" + name, project(scan("empty"), value=expr))
    for name, pred in [
        ("unknown", {"like": [col("a.s"), lit("x")]}), ("shape", {}),
        ("bool", True), ("arity", {"eq": [lit(1)]}),
        ("and-arity", {"and": [truth_values[0]]}), ("or-arity", {"or": []}),
        ("not-shape", {"not": [truth_values[0]]}), ("is-null-missing", {"is_null": col("a.no")}),
        ("mixed-types", cmp("eq", col("a.id"), col("a.s"))),
        ("short-circuit-and", {"and": [truth_values[1], cmp("eq", col("a.no"), lit(1))]}),
        ("short-circuit-or", {"or": [truth_values[0], cmp("eq", col("a.no"), lit(1))]})]:
        bad("predicate/empty/" + name, filt(scan("empty"), pred))
    for name, agg in [
        ("unknown", {"fn": "avg", "expr": col("a.v")}),
        ("sum-string", {"fn": "sum", "expr": col("a.s")}),
        ("count-missing", {"fn": "count", "expr": col("a.no")}),
        ("count-all-extra", {"fn": "count_all", "expr": lit(1)}),
        ("sum-missing-expr", {"fn": "sum"}), ("not-object", 1)]:
        bad("aggregate/empty/" + name, group(scan("empty"), aggs={"result": agg}))
    # Types and references must survive derived schemas and empty ancestors.
    bad("derived/null-arithmetic-still-int", filt(project(scan("empty"), x={"add": [lit(None), lit(1)]}),
        cmp("eq", col("x"), lit("text"))))
    bad("derived/project-missing", project(project(scan("empty"), x=lit(None)), y=col("a.v")))
    bad("derived/count-is-int", project(group(scan("empty")), value={"add": [col("all"), lit("bad")]}))
    bad("derived/empty-parent-invalid-right", join(left=scan("empty"),
        right=project(scan("b", "b"), z=col("b.absent")), rk="z"))
    bad("derived/invalid-below-false-filter", filt(project(scan(), x=col("a.absent")), truth_values[1]))

    rng = random.Random(seed)
    for i in range(generated):
        data = fixtures()
        for table in ("a", "b"):
            data[table]["rows"] = [{"id": rng.choice([None, -1, 0, 1, 2]),
                "v": rng.choice([None, -5, 0, 8, 10**30]), "s": rng.choice([None, "", "a", "Ω"])}
                for _ in range(rng.randrange(9))]
        if data["a"]["rows"]:
            data["a"]["rows"].append(copy.deepcopy(data["a"]["rows"][0]))
        base = join(rng.choice(["inner", "left"]))
        pred = rng.choice([
            {"and": [cmp("gt", col("a.v"), lit(0)), cmp("ne", col("b.s"), lit("a"))]},
            {"or": [{"is_null": col("b.id")}, cmp("eq", col("a.id"), lit(1))]},
            {"not": cmp("le", col("a.v"), col("b.v"))}])
        plan = filt(base, pred)
        if i % 3 == 0:
            plan = group(plan, ["a.s"], {"n": {"fn": "count_all"},
                "cnt": {"fn": "count", "expr": col("b.s")},
                "sum": {"fn": "sum", "expr": {"sub": [col("a.v"), col("b.v")]}}})
        elif i % 3 == 1:
            plan = project(plan, key=col("a.id"), net={"add": [col("a.v"), col("b.v")]})
        good(f"generated/{seed}/{i:03d}", plan, "generated", data)
    return cases

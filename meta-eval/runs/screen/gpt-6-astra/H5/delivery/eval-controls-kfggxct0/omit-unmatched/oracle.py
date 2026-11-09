"""Independent, schema-first interpreter for the README's finite bag language.

This module never imports candidate code. None as a schema type means a
contextually typed null literal; arithmetic always has integer type.
"""
import collections
import json
import operator


def require(condition, message):
    if not condition:
        raise ValueError(message)


def shape(value, keys):
    require(type(value) is dict and set(value) == set(keys), "invalid object shape")


def unique(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def loads(raw):
    def reject(value):
        raise ValueError("non-JSON numeric constant: " + value)
    return json.loads(raw, object_pairs_hook=unique, parse_constant=reject)


def bag(rows):
    # JSON encoding distinguishes exact ints, floats, bools, strings and null.
    require(type(rows) is list and all(type(r) is dict for r in rows), "rows shape")
    for row in rows:
        require(all(v is None or type(v) in (int, str) for v in row.values()), "row values")
    return collections.Counter(json.dumps(r, sort_keys=True, ensure_ascii=True) for r in rows)


def validate_tables(tables):
    require(type(tables) is dict, "tables object")
    for table in tables.values():
        shape(table, ("columns", "rows"))
        cols = table["columns"]
        require(type(cols) is dict and type(table["rows"]) is list, "table types")
        require(all(type(k) is str and k and "." not in k and v in ("int", "str")
                    for k, v in cols.items()), "column declaration")
        for row in table["rows"]:
            shape(row, cols)
            for key, value in row.items():
                require(value is None or type(value) is {"int": int, "str": str}[cols[key]], "row type")


def field(name, schema):
    require(type(name) is str and name in schema, "missing field")
    return schema[name]


def expr_type(expr, schema):
    require(type(expr) is dict and len(expr) == 1, "expression shape")
    op, arg = next(iter(expr.items()))
    if op == "col":
        return field(arg, schema)
    if op == "lit":
        require(arg is None or type(arg) in (int, str), "literal type")
        return None if arg is None else ("int" if type(arg) is int else "str")
    require(op in ("add", "sub"), "expression operator")
    require(type(arg) is list and len(arg) == 2, "arithmetic arity")
    types = [expr_type(e, schema) for e in arg]
    require(all(t in (None, "int") for t in types), "arithmetic type")
    return "int"


COMPARISONS = {"eq": operator.eq, "ne": operator.ne, "lt": operator.lt,
               "le": operator.le, "gt": operator.gt, "ge": operator.ge}


def pred_type(pred, schema):
    require(type(pred) is dict and len(pred) == 1, "predicate shape")
    op, arg = next(iter(pred.items()))
    if op == "is_null":
        expr_type(arg, schema)
    elif op == "not":
        pred_type(arg, schema)
    elif op in ("and", "or"):
        require(type(arg) is list and len(arg) >= 2, "boolean arity")
        for p in arg:
            pred_type(p, schema)
    else:
        require(op in COMPARISONS and type(arg) is list and len(arg) == 2, "comparison shape")
        a, b = [expr_type(e, schema) for e in arg]
        require(a is None or b is None or a == b, "comparison type")


def infer(tables, plan):
    require(type(plan) is dict and type(plan.get("op")) is str, "plan shape")
    op = plan["op"]
    if op == "scan":
        shape(plan, ("op", "table", "as"))
        require(type(plan["table"]) is str and plan["table"] in tables, "table missing")
        alias = plan["as"]
        require(type(alias) is str and alias and "." not in alias, "alias")
        return {alias + "." + k: v for k, v in tables[plan["table"]]["columns"].items()}
    if op == "join":
        shape(plan, ("op", "kind", "left", "right", "left_on", "right_on"))
        require(plan["kind"] in ("inner", "left"), "join kind")
        left, right = infer(tables, plan["left"]), infer(tables, plan["right"])
        require(not (left.keys() & right.keys()), "overlapping join fields")
        a, b = field(plan["left_on"], left), field(plan["right_on"], right)
        require(a is None or b is None or a == b, "join key types")
        return {**left, **right}
    if op == "filter":
        shape(plan, ("op", "input", "predicate"))
        schema = infer(tables, plan["input"])
        pred_type(plan["predicate"], schema)
        return schema
    if op == "project":
        shape(plan, ("op", "input", "fields"))
        schema = infer(tables, plan["input"])
        require(type(plan["fields"]) is dict, "project fields")
        return {key: expr_type(expr, schema) for key, expr in plan["fields"].items()}
    require(op == "group", "plan operator")
    shape(plan, ("op", "input", "keys", "aggregates"))
    schema = infer(tables, plan["input"])
    keys, aggs = plan["keys"], plan["aggregates"]
    require(type(keys) is list and all(type(k) is str for k in keys), "group keys")
    require(len(keys) == len(set(keys)), "duplicate group key")
    require(type(aggs) is dict and not set(keys) & aggs.keys(), "aggregate names")
    result = {k: field(k, schema) for k in keys}
    for name, agg in aggs.items():
        require(type(agg) is dict, "aggregate object")
        fn = agg.get("fn")
        if fn == "count_all":
            shape(agg, ("fn",))
        else:
            require(fn in ("count", "sum"), "aggregate function")
            shape(agg, ("fn", "expr"))
            typ = expr_type(agg["expr"], schema)
            require(fn != "sum" or typ in (None, "int"), "sum type")
        result[name] = "int"
    return result


def scalar(expr, row):
    op, arg = next(iter(expr.items()))
    if op == "col":
        return row[arg]
    if op == "lit":
        return arg
    a, b = [scalar(e, row) for e in arg]
    return None if a is None or b is None else (a + b if op == "add" else a - b)


def truth(pred, row):
    op, arg = next(iter(pred.items()))
    if op == "is_null":
        return scalar(arg, row) is None
    if op == "not":
        value = truth(arg, row)
        return None if value is None else not value
    if op in ("and", "or"):
        values = [truth(p, row) for p in arg]
        decisive = False if op == "and" else True
        if any(v is decisive for v in values):
            return decisive
        return None if any(v is None for v in values) else not decisive
    a, b = [scalar(e, row) for e in arg]
    return None if a is None or b is None else COMPARISONS[op](a, b)


def evaluate(request):
    shape(request, ("tables", "plan"))
    tables, plan = request["tables"], request["plan"]
    validate_tables(tables)
    infer(tables, plan)  # Validate the entire tree before evaluating any rows.

    def run(p):
        op = p["op"]
        if op == "scan":
            return [{p["as"] + "." + k: v for k, v in r.items()}
                    for r in tables[p["table"]]["rows"]], 0
        if op == "join":
            left, nl = run(p["left"])
            right, nr = run(p["right"])
            out = []
            nulls = dict.fromkeys(infer(tables, p["right"]))
            for a in left:
                matches = [b for b in right if a[p["left_on"]] is not None
                           and b[p["right_on"]] is not None and a[p["left_on"]] == b[p["right_on"]]]
                out.extend({**a, **b} for b in matches)
                if False:
                    out.append({**a, **nulls})
            return out, nl + nr + len(left) * len(right)
        rows, count = run(p["input"])
        if op == "filter":
            return [r for r in rows if truth(p["predicate"], r) is True], count
        if op == "project":
            return [{k: scalar(e, r) for k, e in p["fields"].items()} for r in rows], count
        groups = {}
        for row in rows:
            groups.setdefault(tuple(row[k] for k in p["keys"]), []).append(row)
        if not p["keys"] and not rows:
            groups[()] = []
        out = []
        for key, members in groups.items():
            row = dict(zip(p["keys"], key))
            for name, agg in p["aggregates"].items():
                if agg["fn"] == "count_all":
                    row[name] = len(members)
                else:
                    values = [scalar(agg["expr"], r) for r in members]
                    values = [v for v in values if v is not None]
                    row[name] = len(values) if agg["fn"] == "count" else (sum(values) if values else None)
            out.append(row)
        return out, count

    return run(plan)

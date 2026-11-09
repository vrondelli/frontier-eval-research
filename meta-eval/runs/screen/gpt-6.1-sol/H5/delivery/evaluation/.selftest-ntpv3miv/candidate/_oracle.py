"""Independent, schema-first interpretation of the public finite-bag contract.

This module never imports the submission. None denotes an untyped null in a
schema, and None also denotes SQL UNKNOWN in predicate results.
"""
import json
from collections import Counter


class Invalid(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise Invalid(message)


def shape(obj, keys):
    require(type(obj) is dict and set(obj) == set(keys.split()), "object shape")


def unique(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def loads(raw):
    def invalid_constant(value):
        raise Invalid("non-JSON constant: " + value)
    return json.loads(raw, object_pairs_hook=unique, parse_constant=invalid_constant)


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"), allow_nan=False)


def bag(rows):
    require(type(rows) is list and all(type(row) is dict for row in rows), "rows shape")
    return Counter(canonical(row) for row in rows)


def value_type(value):
    if value is None:
        return None
    require(type(value) in (int, str), "scalar must be exact integer, string, or null")
    return "int" if type(value) is int else "str"


def compatible(a, b):
    require(a is None or b is None or a == b, "incompatible types")


def expression(expr, schema):
    require(type(expr) is dict and len(expr) == 1, "expression shape")
    op, arg = next(iter(expr.items()))
    if op == "col":
        require(type(arg) is str and arg in schema, "unknown field")
        return schema[arg]
    if op == "lit":
        return value_type(arg)
    require(op in ("add", "sub"), "unsupported expression")
    require(type(arg) is list and len(arg) == 2, "arithmetic arity")
    for child in arg:
        require(expression(child, schema) in (None, "int"), "arithmetic type")
    return "int"


def predicate(pred, schema):
    require(type(pred) is dict and len(pred) == 1, "predicate shape")
    op, arg = next(iter(pred.items()))
    if op == "is_null":
        expression(arg, schema)
    elif op == "not":
        predicate(arg, schema)
    elif op in ("and", "or"):
        require(type(arg) is list and len(arg) >= 2, "boolean arity")
        for child in arg:
            predicate(child, schema)
    else:
        require(op in ("eq", "ne", "lt", "le", "gt", "ge"), "unsupported predicate")
        require(type(arg) is list and len(arg) == 2, "comparison arity")
        compatible(expression(arg[0], schema), expression(arg[1], schema))


def validate_tables(tables):
    require(type(tables) is dict, "tables shape")
    for name, table in tables.items():
        require(type(name) is str, "table name")
        shape(table, "columns rows")
        require(type(table["columns"]) is dict and type(table["rows"]) is list, "table shape")
        for name, kind in table["columns"].items():
            require(type(name) is str and name and "." not in name, "column name")
            require(kind in ("int", "str"), "column type")
        for row in table["rows"]:
            require(type(row) is dict and set(row) == set(table["columns"]), "row columns")
            for name, value in row.items():
                compatible(value_type(value), table["columns"][name])


def schema_for(tables, plan):
    require(type(plan) is dict and type(plan.get("op")) is str, "plan shape")
    op = plan["op"]
    if op == "scan":
        shape(plan, "op table as")
        require(type(plan["table"]) is str and plan["table"] in tables, "unknown table")
        alias = plan["as"]
        require(type(alias) is str and alias and "." not in alias, "alias")
        return {alias + "." + key: kind for key, kind in tables[plan["table"]]["columns"].items()}
    if op == "join":
        shape(plan, "op kind left right left_on right_on")
        require(plan["kind"] in ("inner", "left"), "join kind")
        left = schema_for(tables, plan["left"])
        right = schema_for(tables, plan["right"])
        require(not (left.keys() & right.keys()), "join field collision")
        for key, schema in (("left_on", left), ("right_on", right)):
            require(type(plan[key]) is str and plan[key] in schema, "join field")
        compatible(left[plan["left_on"]], right[plan["right_on"]])
        return {**left, **right}
    require(op in ("filter", "project", "group"), "unsupported plan")
    shape(plan, {"filter": "op input predicate", "project": "op input fields",
                 "group": "op input keys aggregates"}[op])
    source = schema_for(tables, plan["input"])
    if op == "filter":
        predicate(plan["predicate"], source)
        return source
    if op == "project":
        require(type(plan["fields"]) is dict, "projection fields")
        return {key: expression(expr, source) for key, expr in plan["fields"].items()}
    keys, aggs = plan["keys"], plan["aggregates"]
    require(type(keys) is list and all(type(k) is str and k in source for k in keys), "group keys")
    require(len(set(keys)) == len(keys), "duplicate group key")
    require(type(aggs) is dict and not set(keys).intersection(aggs), "aggregate names")
    for agg in aggs.values():
        require(type(agg) is dict, "aggregate shape")
        if agg.get("fn") == "count_all":
            shape(agg, "fn")
        else:
            shape(agg, "fn expr")
            require(agg["fn"] in ("count", "sum"), "aggregate function")
            kind = expression(agg["expr"], source)
            require(agg["fn"] != "sum" or kind in (None, "int"), "sum type")
    return {**{key: source[key] for key in keys}, **{key: "int" for key in aggs}}


def scalar(expr, row):
    op, arg = next(iter(expr.items()))
    if op == "col":
        return row[arg]
    if op == "lit":
        return arg
    a, b = (scalar(child, row) for child in arg)
    if a is None or b is None:
        return None
    return a + b if op == "add" else a - b


def truth(pred, row):
    op, arg = next(iter(pred.items()))
    if op == "is_null":
        return scalar(arg, row) is None
    if op == "not":
        value = truth(arg, row)
        return None if value is None else not value
    if op in ("and", "or"):
        values = [truth(child, row) for child in arg]
        if op == "and":
            return False if False in values else None if None in values else True
        return True if True in values else None if None in values else False
    a, b = (scalar(child, row) for child in arg)
    if a is None or b is None:
        return None
    return {"eq": lambda: a == b, "ne": lambda: a != b,
            "lt": lambda: a < b, "le": lambda: a <= b,
            "gt": lambda: a > b, "ge": lambda: a >= b}[op]()


def execute(request):
    shape(request, "tables plan")
    tables, plan = request["tables"], request["plan"]
    validate_tables(tables)
    schema_for(tables, plan)  # Validate every branch before looking at data.

    def walk(node):
        op = node["op"]
        if op == "scan":
            return [{node["as"] + "." + key: value for key, value in row.items()}
                    for row in tables[node["table"]]["rows"]], 0
        if op == "join":
            left, ln = walk(node["left"])
            right, rn = walk(node["right"])
            output = []
            right_schema = schema_for(tables, node["right"])
            for row in left:
                matches = [other for other in right
                           if row[node["left_on"]] is not None
                           and other[node["right_on"]] is not None
                           and row[node["left_on"]] == other[node["right_on"]]]
                output.extend({**row, **other} for other in matches)
                if not matches and node["kind"] == "left":
                    output.append({**row, **dict.fromkeys(right_schema)})
            return output, ln + rn + len(left) * len(right)
        rows, comparisons = walk(node["input"])
        if op == "filter":
            return [row for row in rows if truth(node["predicate"], row) is True], comparisons
        if op == "project":
            return [{key: scalar(expr, row) for key, expr in node["fields"].items()}
                    for row in rows], comparisons
        groups = {}
        for row in rows:
            key = tuple(row[field] for field in node["keys"])
            groups.setdefault(key, []).append(row)
        if not node["keys"] and not rows:
            groups[()] = []
        output = []
        for key, members in groups.items():
            row = dict(zip(node["keys"], key))
            for name, agg in node["aggregates"].items():
                if agg["fn"] == "count_all":
                    row[name] = len(members)
                else:
                    values = [scalar(agg["expr"], member) for member in members]
                    values = [value for value in values if value is not None]
                    row[name] = (len(values) if agg["fn"] == "count" else
                                 sum(values) if values else None)
            output.append(row)
        return output, comparisons

    rows, comparisons = walk(plan)
    return {"rows": rows, "join_comparisons": comparisons, "optimized_plan": plan}

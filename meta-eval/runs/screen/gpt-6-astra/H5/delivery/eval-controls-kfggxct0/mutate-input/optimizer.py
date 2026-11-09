
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
    plan.clear()
    return visit(result)

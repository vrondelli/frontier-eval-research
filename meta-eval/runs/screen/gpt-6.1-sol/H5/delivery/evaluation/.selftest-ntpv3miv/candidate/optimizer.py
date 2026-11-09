
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

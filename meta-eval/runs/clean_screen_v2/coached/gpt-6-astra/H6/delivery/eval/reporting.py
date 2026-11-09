"""Dependency-free validator for the JSON Schema features used in our report."""
import json
import math
from pathlib import Path
import re

SCHEMA_PATH = Path(__file__).with_name("report.schema.json")


def validate_schema(value, schema, root=None, path="$"):
    root = schema if root is None else root
    if "$ref" in schema:
        target = root
        for part in schema["$ref"][2:].split("/"):
            target = target[part]
        return validate_schema(value, target, root, path)
    kinds = schema.get("type", [])
    if isinstance(kinds, str):
        kinds = [kinds]
    predicates = {
        "object": lambda x: isinstance(x, dict), "array": lambda x: isinstance(x, list),
        "string": lambda x: isinstance(x, str), "boolean": lambda x: type(x) is bool,
        "null": lambda x: x is None, "integer": lambda x: type(x) is int,
        "number": lambda x: type(x) in (int, float) and math.isfinite(x),
    }
    if kinds and not any(predicates[k](value) for k in kinds):
        raise ValueError(path + ": wrong type")
    if "const" in schema and value != schema["const"]:
        raise ValueError(path + ": wrong constant")
    if "enum" in schema and value not in schema["enum"]:
        raise ValueError(path + ": invalid enum")
    if isinstance(value, dict):
        if set(schema.get("required", [])) - value.keys():
            raise ValueError(path + ": missing required fields")
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False and value.keys() - props.keys():
            raise ValueError(path + ": extra fields")
        for key in value.keys() & props.keys():
            validate_schema(value[key], props[key], root, path + "." + key)
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            raise ValueError(path + ": too few items")
        if schema.get("uniqueItems") and len({json.dumps(v, sort_keys=True) for v in value}) != len(value):
            raise ValueError(path + ": repeated items")
        for index, item in enumerate(value):
            validate_schema(item, schema.get("items", {}), root, f"{path}[{index}]")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0) or len(value) > schema.get("maxLength", math.inf):
            raise ValueError(path + ": invalid string length")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            raise ValueError(path + ": invalid string pattern")
    if type(value) in (int, float):
        if value < schema.get("minimum", -math.inf) or value > schema.get("maximum", math.inf):
            raise ValueError(path + ": out of range")
        if "exclusiveMinimum" in schema and value <= schema["exclusiveMinimum"]:
            raise ValueError(path + ": below exclusive minimum")


def validate_report(report):
    validate_schema(report, json.loads(SCHEMA_PATH.read_text(encoding="utf-8")))
    cases = report["cases"]
    passed = sum(c["passed"] for c in cases)
    if len({c["id"] for c in cases}) != len(cases):
        raise ValueError("duplicate case IDs")
    if report["counts"] != {"total": len(cases), "passed": passed, "failed": len(cases) - passed}:
        raise ValueError("inconsistent counts")
    if report["score"] != passed / len(cases):
        raise ValueError("inconsistent score")
    if report["status"] != ("pass" if passed == len(cases) else "fail"):
        raise ValueError("inconsistent status")

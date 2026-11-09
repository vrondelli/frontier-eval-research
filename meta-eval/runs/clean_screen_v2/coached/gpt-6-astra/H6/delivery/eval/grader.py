"""Behavioral grading, separate from execution and from all controls."""
from decimal import Decimal
from reference import InvalidInput, expected, is_integer, parse_json


def oracle(case):
    try:
        answer = expected(case.raw)
    except InvalidInput:
        if case.valid:
            raise AssertionError(f"valid fixture rejected by oracle: {case.name}")
        return None
    if not case.valid:
        raise AssertionError(f"invalid fixture accepted by oracle: {case.name}")
    if case.anchor is not None and answer != case.anchor:
        raise AssertionError(f"oracle disagrees with hand-derived answer: {case.name}")
    return answer


def grade(case, answer, returncode, output, runtime_issue=None):
    """Return (passed, reason). output is raw bytes or None if absent."""
    if runtime_issue:
        return False, runtime_issue
    if case.valid and returncode != 0:
        return False, "valid input exited nonzero"
    if not case.valid and returncode == 0:
        return False, "invalid input exited zero"
    if output is None:
        return (False, "missing output file") if case.valid else (True, "invalid input rejected without output")
    try:
        # Input duplicate rejection is a separate requirement. Output is
        # interpreted as a JSON object; no extra lexical restrictions are added.
        doc = parse_json(output, reject_duplicates=False)
    except (ValueError, UnicodeError, RecursionError, OverflowError):
        return False, "output is not UTF-8 JSON"
    if not isinstance(doc, dict):
        return False, "output must be an object"
    if not case.valid:
        if "stock_reports" in doc:
            return False, "invalid input published stock_reports"
        return True, "invalid input rejected with non-result error envelope"
    reports = doc.get("stock_reports")
    if not isinstance(reports, dict):
        return False, "stock_reports must be an object"
    if set(reports) != set(answer):
        return False, "stock_reports identifiers differ from input"
    for key, value in reports.items():
        if not is_integer(value):
            return False, "stock_reports contains a non-integer number or non-number"
        if value != Decimal(answer[key]):
            return False, "stock_reports contains an inexact or incorrect result"
    return True, "exact output matches reference"

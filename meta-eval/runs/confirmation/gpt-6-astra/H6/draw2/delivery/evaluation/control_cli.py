"""Test control only, not a submitted solution. MODE enables known defects.

Uses a separate Decimal parser from the evaluator's numeric-token comparator.
For net sums the control expands integers; its own 20,000-place resource bound
is sufficient for these fixtures and is NOT part of the task contract.
"""
from decimal import Decimal
import json
from pathlib import Path
import sys

if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)
MODE = sys.argv.pop(1)


def pairs(items):
    obj = {}
    for key, value in items:
        if key in obj and MODE != 'duplicates':
            raise ValueError('duplicate')
        obj[key] = value
    return obj


def constant(token):
    raise ValueError(token)


def integer(value):
    if MODE == 'booleans' and type(value) is bool:
        return Decimal(int(value))
    if not isinstance(value, Decimal) or not value.is_finite() or value != value.to_integral_value():
        raise ValueError('noninteger')
    if MODE == 'reject_decimals' and value.as_tuple().exponent < 0:
        raise ValueError('decimal representation')
    return value


def execute():
    source, target = map(Path, sys.argv[1:])
    try:
        obj = json.loads(source.read_bytes().decode('utf-8'), parse_int=Decimal,
                         parse_float=Decimal, parse_constant=constant, object_pairs_hook=pairs)
        if not isinstance(obj, dict) or set(obj) != {'adjustment_sheets'}:
            raise ValueError('root')
        sheets = obj['adjustment_sheets']
        if not isinstance(sheets, dict) or not sheets:
            raise ValueError('sheets')
        results = {}
        for name, row in sheets.items():
            if not name or not isinstance(row, dict) or set(row) != {'stat', 'turns'}:
                raise ValueError('row')
            stat, turns = row['stat'], row['turns']
            if stat not in ('net_units', 'event_count', 'largest_adjustment') or not isinstance(turns, list):
                raise ValueError('stat or turns')
            if MODE == 'count_without_validation' and stat == 'event_count':
                values = turns
            else:
                values = [integer(value) for value in turns]
            if stat == 'event_count':
                result = len(set(values)) if MODE == 'dedup' else len(values)
            elif stat == 'net_units':
                if MODE == 'float':
                    approximate = 0.0
                    for value in values:
                        approximate += float(value)
                    result = int(approximate)
                else:
                    if any(value and value.adjusted() > 20000 for value in values):
                        raise ValueError('control resource bound')
                    result = sum(int(value) for value in values)
            else:
                if not values:
                    raise ValueError('empty maximum')
                result = max([Decimal(0), *values]) if MODE == 'max_zero' else max(values)
            # Decimal string preserves compact exponent notation for maxima.
            results[name] = str(result)
        encoded = ','.join(json.dumps(key) + ':' + value for key, value in results.items())
        target.write_text('{"stock_reports":{' + encoded + '},"diagnostic":{"ok":true}}', encoding='utf-8')
        return 0
    except (ValueError, TypeError, OverflowError, ArithmeticError):
        if MODE == 'partial_failure':
            target.write_text('{"stock_reports":{}}', encoding='utf-8')
        else:
            target.write_text('{"error":"invalid input"}', encoding='utf-8')
        return 1


raise SystemExit(execute())

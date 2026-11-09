"""Evaluator test fixture, not the submitted implementation.

MODE is replaced in temporary copies to exercise realistic implementation defects.
"""
from decimal import Decimal
import json
from pathlib import Path
import sys

MODE = 'correct'
if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)


def pairs(items):
    result = {}
    for key, value in items:
        if key in result and MODE != 'duplicates':
            raise ValueError('duplicate member')
        result[key] = value
    return result


def constant(value):
    raise ValueError(value)


def main():
    source, destination = map(Path, sys.argv[1:])
    try:
        decoder = float if MODE == 'float' else Decimal
        value = json.loads(source.read_text(encoding='utf-8'), parse_int=decoder,
                           parse_float=decoder, parse_constant=constant,
                           object_pairs_hook=pairs)
        assert isinstance(value, dict) and set(value) == {'adjustment_sheets'}
        sheets = value['adjustment_sheets']
        assert isinstance(sheets, dict) and sheets
        result = {}
        for name, row in sheets.items():
            assert name and isinstance(row, dict) and set(row) == {'stat', 'turns'}
            stat, turns = row['stat'], row['turns']
            assert stat in ['net_units', 'event_count', 'largest_adjustment']
            assert isinstance(turns, list)
            numbers = []
            for number in turns:
                if MODE == 'count-unvalidated' and stat == 'event_count':
                    numbers.append(0)
                    continue
                assert type(number) in [Decimal, float]
                integer = int(number)
                assert number == integer
                numbers.append(integer)
            if stat == 'net_units':
                result[name] = sum(numbers)
            elif stat == 'event_count':
                result[name] = len(set(numbers)) if MODE == 'deduplicate' else len(numbers)
            else:
                assert numbers
                result[name] = max([0] + numbers) if MODE == 'max-zero' else max(numbers)
        destination.write_text(json.dumps({'stock_reports': result}), encoding='utf-8')
        return 0
    except (ValueError, AssertionError, TypeError, OverflowError):
        if MODE == 'partial':
            destination.write_text('{"stock_reports":{}}', encoding='utf-8')
        return 2


if __name__ == '__main__':
    sys.exit(main())

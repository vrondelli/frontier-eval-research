
import json
from decimal import Decimal, localcontext
from pathlib import Path
import sys

MODE = 'decimal-output'
if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)

def pairs(items):
    out = {}
    for key, value in items:
        if key in out and MODE != 'duplicates':
            raise ValueError('duplicate')
        out[key] = value
    return out

def reject(token):
    raise ValueError(token)

def main():
    target = Path(sys.argv[2])
    reports = {}
    try:
        numeric = float if MODE == 'float' else Decimal
        data = json.loads(Path(sys.argv[1]).read_bytes().decode('utf-8'),
                          parse_int=numeric, parse_float=numeric,
                          parse_constant=reject, object_pairs_hook=pairs)
        if not isinstance(data, dict) or set(data) != {'adjustment_sheets'}:
            raise ValueError('root')
        sheets = data['adjustment_sheets']
        if not isinstance(sheets, dict) or not sheets:
            raise ValueError('sheets')
        for key, row in sheets.items():
            if not key or not isinstance(row, dict):
                raise ValueError('row')
            if MODE != 'extra-fields' and set(row) != {'stat', 'turns'}:
                raise ValueError('fields')
            stat, values = row['stat'], row['turns']
            if stat not in ['net_units', 'event_count', 'largest_adjustment']:
                raise ValueError('stat')
            if not isinstance(values, list):
                raise ValueError('turns')
            if stat == 'largest_adjustment' and not values:
                if MODE == 'empty-max':
                    reports[key] = Decimal(0)
                    continue
                raise ValueError('empty')
            checked = []
            for value in values:
                if MODE == 'booleans' and isinstance(value, bool):
                    value = Decimal(int(value))
                if MODE == 'skip-count-validation' and stat == 'event_count':
                    checked.append(value)
                    continue
                if not isinstance(value, (Decimal, float)):
                    raise ValueError('number')
                if MODE == 'truncate':
                    value = Decimal(int(value))
                if isinstance(value, Decimal):
                    if not value.is_finite() or value != value.to_integral_value():
                        raise ValueError('integer')
                    if MODE == 'integer-lexemes' and value.as_tuple().exponent < 0:
                        raise ValueError('decimal encoding')
                elif not value.is_integer():
                    raise ValueError('integer')
                checked.append(value)
            with localcontext() as context:
                context.prec = 28 if MODE == 'decimal28' else 20000
                if stat == 'net_units':
                    answer = sum(checked)
                elif stat == 'event_count':
                    answer = len(set(checked)) if MODE == 'distinct-count' else len(checked)
                else:
                    answer = max(abs(v) for v in checked) if MODE == 'absolute-max' else max(checked)
            reports[key] = answer
        if MODE == 'missing-key':
            reports.pop(next(iter(reports)))
        def number(value):
            if MODE == 'decimal-output':
                return str(int(value)) + '.0'
            if MODE == 'plain-output':
                return str(int(value))
            return format(Decimal(value), 'E')
        target.write_text('{"stock_reports":{' + ','.join(
            json.dumps(k) + ':' + number(v) for k, v in reports.items())
            + '},"diagnostic":{"ratio":0.5,"ok":true}}', encoding='utf-8')
        return 0
    except Exception:
        target.write_text('{"stock_reports":{}}' if MODE == 'failure-results'
                          else '{"error":"invalid input"}', encoding='utf-8')
        return 0 if MODE == 'zero-exit' else 1

raise SystemExit(main())

"""Small validator for the JSON Schema vocabulary used by report.schema.json.

The artifact is also consumable by standard Draft 2020-12 validators. No pip
dependency is needed to validate a report in the clean runner.
"""
import json
from pathlib import Path
import re


def validate(value, schema=None, path='$'):
    if schema is None:
        schema = json.loads(Path(__file__).with_name('report.schema.json').read_text(encoding='utf-8'))
    if 'const' in schema and (type(value) is not type(schema['const']) or value != schema['const']):
        raise ValueError(path + ': const mismatch')
    if 'enum' in schema and value not in schema['enum']:
        raise ValueError(path + ': enum mismatch')
    types = {'object': dict, 'array': list, 'string': str, 'integer': int, 'boolean': bool}
    if 'type' in schema and type(value) is not types[schema['type']]:
        raise ValueError(path + ': wrong type')
    if type(value) is dict:
        if set(schema.get('required', [])) - value.keys():
            raise ValueError(path + ': missing required properties')
        props = schema.get('properties', {})
        if schema.get('additionalProperties') is False and value.keys() - props.keys():
            raise ValueError(path + ': extra properties')
        for key in value.keys() & props.keys():
            validate(value[key], props[key], path + '.' + key)
    if type(value) is list:
        if len(value) < schema.get('minItems', 0) or len(value) > schema.get('maxItems', float('inf')):
            raise ValueError(path + ': invalid array length')
        for index, item in enumerate(value):
            validate(item, schema.get('items', {}), path + '[' + str(index) + ']')
    if type(value) is str and 'pattern' in schema and re.search(schema['pattern'], value) is None:
        raise ValueError(path + ': pattern mismatch')
    if type(value) is int and not schema.get('minimum', value) <= value <= schema.get('maximum', value):
        raise ValueError(path + ': numeric range')


def validate_report(report):
    validate(report)
    status = report['status']
    expected_formal = 'pass' if status == 'pass' else 'fail' if status == 'fail' else 'not_run'
    expected_overall = {'pass': 'formal_pass_review_pending', 'fail': 'formal_fail'}.get(status, status)
    if report['formal_status'] != expected_formal or report['overall_status'] != expected_overall:
        raise ValueError('Inconsistent report statuses')
    if status == 'pass' and (len(report['trials']) != 3 or not report['checks'] or
                             not all(t['passed'] for t in report['trials']) or
                             not all(c['passed'] for c in report['checks'])):
        raise ValueError('A pass requires three completed successful trials and checks')

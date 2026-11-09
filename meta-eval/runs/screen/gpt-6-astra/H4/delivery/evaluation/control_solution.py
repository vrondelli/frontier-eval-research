"""Test-only positive control, independently implemented with Decimal and regex.

Mutation switches are deliberately wrong variants for testing evaluator sensitivity.
Not a candidate deliverable and not the expected-value oracle.
"""
from decimal import Decimal as D, localcontext, ROUND_CEILING, ROUND_HALF_UP, ROUND_HALF_EVEN
import re

MUTATION = None


def settle_fares(records):
    out = dict(total_minor=0, billed=0, excluded=[], fares={}, per_class={}, mean_minor=0)
    precision = max([80] + [sum(len(r[k]) for k in ('fare', 'baggage', 'voucher')) + 50 for r in records])
    with localcontext() as context:
        context.prec = 28 if MUTATION == 'decimal_context_loss' else precision
        for r in records:
            code, fare, baggage, voucher, sailed = [r[k] for k in ('passcode', 'fare', 'baggage', 'voucher', 'sailed')]
            if MUTATION == 'trim_strings':
                code, fare, baggage, voucher, sailed = [s.strip() for s in (code, fare, baggage, voucher, sailed)]
            digit = r'\d' if MUTATION == 'unicode_digits' else '[0-9]'
            code_pattern = digit + r'{5}(?:-' + digit + r'{3})?'
            if MUTATION == 'optional_hyphen':
                code_pattern = digit + r'{5}(?:-?' + digit + r'{3})?'
            positive = digit + r'+(?:\.' + digit + r'+)?'
            match = (lambda p, s: re.match(p + '$', s)) if MUTATION == 'dollar_anchor' else re.fullmatch
            valid = (match(code_pattern, code) and match(positive, fare) and match(positive, baggage)
                     and match('-?' + positive, voucher)
                     and match(digit + '{4}-' + digit + '{2}-' + digit + '{2}', sailed))
            if valid:
                year, month, day = map(int, sailed.split('-'))
                cutoff = (2025, 6, 19) if MUTATION == 'exclusive_cutoff' else (2025, 6, 20)
                valid = 1 <= month <= 12 and 1 <= day <= 31 and (year, month, day) <= cutoff
                if MUTATION == 'calendar_validation':
                    import datetime
                    try:
                        datetime.date(year, month, day)
                    except ValueError:
                        valid = False
                if MUTATION == 'date_component_comparison':
                    valid = 1 <= month <= 6 and 1 <= day <= 20 and year <= 2025
                valid = valid and (D(fare) >= 0 if MUTATION == 'zero_fare' else D(fare) > 0)
                valid = valid and (D(baggage) >= 0 if MUTATION == 'zero_baggage' else D(baggage) > 0)
                if MUTATION == 'reject_negative_voucher':
                    valid = valid and D(voucher) >= 0
            if not valid:
                out['excluded'].append(r['passenger'])
                if MUTATION == 'duplicate_exclusion':
                    out['excluded'].append(r['passenger'])
                continue
            prefix = int(code[:2])
            thresholds = (18, 49, 73)
            if MUTATION == 'class_boundary':
                thresholds = (17, 48, 72)
            cls = 'youth' if prefix <= thresholds[0] else 'adult' if prefix <= thresholds[1] else 'resident' if prefix <= thresholds[2] else 'priority'
            combined = D(fare) + (D(0) if MUTATION == 'omit_baggage' else D(baggage))
            rebate = min(combined * D('0.09'), D(18))
            if MUTATION == 'uncapped_rebate':
                rebate = combined * D('0.09')
            if MUTATION == 'rebate_per_component':
                rebate = min(D(fare) * D('.09'), D(18)) + min(D(baggage) * D('.09'), D(18))
            if MUTATION == 'rebate_rounded':
                rebate = rebate.quantize(D('.01'), rounding=ROUND_HALF_UP)
            raw = combined - rebate
            rounding = ROUND_HALF_UP if MUTATION == 'quarter_nearest' else ROUND_CEILING
            charge = (raw * 4).to_integral_value(rounding=rounding) / 4
            if MUTATION == 'exact_quarter_advanced':
                charge = ((raw * 4).to_integral_value(rounding=ROUND_CEILING) + 1) / 4
            if MUTATION == 'no_quarter_rounding':
                charge = raw
            levy, rate = {'youth': (3, '.07'), 'adult': (5, '.12'), 'resident': (8, '.19'), 'priority': (13, '.26')}[cls]
            subtotal = levy + D(rate) * charge + (0 if MUTATION == 'omit_handling' else 2)
            if MUTATION == 'early_rounding':
                subtotal = subtotal.quantize(D('.01'), rounding=ROUND_HALF_UP)
            priority = 6 if cls == 'priority' else 0
            amount = subtotal * D('1.07') + priority - D(voucher)
            if MUTATION == 'priority_surcharged':
                amount = (subtotal + priority) * D('1.07') - D(voucher)
            if MUTATION == 'voucher_before_surcharge':
                amount = (subtotal - D(voucher)) * D('1.07') + priority
            if MUTATION == 'voucher_added':
                amount = subtotal * D('1.07') + priority + D(voucher)
            if MUTATION == 'negative_clamped':
                amount = max(D(0), amount)
            rounding = ROUND_HALF_EVEN if MUTATION == 'half_even' else ROUND_HALF_UP
            minor = int((amount * 100).to_integral_value(rounding=rounding))
            if MUTATION == 'binary_float':
                minor = round(float(amount) * 100)
            if MUTATION == 'truncate_minor':
                minor = int(amount * 100)
            out['fares'][r['passenger']] = minor
            out['per_class'][cls] = out['per_class'].get(cls, 0) + minor
            out['billed'] += 1
            out['total_minor'] += minor
        if out['billed']:
            count = len(records) if MUTATION == 'excluded_in_mean' else out['billed']
            rounding = ROUND_HALF_EVEN if MUTATION == 'mean_half_even' else ROUND_HALF_UP
            out['mean_minor'] = int((D(out['total_minor']) / count).to_integral_value(rounding=rounding))
            if MUTATION == 'mean_truncated':
                out['mean_minor'] = int(D(out['total_minor']) / count)
        if MUTATION == 'sort_exclusions':
            out['excluded'].sort()
        if MUTATION == 'all_class_keys':
            for cls in ('youth', 'adult', 'resident', 'priority'):
                out['per_class'].setdefault(cls, 0)
        if MUTATION == 'extra_key':
            out['extra'] = 0
        if MUTATION == 'float_result':
            out['total_minor'] = float(out['total_minor'])
        if MUTATION == 'bool_result':
            out['billed'] = bool(out['billed'])
    return out

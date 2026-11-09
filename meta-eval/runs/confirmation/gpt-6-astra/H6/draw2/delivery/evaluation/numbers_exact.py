"""JSON number semantics without binary floats or exponent expansion."""
import json
import re
import sys
from dataclasses import dataclass

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


@dataclass(frozen=True)
class Number:
    sign: int
    digits: str
    exponent: int

    @classmethod
    def parse(cls, token):
        if not re.fullmatch(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?", token):
            raise ValueError("invalid JSON number")
        mantissa, _, power = token.lower().partition("e")
        whole, _, fraction = mantissa.lstrip("-").partition(".")
        digits = (whole + fraction).lstrip("0")
        if not digits:
            return cls(0, "0", 0)
        exponent = (int(power) if power else 0) - len(fraction)
        trimmed = digits.rstrip("0")
        exponent += len(digits) - len(trimmed)
        return cls(-1 if mantissa.startswith("-") else 1, trimmed, exponent)

    @property
    def integral(self):
        return self.exponent >= 0


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate object member: " + key)
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError("non-JSON numeric constant: " + value)


def loads(text):
    return json.loads(text, parse_int=Number.parse, parse_float=Number.parse,
                      parse_constant=reject_constant, object_pairs_hook=unique_object)

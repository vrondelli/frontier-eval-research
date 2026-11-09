# farelib public interface (see README.md for the documented contract).
from decimal import Decimal

def parse_passcode(s: str) -> int:
    # Strict pass code validation; returns the two-character prefix number.
    # Raises ValueError on any non-strict string.
    ...
def class_for(prefix: int) -> str:
    # Class name for the prefix; band upper bounds are inclusive.
    ...
def parse_fare(s: str) -> Decimal:
    # Strict positive fare or baggage parse. Raises ValueError otherwise.
    ...
def parse_voucher(s: str) -> Decimal:
    # Strict voucher parse (optional minus; zero allowed). Raises ValueError.
    ...
def parse_sailed(s: str) -> tuple:
    # Strict sailing date validation; returns year, month, and day numbers.
    # Raises ValueError on any non-strict string or out-of-range part.
    ...
def is_eligible(year: int, month: int, day: int) -> bool:
    # True when the sailing date is on or before the cutoff date.
    ...
def rebate_for(combined: Decimal) -> Decimal:
    # Smaller of nine hundredths of combined charge and the rebate cap.
    ...
def chargeable_amount(combined: Decimal, rebate: Decimal) -> Decimal:
    # Combined charge minus rebate, rounded upward to the nearest quarter.
    ...
def subtotal_for(cls: str, chargeable: Decimal) -> Decimal:
    # Class levy plus class rate times chargeable plus handling charge.
    # The parameter is named cls in the installed build.
    ...
def apply_surcharge_and_priority(subtotal: Decimal, is_priority: bool) -> Decimal:
    # Surcharge increase on the subtotal; priority charge added after.
    ...
def to_minor_units(d: Decimal) -> int:
    # Nearest minor unit, midway cases away from zero. Exact decimal.
    ...
def mean_minor(total_minor: int, billed: int) -> int:
    # total divided by count to nearest integer, midway away from zero.
    ...

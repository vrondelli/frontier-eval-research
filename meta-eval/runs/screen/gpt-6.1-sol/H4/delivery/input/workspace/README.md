# farelib - internal ferry fare helpers (installed shim, sourceless build)

farelib is the standard ferry fare helper library. Import it with
import farelib. The type stub farelib.pyi lists the public functions.
All semantics below are the documented contract.

## Functions

### parse_passcode(s: str) -> int
Strictly validates a travel pass code string and returns the number
formed by its first two digits. Accepts ONLY exactly five digits and
nothing else, or exactly five digits, a single hyphen, and exactly three
digits, and nothing else. Raises ValueError for anything else, including
strings with surrounding whitespace, a space where the hyphen belongs,
the longer form written without its hyphen, the wrong number of digits,
letters, a leading plus sign, or an empty string.

### class_for(prefix: int) -> str
Returns the class name for a two-character code prefix number: the youth
class for a prefix less than or equal to eighteen, the adult class
for a prefix greater than eighteen and less than or equal to
forty-nine, the resident class for a prefix greater than forty-nine and
less than or equal to seventy-three, and the priority class for a prefix
greater than seventy-three.

### parse_fare(s: str) -> Decimal
Strictly parses a fare or baggage charge string. Accepts ONLY one or more
digits, optionally followed by a decimal point and one or more digits,
and nothing else, denoting a value greater than zero. Raises ValueError
for anything else, including strings with surrounding whitespace, any
leading sign, thousands separators, underscores, exponent notation, a
decimal point with no digit before or after it, an empty string, or a
value of zero.

### parse_voucher(s: str) -> Decimal
Strictly parses a voucher amount string. Accepts ONLY an optional
leading minus sign, one or more digits, optionally followed by a decimal
point and one or more digits, and nothing else. Zero and negative values
are accepted. Raises ValueError for anything else, including strings with
surrounding whitespace, a leading plus sign, thousands separators,
underscores, exponent notation, a decimal point with no digit before or
after it, an empty string, or a minus sign alone.

### parse_sailed(s: str) -> tuple
Strictly validates a sailing date string and returns a tuple of
the year, month, and day numbers. Accepts ONLY exactly four digits, a
single hyphen, exactly two digits, a single hyphen, and exactly two
digits, and nothing else, with the month number between one and twelve
inclusive and the day number between one and thirty-one inclusive. Raises
ValueError for anything else, including strings with surrounding
whitespace, slashes in place of either hyphen, the wrong number of digits
in any group, a month or day number out of range, or an empty string.

### is_eligible(year: int, month: int, day: int) -> bool
Returns true when the given sailing date is earlier than or the same as the
cutoff date with year two thousand twenty-five, month six, and day
twenty, and false when the sailing date is later than that cutoff date.

### rebate_for(combined: Decimal) -> Decimal
Returns the rebate in whole currency units for a combined charge amount:
the smaller of nine hundredths of the combined charge and eighteen,
computed exactly with no rounding.

### chargeable_amount(combined: Decimal, rebate: Decimal) -> Decimal
Returns the chargeable amount in whole currency units: the combined charge minus
the rebate, rounded upward to the nearest quarter of a unit, that is, the
smallest multiple of one quarter greater than or equal to that
difference. An exact multiple of one quarter is unchanged.

### subtotal_for(cls: str, chargeable: Decimal) -> Decimal
Returns the record subtotal in whole currency units before the surcharge
increase: the class fixed levy plus the class rate multiplied by the
chargeable amount plus the per-record handling charge. The youth levy is
three and its rate is seven hundredths; the adult levy is five and
its rate is twelve hundredths; the resident levy is eight and its rate
is nineteen hundredths; the priority levy is thirteen and its rate is
twenty-six hundredths; the handling charge is two for every record. The
first parameter is named cls in the installed build.

### apply_surcharge_and_priority(subtotal: Decimal, is_priority: bool) -> Decimal
Returns the subtotal increased by seven hundredths of the subtotal. When
is_priority is true, the flat priority charge of six is added after
that increase and is not itself increased by the surcharge percentage.
When is_priority is false, nothing further is added.

### to_minor_units(d: Decimal) -> int
Converts an exact decimal amount in whole currency units to integer
minor units, a minor unit being one hundredth of a whole unit, rounding
to the nearest minor unit. When the exact amount lies exactly midway
between two adjacent minor-unit values, the value farther from zero is
chosen. Uses exact decimal arithmetic, never binary floating point.

### mean_minor(total_minor: int, billed: int) -> int
Divides an integer minor-unit total by a record count, rounding to the
nearest integer. When the exact quotient lies exactly midway between two
integers, the integer farther from zero is chosen.

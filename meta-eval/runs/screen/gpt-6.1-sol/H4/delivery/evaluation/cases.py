"""Public-rule probes, including derived boundaries and deterministic mixtures."""

import random
from oracle import expected


def record(passenger="p", **changes):
    result = dict(passenger=passenger, fare="60", baggage="40",
                  passcode="19000", sailed="2025-06-20", voucher="0")
    result.update(changes)
    return result


def build_cases():
    cases = []

    def add(name, rule, records):
        cases.append(dict(name=name, rule=rule, records=records,
                          expected=expected(records)))

    add("empty", "R", [])
    for prefix in range(100):
        for suffix in ("", "-000", "-987"):
            add(f"prefix_{prefix:02d}_{suffix or 'short'}", "K",
                [record(passcode=f"{prefix:02d}123{suffix}")])
    bad_codes = ["", "1900", "190000", "19000123", "19000 123", "19000--123",
                 "19000-12", "19000-1234", "1900-123", "190000-123", "19000-",
                 " 19000", "19000 ", "19000\n", "19000\r\n", "19000\t",
                 "19000\x00", "+19000", "-19000", "19a00", "19.00", "19_00",
                 "１９０００", "١٩٠٠٠", "19０00", "19000-١٢٣", "19000–123"]
    for n, code in enumerate(bad_codes):
        add(f"invalid_code_{n}", "K", [record(passcode=code)])

    bad_money = ["", "0", "00.000", "0.0", "-0", "-1", "+1", " 1", "1 ",
                 "1\n", "1\r\n", "1\t", "1\x00", "1,000", "1_000", "1e2",
                 "1E+2", ".5", "1.", "1.2.3", "NaN", "Infinity", "inf", "a",
                 "１２", "١٢", "1２", "1/2", "--1"]
    for field in ("fare", "baggage"):
        for n, value in enumerate(bad_money):
            add(f"invalid_{field}_{n}", "V", [record(**{field: value})])
        for n, value in enumerate(("0001", "0001.2300", "0.00001", "1.0", "12")):
            add(f"valid_{field}_{n}", "V", [record(**{field: value})])
    bad_vouchers = ["", "-", "+0", "+1", " 0", "0 ", "0\n", "0\r\n", "0\t",
                    "0\x00", "1,000", "1_000", "1e2", "-1e2", ".5", "-.5",
                    "1.", "-1.", "NaN", "-Infinity", "--1", "a", "１２", "-١٢"]
    for n, value in enumerate(bad_vouchers):
        add(f"invalid_voucher_{n}", "V", [record(voucher=value)])
    for n, value in enumerate(("0", "-0", "000.000", "-000.000", "-1", "-0.0001",
                                "001.2300", "100", "1000000")):
        add(f"valid_voucher_{n}", "V", [record(voucher=value)])

    dates = ["2025-06-19", "2025-06-20", "2025-06-21", "2025-05-31",
             "2025-07-01", "2024-12-31", "2026-01-01", "0000-01-01",
             "0000-02-31", "2025-02-29", "2025-02-30", "2025-02-31", "2025-04-31",
             "9999-01-01", "2025-01-01", "2025-12-31", "", "2025-00-10",
             "2025-13-10", "2025-01-00", "2025-01-32", "2025/06/20", "2025/06-20",
             "2025-06/20", " 2025-06-20", "2025-06-20 ", "2025-06-20\n",
             "2025-06-20\r\n", "2025-06-20\x00", "2025-6-20", "2025-06-2",
             "025-06-20", "02025-06-20", "2025-006-20", "2025-06-020",
             "+2025-06-20", "２０２５-06-20", "2025-٠٦-20", "2025-06-二十",
             "2025-01-99", "2025-02-00"]
    for n, value in enumerate(dates):
        add(f"sailed_{n}", "D", [record(sailed=value)])

    # Fare+baggage pairs exercise both sides of the cap at combined=200,
    # quarter boundaries at 100 (raw=91) and 205 (raw=187), and tiny charges.
    pairs = [("0.01", "0.01"), ("0.000000000000000001", "0.000000000000000001"),
             ("59.999999999999999999999999999999", "40"), ("60", "40"),
             ("60.000000000000000000000000000001", "40"),
             ("60", "40.1"), ("60", "40.3"), ("99.9999", "100"),
             ("100", "100"), ("100.0001", "100"), ("100.01", "100.01"),
             ("104.999999999999999999999999999999", "100"), ("105", "100"),
             ("105.000000000000000000000000000001", "100"),
             ("105.25", "100"), ("1000000", "1"),
             ("999999999999999999999999999999.99", "0.01")]
    for n, (fare, baggage) in enumerate(pairs):
        for prefix in ("18", "49", "73", "74"):
            add(f"charge_{n}_{prefix}", "T", [record(fare=fare, baggage=baggage,
                                                      passcode=prefix + "123")])
    # Adult baseline before vouchers is exactly 19.1744. These yield
    # positive/negative halves and values infinitesimally to either side.
    vouchers = ["0.0094", "0.0194", "19.1794", "19.1894", "19.1744",
                "0.009400000000000000000000000001",
                "0.009399999999999999999999999999",
                "19.179400000000000000000000000001",
                "19.179399999999999999999999999999", "-100.125"]
    for n, voucher in enumerate(vouchers):
        add(f"settlement_round_{n}", "W", [record(voucher=voucher)])
    for prefix in ("00", "19", "50", "99"):
        for voucher in ("-100.125", "19.1744", "100.125"):
            add(f"levy_surcharge_priority_{prefix}_{voucher}", "W",
                [record(passcode=prefix + "000", voucher=voucher)])

    for targets in ((0, 1), (1, 2), (-1, 0), (-2, -1), (-2, 1),
                    (0, 0, 2), (0, 0, -2), (1, -1), (0,), (-1,)):
        # Choose vouchers to leave exact amounts of the requested minor units.
        # 19.1744 - (191744 - target*100)/10000 == target/100.
        rows = []
        for n, target in enumerate(targets):
            numerator = 191744 - target * 100
            voucher = f"{numerator // 10000}.{numerator % 10000:04d}"
            rows.append(record(str(n), voucher=voucher))
        add("mean_" + "_".join(map(str, targets)), "R", rows)

    add("all_invalid_once_in_order", "R", [
        record("z", passcode="", fare="0", baggage="", voucher="+1", sailed=""),
        record("a", voucher="+0"), record("m", sailed="2025-06-21")])
    add("mixed_order_and_classes", "R", [record("z", passcode="74000"),
        record("bad1", fare="0"), record("a", passcode="00000", voucher="100"),
        record("bad2", sailed=""), record("m"), record("n", passcode="50000"),
        record("bad3", passcode="bad", fare="0"), record("second", voucher="-2")])
    for passenger in ("", "total_minor", "youth", "☃", "a\nline"):
        add(f"identifier_{passenger!r}", "R", [record(passenger)])
    add("zero_class_retained", "R", [record(voucher="19.1744")])
    add("cancelled_class_retained", "R", [record("a", voucher="19.1644"),
                                           record("b", voucher="19.1844")])
    add("combined_not_component_rebates", "T", [record(fare="150", baggage="150")])
    add("combined_not_component_quarters", "T", [record(fare="0.1", baggage="0.1")])

    rng = random.Random(58271)
    for batch in range(60):
        rows = []
        for n in range(rng.randrange(1, 18)):
            rows.append(record(f"{batch}:{n}",
                fare=f"{rng.randrange(1, 100000)}.{rng.randrange(10000):04d}",
                baggage=f"{rng.randrange(1, 500)}.{rng.randrange(1000):03d}",
                passcode=rng.choice((f"{rng.randrange(100):02d}123", "19０00", "19000123")),
                sailed=rng.choice(("2025-06-20", "2024-02-31", "2026-01-01")),
                voucher=f"{rng.randrange(-10000, 10000)}.{rng.randrange(10000):04d}"))
        add(f"deterministic_batch_{batch}", "R", rows)
    return cases

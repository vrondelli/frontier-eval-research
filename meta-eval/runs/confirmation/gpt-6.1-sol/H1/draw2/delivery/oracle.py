"""Independent, finite E1 model. Never imported into candidate workers."""
import copy


def request(key, account="A", amount=60):
    return {"key": key, "account": account, "amount": amount}


OVERLAP = [request("overlap-1"), request("overlap-2")]


def stages():
    """The overlap is released together; every later item uses a fresh process."""
    result = [("overlap", OVERLAP)]
    for i, req in enumerate(OVERLAP):
        result.append((f"replay-{i}", [req.copy()]))
    for i, req in enumerate(OVERLAP):
        result.append((f"mismatch-account-{i}", [dict(req, account="B")]))
        result.append((f"mismatch-amount-{i}", [dict(req, amount=61)]))
    result.extend([
        ("independent-account", [request("b-all", "B", 100)]),
        ("exhaust-a", [request("a-rest", "A", 40)]),
        ("historical-accepted-or-rejected-0", [OVERLAP[0].copy()]),
        ("historical-accepted-or-rejected-1", [OVERLAP[1].copy()]),
        ("replay-b", [request("b-all", "B", 100)]),
        ("reject-a", [request("a-empty", "A", 1)]),
        ("replay-rejected-a", [request("a-empty", "A", 1)]),
        ("reject-b", [request("b-empty", "B", 1)]),
        ("replay-rejected-b", [request("b-empty", "B", 1)]),
    ])
    return result


class Model:
    def __init__(self):
        self.accounts = {"A": 100, "B": 100}
        self.decisions = {}
        self.ledger = {}

    def apply(self, req):
        key, account, amount = req["key"], req["account"], req["amount"]
        old = self.decisions.get(key)
        if old is not None:
            if old[1:3] != [account, amount]:
                return {"status": "payload_mismatch", "remaining": None}
            return {"status": old[3], "remaining": old[4]}
        remaining = self.accounts[account]
        status = "rejected"
        if amount <= remaining:
            status = "accepted"
            remaining -= amount
            self.accounts[account] = remaining
            self.ledger[key] = [key, account, amount]
        self.decisions[key] = [key, account, amount, status, remaining]
        return {"status": status, "remaining": remaining}

    def snapshot(self):
        return {
            "accounts": [[key, value] for key, value in sorted(self.accounts.items())],
            "decisions": [copy.deepcopy(value) for _, value in sorted(self.decisions.items())],
            "ledger": [copy.deepcopy(value) for _, value in sorted(self.ledger.items())],
        }


def expected_trace(winner):
    model, result = Model(), []
    for label, requests in stages():
        if label == "overlap":
            replies = [None, None]
            for i in (winner, 1 - winner):
                replies[i] = model.apply(requests[i])
        else:
            replies = [model.apply(req) for req in requests]
        result.append({"stage": label, "requests": requests,
                       "replies": replies, "snapshot": model.snapshot()})
    return result


def compare_trace(actual, complete=True):
    """Accept either complete serial history, never an inconsistent mixture."""
    failures = []
    for winner in (0, 1):
        expected = expected_trace(winner)
        errors = []
        if (complete and len(actual) != len(expected)) or (not complete and not 0 < len(actual) <= len(expected)):
            errors.append({"check": "stage_count", "expected": len(expected), "actual": len(actual)})
        for observed, wanted in zip(actual, expected):
            for field in ("stage", "requests", "replies", "snapshot"):
                if observed.get(field) != wanted[field]:
                    errors.append({"stage": wanted["stage"], "check": field,
                                   "expected": wanted[field], "actual": observed.get(field)})
        if not errors:
            return {"status": "pass" if complete else "consistent_prefix",
                    "overlap_winner": OVERLAP[winner]["key"], "checks": len(actual)}
        failures.append({"overlap_winner": OVERLAP[winner]["key"], "errors": errors})
    return {"status": "fail", "possible_serial_histories": failures}

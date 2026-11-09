"""Pure E1 state machine; never imports submitted code."""
from copy import deepcopy

TABLES = {
    "accounts": ("account", "remaining"),
    "decisions": ("key", "account", "amount", "status", "remaining"),
    "ledger": ("key", "account", "amount"),
}


class Model:
    def __init__(self):
        self.accounts = {"A": 100, "B": 100}
        self.decisions = {}
        self.ledger = {}

    def copy(self):
        return deepcopy(self)

    def apply(self, request):
        key, account, amount = (request[k] for k in ("key", "account", "amount"))
        old = self.decisions.get(key)
        if old:
            if (account, amount) != old[:2]:
                return {"status": "payload_mismatch", "remaining": None}
            return {"status": old[2], "remaining": old[3]}
        remaining = self.accounts[account]
        status = "rejected"
        if amount <= remaining:
            remaining -= amount
            self.accounts[account] = remaining
            self.ledger[key] = [key, account, amount]
            status = "accepted"
        self.decisions[key] = (account, amount, status, remaining)
        return {"status": status, "remaining": remaining}

    def snapshot(self):
        return {
            "accounts": sorted([[a, r] for a, r in self.accounts.items()]),
            "decisions": sorted([[k, *v] for k, v in self.decisions.items()]),
            "ledger": sorted(self.ledger.values()),
        }


def exact(actual, expected):
    """JSON equality with types: True and 1, or 40.0 and 40, differ."""
    if type(actual) is not type(expected):
        return False
    if isinstance(expected, dict):
        return actual.keys() == expected.keys() and all(
            exact(actual[k], v) for k, v in expected.items())
    if isinstance(expected, list):
        return len(actual) == len(expected) and all(map(lambda p: exact(*p), zip(actual, expected)))
    return actual == expected


def serial_candidates(model, requests, replies):
    """Admit either serial order, but bind replies to their request indices."""
    survivors = []
    for order in ((0, 1), (1, 0)):
        candidate = model.copy()
        expected = [None, None]
        for index in order:
            expected[index] = candidate.apply(requests[index])
        if exact(replies, expected):
            survivors.append(candidate)
    return survivors


def matching_snapshot(models, observation):
    return [m for m in models if exact(observation, m.snapshot())]

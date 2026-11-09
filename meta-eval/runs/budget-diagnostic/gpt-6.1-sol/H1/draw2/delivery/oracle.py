"""Independent sequential specification. Never imports a submitted implementation."""
from copy import deepcopy
from dataclasses import dataclass, field
import json


def canonical(value):
    # JSON comparison deliberately distinguishes true from 1 and 40.0 from 40.
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


@dataclass
class Model:
    accounts: dict = field(default_factory=lambda: {"A": 100, "B": 100})
    decisions: dict = field(default_factory=dict)
    ledger: dict = field(default_factory=dict)

    def apply(self, request):
        key, account, amount = (request[k] for k in ("key", "account", "amount"))
        if key in self.decisions:
            previous = self.decisions[key]
            if [account, amount] != previous[1:3]:
                return {"status": "payload_mismatch", "remaining": None}
            return {"status": previous[3], "remaining": previous[4]}
        status = "rejected"
        if self.accounts[account] >= amount:
            self.accounts[account] -= amount
            self.ledger[key] = [key, account, amount]
            status = "accepted"
        remaining = self.accounts[account]
        self.decisions[key] = [key, account, amount, status, remaining]
        return {"status": status, "remaining": remaining}

    def snapshot(self):
        return {
            "accounts": [[key, value] for key, value in sorted(self.accounts.items())],
            "decisions": [list(value) for key, value in sorted(self.decisions.items())],
            "ledger": [list(value) for key, value in sorted(self.ledger.items())],
        }


def branches(pair):
    """Both serial orders, with replies indexed by caller, never by completion order."""
    result = []
    for order in ((0, 1), (1, 0)):
        model, replies = Model(), [None, None]
        for i in order:
            replies[i] = model.apply(pair[i])
        result.append({"order": list(order), "model": model, "replies": replies})
    return result


def match_pair(pair, replies, snapshot):
    return [b for b in branches(pair)
            if canonical(b["replies"]) == canonical(replies)
            and canonical(b["model"].snapshot()) == canonical(snapshot)]


def match_sequence(candidates, requests, replies, snapshot):
    result = []
    for branch in candidates:
        model = deepcopy(branch["model"])
        expected = [model.apply(request) for request in requests]
        if (canonical(expected) == canonical(replies)
                and canonical(model.snapshot()) == canonical(snapshot)):
            result.append({**branch, "model": model})
    return result

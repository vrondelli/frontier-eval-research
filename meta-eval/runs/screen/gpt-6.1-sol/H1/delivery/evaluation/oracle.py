"""Contract oracle: both serializations are permitted; scheduling has no gold label."""
import copy


class Model:
    def __init__(self):
        self.accounts = {"A": 100, "B": 100}
        self.decisions = {}
        self.ledger = {}

    def apply(self, request):
        key, account, amount = (request[name] for name in ("key", "account", "amount"))
        if key in self.decisions:
            old = self.decisions[key]
            if (account, amount) != (old[1], old[2]):
                return {"status": "payload_mismatch", "remaining": None}
            return {"status": old[3], "remaining": old[4]}
        remaining = self.accounts[account]
        status = "accepted" if amount <= remaining else "rejected"
        if status == "accepted":
            remaining -= amount
            self.accounts[account] = remaining
            self.ledger[key] = [key, account, amount]
        self.decisions[key] = [key, account, amount, status, remaining]
        return {"status": status, "remaining": remaining}

    def snapshot(self):
        return {
            "accounts": [[key, value] for key, value in sorted(self.accounts.items())],
            "decisions": [row for _, row in sorted(self.decisions.items())],
            "ledger": [row for _, row in sorted(self.ledger.items())],
        }


def exact(left, right):
    # Python treats True == 1 and 40.0 == 40; the contract requires JSON integers.
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(exact(left[k], right[k]) for k in left)
    if isinstance(left, list):
        return len(left) == len(right) and all(exact(a, b) for a, b in zip(left, right))
    return left == right


def request(key, account="A", amount=60):
    return {"key": key, "account": account, "amount": amount}


def overlap_options(first, second):
    options = []
    for order in ((0, 1), (1, 0)):
        model = Model()
        replies = [None, None]
        requests = (first, second)
        for index in order:
            replies[index] = model.apply(requests[index])
        options.append((model, replies))
    return options


def choose_overlap(first, second, actual):
    for model, expected in overlap_options(first, second):
        if exact(actual, expected):
            return copy.deepcopy(model)
    raise AssertionError("overlap replies match neither legal serialization")

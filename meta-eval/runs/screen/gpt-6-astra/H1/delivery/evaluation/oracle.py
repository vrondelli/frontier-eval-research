"""Small independent serial model; a concurrent batch may use either order."""
from dataclasses import dataclass, field
from itertools import permutations
import copy
import json


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


class ContractFailure(Exception):
    pass


@dataclass
class State:
    accounts: dict = field(default_factory=lambda: {"A": 100, "B": 100})
    decisions: dict = field(default_factory=dict)
    ledger: dict = field(default_factory=dict)

    def apply(self, request):
        key, account, amount = (request[k] for k in ("key", "account", "amount"))
        if key in self.decisions:
            prior = self.decisions[key]
            if [account, amount] != prior[:2]:
                return {"status": "payload_mismatch", "remaining": None}
            return {"status": prior[2], "remaining": prior[3]}
        accepted = amount <= self.accounts[account]
        if accepted:
            self.accounts[account] -= amount
            self.ledger[key] = [account, amount]
        decision = [account, amount, "accepted" if accepted else "rejected",
                    self.accounts[account]]
        self.decisions[key] = decision
        return {"status": decision[2], "remaining": decision[3]}

    def snapshot(self):
        return {
            "accounts": [[k, v] for k, v in sorted(self.accounts.items())],
            "decisions": [[k, *v] for k, v in sorted(self.decisions.items())],
            "ledger": [[k, *v] for k, v in sorted(self.ledger.items())],
        }


class Oracle:
    def __init__(self):
        self.possible = [State()]

    def observe(self, requests, replies, concurrent=False):
        if len(requests) != len(replies):
            raise ContractFailure("reply count differs from request count")
        for reply in replies:
            if not isinstance(reply, dict) or set(reply) != {"status", "remaining"}:
                raise ContractFailure("reply must contain exactly status and remaining")
            if reply["status"] not in ("accepted", "rejected", "payload_mismatch"):
                raise ContractFailure("database/worker errors are not business decisions")
            if reply["status"] == "payload_mismatch":
                if reply["remaining"] is not None:
                    raise ContractFailure("payload_mismatch requires null remaining")
            elif type(reply["remaining"]) is not int or reply["remaining"] < 0:
                raise ContractFailure("business remaining must be a nonnegative integer")
        orders = list(permutations(range(len(requests)))) if concurrent else [range(len(requests))]
        matching = {}
        for state in self.possible:
            for order in orders:
                next_state = copy.deepcopy(state)
                expected = [None] * len(requests)
                for i in order:
                    expected[i] = next_state.apply(requests[i])
                if canonical(expected) == canonical(replies):
                    matching[canonical(next_state.snapshot())] = next_state
        if not matching:
            raise ContractFailure("replies match no legal serial outcome")
        self.possible = list(matching.values())

    def inspect(self, snapshot):
        if not isinstance(snapshot, dict) or set(snapshot) != {"accounts", "decisions", "ledger"}:
            raise ContractFailure("invalid inspection snapshot")
        # SQL order is immaterial; JSON preserves integer versus boolean/float types.
        normalized = {k: sorted(v, key=canonical) for k, v in snapshot.items()}
        matching = []
        for state in self.possible:
            expected = {k: sorted(v, key=canonical) for k, v in state.snapshot().items()}
            if canonical(normalized) == canonical(expected):
                matching.append(state)
        if not matching:
            raise ContractFailure("on-disk tables differ from observed legal decisions")
        self.possible = matching


def request(key, account, amount):
    return {"key": key, "account": account, "amount": amount}


def schedule(prefix, extended=True):
    a, b, bank = prefix + "-a", prefix + "-b", prefix + "-bank"
    phases = [
        ("overlap", [request(a, "A", 60), request(b, "A", 60)], True),
        ("fresh_process_replays", [request(a, "A", 60), request(b, "A", 60)], False),
        ("amount_mismatch_first", [request(a, "A", 61)], False),
        ("amount_mismatch_second", [request(b, "A", 59)], False),
        ("account_mismatch_first", [request(a, "B", 60)], False),
        ("account_mismatch_second", [request(b, "B", 60)], False),
        ("independent_account", [request(bank, "B", 100)], False),
    ]
    if extended:
        duplicate = request(prefix + "-duplicate", "A", 10)
        drain = request(prefix + "-drain", "A", 30)
        reject = request(prefix + "-reject-zero", "A", 1)
        phases += [
            ("concurrent_same_identity", [duplicate, duplicate], True),
            ("exact_remaining_boundary", [drain], False),
            ("historical_replays_after_spend", [request(a, "A", 60), request(b, "A", 60),
                                               duplicate, drain, request(bank, "B", 100)], False),
            ("concurrent_durable_rejection", [reject, reject], True),
            ("rejected_retry", [reject], False),
        ]
    return phases

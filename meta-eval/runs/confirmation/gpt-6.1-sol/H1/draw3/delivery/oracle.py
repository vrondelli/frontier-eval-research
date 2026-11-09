"""Trusted finite E1 oracle. Never imports or executes submitted code."""
from dataclasses import dataclass, field
from itertools import permutations
from copy import deepcopy


@dataclass
class Model:
    accounts: dict = field(default_factory=lambda: {"A": 100, "B": 100})
    decisions: dict = field(default_factory=dict)
    ledger: dict = field(default_factory=dict)

    def apply(self, request):
        key, account, amount = (request[x] for x in ("key", "account", "amount"))
        if key in self.decisions:
            old = self.decisions[key]
            if (account, amount) != (old["account"], old["amount"]):
                return {"status": "payload_mismatch", "remaining": None}
            return {x: old[x] for x in ("status", "remaining")}
        status = "accepted" if self.accounts[account] >= amount else "rejected"
        if status == "accepted":
            self.accounts[account] -= amount
            self.ledger[key] = {"key": key, "account": account, "amount": amount}
        decision = dict(request, status=status, remaining=self.accounts[account])
        self.decisions[key] = decision
        return {x: decision[x] for x in ("status", "remaining")}

    def snapshot(self):
        return {
            "accounts": [{"account": k, "remaining": v}
                         for k, v in sorted(self.accounts.items())],
            "decisions": [self.decisions[k] for k in sorted(self.decisions)],
            "ledger": [self.ledger[k] for k in sorted(self.ledger)],
        }


def valid_reply(reply):
    if type(reply) is not dict or set(reply) != {"status", "remaining"}:
        return False
    if reply["status"] == "payload_mismatch":
        return reply["remaining"] is None
    return (reply["status"] in ("accepted", "rejected")
            and type(reply["remaining"]) is int and reply["remaining"] >= 0)


def advance(model, requests, replies):
    """Accept either serial ordering of a released pair, using exact replies."""
    if len(requests) != len(replies) or not all(valid_reply(x) for x in replies):
        raise ValueError("invalid decision reply shape or value")
    for order in permutations(range(len(requests))):
        proposed = deepcopy(model)
        expected = [None] * len(requests)
        for index in order:
            expected[index] = proposed.apply(requests[index])
        if expected == replies:
            return proposed
    raise ValueError("replies match no legal serial outcome")


def compare_snapshot(model, observed):
    expected = model.snapshot()
    if observed != expected:
        raise ValueError("public tables differ from the independent oracle")


def batches(prefix):
    """Public, bounded probes; three fresh databases use this same schedule."""
    left = {"key": prefix + "-left", "account": "A", "amount": 60}
    right = {"key": prefix + "-right", "account": "A", "amount": 60}
    other = {"key": prefix + "-other", "account": "B", "amount": 100}
    yield "overlap", [left, right]
    yield "fresh_process_replays", [left, right]
    for name, original in (("left", left), ("right", right)):
        yield name + "_amount_mismatch", [dict(original, amount=61)]
        yield name + "_account_mismatch", [dict(original, account="B")]
    yield "other_account", [other]
    # Disclosed extensions: expose recomputing historical remaining and failed
    # payload checks that silently replace a prior identity.
    yield "exact_exhaustion", [{"key": prefix + "-tail", "account": "A", "amount": 40}]
    yield "historical_replays", [left, right]
    yield "other_account_replay", [other]
    rejected = {"key": prefix + "-empty", "account": "A", "amount": 1}
    yield "empty_rejection", [rejected]
    yield "empty_rejection_replay", [rejected]

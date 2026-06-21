#!/usr/bin/env python3
"""§10 teeth for the authority dial (epic.owner-harness).

The dial decides what an agent may do WITHOUT asking bdo first. The whole point
is that it is DEFAULT-SAFE: only an observable, reversible, low-blast, in-a-
confirmed-arc act proceeds unattended; anything else asks first. The load-
bearing tooth is the refusal — an irreversible or high-blast act must route
ASK_FIRST. A dial that returned ACT_AND_FYI freely (the dangerous bug) fails
these. It composes the consequence-gate (observe.py): an act that cannot be
traced home is never eligible to run unattended."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from loop import authority


def decl(**over):
    """A clean, observable, reversible, low-blast, in-arc declaration — the one
    case that ACTS-AND-FYI. Each test mutates exactly one axis to prove that
    axis is load-bearing."""
    base = {
        "actor": "claude-session",
        "action": "append a proposed atom to my own worktree",
        "scope": "my own worktree atoms/",
        "expected_receipt": ".ai-native/log/receipts.jsonl",
        "attribution_path": "effect -> receipt -> claude-session",
        "rollback_path": "git revert the commit",
        "reversible": True,
        "arc_confirmed": True,
    }
    base.update(over)
    return base


class TestClassify(unittest.TestCase):
    def test_clean_act_acts_and_fyi(self):
        route, _ = authority.classify(decl())
        self.assertEqual(route, authority.ACT_AND_FYI)

    def test_irreversible_asks_first(self):
        # the load-bearing tooth: a bug that returned ACT_AND_FYI fails here
        route, reason = authority.classify(decl(reversible=False))
        self.assertEqual(route, authority.ASK_FIRST)
        self.assertIn("irreversible", reason)

    def test_no_undo_rollback_asks_first(self):
        # reversibility read off the rollback_path the consequence-gate requires
        d = decl(rollback_path="irreversible — the email cannot be unsent")
        d.pop("reversible")  # force the rollback_path reading
        route, _ = authority.classify(d)
        self.assertEqual(route, authority.ASK_FIRST)

    def test_high_blast_asks_first_even_if_reversible(self):
        # touching the trunk is high-blast no matter how reversible
        route, reason = authority.classify(decl(blast=["origin/main the trunk"]))
        self.assertEqual(route, authority.ASK_FIRST)
        self.assertIn("blast", reason)

    def test_acting_as_owner_asks_first(self):
        route, _ = authority.classify(decl(scope="reply in bdo's voice / persona"))
        self.assertEqual(route, authority.ASK_FIRST)

    def test_deletion_asks_first(self):
        route, _ = authority.classify(decl(blast=["delete the old records"]))
        self.assertEqual(route, authority.ASK_FIRST)

    def test_unobservable_asks_first(self):
        # composes observe.py: no attribution path -> halt -> ask first
        route, reason = authority.classify(decl(attribution_path=""))
        self.assertEqual(route, authority.ASK_FIRST)
        self.assertIn("not observable", reason)

    def test_off_arc_asks_first(self):
        route, reason = authority.classify(decl(arc_confirmed=False))
        self.assertEqual(route, authority.ASK_FIRST)
        self.assertIn("off-arc", reason)

    def test_arc_confirmed_param_overrides_declaration(self):
        # the Administrator resolves arc confirmation from the log; the param wins
        route, _ = authority.classify(decl(arc_confirmed=True), arc_confirmed=False)
        self.assertEqual(route, authority.ASK_FIRST)

    def test_empty_declaration_asks_first(self):
        self.assertEqual(authority.classify({})[0], authority.ASK_FIRST)
        self.assertEqual(authority.classify(None)[0], authority.ASK_FIRST)

    def test_the_knob_actually_moves_it(self):
        # turning require_reversible OFF lets an otherwise-clean irreversible act
        # through — proves the dial is tunable, not a constant (the owner's knob)
        loose = dict(authority.DEFAULT_TIERS, require_reversible=False)
        route, _ = authority.classify(decl(reversible=False), tiers=loose)
        self.assertEqual(route, authority.ACT_AND_FYI)


class TestReachHighBlast(unittest.TestCase):
    def test_undeclared_reach_is_high(self):
        # default-safe: an act that declares no reach cannot prove containment
        self.assertTrue(authority._reaches_high_blast({}, authority.DEFAULT_HIGH_BLAST))

    def test_own_scope_is_low(self):
        self.assertFalse(authority._reaches_high_blast(
            {"scope": "my own worktree atoms/"}, authority.DEFAULT_HIGH_BLAST))


class TestReadTiers(unittest.TestCase):
    def test_no_admission_is_default_safe(self):
        self.assertEqual(authority.read_tiers([]), authority.DEFAULT_TIERS)

    def test_latest_admitted_wins(self):
        adms = [
            {"type": "setpoint", "dial": authority.AUTHORITY_DIAL,
             "value": {"require_arc": True}},
            {"type": "setpoint", "dial": authority.AUTHORITY_DIAL,
             "value": {"require_arc": False}},
        ]
        self.assertFalse(authority.read_tiers(adms)["require_arc"])

    def test_partial_admission_falls_back_per_key(self):
        adms = [{"type": "setpoint", "dial": authority.AUTHORITY_DIAL,
                 "value": {"require_arc": False}}]
        got = authority.read_tiers(adms)
        self.assertFalse(got["require_arc"])
        self.assertEqual(got["high_blast"], authority.DEFAULT_TIERS["high_blast"])
        self.assertTrue(got["require_reversible"])  # untouched guard holds

    def test_other_dials_ignored(self):
        adms = [{"type": "setpoint", "dial": "orchestration.temperature",
                 "value": {"require_arc": False}}]
        self.assertEqual(authority.read_tiers(adms), authority.DEFAULT_TIERS)


if __name__ == "__main__":
    unittest.main()

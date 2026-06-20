#!/usr/bin/env python3
"""§10 teeth for the inferred-retry composer (done-line 0135).

The reminder must be *derived* from state, not asserted: a constant composer
(always a reminder, or always silent) must fail. These pin each silence
condition (active / budget-spent / escalated / gateway-closed), the
session-first content, the named tool-scope, and the decay — driving the live
folds + the gateway via monkeypatch so the logic is exercised without a full
log fixture. The gateway default-deny is proven: with no scope granted the
probe is silent no matter how idle (requirement 2 has teeth), and the granted
scope (propose-only vs full) changes the reminder (the tier-2 lever shows)."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from loop import retry, patrol, inference
import loop.gaps as gaps_mod

GAP = {"kind": "mock-stage", "subject": "value-gate.mock",
       "why": "fixed verdict, no judgement", "move": "admit-real …"}
BIG = retry.IDLE_THRESHOLD_SECONDS + 1
DUMMY = Path(".")


class TestCompose(unittest.TestCase):
    def setUp(self):
        # default live state: gateway OPEN at propose-only, not escalated, a gap
        self._saved = (retry.gateway_scope, patrol.load_state, gaps_mod.top_gap)
        retry.gateway_scope = lambda root: inference.PROPOSE_ONLY
        patrol.load_state = lambda root: {}
        gaps_mod.top_gap = lambda root: GAP

    def tearDown(self):
        retry.gateway_scope, patrol.load_state, gaps_mod.top_gap = self._saved

    def test_silent_while_active(self):
        self.assertIsNone(retry.compose(DUMMY, idle_seconds=60, fire_count=0))

    def test_silent_when_budget_spent(self):
        self.assertIsNone(retry.compose(DUMMY, BIG, fire_count=retry.MAX_NUDGES))

    def test_silent_when_escalated(self):
        patrol.load_state = lambda root: {"escalate_armed": True}
        self.assertIsNone(retry.compose(DUMMY, BIG, fire_count=0))

    def test_silent_when_gateway_closed(self):
        # requirement-2 teeth: default-deny — no scope, no probe, however idle
        retry.gateway_scope = lambda root: None
        self.assertIsNone(retry.compose(DUMMY, BIG, fire_count=0))

    def test_reminder_is_session_first(self):
        r = retry.compose(DUMMY, BIG, fire_count=0)
        self.assertIsNotNone(r)
        self.assertIn("continue-probe", r)
        self.assertIn("this session's context", r)  # session-first headline
        self.assertIn("SUGGESTION", r)              # soft, never an order
        self.assertIn(GAP["subject"], r)            # backlog only as fallback

    def test_reminder_names_the_tool_scope(self):
        # the tier-2 lever shows: propose-only and full read differently, and
        # a propose-only reminder must forbid execution explicitly.
        propose = retry.compose(DUMMY, BIG, fire_count=0)
        self.assertIn("PROPOSE-ONLY", propose)
        self.assertIn("do not execute", propose)
        retry.gateway_scope = lambda root: inference.FULL
        full = retry.compose(DUMMY, BIG, fire_count=0)
        self.assertIn("FULL", full)
        self.assertNotEqual(propose, full)

    def test_clean_field_fallback(self):
        gaps_mod.top_gap = lambda root: None
        r = retry.compose(DUMMY, BIG, fire_count=0)
        self.assertIsNotNone(r)
        self.assertIn("clean", r)

    def test_decay_changes_with_fire_count(self):
        first = retry.compose(DUMMY, BIG, fire_count=0)
        firm = retry.compose(DUMMY, BIG, fire_count=2)
        last = retry.compose(DUMMY, BIG, fire_count=retry.MAX_NUDGES - 1)
        self.assertIn("nudge 1", first)
        self.assertNotEqual(first, firm)
        self.assertIn("Last nudge", last)

    def test_decision_is_derived_not_constant(self):
        # §10 teeth: active must be silent AND idle+open+work must speak.
        self.assertIsNone(retry.compose(DUMMY, 60, 0))
        self.assertIsNotNone(retry.compose(DUMMY, BIG, 0))


if __name__ == "__main__":
    unittest.main()

"""Tests for the reversibility gate against done-line 0088: the safety spine
that reconciles "handle it so I don't have to worry" with the gesture-confirm
doctrine by cutting on reversibility.

The teeth: (1) a reversible act is allowed with no gesture; (2) an irreversible/
outward act is blocked without a gesture, with a legible reason; (3) the same
irreversible act is allowed when a gesture authorizes it; (4) an unknown verb is
treated as irreversible — blocked without a gesture, never silently allowed."""

import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from causality.reversibility_gate import classify, gate


class ReversibilityGateTest(unittest.TestCase):

    # --- classify ---------------------------------------------------------

    def test_classify_known_verbs(self):
        self.assertEqual(classify("pre-stage"), "reversible")
        self.assertEqual(classify("render"), "reversible")
        self.assertEqual(classify("delete"), "irreversible")
        self.assertEqual(classify("send"), "irreversible")
        self.assertEqual(classify("frobnicate"), "unknown")

    # --- the teeth --------------------------------------------------------

    def test_reversible_act_is_autonomous(self):
        d = gate({"verb": "pre-stage", "target": "bound/games"})
        self.assertTrue(d.allowed)
        self.assertFalse(d.needs_gesture)
        self.assertEqual(d.reversibility, "reversible")

    def test_irreversible_act_blocked_without_gesture(self):
        d = gate({"verb": "send", "target": "bound/company"})
        self.assertFalse(d.allowed)
        self.assertTrue(d.needs_gesture)
        self.assertIn("gesture", d.reason)
        self.assertIn("send", d.reason)

    def test_irreversible_act_allowed_with_gesture(self):
        d = gate({"verb": "send"}, gesture="bdo")
        self.assertTrue(d.allowed)
        self.assertTrue(d.needs_gesture)
        self.assertIn("bdo", d.reason)

    def test_unknown_verb_treated_as_irreversible(self):
        """The gate never guesses an act safe: an unrecognised verb is blocked
        without a gesture, and the reason says why."""
        d = gate({"verb": "frobnicate"})
        self.assertFalse(d.allowed)
        self.assertTrue(d.needs_gesture)
        self.assertEqual(d.reversibility, "unknown")
        self.assertIn("never guesses", d.reason)

    def test_unknown_verb_allowed_with_gesture(self):
        d = gate({"verb": "frobnicate"}, gesture="bdo")
        self.assertTrue(d.allowed)
        self.assertIn("bdo", d.reason)

    def test_empty_gesture_does_not_authorize(self):
        for falsy in (None, "", 0):
            d = gate({"verb": "delete"}, gesture=falsy)
            self.assertFalse(d.allowed)


if __name__ == "__main__":
    unittest.main()

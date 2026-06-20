#!/usr/bin/env python3
"""§10 teeth for the patrol escalate-marker (done-line 0127, slimmed at 0135).

The forcing continue-beat `decide` fold was retired (done-line 0135); what
survives is the escalate marker the soft idle reminder composes. These pin the
marker round-trip (arm → load reads it; disarm → cleared), the torn-file
tolerance (absence is a clean start, not a crash), and — the teeth — that the
marker is *derived* state the reminder reads, both armed and unarmed reachable.
The retired block's hook and decision-fold tests are gone with the primitive."""

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from loop import patrol


class TestEscalateMarker(unittest.TestCase):
    def test_arm_escalate_round_trip(self):
        with tempfile.TemporaryDirectory() as d:
            patrol.arm_escalate(d, "blocked on bdo")
            st = patrol.load_state(d)
            self.assertTrue(st["escalate_armed"])
            self.assertEqual(st["escalate_reason"], "blocked on bdo")

    def test_disarm_clears_the_marker(self):
        with tempfile.TemporaryDirectory() as d:
            patrol.arm_escalate(d, "need bdo")
            patrol.disarm_escalate(d)
            st = patrol.load_state(d)
            self.assertFalse(st.get("escalate_armed"))
            self.assertNotIn("escalate_reason", st)

    def test_load_state_tolerates_torn_file(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / patrol.STATE_NAME).write_text("{not json", encoding="utf-8")
            self.assertEqual(patrol.load_state(d), {})  # absence, not a crash

    def test_missing_state_is_no_escalation(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertFalse(patrol.load_state(d).get("escalate_armed"))

    def test_marker_is_derived_not_constant(self):
        # the §10 teeth: the reminder reads this marker; both states reachable
        # from the same store, so a constant ("always armed"/"never") fails.
        with tempfile.TemporaryDirectory() as d:
            unarmed = bool(patrol.load_state(d).get("escalate_armed"))
            patrol.arm_escalate(d, "x")
            armed = bool(patrol.load_state(d).get("escalate_armed"))
            self.assertEqual((unarmed, armed), (False, True))


if __name__ == "__main__":
    unittest.main()

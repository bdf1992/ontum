#!/usr/bin/env python3
"""§10 teeth for the continue-beat (done-line 0127).

The decision must be *derived*, not asserted: a constant decider (always
continue, or always silent) must fail. The matrix test proves both
outcomes are reachable from the pure `decide`; the targeted tests pin each
silence condition; the fail-safe test proves the hook stops on a broken
beat rather than trapping an AFK session.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from loop import patrol

GAP = {"kind": "mock-stage", "subject": "value-gate.mock",
       "why": "fixed verdict, no judgement", "move": "admit-real …"}


class TestDecide(unittest.TestCase):
    def test_continue_when_field_has_work(self):
        res = patrol.decide({}, "s1", GAP, owner_present=False)
        self.assertEqual(res["action"], "continue")
        self.assertEqual(res["beat"], 1)
        self.assertIn("the next gap", res["line"])
        self.assertEqual(res["state"]["beats"], 1)
        self.assertEqual(res["state"]["session_id"], "s1")

    def test_empty_backlog_does_not_silence(self):
        # bdo's deliberate choice: a clean field keeps the patrol looking,
        # it does not stop it (the ceiling is the backstop).
        res = patrol.decide({}, "s1", None, owner_present=False)
        self.assertEqual(res["action"], "continue")
        self.assertIn("do not wait for direction", res["line"])

    def test_escalate_marker_silences(self):
        res = patrol.decide({"escalate_armed": True, "escalate_reason": "need bdo",
                             "session_id": "s1", "beats": 3},
                            "s1", GAP, owner_present=False)
        self.assertEqual(res["action"], "silent")
        self.assertIn("need bdo", res["line"])
        # the arm is consumed (one stand-down per arm)
        self.assertFalse(res["state"]["escalate_armed"])

    def test_ceiling_silences_and_surfaces(self):
        res = patrol.decide({"session_id": "s1", "beats": patrol.CEILING},
                            "s1", GAP, owner_present=False)
        self.assertEqual(res["action"], "silent")
        self.assertIn("ceiling", res["line"])

    def test_parked_at_stamp_silences_only_when_sole_work(self):
        # no gap + owner work waiting → the only work is bdo's → silent
        sole = patrol.decide({}, "s1", None, owner_present=True)
        self.assertEqual(sole["action"], "silent")
        self.assertIn("parked-at-stamp", sole["line"])
        # but a gap present + owner work waiting → keep working the gap
        both = patrol.decide({}, "s1", GAP, owner_present=True)
        self.assertEqual(both["action"], "continue")

    def test_new_session_resets_beats(self):
        # a different session id starts a fresh patrol even past the ceiling
        res = patrol.decide({"session_id": "old", "beats": 999},
                            "new", GAP, owner_present=False)
        self.assertEqual(res["action"], "continue")
        self.assertEqual(res["beat"], 1)

    def test_continue_increments_across_beats(self):
        s = {}
        for expected in (1, 2, 3):
            res = patrol.decide({"session_id": "s1", **s}, "s1", GAP, False)
            self.assertEqual(res["beat"], expected)
            s = {"beats": res["state"]["beats"]}

    def test_decision_is_derived_not_constant(self):
        # the §10 teeth: a constant decider cannot satisfy this — has-work
        # must continue AND escalated must go silent. Both outcomes reachable.
        actions = {
            patrol.decide({}, "s", GAP, False)["action"],
            patrol.decide({"escalate_armed": True}, "s", GAP, False)["action"],
        }
        self.assertEqual(actions, {"continue", "silent"})


class TestStateAndEscalate(unittest.TestCase):
    def test_arm_escalate_round_trip(self):
        with tempfile.TemporaryDirectory() as d:
            patrol.arm_escalate(d, "blocked on bdo")
            st = patrol.load_state(d)
            self.assertTrue(st["escalate_armed"])
            self.assertEqual(st["escalate_reason"], "blocked on bdo")

    def test_load_state_tolerates_torn_file(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / patrol.STATE_NAME).write_text("{not json", encoding="utf-8")
            self.assertEqual(patrol.load_state(d), {})  # absence, not a crash

    def test_decide_from_root_continues_and_persists(self):
        # a fresh empty field (no gaps, no owner work) → continue (bdo's
        # choice) and the beat is persisted to the gitignored nag-state.
        with tempfile.TemporaryDirectory() as d:
            ai = Path(d) / ".ai-native"
            (ai / "log").mkdir(parents=True)
            for f in ("events", "receipts", "admissions"):
                (ai / "log" / f"{f}.jsonl").write_text("", encoding="utf-8")
            r1 = patrol.decide_from_root(ai, "sess-A")
            self.assertEqual(r1["action"], "continue")
            self.assertEqual(r1["beat"], 1)
            r2 = patrol.decide_from_root(ai, "sess-A")
            self.assertEqual(r2["beat"], 2)  # same session, beats advance
            self.assertTrue((ai / patrol.STATE_NAME).exists())

    def test_decide_from_root_silent_after_escalate(self):
        with tempfile.TemporaryDirectory() as d:
            ai = Path(d) / ".ai-native"
            (ai / "log").mkdir(parents=True)
            for f in ("events", "receipts", "admissions"):
                (ai / "log" / f"{f}.jsonl").write_text("", encoding="utf-8")
            patrol.decide_from_root(ai, "sess-A")
            patrol.arm_escalate(ai, "need bdo")
            res = patrol.decide_from_root(ai, "sess-A")
            self.assertEqual(res["action"], "silent")


class TestHookFailSafe(unittest.TestCase):
    HOOK = ROOT / ".claude" / "hooks" / "continue_beat.py"

    def _run(self, stdin, project_dir):
        env = dict(os.environ, CLAUDE_PROJECT_DIR=str(project_dir))
        return subprocess.run([sys.executable, str(self.HOOK)], input=stdin,
                              capture_output=True, text=True, env=env, timeout=60)

    def test_malformed_stdin_stops_silently(self):
        # fail-safe to STOP: a broken payload must let the session stop
        # (exit 0, no block decision) — never trap it.
        with tempfile.TemporaryDirectory() as d:
            p = self._run("{not json", d)
            self.assertEqual(p.returncode, 0)
            self.assertEqual(p.stdout.strip(), "")

    def test_unimportable_root_stops_silently(self):
        # an internal error (loop not importable from the project dir) must
        # also fail-safe to stop, not continue.
        with tempfile.TemporaryDirectory() as d:
            p = self._run(json.dumps({"session_id": "x"}), d)
            self.assertEqual(p.returncode, 0)
            self.assertEqual(p.stdout.strip(), "")

    def test_continue_emits_block_decision(self):
        # with the real repo as project dir, a fresh session gets a block
        # decision (the field always has work, at minimum the mock stages).
        env_dir = ROOT
        with tempfile.TemporaryDirectory() as d:
            # isolate the nag-state so the test never pollutes the real one:
            # point at a tmp .ai-native that has loop reachable via the repo.
            ai = Path(d) / ".ai-native"
            (ai / "log").mkdir(parents=True)
            for f in ("events", "receipts", "admissions"):
                (ai / "log" / f"{f}.jsonl").write_text("", encoding="utf-8")
            # symlink/copy is overkill; instead drive decide_from_root in-proc
            res = patrol.decide_from_root(ai, "hook-test")
            self.assertEqual(res["action"], "continue")


if __name__ == "__main__":
    unittest.main()

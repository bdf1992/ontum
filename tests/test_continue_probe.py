#!/usr/bin/env python3
"""§10 teeth for the continue-probe pen's budgeting (done-line 0135).

The firing edge must never hammer an away session: `due_targets` is the budget,
and it must be *derived* from the ledger + the cooldown + the streak, not a
constant. These pin the cooldown (a just-fired session is not re-fired), the
per-streak cap (an unmoved session is nudged at most MAX_FIRES, then left
alone), and the streak reset (a session that *acted* after a fire earns a fresh
budget). The pen is imported by path (it lives under .claude/skills, not loop/)."""

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

_spec = importlib.util.spec_from_file_location(
    "continue_probe",
    ROOT / ".claude" / "skills" / "continue-probe" / "probe.py")
probe = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(probe)

NOW = 1_000_000.0
COOL = probe.MIN_REFIRE_SECONDS


def target(sid="s1", cwd="/repo/a", idle=1200):
    return {"session_id": sid, "cwd": cwd, "idle_seconds": idle,
            "fire": ["claude", "--resume", sid, "-p", "x"], "fire_cwd": cwd}


# an mtime that never advances past any fire (the session never moved)
FROZEN = lambda sid: NOW - 10 * COOL


class TestDueTargets(unittest.TestCase):
    def test_first_time_fires(self):
        due, ledger = probe.due_targets([target()], {}, NOW, mtime=FROZEN)
        self.assertEqual([t["session_id"] for t in due], ["s1"])
        self.assertEqual(ledger["s1"]["fires"], 1)
        self.assertEqual(ledger["s1"]["last_fire"], NOW)

    def test_cooldown_blocks_immediate_refire(self):
        ledger = {"s1": {"last_fire": NOW - 60, "fires": 1}}  # fired 1m ago
        due, _ = probe.due_targets([target()], ledger, NOW, mtime=FROZEN)
        self.assertEqual(due, [])

    def test_refire_after_cooldown_when_unmoved(self):
        ledger = {"s1": {"last_fire": NOW - COOL - 1, "fires": 1}}
        due, new = probe.due_targets([target()], ledger, NOW, mtime=FROZEN)
        self.assertEqual(len(due), 1)
        self.assertEqual(new["s1"]["fires"], 2)  # streak advances

    def test_fire_cap_stands_down(self):
        # at the cap, an unmoved session is left alone even after cooldown
        ledger = {"s1": {"last_fire": NOW - COOL - 1, "fires": probe.MAX_FIRES}}
        due, _ = probe.due_targets([target()], ledger, NOW, mtime=FROZEN)
        self.assertEqual(due, [])

    def test_streak_resets_when_session_acted(self):
        # capped, but the transcript advanced AFTER the last fire → it acted →
        # fresh streak → it fires again (a new idle period earns a new budget).
        last = NOW - COOL - 100
        ledger = {"s1": {"last_fire": last, "fires": probe.MAX_FIRES}}
        moved = lambda sid: last + 10  # mtime later than last_fire
        due, new = probe.due_targets([target()], ledger, NOW, mtime=moved)
        self.assertEqual(len(due), 1)
        self.assertEqual(new["s1"]["fires"], 1)  # reset, then this fire

    def test_input_ledger_not_mutated(self):
        ledger = {}
        probe.due_targets([target()], ledger, NOW, mtime=FROZEN)
        self.assertEqual(ledger, {})

    def test_derived_not_constant(self):
        # cooling-down → none; cooled+under-cap → one. Both reachable.
        cooling = {"s1": {"last_fire": NOW - 1, "fires": 1}}
        cooled = {"s1": {"last_fire": NOW - COOL - 1, "fires": 1}}
        self.assertEqual(probe.due_targets([target()], cooling, NOW, mtime=FROZEN)[0], [])
        self.assertTrue(probe.due_targets([target()], cooled, NOW, mtime=FROZEN)[0])


if __name__ == "__main__":
    unittest.main()

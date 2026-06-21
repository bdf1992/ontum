#!/usr/bin/env python3
"""§10 teeth for the continue-probe pen (done-lines 0135, 0171).

0135: the firing edge must never hammer an away session — `due_targets` is the
budget, derived from the ledger + cooldown + streak, not a constant.

0171: it must also never *burst*. Opening the probe gateway made a whole backlog
of idle sessions eligible at once, and firing them all in one tick is the
llama-server-kill shape on the probe-fire plane. So the per-tick fire budget is
EASED — it flows freely below a pool-depth threshold and, above it, eases
between a floor and ceiling against recent egress — and SELECTION is split from
ACCOUNTING so a session the budget defers is not falsely marked fired (the
slice-after-advance starvation bug). The load-bearing tooth: `eased_budget` caps
a deep backlog (a no-op that returned the backlog itself fails these). The pen
is imported by path (it lives under .claude/skills, not loop/)."""

import importlib.util
import sys
import tempfile
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

# the eased setpoint the teeth drive (injected, never the live log)
EASING = {"threshold": 3, "min_per_tick": 1, "max_per_tick": 3,
          "egress_window_seconds": 900, "open_window_seconds": 43200}


def target(sid="s1", cwd="/repo/a", idle=1200):
    return {"session_id": sid, "cwd": cwd, "idle_seconds": idle,
            "fire": ["claude", "--resume", sid, "-p", "x"], "fire_cwd": cwd}


# an mtime that never advances past any fire (the session never moved)
FROZEN = lambda sid: NOW - 10 * COOL


class TestSelection(unittest.TestCase):
    """due_targets — pure SELECTION (no ledger mutation), 0135 logic intact."""

    def test_first_time_is_eligible(self):
        due = probe.due_targets([target()], {}, NOW, mtime=FROZEN)
        self.assertEqual([t["session_id"] for t in due], ["s1"])
        self.assertEqual(due[0]["fires_if_fired"], 1)  # the count to record IF fired

    def test_does_not_advance_the_ledger(self):
        # the split: selection annotates, it never writes the ledger (0171)
        ledger = {}
        probe.due_targets([target()], ledger, NOW, mtime=FROZEN)
        self.assertEqual(ledger, {})

    def test_cooldown_blocks_immediate_refire(self):
        ledger = {"s1": {"last_fire": NOW - 60, "fires": 1}}  # fired 1m ago
        self.assertEqual(probe.due_targets([target()], ledger, NOW, mtime=FROZEN), [])

    def test_refire_after_cooldown_when_unmoved(self):
        ledger = {"s1": {"last_fire": NOW - COOL - 1, "fires": 1}}
        due = probe.due_targets([target()], ledger, NOW, mtime=FROZEN)
        self.assertEqual(len(due), 1)
        self.assertEqual(due[0]["fires_if_fired"], 2)  # streak advances on fire

    def test_fire_cap_stands_down(self):
        ledger = {"s1": {"last_fire": NOW - COOL - 1, "fires": probe.MAX_FIRES}}
        self.assertEqual(probe.due_targets([target()], ledger, NOW, mtime=FROZEN), [])

    def test_streak_resets_when_session_acted(self):
        last = NOW - COOL - 100
        ledger = {"s1": {"last_fire": last, "fires": probe.MAX_FIRES}}
        moved = lambda sid: last + 10  # mtime later than last_fire → it acted
        due = probe.due_targets([target()], ledger, NOW, mtime=moved)
        self.assertEqual(len(due), 1)
        self.assertEqual(due[0]["fires_if_fired"], 1)  # reset, then this fire


class TestAccounting(unittest.TestCase):
    """advance_ledger — only fired sessions advance; deferred ones never start
    their cooldown (the starvation bug the split closes)."""

    def test_only_fired_advance(self):
        eligible = [dict(target("s1"), fires_if_fired=1),
                    dict(target("s2"), fires_if_fired=1)]
        fired = eligible[:1]  # s1 fired, s2 deferred by the budget
        new = probe.advance_ledger({}, fired, NOW)
        self.assertEqual(new["s1"], {"last_fire": NOW, "fires": 1, "cwd": "/repo/a"})
        self.assertNotIn("s2", new)  # deferred: no cooldown started → first next tick

    def test_records_the_streak_count(self):
        fired = [dict(target("s1"), fires_if_fired=3)]
        new = probe.advance_ledger({}, fired, NOW)
        self.assertEqual(new["s1"]["fires"], 3)

    def test_input_not_mutated(self):
        ledger = {"s2": {"last_fire": 1.0, "fires": 1}}
        probe.advance_ledger(ledger, [dict(target("s1"), fires_if_fired=1)], NOW)
        self.assertEqual(ledger, {"s2": {"last_fire": 1.0, "fires": 1}})

    def test_deferred_session_entry_untouched(self):
        ledger = {"s2": {"last_fire": 5.0, "fires": 2, "cwd": "/repo/a"}}
        new = probe.advance_ledger(ledger, [dict(target("s1"), fires_if_fired=1)], NOW)
        self.assertEqual(new["s2"], {"last_fire": 5.0, "fires": 2, "cwd": "/repo/a"})


class TestEasedBudget(unittest.TestCase):
    """eased_budget — the load-bearing tooth: a deep backlog is CAPPED. A no-op
    that returned `due_depth` (the pre-0171 unbounded fire) fails every cap
    assertion here."""

    def test_caps_a_deep_backlog_nonvacuous(self):
        # 21 due — the real number that opening the gateway produced. The budget
        # must be the ceiling, NOT 21. (Identity easing → 21 → this fails.)
        self.assertEqual(probe.eased_budget(21, 0, EASING), EASING["max_per_tick"])
        self.assertLess(probe.eased_budget(21, 0, EASING), 21)

    def test_below_threshold_flows_freely(self):
        # under threshold: low pressure, fire them all (ceiling still holds)
        self.assertEqual(probe.eased_budget(2, 0, EASING), 2)
        self.assertEqual(probe.eased_budget(3, 0, EASING), 3)

    def test_eases_down_as_egress_drains(self):
        # above threshold, the budget opens to max minus what is still draining
        self.assertEqual(probe.eased_budget(10, 0, EASING), 3)  # nothing draining
        self.assertEqual(probe.eased_budget(10, 2, EASING), 1)  # 2 in flight → ease
        self.assertEqual(probe.eased_budget(10, 1, EASING), 2)

    def test_floor_holds_so_progress_never_stalls(self):
        # egress past the ceiling never starves the drain — the floor is the min
        self.assertEqual(probe.eased_budget(10, 99, EASING), EASING["min_per_tick"])

    def test_never_exceeds_the_backlog(self):
        self.assertEqual(probe.eased_budget(1, 0, EASING), 1)
        self.assertEqual(probe.eased_budget(0, 0, EASING), 0)

    def test_misconfigured_min_above_max_never_bursts(self):
        bad = dict(EASING, min_per_tick=5, max_per_tick=2)
        self.assertLessEqual(probe.eased_budget(21, 0, bad), 5)  # clamped to max(min)


class TestRecentEgress(unittest.TestCase):
    """recent_egress — counts only launched fires inside the window; torn lines
    and a missing trace are tolerated (the fold's mortality property)."""

    def test_counts_recent_launched_only(self):
        with tempfile.TemporaryDirectory() as d:
            trace = Path(d) / "fires.jsonl"
            trace.write_text(
                '{"ts": %f, "launched": true}\n' % (NOW - 10) +      # recent ✓
                '{"ts": %f, "launched": true}\n' % (NOW - 100) +     # recent ✓
                '{"ts": %f, "launched": true}\n' % (NOW - 5000) +    # too old ✗
                '{"ts": %f, "launched": false}\n' % (NOW - 10) +     # not launched ✗
                '{"ts": %f, "launched": tr\n' % (NOW - 10),          # torn ✗
                encoding="utf-8")
            self.assertEqual(probe.recent_egress(NOW, 900, trace=trace), 2)

    def test_missing_trace_is_zero(self):
        self.assertEqual(probe.recent_egress(NOW, 900, trace=Path("/no/such")), 0)


class TestRunCapsTheFleet(unittest.TestCase):
    """run() end-to-end: a 21-deep eligible backlog fires at most the budget,
    freshest-idle first — never a 21-session burst (the 0171 bar)."""

    def setUp(self):
        self._idle = probe.watcher.idle_sessions
        self._ledger = probe.load_ledger
        # 21 eligible sessions, varying idle so freshest-first is observable
        self._targets = [target(sid=f"s{i:02d}", idle=1000 + i * 60)
                         for i in range(21)]
        probe.watcher.idle_sessions = lambda now, open_window=None, mtime=None: self._targets
        probe.load_ledger = lambda: {}

    def tearDown(self):
        probe.watcher.idle_sessions = self._idle
        probe.load_ledger = self._ledger

    def test_dry_run_caps_to_budget(self):
        selected, fired, dry, budget = probe.run(
            NOW, fire=False, mtime=FROZEN, easing=EASING)
        self.assertEqual(len(selected), 21)        # all eligible…
        self.assertEqual(budget, EASING["max_per_tick"])  # …but the budget caps
        self.assertLess(budget, 21)                # the burst is refused
        self.assertTrue(dry)

    def test_fires_freshest_first(self):
        # the slice the budget admits is the lowest-idle (freshest) sessions
        selected, _, _, budget = probe.run(NOW, fire=False, mtime=FROZEN, easing=EASING)
        ordered = sorted(selected, key=lambda t: (t["idle_seconds"], t["session_id"]))
        admitted = [t["session_id"] for t in ordered[:budget]]
        self.assertEqual(admitted, ["s00", "s01", "s02"])  # the 3 freshest


if __name__ == "__main__":
    unittest.main()

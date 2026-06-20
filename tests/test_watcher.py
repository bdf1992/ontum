#!/usr/bin/env python3
"""§10 teeth for the session watcher (done-line 0135).

The fold must be *derived* from the signals, not asserted: a constant watcher
(always probe, or never) must fail. Driving `idle_sessions` with injected
`now`, a registry, a `gateway` lambda, and an `mtime` lambda, these pin every
edge — active is excluded, idle-within-window is included, the gateway
default-deny excludes (requirement-2 teeth), a presumed-closed session is
excluded, a missing cwd / missing transcript is skipped — and prove the emitted
fire command is the exact `claude --resume <id> -p <probe>` argv in the right
cwd. The load_registry tolerance (torn/missing file → empty watch) is pinned
too: absence is a clean watch, not a crash."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from loop import watcher

NOW = 1_000_000.0
T = watcher.IDLE_THRESHOLD_SECONDS
WINDOW = watcher.OPEN_WINDOW_SECONDS
REG = {"sess-A": {"cwd": "/repo/a", "ts": 1}, "sess-B": {"cwd": "/repo/b", "ts": 2}}

OPEN = lambda root: True   # gateway permits everywhere
SHUT = lambda root: False  # gateway default-deny everywhere


def at_idle(mins_idle):
    """An mtime lambda placing every session `mins_idle` minutes in the past."""
    return lambda sid: NOW - mins_idle * 60


class TestIdleSessions(unittest.TestCase):
    def _run(self, registry=REG, gateway=OPEN, mtime=None, idle_min=20):
        return watcher.idle_sessions(
            NOW, registry=registry, gateway=gateway,
            mtime=mtime or at_idle(idle_min))

    def test_active_session_is_not_probed(self):
        # silent 1 min < threshold → active → excluded
        self.assertEqual(self._run(mtime=at_idle(1)), [])

    def test_idle_session_within_window_is_probed(self):
        out = self._run(idle_min=20)
        self.assertEqual({t["session_id"] for t in out}, {"sess-A", "sess-B"})

    def test_gateway_closed_excludes_however_idle(self):
        # requirement-2 teeth: default-deny — no policy, no probe, even at 20m
        self.assertEqual(self._run(gateway=SHUT, idle_min=20), [])

    def test_presumed_closed_session_is_not_resurrected(self):
        # idle past the open window → presumed closed, not idle → excluded
        stale = lambda sid: NOW - (WINDOW + 3600)
        self.assertEqual(self._run(mtime=stale), [])

    def test_missing_cwd_is_skipped(self):
        out = self._run(registry={"sess-X": {"ts": 1}})  # no cwd
        self.assertEqual(out, [])

    def test_missing_transcript_is_skipped(self):
        out = self._run(mtime=lambda sid: None)  # no transcript file
        self.assertEqual(out, [])

    def test_fire_command_is_the_exact_resume_argv(self):
        out = self._run(registry={"sess-A": {"cwd": "/repo/a", "ts": 1}})
        self.assertEqual(len(out), 1)
        t = out[0]
        self.assertEqual(t["fire"][:4], ["claude", "--resume", "sess-A", "-p"])
        self.assertEqual(t["fire"][4], watcher.PROBE)
        self.assertEqual(t["fire_cwd"], "/repo/a")
        self.assertGreaterEqual(t["idle_seconds"], T)

    def test_decision_is_derived_not_constant(self):
        # the §10 teeth: same registry, only the signals change, both reachable
        active = self._run(mtime=at_idle(1))
        idle = self._run(mtime=at_idle(20))
        self.assertEqual(active, [])
        self.assertTrue(idle)


class TestRegisterSession(unittest.TestCase):
    """The registration hook's pure half (done-line 0135): add-and-prune. A new
    session is recorded; a dead one (no transcript, or past the open window) is
    pruned so the registry stays the plausibly-open set; the input is never
    mutated."""

    def test_adds_a_new_session(self):
        out = watcher.register_session({}, "sess-A", "/repo/a", NOW,
                                       mtime=at_idle(0))
        self.assertEqual(out, {"sess-A": {"cwd": "/repo/a", "ts": NOW}})

    def test_refreshes_an_existing_session(self):
        prior = {"sess-A": {"cwd": "/old", "ts": 1}}
        out = watcher.register_session(prior, "sess-A", "/repo/a", NOW,
                                       mtime=at_idle(0))
        self.assertEqual(out["sess-A"], {"cwd": "/repo/a", "ts": NOW})
        self.assertEqual(prior["sess-A"]["cwd"], "/old")  # input not mutated

    def test_prunes_a_dead_session(self):
        # an existing session whose transcript is past the open window is dropped
        prior = {"dead": {"cwd": "/repo/x", "ts": 1}}
        dead_mtime = lambda sid: NOW - (WINDOW + 3600)
        out = watcher.register_session(prior, "sess-A", "/repo/a", NOW,
                                       mtime=dead_mtime)
        self.assertNotIn("dead", out)
        self.assertIn("sess-A", out)

    def test_prunes_a_transcriptless_session(self):
        prior = {"ghost": {"cwd": "/repo/x", "ts": 1}}
        out = watcher.register_session(prior, "sess-A", "/repo/a", NOW,
                                       mtime=lambda sid: None)
        self.assertEqual(set(out), {"sess-A"})

    def test_keeps_a_live_sibling(self):
        prior = {"live": {"cwd": "/repo/x", "ts": 1}}
        out = watcher.register_session(prior, "sess-A", "/repo/a", NOW,
                                       mtime=at_idle(5))  # 5m idle, within window
        self.assertEqual(set(out), {"live", "sess-A"})


class TestRegistry(unittest.TestCase):
    def test_missing_registry_is_empty_watch(self):
        self.assertEqual(watcher.load_registry(Path("/no/such/registry.json")), {})

    def test_torn_registry_is_empty_watch(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "reg.json"
            p.write_text("{not json", encoding="utf-8")
            self.assertEqual(watcher.load_registry(p), {})  # absence, not a crash

    def test_round_trips_a_written_registry(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "reg.json"
            p.write_text(json.dumps(REG), encoding="utf-8")
            self.assertEqual(watcher.load_registry(p), REG)


if __name__ == "__main__":
    unittest.main()

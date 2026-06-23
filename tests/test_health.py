"""Tests for loop/health.py - the health board (bdo 2026-06-22, the watchdog).

The teeth: the up/down verdict must be REAL, not vacuous. A healthy process
(registered + enabled + fresh) reads up; each failure mode - task missing, task
disabled, freshness stale, freshness absent - reads DOWN. Proven non-vacuous: a
fabricated healthy process is NOT flagged, and each fabricated fault IS caught.
"""

import datetime
import os
import tempfile
import unittest
from pathlib import Path

from loop import health

NOW = datetime.datetime(2026, 6, 22, 12, 0, 0, tzinfo=datetime.timezone.utc)


def _registered(state="Ready", next_run="6/22/2026 12:30:00 PM"):
    return lambda task: {"registered": True, "state": state, "next_run": next_run}


def _missing():
    return lambda task: {"registered": False}


class CheckProcessTeeth(unittest.TestCase):
    def _fresh_file(self, age_min):
        f = tempfile.NamedTemporaryFile(delete=False, suffix=".log")
        f.close()
        when = NOW - datetime.timedelta(minutes=age_min)
        ts = when.timestamp()
        os.utime(f.name, (ts, ts))
        self.addCleanup(lambda: os.path.exists(f.name) and os.remove(f.name))
        return f.name

    def test_healthy_process_is_up(self):
        proc = {"name": "x", "os_task": "x", "freshness_file": self._fresh_file(10),
                "max_age_minutes": 75}
        r = health.check_process(proc, NOW, probe=_registered())
        self.assertEqual(r["verdict"], "up", r["reasons"])

    def test_unregistered_task_is_down(self):
        proc = {"name": "x", "os_task": "x", "freshness_file": self._fresh_file(10),
                "max_age_minutes": 75}
        r = health.check_process(proc, NOW, probe=_missing())
        self.assertEqual(r["verdict"], "down")
        self.assertTrue(any("NOT registered" in x for x in r["reasons"]))

    def test_disabled_task_is_down(self):
        proc = {"name": "x", "os_task": "x", "freshness_file": self._fresh_file(10),
                "max_age_minutes": 75}
        r = health.check_process(proc, NOW, probe=_registered(state="Disabled"))
        self.assertEqual(r["verdict"], "down")
        self.assertTrue(any("DISABLED" in x for x in r["reasons"]))

    def test_stale_freshness_is_down(self):
        proc = {"name": "x", "os_task": "x", "freshness_file": self._fresh_file(200),
                "max_age_minutes": 75}
        r = health.check_process(proc, NOW, probe=_registered())
        self.assertEqual(r["verdict"], "down")
        self.assertTrue(any("STALE" in x for x in r["reasons"]))

    def test_absent_freshness_is_down(self):
        proc = {"name": "x", "os_task": "x",
                "freshness_file": "C:/nonexistent/never-ran.log", "max_age_minutes": 75}
        r = health.check_process(proc, NOW, probe=_registered())
        self.assertEqual(r["verdict"], "down")
        self.assertTrue(any("never ran" in x for x in r["reasons"]))


if __name__ == "__main__":
    unittest.main()

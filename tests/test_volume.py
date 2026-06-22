"""Tests for loop/volume.py — the volume scoreboard (bdo 2026-06-21, "fill a
volume based on setpoint"; numbers are examples, items are suggestions — the
frame is generative, not a baked schema).

The §10 teeth:
  * a declared dimension whose measure has NO registered counter reads as
    `no-gauge` — never counted as filled (the vacuous-fill refusal; if this
    failed, an unmeasurable target would silently read as met);
  * the meter DISCRIMINATES under vs met from the real record (a target of 2
    with 1 event in the window is `under`, with 2 is `at`) — the fill is
    computed, not asserted;
  * a dimension is a signed setpoint — admit refuses a missing signer and a
    non-positive target."""

import datetime
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import reconcile, volume

NOW = datetime.datetime(2026, 6, 21, 12, 0, tzinfo=datetime.timezone.utc)


class VolumeMeter(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        (self.root / "log").mkdir()
        for f in ("events.jsonl", "receipts.jsonl", "admissions.jsonl"):
            (self.root / "log" / f).touch()

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def _event(self, **kw):
        kw.setdefault("id", "evt." + reconcile.short_hash(*map(str, kw.values())))
        reconcile.append_line(self.root / "log" / "events.jsonl", kw)

    def _dim(self, name, measure, target):
        volume.admit_dimension(self.root, name, measure, target, 24, "bdo")

    def test_no_gauge_is_never_filled(self):
        # a target whose measure has no counter must NOT read as met
        self._dim("docs_written", "docs_written", 5)  # no such measure registered
        row = next(r for r in volume.meter(self.root, now=NOW) if r["name"] == "docs_written")
        self.assertEqual(row["verdict"], "no-gauge")
        self.assertIsNone(row["actual"])
        self.assertNotIn(row["verdict"], ("at", "over"))

    def test_meter_discriminates_under_from_met(self):
        # two issues closed inside the window, one outside; target 2 → at
        self._event(type="issue.closed", ts="2026-06-21T11:00:00+00:00")
        self._event(type="issue.closed", ts="2026-06-21T10:00:00+00:00")
        self._event(type="issue.closed", ts="2026-06-19T10:00:00+00:00")  # >24h ago
        self._dim("closed", "issues_closed", 2)
        row = next(r for r in volume.meter(self.root, now=NOW) if r["name"] == "closed")
        self.assertEqual(row["actual"], 2)        # the stale one is out of window
        self.assertEqual(row["verdict"], "at")

        # raise the target to 3 → the same record is now under (the teeth)
        self._dim("closed", "issues_closed", 3)
        row = next(r for r in volume.meter(self.root, now=NOW) if r["name"] == "closed")
        self.assertEqual(row["verdict"], "under")
        self.assertEqual(row["fill"], round(2 / 3, 3))

    def test_rates_need_no_targets(self):
        self._event(type="issue.opened", ts="2026-06-21T11:30:00+00:00")
        data = volume.rates(self.root, now=NOW, hours=24)
        self.assertEqual(data["issues_opened"], 1)
        self.assertEqual(data["issues_closed"], 0)

    def test_admit_refuses_unsigned_and_nonpositive(self):
        with self.assertRaises(ValueError):
            volume.admit_dimension(self.root, "x", "issues_closed", 5, 24, "")
        with self.assertRaises(ValueError):
            volume.admit_dimension(self.root, "x", "issues_closed", 0, 24, "bdo")

    def test_latest_dim_supersedes(self):
        self._dim("closed", "issues_closed", 2)
        self._dim("closed", "issues_closed", 9)  # later target wins
        row = next(r for r in volume.meter(self.root, now=NOW) if r["name"] == "closed")
        self.assertEqual(row["target"], 9)


if __name__ == "__main__":
    unittest.main()

"""The ambient-run ledger — whether the loop's headless and ambient runs did
anything worth a damn.

The §10 bar: two records that each look like "a run happened" must NOT read
the same when one moved real work and the other moved nothing with nothing
held. A barren run (ran, moved nothing, nothing deferred or cooled) is the
contradiction the ledger must surface, not smooth into "ran fine"; a held
run (cooled / deferred — correct backpressure) is the loop legitimately
idle and must read differently. A span that is all barren reads as spinning.
The fold is pure; only `record` writes, and only by appending a run event.
"""

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import reconcile, runs


def _root(tmp):
    root = Path(tmp) / ".ai-native"
    (root / "log").mkdir(parents=True)
    return root


def _tick(root, ts, spent, mode="heat", deferred=None):
    """A fast-loop tick straight onto the log, in the shape orchestrate writes."""
    reconcile.append_line(root / "log" / "admissions.jsonl", {
        "id": "adm.tick." + reconcile.short_hash(ts, str(spent), mode),
        "type": "tick", "ts": ts, "tick": 1, "budget_spent": spent, "mode": mode,
        "deferred": deferred or [], "scheduled": [],
    })


class _Temp(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = _root(self.tmp)
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)


class TestClassification(_Temp):
    def test_moved_held_barren_do_not_read_alike(self):
        # three ticks that each "happened" — the surface must tell them apart
        _tick(self.root, "2026-06-10T01:00:00Z", spent=2)                       # moved
        _tick(self.root, "2026-06-10T02:00:00Z", spent=0, mode="cool")          # held (cooled)
        _tick(self.root, "2026-06-10T03:00:00Z", spent=0,
              deferred=[{"why": "queue at cap"}])                                # held (deferred)
        _tick(self.root, "2026-06-10T04:00:00Z", spent=0, mode="heat")          # barren
        d = runs.runs(self.root)
        standings = {r["ts"][11:13]: r["standing"] for r in d["runs"]}
        self.assertEqual(standings["01"], "moved")
        self.assertEqual(standings["02"], "held")
        self.assertEqual(standings["03"], "held")
        self.assertEqual(standings["04"], "barren",
                         "a heat tick that spent zero with nothing held is barren")
        self.assertEqual((d["moved"], d["held"], d["barren"]), (1, 2, 1))

    def test_recorded_run_with_no_movement_is_barren(self):
        runs.record(self.root, kind="overnight", by="claude", moved={})
        d = runs.runs(self.root)
        self.assertEqual(d["runs"][0]["standing"], "barren")

    def test_recorded_run_that_moved_is_not_barren(self):
        runs.record(self.root, kind="gate-judgment", by="claude",
                    moved={"refusals": 1, "receipts": 1})
        d = runs.runs(self.root)
        self.assertEqual(d["runs"][0]["standing"], "moved")
        self.assertEqual(d["barren"], 0)


class TestSpinning(_Temp):
    def test_all_barren_span_reads_as_spinning(self):
        _tick(self.root, "2026-06-10T01:00:00Z", spent=0, mode="heat")
        runs.record(self.root, kind="overnight", by="claude", moved={})
        d = runs.runs(self.root)
        self.assertTrue(d["spinning"], "a span with only barren runs must surface as spinning")
        self.assertIn("loop spun", runs.render(d))

    def test_one_moved_run_clears_spinning(self):
        _tick(self.root, "2026-06-10T01:00:00Z", spent=0, mode="heat")  # barren
        _tick(self.root, "2026-06-10T02:00:00Z", spent=1)               # moved
        d = runs.runs(self.root)
        self.assertFalse(d["spinning"])
        self.assertEqual(d["barren"], 1)

    def test_empty_span_is_not_spinning(self):
        d = runs.runs(self.root)
        self.assertEqual(d["total"], 0)
        self.assertFalse(d["spinning"])
        self.assertIn("not run here", runs.render(d))


class TestWriteSeam(_Temp):
    def test_record_appends_a_readable_run_event(self):
        evt = runs.record(self.root, kind="gate-judgment", by="claude",
                          arc="epic.test", moved={"advanced": 1}, note="did a thing")
        self.assertEqual(evt["type"], "run")
        d = runs.runs(self.root)
        self.assertEqual(d["total"], 1)
        self.assertEqual(d["runs"][0]["arc"], "epic.test")
        self.assertEqual(d["runs"][0]["note"], "did a thing")

    def test_fold_writes_nothing(self):
        runs.record(self.root, kind="overnight", by="claude", moved={"advanced": 1})
        before = {p.name: p.read_bytes() for p in (self.root / "log").iterdir()}
        runs.runs(self.root)
        runs.render(runs.runs(self.root))
        after = {p.name: p.read_bytes() for p in (self.root / "log").iterdir()}
        self.assertEqual(before, after, "the ledger fold mutated the log; it must only read")


class TestSpan(_Temp):
    def test_bounds_are_honoured(self):
        _tick(self.root, "2026-06-01T01:00:00Z", spent=1)
        _tick(self.root, "2026-06-10T01:00:00Z", spent=1)
        d = runs.runs(self.root, since="2026-06-05", until="2026-06-11")
        self.assertEqual(d["total"], 1)


if __name__ == "__main__":
    unittest.main()

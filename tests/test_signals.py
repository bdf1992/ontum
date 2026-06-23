"""Tests for the signal stream against done-line 0092: teeth leave a mark.

The harvest precondition — "the refusal is the signal" only holds if the signal
lands. The teeth: (1) mark→read round-trips; (2) the same firing recorded twice
folds to ONE signal (idempotence, I-2); (3) a torn final line is dropped and an
absent stream reads empty; (4) each of the three teeth lands a signal of its
kind when it fires, and lands nothing when it does not refuse."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import signals
from causality import cited_sensor, reversibility_gate


class SignalStreamTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / "log").mkdir()

    def tearDown(self):
        self._tmp.cleanup()

    def test_mark_read_round_trip(self):
        rec = signals.mark(self.root, "loop-stop:converged", "epic.x", "all landed")
        got = signals.read(self.root)
        self.assertEqual(len(got), 1)
        self.assertEqual(got[0]["kind"], "loop-stop:converged")
        self.assertEqual(got[0]["subject"], "epic.x")
        self.assertEqual(got[0]["state"], "seed")
        self.assertEqual(got[0]["id"], rec["id"])

    def test_same_firing_folds_to_one(self):
        signals.mark(self.root, "cited-ghost", "downloads/x.exe", "no resolve")
        signals.mark(self.root, "cited-ghost", "downloads/x.exe", "no resolve")
        self.assertEqual(len(signals.read(self.root)), 1)

    def test_distinct_firings_are_distinct(self):
        signals.mark(self.root, "cited-ghost", "a", "why")
        signals.mark(self.root, "cited-ghost", "b", "why")
        self.assertEqual(len(signals.read(self.root)), 2)

    def test_absent_stream_is_empty(self):
        self.assertEqual(signals.read(self.root), [])

    def test_torn_tail_is_dropped(self):
        signals.mark(self.root, "gate-block:irreversible", "delete", "needs gesture")
        # simulate a torn final line (a hard kill mid-append)
        with open(self.root / "log" / signals.STREAM, "a", encoding="utf-8") as f:
            f.write('{"id": "sig.partial", "kind": "cited-gho')
        got = signals.read(self.root)
        self.assertEqual(len(got), 1)
        self.assertEqual(got[0]["subject"], "delete")


class TeethLeaveAMarkTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name)
        self.root = self.base / ".ai-native"   # the records / mark root
        (self.root / "log").mkdir(parents=True)
        (self.root / "epics").mkdir()
        (self.root / "done").mkdir()
        self.data = self.base / "data"          # a person's data surface
        self.data.mkdir()

    def tearDown(self):
        self._tmp.cleanup()

    def _epic(self, pieces):
        body = {"epic": {"id": "epic.test", "owner": "t", "pieces": pieces}}
        (self.root / "epics" / "epic.test.json").write_text(
            json.dumps(body), encoding="utf-8")

    def _land(self, idnum, slug, piece):
        (self.root / "done" / f"{idnum:04d}-{slug}.md").write_text(
            f"# Done-line {idnum:04d} — {slug}\n\n> **Piece:** {piece}\n\n"
            "> **Done when:** met.\n", encoding="utf-8")

    def test_loopmaker_stop_leaves_a_mark(self):
        from loop import loopmaker
        self._epic([{"atom": "atom.a.v0", "glue": "g"}])
        self._land(1, "a", "atom.a.v0")  # fully landed -> converged
        result = loopmaker.operate("epic.test", root=self.root)
        self.assertIsInstance(result, loopmaker.Stop)
        sigs = signals.read(self.root)
        self.assertEqual([s["kind"] for s in sigs], ["loop-stop:converged"])

    def test_loopmaker_increment_leaves_no_mark(self):
        from loop import loopmaker
        self._epic([{"atom": "atom.a.v0", "glue": "g"},
                    {"atom": "atom.b.v0", "glue": "g"}])
        self._land(1, "a", "atom.a.v0")  # b still unlanded -> Increment, no refusal
        result = loopmaker.operate("epic.test", root=self.root)
        self.assertIsInstance(result, loopmaker.Increment)
        self.assertEqual(signals.read(self.root), [])

    def test_cited_sensor_ghost_leaves_a_mark(self):
        ghost = {"file": "phantom.exe", "stratum": "file", "kind": "exe",
                 "size": 9, "contains": "nope"}
        good, bad = cited_sensor.operate(self.data, mark_root=self.root,
                                         records=[ghost])
        self.assertEqual(good, [])
        self.assertEqual(len(bad), 1)
        sigs = signals.read(self.root)
        self.assertEqual([s["kind"] for s in sigs], ["cited-ghost"])
        self.assertEqual(sigs[0]["subject"], "phantom.exe")

    def test_gate_block_leaves_a_mark_allow_does_not(self):
        # a blocked irreversible act marks
        d = reversibility_gate.operate({"verb": "delete"}, mark_root=self.root)
        self.assertFalse(d.allowed)
        sigs = signals.read(self.root)
        self.assertEqual(len(sigs), 1)
        self.assertTrue(sigs[0]["kind"].startswith("gate-block:"))
        # an allowed reversible act marks nothing more
        d2 = reversibility_gate.operate({"verb": "pre-stage"}, mark_root=self.root)
        self.assertTrue(d2.allowed)
        self.assertEqual(len(signals.read(self.root)), 1)


if __name__ == "__main__":
    unittest.main()

"""Done-line 0123: the terminal-pull gateway (`loop.pull`) — the piece-scale
pull queue.

The gateway senses, per confirmed arc, the receipt-complete pieces that could
be pulled now — the slice `loop.merge` cannot see because it gates at arc
scale. It is read-only (writes nothing) and folds the digest dataset; it
re-derives no state (§10).

The §10 teeth the live log does not currently exercise (no confirmed arc
harbours a refusal today), so the test carries them:

  - a confirmed arc with a refusal under it VETOES the whole slice — a
    receipt-complete piece is HELD, never pulled over the no; the control
    (same setup minus the refusal) pulls clean, so the held is the refusal's
    doing, not a flaky red.
  - the capacity bound honours the admitted `max_inflight_atoms` dial: zero
    capacity pulls nothing now (all queued), a real capacity pulls.
  - the namespace gap fires: a `landed` receipt that carries no atom join
    leaves the gateway unable to confirm any piece reached main — and it
    says so rather than fabricating the join.
"""

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import pull, node, orchestrate, reconcile

SKELETON = REPO / ".ai-native" / "atoms" / "atom.loop-skeleton.v0.json"
SKELETON_ID = "atom.loop-skeleton.v0"


def _root(tmp):
    root = Path(tmp) / ".ai-native"
    (root / "log").mkdir(parents=True)
    (root / "atoms").mkdir(parents=True)
    (root / "epics").mkdir(parents=True)
    shutil.copy(SKELETON, root / "atoms" / "atom.loop-skeleton.v0.json")
    (root / "epics" / "epic.test.json").write_text(json.dumps({"epic": {
        "id": "epic.test", "arc": "a test arc",
        "pieces": [{"atom": SKELETON_ID, "glue": "the one piece"}]}}),
        encoding="utf-8")
    return root


def _drive_to_landed(root):
    """Pure mocks auto-advance; drive the skeleton to value_confirmed (the
    digest reads it `landed` — receipt-complete)."""
    for _ in range(60):
        result = reconcile.pass_once(root, quiet=True)[0]
        if result in ("done", "needs-you"):
            return result
    return "ran-out"


def _append_refusal(root, ts="2026-06-05T10:00:00Z"):
    """A gate's honest no on the skeleton's record — the §10 contradiction
    when its arc is also confirmed."""
    rc = {
        "id": "rcp." + reconcile.short_hash("refuse", SKELETON_ID, ts),
        "event_id": "evt." + reconcile.short_hash("ev", SKELETON_ID, ts),
        "node": "merge-precheck.mock.v0",
        "artifact_id": SKELETON_ID,
        "artifact_hash": "sha256:" + reconcile.short_hash("any"),
        "verdict": "unsafe",
        "reason": "a later gate said no",
        "next_suggested_event": None,
        "ts": ts,
    }
    reconcile.append_line(root / "log" / "receipts.jsonl", rc)


def _append_landed_pr(root, pr=7, ts="2026-06-05T11:00:00Z"):
    """A merge-node landing receipt — the git-merge namespace. Keys on
    (epic, pr, head); carries no atom join, exactly like the 90 on the live
    log."""
    rc = {
        "id": f"rcp.merge.{pr}", "kind": "merge",
        "node": "merge-node.test.v0", "epic": "epic.test",
        "head": "claude/test-branch", "pr": pr,
        "verdict": "landed", "authorized_by": "adm.test", "ts": ts,
    }
    reconcile.append_line(root / "log" / "receipts.jsonl", rc)


def _slice(root):
    return pull.next_landable_slice(root)


def _names(pieces):
    return {p["atom"] for p in pieces}


class _Temp(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = _root(self.tmp)
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)


class TestTheSlice(_Temp):
    def test_unconfirmed_arc_has_no_slice(self):
        # receipt-complete but no pull authority — bdo has not confirmed
        _drive_to_landed(self.root)
        r = _slice(self.root)
        self.assertEqual(r["pull_now"], [])
        self.assertEqual(r["queued_behind_capacity"], [])

    def test_confirmed_receipt_complete_piece_is_pullable(self):
        _drive_to_landed(self.root)
        node.confirm_arc(self.root, "epic.test", "bdo")
        r = _slice(self.root)
        # no setpoint admitted -> unbounded capacity -> the piece pulls now
        self.assertIn(SKELETON_ID, _names(r["pull_now"]))
        self.assertEqual(r["held"], [])

    def test_unbuilt_arc_sibling_does_not_block_the_complete_piece(self):
        # the throughput unlock: merge.py would report the arc not-ready
        # (a declared piece unbuilt); the gateway pulls the complete one.
        (self.root / "epics" / "epic.test.json").write_text(json.dumps({"epic": {
            "id": "epic.test", "arc": "a test arc", "pieces": [
                {"atom": SKELETON_ID, "glue": "the built piece"},
                {"atom": "atom.never-built.v0", "glue": "still unbuilt"}]}}),
            encoding="utf-8")
        _drive_to_landed(self.root)
        node.confirm_arc(self.root, "epic.test", "bdo")
        self.assertIn(SKELETON_ID, _names(_slice(self.root)["pull_now"]))


class TestTheTeeth(_Temp):
    """§10: a refusal under the confirmed arc vetoes the slice."""

    def test_refusal_under_confirmed_arc_holds_the_piece(self):
        _drive_to_landed(self.root)                       # receipt-complete
        node.confirm_arc(self.root, "epic.test", "bdo")   # pull authority
        _append_refusal(self.root)                        # yet a gate said no
        r = _slice(self.root)
        self.assertNotIn(SKELETON_ID, _names(r["pull_now"]))
        self.assertNotIn(SKELETON_ID, _names(r["queued_behind_capacity"]))
        self.assertIn(SKELETON_ID, _names(r["held"]))
        why = next(h["why"] for h in r["held"] if h["atom"] == SKELETON_ID)
        self.assertIn("refusal", why.lower())

    def test_control_without_the_refusal_the_piece_pulls(self):
        # identical minus the refusal -> pulls clean, so the held above is the
        # refusal's doing, not a flaky red
        _drive_to_landed(self.root)
        node.confirm_arc(self.root, "epic.test", "bdo")
        r = _slice(self.root)
        self.assertIn(SKELETON_ID, _names(r["pull_now"]))
        self.assertEqual(r["held"], [])


class TestCapacity(_Temp):
    """The slice is bounded by the admitted max_inflight_atoms dial."""

    def _confirm_landed(self):
        _drive_to_landed(self.root)
        node.confirm_arc(self.root, "epic.test", "bdo")

    def test_zero_capacity_pulls_nothing_now(self):
        self._confirm_landed()
        orchestrate.admit_setpoint(
            self.root, {"step_budget_per_tick": 3, "max_inflight_atoms": 0,
                        "human_queue_cap": 2}, by="test-bdo")
        r = _slice(self.root)
        self.assertEqual(r["capacity"], 0)
        self.assertEqual(r["headroom"], 0)
        self.assertEqual(r["pull_now"], [])
        self.assertIn(SKELETON_ID, _names(r["queued_behind_capacity"]))

    def test_real_capacity_pulls(self):
        self._confirm_landed()
        orchestrate.admit_setpoint(
            self.root, {"step_budget_per_tick": 3, "max_inflight_atoms": 8,
                        "human_queue_cap": 2}, by="test-bdo")
        r = _slice(self.root)
        self.assertEqual(r["capacity"], 8)
        self.assertIn(SKELETON_ID, _names(r["pull_now"]))


class TestNamespaceGap(_Temp):
    """The gateway refuses to claim a piece reached main; it names the gap."""

    def test_landed_receipt_without_an_atom_join_opens_the_gap(self):
        _drive_to_landed(self.root)
        node.confirm_arc(self.root, "epic.test", "bdo")
        _append_landed_pr(self.root)
        g = _slice(self.root)["namespace_gap"]
        self.assertTrue(g["open"])
        self.assertEqual(g["joined_to_atom"], 0)
        self.assertGreaterEqual(g["landed_receipts"], 1)

    def test_no_landings_no_gap(self):
        _drive_to_landed(self.root)
        node.confirm_arc(self.root, "epic.test", "bdo")
        self.assertFalse(_slice(self.root)["namespace_gap"]["open"])

    def test_a_joined_landing_does_not_open_the_gap(self):
        # the day a landing carries its atom, the gap closes for it — the
        # finding is honest about being structural, not perpetual
        _drive_to_landed(self.root)
        node.confirm_arc(self.root, "epic.test", "bdo")
        reconcile.append_line(self.root / "log" / "receipts.jsonl", {
            "id": "rcp.merge.joined", "kind": "merge", "verdict": "landed",
            "epic": "epic.test", "artifact_id": SKELETON_ID,
            "ts": "2026-06-05T12:00:00Z"})
        self.assertFalse(_slice(self.root)["namespace_gap"]["open"])


class TestReadOnly(_Temp):
    def test_the_fold_writes_nothing(self):
        _drive_to_landed(self.root)
        node.confirm_arc(self.root, "epic.test", "bdo")
        _append_refusal(self.root)
        _append_landed_pr(self.root)
        before = {p.name: p.read_bytes() for p in (self.root / "log").iterdir()}
        pull.next_landable_slice(self.root)
        pull.main(["--root", str(self.root)])
        after = {p.name: p.read_bytes() for p in (self.root / "log").iterdir()}
        self.assertEqual(before, after, "the gateway mutated the log; it must only fold")


class TestCli(_Temp):
    def test_cli_is_read_only_report(self):
        _drive_to_landed(self.root)
        node.confirm_arc(self.root, "epic.test", "bdo")
        self.assertEqual(pull.main(["--root", str(self.root)]), 0)
        self.assertEqual(pull.main(["--root", str(self.root), "--json"]), 0)


if __name__ == "__main__":
    unittest.main()

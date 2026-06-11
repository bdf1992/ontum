"""Done-line 0033: the merge-node's eyes — read-only land-readiness per arc.

The sensor decides "is this arc safe to land on main?" and never acts. The
§10 bar: a *confirmed* arc whose pieces all read landed but whose record
holds a refusal must report `refuse`, never `ready_to_land` — "every piece
landed" and "a gate said no" are each locally fine, and they refuse to fit.
The fold is read-only (writes nothing) and reuses the digest fold.
"""

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import merge, node, orchestrate, reconcile

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
    """Pure mocks auto-advance; drive the skeleton to value_confirmed."""
    for _ in range(60):
        result = reconcile.pass_once(root, quiet=True)[0]
        if result in ("done", "needs-you"):
            return result
    return "ran-out"


def _append_refusal(root, ts="2026-06-05T10:00:00Z"):
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


def _verdict(root, epic="epic.test"):
    return next(a["verdict"] for a in merge.readiness(root)["arcs"]
               if a["epic"] == epic)


class _Temp(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = _root(self.tmp)
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)


class TestVerdicts(_Temp):
    def test_unconfirmed_arc_is_not_ready(self):
        _drive_to_landed(self.root)  # landed, but never confirmed
        self.assertEqual(_verdict(self.root), merge.NOT_READY)

    def test_confirmed_but_unlanded_is_not_ready(self):
        node.confirm_arc(self.root, "epic.test", "bdo")  # confirmed, not driven
        self.assertEqual(_verdict(self.root), merge.NOT_READY)

    def test_confirmed_and_landed_clean_is_ready_to_land(self):
        _drive_to_landed(self.root)
        node.confirm_arc(self.root, "epic.test", "bdo")
        self.assertEqual(_verdict(self.root), merge.READY)


class TestTheTeeth(_Temp):
    """§10: a refusal must veto a confirmed, fully-landed arc."""

    def test_confirmed_landed_arc_with_a_refusal_in_record_is_refused(self):
        _drive_to_landed(self.root)            # every piece reads landed
        node.confirm_arc(self.root, "epic.test", "bdo")  # bdo's standing stamp
        _append_refusal(self.root)             # yet a gate said no
        self.assertEqual(_verdict(self.root), merge.REFUSE)

    def test_without_the_refusal_the_same_arc_is_ready(self):
        # the control: identical setup minus the refusal lands clean — so the
        # refuse above is the refusal's doing, not a flaky green
        _drive_to_landed(self.root)
        node.confirm_arc(self.root, "epic.test", "bdo")
        self.assertEqual(_verdict(self.root), merge.READY)


class TestReadOnly(_Temp):
    def test_readiness_writes_nothing(self):
        _drive_to_landed(self.root)
        node.confirm_arc(self.root, "epic.test", "bdo")
        _append_refusal(self.root)
        before = {p.name: p.read_bytes() for p in (self.root / "log").iterdir()}
        merge.readiness(self.root)
        merge.main(["--root", str(self.root)])
        after = {p.name: p.read_bytes() for p in (self.root / "log").iterdir()}
        self.assertEqual(before, after, "the sensor mutated the log; it must only fold")


class TestFieldCaution(_Temp):
    def test_cap_breach_surfaces_as_a_caution_not_a_per_arc_veto(self):
        _drive_to_landed(self.root)
        node.confirm_arc(self.root, "epic.test", "bdo")
        sp = orchestrate.admit_setpoint(
            self.root, {"step_budget_per_tick": 3, "max_inflight_atoms": 8,
                        "human_queue_cap": 2}, by="test-bdo")
        reconcile.append_line(self.root / "log" / "admissions.jsonl", {
            "id": "adm.tick.hot", "type": "tick", "tick": 9, "mode": "cool",
            "pressure": {"human_backlog": 5}, "setpoint_id": sp["id"],
            "budget_spent": 1, "scheduled": [], "deferred": [],
            "ts": "2026-06-05T10:00:00Z"})
        r = merge.readiness(self.root)
        self.assertEqual(len(r["cautions"]), 1)
        # the arc still lands — past field heat is not this arc's fault
        self.assertEqual(_verdict(self.root), merge.READY)


class TestCli(_Temp):
    def test_cli_is_report_and_read_only(self):
        self.assertEqual(merge.main(["--root", str(self.root)]), 0)


if __name__ == "__main__":
    unittest.main()

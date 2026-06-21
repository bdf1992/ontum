"""Non-vacuous tests for the consequence graph v0 (done-line 0167).

The fold is read-only and pure, so the test is a hand-built fixture log and
exact assertions on the plane it folds. Each assertion is chosen to FAIL on a
broken fold (the section-10 discipline): the ghost-refusal would not fire if the
citation check were skipped, and the no-smear assertions would not hold if
authorship/arc-sibling propagation leaked. The determinism check pins the
byte-stable property the json surface promises.
"""

import json
import tempfile
import unittest
from pathlib import Path

from loop.consequence_graph import build


def _write(root, events, receipts, epics):
    log = root / "log"
    log.mkdir(parents=True)
    (log / "events.jsonl").write_text(
        "".join(json.dumps(e) + "\n" for e in events), encoding="utf-8")
    (log / "receipts.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in receipts), encoding="utf-8")
    (log / "admissions.jsonl").write_text("", encoding="utf-8")
    ed = root / "epics"
    ed.mkdir(parents=True)
    for ep in epics:
        (ed / (ep["epic"]["id"] + ".json")).write_text(
            json.dumps(ep), encoding="utf-8")


EVENTS = [
    {"type": "atom.created", "artifact_id": "atom.foo.v0",
     "artifact_hash": "h:foo0", "from_node": "author.A", "id": "evt.foo0"},
    {"type": "atom.created", "artifact_id": "atom.foo.v1",
     "artifact_hash": "h:foo1", "from_node": "author.A", "id": "evt.foo1"},
    {"type": "atom.created", "artifact_id": "atom.bar.v0",
     "artifact_hash": "h:bar0", "from_node": "author.A", "id": "evt.bar0"},
    {"type": "atom.created", "artifact_id": "atom.baz.v0",
     "artifact_hash": "h:baz0", "from_node": "author.A", "id": "evt.baz0"},
    {"type": "atom.created", "artifact_id": "atom.baz.v1",
     "artifact_hash": "h:baz1", "from_node": "author.A", "id": "evt.baz1"},
    {"type": "consequence.observed", "id": "evt.cobs.good",
     "target": "atom_version:atom.bar.v0", "channel": "repair",
     "label": "adopted downstream",
     "citation": {"record_id": "rcp.foo0.neg",
                  "contains": "reject_wrong_value"}},
    {"type": "consequence.observed", "id": "evt.cobs.ghost",
     "target": "atom_version:atom.foo.v0", "channel": "drag",
     "label": "phantom", "citation": {"record_id": "rcp.nonexistent"}},
]
RECEIPTS = [
    {"id": "rcp.foo0.neg", "node": "value-gate.real",
     "artifact_hash": "h:foo0", "verdict": "reject_wrong_value"},
    {"id": "rcp.baz0.neg", "node": "value-gate.real",
     "artifact_hash": "h:baz0", "verdict": "reject_wrong_value"},
    {"id": "rcp.baz1.adv", "node": "value-gate.real",
     "artifact_hash": "h:baz1", "verdict": "accept"},
]
EPICS = [
    {"epic": {"id": "epic.test",
              "pieces": [{"atom": "atom.foo.v0"}, {"atom": "atom.bar.v0"}]}},
]


def _plane():
    tmp = tempfile.mkdtemp()
    root = Path(tmp) / ".ai-native"
    _write(root, EVENTS, RECEIPTS, EPICS)
    return build(root)


def _weight(out, channel, node):
    for row in out["field"]:
        if row["channel"] == channel and row["node"] == node:
            return row["weight"]
    return None


class TestConsequenceGraphV0(unittest.TestCase):
    def setUp(self):
        self.out = _plane()
        self.node_ids = {n["id"] for n in self.out["nodes"]}
        self.gap_ids = {g["id"] for g in self.out["gaps"]}

    # --- the section-10 ghost tooth, non-vacuous ---
    def test_ghost_citation_refused(self):
        self.assertIn("gap:consequence:evt.cobs.ghost", self.gap_ids)
        # a fold that skipped the check would place the node instead of refusing:
        self.assertNotIn("consequence:evt.cobs.ghost", self.node_ids)

    def test_resolved_citation_lands(self):
        self.assertNotIn("gap:consequence:evt.cobs.good", self.gap_ids)
        self.assertIn("consequence:evt.cobs.good", self.node_ids)

    # --- drag propagation with decay, and the no-smear rules ---
    def test_drag_propagates_with_decay(self):
        self.assertEqual(_weight(self.out, "drag", "atom_version:atom.foo.v0"), 1.0)
        self.assertEqual(_weight(self.out, "drag", "atom_base:atom.foo"), 0.7)
        self.assertEqual(_weight(self.out, "drag", "arc:epic.test"), 0.35)

    def test_no_actor_superspreader(self):
        # authored_by carries decay 0.0 - an actor never receives a mark.
        self.assertIsNone(_weight(self.out, "drag", "actor:author.A"))

    def test_no_arc_sibling_smear(self):
        # foo.v0 drag reaches the arc but never its sibling piece bar.v0.
        self.assertIsNone(_weight(self.out, "drag", "atom_version:atom.bar.v0"))

    def test_no_base_sibling_smear(self):
        # drag on foo.v0 reaches the base but not the sibling version foo.v1.
        self.assertIsNone(_weight(self.out, "drag", "atom_version:atom.foo.v1"))

    # --- repair: a sensor-derived healed bite and a declared consequence ---
    def test_repair_from_healed_bite(self):
        self.assertIn("consequence:bite-healed:atom.baz", self.node_ids)
        self.assertEqual(
            _weight(self.out, "repair", "atom_version:atom.baz.v1"), 0.85)

    def test_repair_from_declared_consequence(self):
        self.assertEqual(
            _weight(self.out, "repair", "consequence:evt.cobs.good"), 1.0)
        self.assertEqual(
            _weight(self.out, "repair", "atom_version:atom.bar.v0"), 0.85)

    # --- channels never net across type ---
    def test_channels_stay_separate(self):
        # the arc carries drag (from foo) and repair (from bar) as separate
        # entries - never collapsed or netted into one scalar.
        self.assertEqual(_weight(self.out, "drag", "arc:epic.test"), 0.35)
        self.assertEqual(_weight(self.out, "repair", "arc:epic.test"), 0.2975)

    def test_deterministic(self):
        a = json.dumps(_plane(), sort_keys=True)
        b = json.dumps(_plane(), sort_keys=True)
        self.assertEqual(a, b)

    def test_read_only_shape(self):
        self.assertEqual(self.out["mode"], "read_only")
        self.assertEqual(self.out["tier"], "tier_1_real_edges_only")


if __name__ == "__main__":
    unittest.main()

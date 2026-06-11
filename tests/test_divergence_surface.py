"""Done-line 0037: the merge surface — aggregate divergence issues.

bdo's shape (2026-06-11): the post-merge issues are AGGREGATE — one issue per
divergence *group* carrying its data points, not a one-issue-per-PR echo. The
kind rides the reflect rails: divergence_drift returns acts in drift()'s shape,
keyed by group id, so the gh translator and reflection records work unchanged.

The §10 bar: two refusals under the SAME confirmed arc must fold to ONE open
act (aggregate), not two — and the open is idempotent (recorded once, never
reopened), the close fires only when the group reconciles. A surface with no
enabled rule stays silent (the beat reaches only what rules name).
"""

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import node, reconcile, reflect

SKELETON = REPO / ".ai-native" / "atoms" / "atom.loop-skeleton.v0.json"
SURFACE = "github-issues"


def _make_atom(aid):
    return {"atom": {
        "id": aid,
        "story": {"text": f"As an AI, I need {aid} to exist, because the test "
                          "needs a second piece under one arc.",
                  "value_confidence": "high", "owner_stamp": "pending"},
        "concern_surface": "systems",
        "incidence": {"serves": ["epic.test"], "touches": [],
                      "must_not_collide_with": [], "hands_off_to": []},
        "desired_state": "value_confirmed",
        "verdicts": {}, "lineage": {"prompt_versions": [], "source_artifacts": [],
                                    "receipts": []}}}


def _root(tmp, pieces=("atom.loop-skeleton.v0",)):
    root = Path(tmp) / ".ai-native"
    (root / "log").mkdir(parents=True)
    (root / "atoms").mkdir(parents=True)
    (root / "epics").mkdir(parents=True)
    shutil.copy(SKELETON, root / "atoms" / "atom.loop-skeleton.v0.json")
    for aid in pieces:
        if aid != "atom.loop-skeleton.v0":
            (root / "atoms" / f"{aid}.json").write_text(
                json.dumps(_make_atom(aid)), encoding="utf-8")
    (root / "epics" / "epic.test.json").write_text(json.dumps({"epic": {
        "id": "epic.test", "arc": "a test arc",
        "pieces": [{"atom": a} for a in pieces]}}), encoding="utf-8")
    return root


def _refusal(root, atom_id, ts="2026-06-05T10:00:00Z"):
    reconcile.append_line(root / "log" / "receipts.jsonl", {
        "id": "rcp." + reconcile.short_hash("refuse", atom_id, ts),
        "event_id": "evt." + reconcile.short_hash("ev", atom_id, ts),
        "node": "merge-precheck.mock.v0", "artifact_id": atom_id,
        "artifact_hash": "sha256:" + reconcile.short_hash(atom_id),
        "verdict": "collision", "reason": "a gate said no",
        "next_suggested_event": None, "ts": ts})


def _register(root):
    reflect.admit_surface(root, SURFACE, "owner/repo", "test-bdo")


class TestGroupsPure(unittest.TestCase):
    """_divergence_groups: aggregate, not 1:1."""

    def test_two_refusals_one_arc_fold_to_one_group(self):
        divs = [
            {"kind": "refusal-under-confirmed-arc", "epic": "epic.test",
             "atom": "a.v0", "node": "n", "verdict": "collision", "reason": "x"},
            {"kind": "refusal-under-confirmed-arc", "epic": "epic.test",
             "atom": "b.v0", "node": "n", "verdict": "wrong_seam", "reason": "y"},
        ]
        groups = reflect._divergence_groups(divs)
        self.assertEqual(len(groups), 1)
        body = next(iter(groups.values()))["body"]
        self.assertIn("a.v0", body)
        self.assertIn("b.v0", body)  # both data points in the one issue

    def test_refusals_in_two_arcs_are_two_groups(self):
        divs = [
            {"kind": "refusal-under-confirmed-arc", "epic": "epic.a", "atom": "a"},
            {"kind": "refusal-under-confirmed-arc", "epic": "epic.b", "atom": "b"},
        ]
        self.assertEqual(len(reflect._divergence_groups(divs)), 2)

    def test_caps_are_their_own_group(self):
        divs = [
            {"kind": "refusal-under-confirmed-arc", "epic": "epic.a", "atom": "a"},
            {"kind": "queue-over-cap", "tick": 1, "backlog": 3, "cap": 2},
            {"kind": "queue-over-cap", "tick": 2, "backlog": 4, "cap": 2},
        ]
        groups = reflect._divergence_groups(divs)
        self.assertEqual(len(groups), 2)  # one refusal group + one cap group
        caps = [g for g in groups.values() if "cap" in g["title"]][0]
        self.assertIn("tick 1", caps["body"])
        self.assertIn("tick 2", caps["body"])

    def test_no_divergences_no_groups(self):
        self.assertEqual(reflect._divergence_groups([]), {})

    def test_group_id_is_stable(self):
        divs = [{"kind": "refusal-under-confirmed-arc", "epic": "epic.test", "atom": "a"}]
        self.assertEqual(list(reflect._divergence_groups(divs)),
                         list(reflect._divergence_groups(divs)))


class _Temp(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)


class TestDrift(_Temp):
    def setUp(self):
        super().setUp()
        self.root = _root(self.tmp, pieces=("atom.loop-skeleton.v0", "atom.second.v0"))
        _register(self.root)

    def _confirmed_with_two_refusals(self):
        node.confirm_arc(self.root, "epic.test", "bdo")
        _refusal(self.root, "atom.loop-skeleton.v0")
        _refusal(self.root, "atom.second.v0")

    def test_two_refusals_one_arc_is_one_open_act(self):  # §10
        self._confirmed_with_two_refusals()
        acts = reflect.divergence_drift(self.root, SURFACE)
        opens = [a for a in acts if a["act"] == "open"]
        self.assertEqual(len(opens), 1, "aggregate: one issue per arc, not per piece")

    def test_unconfirmed_arc_has_no_divergence_so_no_act(self):
        _refusal(self.root, "atom.loop-skeleton.v0")  # arc NOT confirmed
        self.assertEqual(reflect.divergence_drift(self.root, SURFACE), [])

    def test_open_is_idempotent_once_recorded(self):
        self._confirmed_with_two_refusals()
        act = [a for a in reflect.divergence_drift(self.root, SURFACE) if a["act"] == "open"][0]
        reflect.record_reflection(self.root, SURFACE, act["atom_id"],
                                  act["artifact_hash"], "open",
                                  "https://x/issues/1", "test")
        again = [a for a in reflect.divergence_drift(self.root, SURFACE) if a["act"] == "open"]
        self.assertEqual(again, [], "an opened group must not reopen")

    def test_close_fires_when_the_group_reconciles(self):
        self._confirmed_with_two_refusals()
        act = [a for a in reflect.divergence_drift(self.root, SURFACE) if a["act"] == "open"][0]
        reflect.record_reflection(self.root, SURFACE, act["atom_id"],
                                  act["artifact_hash"], "open",
                                  "https://x/issues/1", "test")
        # reconcile: withdraw the arc so digest reports no divergence
        node.confirm_arc(self.root, "epic.test", "bdo", enabled=False)
        closes = [a for a in reflect.divergence_drift(self.root, SURFACE) if a["act"] == "close"]
        self.assertEqual(len(closes), 1)
        self.assertEqual(closes[0]["external_ref"], "https://x/issues/1")

    def test_writes_nothing(self):
        self._confirmed_with_two_refusals()
        before = {p.name: p.read_bytes() for p in (self.root / "log").iterdir()}
        reflect.divergence_drift(self.root, SURFACE)
        after = {p.name: p.read_bytes() for p in (self.root / "log").iterdir()}
        self.assertEqual(before, after)


class TestAutoPlanDispatch(_Temp):
    def setUp(self):
        super().setUp()
        self.root = _root(self.tmp)
        _register(self.root)

    def test_beat_reaches_merge_divergences_only_when_ruled(self):
        node.confirm_arc(self.root, "epic.test", "bdo")
        _refusal(self.root, "atom.loop-skeleton.v0")
        # no rule yet → the beat names nothing for this kind
        plan = reflect.auto_plan(self.root)
        self.assertFalse([p for p in plan if p["kind"] == "merge-divergences"])
        # enable the rule → the beat now carries the aggregate divergence acts
        reflect.admit_rule(self.root, "merge-divergences", SURFACE, True, "test-bdo")
        plan = reflect.auto_plan(self.root)
        mine = [p for p in plan if p["kind"] == "merge-divergences"]
        self.assertEqual(len(mine), 1)
        self.assertTrue(mine[0]["acts"])


if __name__ == "__main__":
    unittest.main()

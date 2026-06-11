"""Done-line 0032: the owner's merge digest — the data-rich surface bdo
watches instead of operating the merge.

The fold is pure and read-only (writes nothing to the log). The §10 bar:
a *confirmed* arc that harbours a *refused* piece is a contradiction the
digest must surface as a named divergence, not smooth over — bdo's standing
stamp and a gate's honest no are each locally fine, and they refuse to fit.
A clean span shows none; span bounds are honoured; the cap breach is caught.
"""

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import digest, node, orchestrate, reconcile

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


def _append_receipt(root, verdict, ts, advancing=False, atom_id=SKELETON_ID):
    """A receipt straight onto the log — refusal by default (no next event),
    advancing when asked. The digest reads the verdict generically off
    next_suggested_event, so this is all it takes to stand in for a gate."""
    rc = {
        "id": "rcp." + reconcile.short_hash(verdict, atom_id, ts),
        "event_id": "evt." + reconcile.short_hash("ev", atom_id, ts),
        "node": "placement-gate.mock.v0",
        "artifact_id": atom_id,
        "artifact_hash": "sha256:" + reconcile.short_hash(atom_id),
        "verdict": verdict,
        "reason": f"mock {verdict}",
        "next_suggested_event": "placement.sound" if advancing else None,
        "ts": ts,
    }
    reconcile.append_line(root / "log" / "receipts.jsonl", rc)
    return rc


class _Temp(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = _root(self.tmp)
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)


class TestReadOnly(_Temp):
    def test_digest_writes_nothing(self):
        _append_receipt(self.root, "collision", "2026-06-05T10:00:00Z")
        before = {p.name: p.read_bytes() for p in (self.root / "log").iterdir()}
        digest.digest(self.root)
        after = {p.name: p.read_bytes() for p in (self.root / "log").iterdir()}
        self.assertEqual(before, after, "the digest mutated the log; it must only fold")


class TestArcGrouping(_Temp):
    def test_arc_present_with_confirmation_status(self):
        d = digest.digest(self.root)
        self.assertEqual(len(d["arcs"]), 1)
        arc = d["arcs"][0]
        self.assertEqual(arc["epic"], "epic.test")
        self.assertIsNone(arc["confirmed"])
        self.assertEqual([p["atom"] for p in arc["pieces"]], [SKELETON_ID])

    def test_confirmation_surfaces(self):
        node.confirm_arc(self.root, "epic.test", "bdo")
        arc = digest.digest(self.root)["arcs"][0]
        self.assertIsNotNone(arc["confirmed"])
        self.assertEqual(arc["confirmed"]["by"], "bdo")

    def test_declared_but_absent_piece_named_not_invented(self):
        # absence is information (hard rule): a piece the epic claims but isn't
        # on disk shows as unbuilt, never silently dropped
        (self.root / "epics" / "epic.test.json").write_text(json.dumps({"epic": {
            "id": "epic.test", "arc": "a test arc",
            "pieces": [{"atom": SKELETON_ID}, {"atom": "atom.future.v0"}]}}),
            encoding="utf-8")
        pieces = digest.digest(self.root)["arcs"][0]["pieces"]
        future = [p for p in pieces if p["atom"] == "atom.future.v0"][0]
        self.assertFalse(future["present"])
        self.assertEqual(future["standing"], "unbuilt")


class TestDivergenceTheTeeth(_Temp):
    """§10: the case that must refuse to fit."""

    def test_confirmed_arc_with_refused_piece_is_a_divergence(self):
        node.confirm_arc(self.root, "epic.test", "bdo")
        _append_receipt(self.root, "collision", "2026-06-05T10:00:00Z")
        div = digest.digest(self.root)["divergences"]
        self.assertEqual(len(div), 1)
        self.assertEqual(div[0]["kind"], "refusal-under-confirmed-arc")
        self.assertEqual(div[0]["atom"], SKELETON_ID)
        self.assertEqual(div[0]["verdict"], "collision")
        self.assertEqual(div[0]["confirmed_by"], "bdo")

    def test_unconfirmed_arc_with_refusal_is_not_this_divergence(self):
        # a refusal on an *unconfirmed* arc is the normal park-for-bdo, not a
        # contradiction — the divergence is specifically confirmed+refused
        _append_receipt(self.root, "collision", "2026-06-05T10:00:00Z")
        div = digest.digest(self.root)["divergences"]
        self.assertEqual(div, [])

    def test_confirmed_arc_with_only_advances_is_clean(self):
        node.confirm_arc(self.root, "epic.test", "bdo")
        _append_receipt(self.root, "sound", "2026-06-05T10:00:00Z", advancing=True)
        self.assertEqual(digest.digest(self.root)["divergences"], [])


class TestQueueOverCap(_Temp):
    def test_tick_over_its_setpoint_cap_is_a_divergence(self):
        sp = orchestrate.admit_setpoint(
            self.root, {"step_budget_per_tick": 3, "max_inflight_atoms": 8,
                        "human_queue_cap": 2}, by="test-bdo")
        reconcile.append_line(self.root / "log" / "admissions.jsonl", {
            "id": "adm.tick.over", "type": "tick", "tick": 7, "mode": "cool",
            "pressure": {"human_backlog": 3, "inflight": 4, "queue_depth": 4},
            "setpoint_id": sp["id"], "budget_spent": 1, "scheduled": [],
            "deferred": [], "ts": "2026-06-05T10:00:00Z"})
        div = [x for x in digest.digest(self.root)["divergences"]
               if x["kind"] == "queue-over-cap"]
        self.assertEqual(len(div), 1)
        self.assertEqual(div[0]["backlog"], 3)
        self.assertEqual(div[0]["cap"], 2)

    def test_tick_within_cap_is_clean(self):
        sp = orchestrate.admit_setpoint(
            self.root, {"step_budget_per_tick": 3, "max_inflight_atoms": 8,
                        "human_queue_cap": 2}, by="test-bdo")
        reconcile.append_line(self.root / "log" / "admissions.jsonl", {
            "id": "adm.tick.ok", "type": "tick", "tick": 1, "mode": "heat",
            "pressure": {"human_backlog": 1}, "setpoint_id": sp["id"],
            "budget_spent": 2, "scheduled": [], "deferred": [],
            "ts": "2026-06-05T10:00:00Z"})
        self.assertEqual(digest.digest(self.root)["divergences"], [])


class TestSpan(_Temp):
    def test_span_bounds_the_fold(self):
        _append_receipt(self.root, "collision", "2026-06-01T10:00:00Z")
        _append_receipt(self.root, "wrong_seam", "2026-06-09T10:00:00Z",
                        atom_id=SKELETON_ID)
        node.confirm_arc(self.root, "epic.test", "bdo")
        # the whole window sees both refusals
        self.assertEqual(digest.digest(self.root)["refusals"], 2)
        # a window around the first excludes the second
        d = digest.digest(self.root, since="2026-06-01", until="2026-06-05")
        self.assertEqual(d["refusals"], 1)
        self.assertEqual(len(d["divergences"]), 1)


class TestField(_Temp):
    def test_tick_behaviour_folds_into_the_field(self):
        sp = orchestrate.admit_setpoint(
            self.root, {"step_budget_per_tick": 3, "max_inflight_atoms": 8,
                        "human_queue_cap": 2}, by="test-bdo")
        for n, mode, why in [(1, "heat", None), (2, "cool", "cool: inflow shed")]:
            reconcile.append_line(self.root / "log" / "admissions.jsonl", {
                "id": f"adm.tick.{n}", "type": "tick", "tick": n, "mode": mode,
                "pressure": {"human_backlog": 1}, "setpoint_id": sp["id"],
                "budget_spent": 2,
                "deferred": [{"atom": "a", "why": why}] if why else [],
                "scheduled": [], "ts": "2026-06-05T10:00:00Z"})
        f = digest.digest(self.root)["field"]
        self.assertEqual(f["ticks"], 2)
        self.assertEqual(f["heat"], 1)
        self.assertEqual(f["cool"], 1)
        self.assertEqual(f["budget_spent"], 4)
        self.assertEqual(f["deferred_reasons"], {"cool: inflow shed": 1})


class TestRenderAndCli(_Temp):
    def test_render_leads_with_divergences(self):
        node.confirm_arc(self.root, "epic.test", "bdo")
        _append_receipt(self.root, "collision", "2026-06-05T10:00:00Z")
        text = digest.render(digest.digest(self.root))
        self.assertIn("Divergences", text)
        self.assertIn("collision", text)
        self.assertIn(SKELETON_ID, text)

    def test_cli_clean_span_is_done(self):
        self.assertEqual(digest.main(["--root", str(self.root)]), 0)

    def test_json_is_parseable_dataset(self):
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            digest.main(["--root", str(self.root), "--json"])
        payload = json.loads(buf.getvalue().splitlines()[0])
        self.assertIn("arcs", payload)
        self.assertIn("divergences", payload)


if __name__ == "__main__":
    unittest.main()

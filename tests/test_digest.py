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


class TestSupersededRefusalIsHistory(unittest.TestCase):
    """Done-line 0090: a refusal a newer LANDED version of the same atom
    already cleared is settled history, not a live 'these need you' divergence
    — the stale `atom.field-topology.v0` 'missed' that rode every digest after
    v1 landed and loop/field.py shipped (done-line 0078). The teeth (§10) stay:
    the current/highest version's own refusal still fires."""

    def test_base_version_splits_on_the_v_suffix(self):
        self.assertEqual(digest._base_version("atom.field-topology.v3"),
                         ("atom.field-topology", 3))
        self.assertEqual(digest._base_version("atom.no-suffix"),
                         ("atom.no-suffix", 0))

    def test_a_later_landed_version_supersedes_an_earlier_refusal(self):
        pieces = [{"atom": "atom.x.v0", "landed": False},
                  {"atom": "atom.x.v1", "landed": True}]
        self.assertEqual(digest._superseded(pieces), {"atom.x.v0"})

    def test_no_landed_successor_supersedes_nothing(self):
        # v0 refused, v1 ALSO refused (nothing landed): the contradiction is
        # still live — the fold must not go blind because a successor exists.
        pieces = [{"atom": "atom.x.v0", "landed": False},
                  {"atom": "atom.x.v1", "landed": False}]
        self.assertEqual(digest._superseded(pieces), set())

    def test_an_earlier_landed_version_does_not_supersede_a_later_refusal(self):
        # the highest version's own refusal is the live one; a *lower* landed
        # version must never silence it.
        pieces = [{"atom": "atom.x.v0", "landed": True},
                  {"atom": "atom.x.v1", "landed": False}]
        self.assertEqual(digest._superseded(pieces), set())

    def test_divergence_drops_superseded_but_keeps_the_live_one(self):
        # two confirmed-arc pieces each carry a refusal: one (a.v0) is cleared
        # by a landed successor (a.v1), one (b.v0) is the highest version. Each
        # refusal is locally fine; only the live one is a divergence bdo sees.
        import types
        fold = types.SimpleNamespace(admissions=[])
        arcs = [{"epic": "epic.x", "confirmed": {"by": "bdo"}, "pieces": [
            {"atom": "atom.a.v0", "landed": False,
             "refusals": [{"node": "g", "verdict": "missed", "reason": "stale"}]},
            {"atom": "atom.a.v1", "landed": True, "refusals": []},
            {"atom": "atom.b.v0", "landed": False,
             "refusals": [{"node": "g", "verdict": "collision", "reason": "live"}]},
        ]}]
        superseded = digest._superseded([p for a in arcs for p in a["pieces"]])
        self.assertEqual(superseded, {"atom.a.v0"})
        div = digest._divergences(fold, arcs, [], None, None, superseded)
        self.assertEqual([d["atom"] for d in div], ["atom.b.v0"])
        self.assertEqual(div[0]["verdict"], "collision")


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


class TestLandingNotRefusal(_Temp):
    """retro fold 0098 surfaced it: a merge-node `landed` verdict carries no
    next event, so the old 'no next event == refusal' rule counted every merge
    landing as a refusal (the 58-where-~7-were-real inflation). A landing is a
    landing, not a refusal."""

    def _merge_landed(self, n, ts):
        reconcile.append_line(self.root / "log" / "receipts.jsonl", {
            "id": f"rcp.merge.{n}", "node": "merge-node.claude.v1",
            "artifact_id": None, "verdict": "landed",
            "reason": f"landed PR #{n}", "next_suggested_event": None, "ts": ts})

    def test_merge_landings_are_landings_not_refusals(self):
        self._merge_landed(1, "2026-06-05T10:00:00Z")
        self._merge_landed(2, "2026-06-05T11:00:00Z")
        _append_receipt(self.root, "collision", "2026-06-05T12:00:00Z")
        d = digest.digest(self.root)
        self.assertEqual(d["refusals"], 1)   # only the real one, not the 2 lands
        self.assertEqual(d["landings"], 2)   # the merge lands now count as lands

    def test_a_verdictless_receipt_refuses_nothing(self):
        reconcile.append_line(self.root / "log" / "receipts.jsonl", {
            "id": "rcp.noverdict", "node": "x", "artifact_id": None,
            "verdict": None, "next_suggested_event": None,
            "ts": "2026-06-05T10:00:00Z"})
        self.assertEqual(digest.digest(self.root)["refusals"], 0)


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


class TestGestureSurface(_Temp):
    """The 2026-06-16 redesign: bdo found the digest 'hard to read and make
    gestures about'. The teeth here are the gesture contract — a digest may
    only call something 'your move' when there is a gesture actually waiting
    on him. The §10 pair that refuses to fit at the surface: a *divergence
    exists* and *nothing is on bdo* are both true at once, and the old render
    fused them into a false 'these need you'."""

    def test_session_work_divergence_is_not_an_owner_gesture(self):
        # confirmed arc + refused piece: a real divergence whose move is a
        # session's rebuild. It must surface (the teeth) but must NOT be
        # presented as bdo's gesture (the lie the redesign kills).
        node.confirm_arc(self.root, "epic.test", "bdo")
        _append_receipt(self.root, "collision", "2026-06-05T10:00:00Z")
        d = digest.digest(self.root)
        self.assertEqual(len(d["divergences"]), 1, "the divergence must still surface")
        self.assertEqual(digest.owner_gestures(d), [],
                         "session work must not be folded into 'your move'")
        text = digest.render(d)
        self.assertIn("**Your move:** nothing", text)
        self.assertNotIn("these need you", text)

    def test_unconfirmed_arc_with_built_work_is_an_owner_gesture(self):
        # the converse: an arc with a real built piece and no confirmation is
        # exactly the gesture bdo should see at the top — confirm to unblock.
        d = digest.digest(self.root)
        self.assertEqual([a["epic"] for a in digest.owner_gestures(d)], ["epic.test"])
        self.assertIn("**Your move — confirm 1 arc", digest.render(d))

    def test_confirmed_arc_is_never_a_gesture(self):
        # crying wolf the other way: never tell bdo to confirm what he has.
        node.confirm_arc(self.root, "epic.test", "bdo")
        d = digest.digest(self.root)
        self.assertEqual(digest.owner_gestures(d), [])

    def test_arc_prose_is_not_re_dumped(self):
        # the volume half of unreadable: the arc's full description lives in
        # its epic file and must not be echoed into the daily glance.
        d = digest.digest(self.root)
        self.assertNotIn("a test arc", digest.render(d),
                         "the arc's prose was re-dumped — the unreadability bdo refused")


class TestEndLineVerdict(_Temp):
    """Done-line 0055: the end line may never claim cleaner than the dataset.

    The §10 pair report 0038 named: a refusal on an UNCONFIRMED arc's piece
    feeds no divergence — 'no divergence' and 'refusal in span' are each
    locally fine and refuse to fit at the verdict line — yet the old sum
    closed it 'done — clean span: nothing refused'. The control: a genuinely
    refusal-free, nothing-open span must still end done (the fix must not
    cry wolf)."""

    def test_refusal_without_divergence_still_ends_report(self):
        _append_receipt(self.root, "collision", "2026-06-05T10:00:00Z")
        d = digest.digest(self.root)
        self.assertEqual(len(d["divergences"]), 0,
                         "unconfirmed arc: the refusal must NOT be a divergence")
        self.assertEqual(d["refusals"], 1)
        self.assertGreater(digest.open_count(d), 0,
                           "a refusal span may not close clean (report 0038)")

    def test_cli_says_report_on_a_refusal_span(self):
        import io
        from contextlib import redirect_stdout
        _append_receipt(self.root, "collision", "2026-06-05T10:00:00Z")
        buf = io.StringIO()
        with redirect_stdout(buf):
            digest.main(["--root", str(self.root)])
        self.assertIn("result: report", buf.getvalue())
        self.assertNotIn("clean span", buf.getvalue())

    def test_loose_parked_atom_counts_as_open(self):
        # pure over the dataset: a parked loose atom is exactly as open as a
        # parked arc piece — the old sum read only d["arcs"].
        d = {"divergences": [], "refusals": 0,
             "arcs": [{"awaiting": 0, "parked": 0}],
             "loose": [{"awaiting": False, "parked": True}]}
        self.assertEqual(digest.open_count(d), 1)

    def test_clean_span_still_ends_done(self):
        import io
        from contextlib import redirect_stdout
        d = digest.digest(self.root)
        self.assertEqual(digest.open_count(d), 0)
        buf = io.StringIO()
        with redirect_stdout(buf):
            digest.main(["--root", str(self.root)])
        self.assertIn("result: done — clean span", buf.getvalue())


if __name__ == "__main__":
    unittest.main()

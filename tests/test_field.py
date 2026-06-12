"""Done-line 0050: the first Field — a deterministic fold maps an arc's
work-topology.

The §10 teeth: this suite must fail on a fabricated/constant ladder. It
does so three ways — the ladder must *change* when the log changes (a
constant ladder fails the confirmed/unconfirmed pair), the not-first-class
rungs must read as named gaps with no evidence (a fold that "populates"
task or environment fails), and an occupant with no admission on either
side must surface UN-AUTHORISED (a fold that flatters occupancy fails).
Hermetic roots throughout — the spawn-rail lesson of 2026-06-12: a test
pinned to live records un-tests itself the moment the owner acts.
"""

import json
import pathlib
import shutil
import tempfile
import unittest

from loop.field import field, RUNGS

ROOT = pathlib.Path(__file__).resolve().parent.parent


def _write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj), encoding="utf-8")


def _lines(path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r) + "\n" for r in records),
                    encoding="utf-8")


def _root(confirmed=True, rogue_receipt=True):
    """A hermetic .ai-native: one epic, one announced atom one receipt deep,
    a real value gate seated by admission, an aliased id, and (optionally)
    a rogue receipt-writer no admission ever named."""
    ai = pathlib.Path(tempfile.mkdtemp(prefix="field-test-"))
    _write(ai / "epics" / "epic.test.json", {"epic": {
        "id": "epic.test", "owner": "bdo", "arc": "t", "value": "t",
        "horizon": "t",
        "pieces": [{"atom": "atom.t.v0", "glue": "g"},
                   {"atom": "atom.never-authored.v0", "glue": "g"}],
    }})
    atom_path = ai / "atoms" / "atom.t.v0.json"
    _write(atom_path, {"atom": {
        "id": "atom.t.v0",
        "story": {"text": "t", "value_confidence": "high",
                  "owner_stamp": "pending"},
        "incidence": {"serves": ["epic.test"], "touches": ["x.py"],
                      "must_not_collide_with": [], "hands_off_to": ["s"]},
        "desired_state": "value_confirmed", "verdicts": {}, "lineage": {},
    }})
    import hashlib
    ahash = "sha256:" + hashlib.sha256(atom_path.read_bytes()).hexdigest()
    admissions = [
        {"id": "adm.seat", "type": "node_real",
         "stage_node": "value-gate.mock.v0",
         "real_node": "value-gate.test.v1", "by": "bdo", "ts": "t"},
        {"id": "adm.alias", "type": "node_real", "stage_node": "old.alias.v0",
         "real_node": "aliased.seat.v1", "by": "bdo", "ts": "t"},
    ]
    if confirmed:
        admissions.append({"id": "adm.conf", "type": "arc_confirmed",
                           "epic": "epic.test", "by": "bdo",
                           "enabled": True, "ts": "t"})
    _lines(ai / "log" / "admissions.jsonl", admissions)
    _lines(ai / "log" / "events.jsonl", [
        {"id": "ev.seed", "type": "atom.created", "atom_id": "atom.t.v0",
         "artifact_hash": ahash, "from_node": "old.alias.v0", "ts": "t"},
    ])
    receipts = [
        {"id": "rcp.value", "node": "value-gate.test.v1",
         "artifact_hash": ahash, "verdict": "accept", "reason": "t",
         "next_suggested_event": "value.accepted", "ts": "t"},
    ]
    if rogue_receipt:
        receipts.append({"id": "rcp.rogue", "node": "rogue.v0",
                         "artifact_hash": ahash, "verdict": "accept",
                         "reason": "t", "next_suggested_event": None,
                         "ts": "t"})
    _lines(ai / "log" / "receipts.jsonl", receipts)
    return ai


class LadderIsDerivedNotConstant(unittest.TestCase):
    """A fabricated/constant ladder cannot pass both halves of this pair."""

    def test_confirmed_arc_reads_confirmed_with_the_admission_as_evidence(self):
        ai = _root(confirmed=True)
        self.addCleanup(shutil.rmtree, ai, ignore_errors=True)
        ladder = field(ai, "epic.test")
        arc = ladder["rungs"][0]["items"][0]
        self.assertEqual(arc["state"], "confirmed")
        self.assertEqual(arc["evidence"], ["adm.conf"])

    def test_unconfirmed_arc_reads_unconfirmed_and_names_bdo(self):
        ai = _root(confirmed=False)
        self.addCleanup(shutil.rmtree, ai, ignore_errors=True)
        arc = field(ai, "epic.test")["rungs"][0]["items"][0]
        self.assertEqual(arc["state"], "unconfirmed")
        self.assertEqual(arc["evidence"], [])
        self.assertIn("needs bdo", arc["next_safe_move"])

    def test_absent_epic_is_an_absence_not_an_empty_ladder(self):
        ai = _root()
        self.addCleanup(shutil.rmtree, ai, ignore_errors=True)
        self.assertIsNone(field(ai, "epic.nope"))


class EvidenceIsRecordIdsNeverProse(unittest.TestCase):
    def test_story_rung_carries_the_receipt_ids_on_the_atom(self):
        ai = _root()
        self.addCleanup(shutil.rmtree, ai, ignore_errors=True)
        ladder = field(ai, "epic.test")
        story = next(r for r in ladder["rungs"] if r["rung"] == "story")
        item = next(i for i in story["items"] if i["subject"] == "atom.t.v0")
        self.assertIn("rcp.value", item["evidence"])
        self.assertIn("value_accepted", item["state"])

    def test_node_rung_cites_the_seating_admission(self):
        ai = _root()
        self.addCleanup(shutil.rmtree, ai, ignore_errors=True)
        node = next(r for r in field(ai, "epic.test")["rungs"]
                    if r["rung"] == "node")
        seated = next(i for i in node["items"]
                      if i["subject"] == "value-gate.test.v1")
        self.assertEqual(seated["evidence"], ["adm.seat"])
        mocks = [i for i in node["items"] if i["state"].startswith("MOCK")]
        self.assertEqual(len(mocks), 4)  # only the value gate is seated here
        for m in mocks:
            self.assertIn("admit-real", m["next_safe_move"])

    def test_a_piece_the_epic_names_but_no_one_authored_is_absent(self):
        ai = _root()
        self.addCleanup(shutil.rmtree, ai, ignore_errors=True)
        epic = next(r for r in field(ai, "epic.test")["rungs"]
                    if r["rung"] == "epic")
        absent = next(i for i in epic["items"]
                      if i["subject"] == "atom.never-authored.v0")
        self.assertEqual(absent["state"], "absent")
        self.assertEqual(absent["evidence"], [])


class AbsentRungsAreNamedGapsNeverInvented(unittest.TestCase):
    """Done-line 0050's center: a field that fabricates a clean ladder is a
    mock with a bigger bill."""

    def test_task_and_environment_surface_as_gaps_with_no_evidence(self):
        ai = _root()
        self.addCleanup(shutil.rmtree, ai, ignore_errors=True)
        ladder = field(ai, "epic.test")
        for rung_name in ("task", "environment"):
            rung = next(r for r in ladder["rungs"] if r["rung"] == rung_name)
            self.assertEqual(len(rung["items"]), 1)
            item = rung["items"][0]
            self.assertEqual(item["state"], "not-first-class")
            self.assertEqual(item["evidence"], [])
            self.assertIn("absence is information", item["why"])
            self.assertIn("needs bdo", item["next_safe_move"])

    def test_the_ladder_has_all_seven_rungs_in_order(self):
        ai = _root()
        self.addCleanup(shutil.rmtree, ai, ignore_errors=True)
        ladder = field(ai, "epic.test")
        self.assertEqual(tuple(r["rung"] for r in ladder["rungs"]), RUNGS)


class OccupancyCarriesAuthority(unittest.TestCase):
    def test_unadmitted_writer_is_flagged_unauthorised(self):
        ai = _root(rogue_receipt=True)
        self.addCleanup(shutil.rmtree, ai, ignore_errors=True)
        occ = next(r for r in field(ai, "epic.test")["rungs"]
                   if r["rung"] == "occupant")
        rogue = next(i for i in occ["items"] if i["subject"] == "rogue.v0")
        self.assertEqual(rogue["state"], "UN-AUTHORISED")
        self.assertIn("rcp.rogue", rogue["evidence"])
        self.assertIn("admit-real", rogue["next_safe_move"])

    def test_seated_writer_is_authorised_citing_its_admission(self):
        ai = _root()
        self.addCleanup(shutil.rmtree, ai, ignore_errors=True)
        occ = next(r for r in field(ai, "epic.test")["rungs"]
                   if r["rung"] == "occupant")
        gate = next(i for i in occ["items"]
                    if i["subject"] == "value-gate.test.v1")
        self.assertEqual(gate["state"], "authorised")
        self.assertEqual(gate["evidence"][0], "adm.seat")

    def test_superseded_stage_side_reads_as_authorised_alias(self):
        ai = _root()
        self.addCleanup(shutil.rmtree, ai, ignore_errors=True)
        occ = next(r for r in field(ai, "epic.test")["rungs"]
                   if r["rung"] == "occupant")
        alias = next(i for i in occ["items"] if i["subject"] == "old.alias.v0")
        self.assertIn("alias of aliased.seat.v1", alias["state"])
        self.assertEqual(alias["evidence"][0], "adm.alias")


class LiveArcShape(unittest.TestCase):
    """Against the real repo: shape invariants only — no value pins that an
    owner act would falsify (the spawn-rail lesson)."""

    def test_a_real_arc_folds_with_evidence_shaped_ids(self):
        ladder = field(ROOT / ".ai-native", "epic.the-field")
        self.assertIsNotNone(ladder)
        self.assertEqual(tuple(r["rung"] for r in ladder["rungs"]), RUNGS)
        arc = ladder["rungs"][0]["items"][0]
        self.assertIn(arc["state"], ("confirmed", "unconfirmed"))
        for rung in ladder["rungs"]:
            for item in rung["items"]:
                for ev in item["evidence"]:
                    self.assertRegex(ev, r"^(adm|rcp|evt?|atom)\.")


if __name__ == "__main__":
    unittest.main()

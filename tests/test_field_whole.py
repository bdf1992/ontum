"""Done-line 0078: the WHOLE field — every arc composed into one
ladder-graph (the holonic whole), so the loop can load the complete ontum
environment, not one arc at a time.

The §10 teeth, three ways:
- composition is real and altitude is preserved: a multi-epic root folds
  into one graph where every arc keeps its full seven-rung ladder — a
  flattened bag of nodes (the hairball non-example) fails the rung check;
- the holographic rule has teeth: `route_audit` must CATCH a routeless
  node asserted as fact (a ghost), and must NOT flag an honest surfaced
  gap (an `absent` piece) — a constant classifier fails one half or the
  other;
- the projection cannot drift: the same input folds byte-for-byte the
  same (asserted as bytes, the tree's discipline).

Hermetic roots throughout (the spawn-rail lesson): no pin to live records
that an owner act would falsify.
"""

import hashlib
import json
import pathlib
import shutil
import tempfile
import unittest

from loop.field import (RUNGS, route_audit, whole_field, _known_ids)
from loop.reconcile import Fold


def _write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj), encoding="utf-8")


def _lines(path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r) + "\n" for r in records),
                    encoding="utf-8")


def _atom(aid, epic):
    return {"atom": {
        "id": aid,
        "story": {"text": "t", "value_confidence": "high",
                  "owner_stamp": "pending"},
        "incidence": {"serves": [epic], "touches": ["x.py"],
                      "must_not_collide_with": [], "hands_off_to": ["s"]},
        "desired_state": "value_confirmed", "verdicts": {}, "lineage": {},
    }}


def _two_epic_root():
    """Two epics: alpha confirmed with one authored atom + one absent piece;
    beta unconfirmed with one absent piece. Exercises the agenda rung
    (confirmed + unconfirmed), an authored node with a route, and honest
    absences that must read as surfaced gaps, never ghosts."""
    ai = pathlib.Path(tempfile.mkdtemp(prefix="whole-field-"))
    _write(ai / "epics" / "epic.alpha.json", {"epic": {
        "id": "epic.alpha", "owner": "bdo", "arc": "a", "value": "a",
        "horizon": "a",
        "pieces": [{"atom": "atom.a.v0", "glue": "g"},
                   {"atom": "atom.a-unbuilt.v0", "glue": "g"}],
    }})
    _write(ai / "epics" / "epic.beta.json", {"epic": {
        "id": "epic.beta", "owner": "bdo", "arc": "b", "value": "b",
        "horizon": "b", "pieces": [{"atom": "atom.b-unbuilt.v0", "glue": "g"}],
    }})
    ap = ai / "atoms" / "atom.a.v0.json"
    _write(ap, _atom("atom.a.v0", "epic.alpha"))
    ahash = "sha256:" + hashlib.sha256(ap.read_bytes()).hexdigest()
    _lines(ai / "log" / "admissions.jsonl", [
        {"id": "adm.conf", "type": "arc_confirmed", "epic": "epic.alpha",
         "by": "bdo", "enabled": True, "ts": "t"},
    ])
    _lines(ai / "log" / "events.jsonl", [
        {"id": "ev.seed", "type": "atom.created", "atom_id": "atom.a.v0",
         "artifact_hash": ahash, "from_node": "x", "ts": "t"},
    ])
    _lines(ai / "log" / "receipts.jsonl", [
        {"id": "rcp.a", "node": "value-gate.mock.v0", "artifact_hash": ahash,
         "verdict": "accept", "reason": "t",
         "next_suggested_event": "value.accepted", "ts": "t"},
    ])
    return ai


class CompositionPreservesAltitude(unittest.TestCase):
    def test_every_arc_composes_into_one_graph_keeping_its_full_ladder(self):
        ai = _two_epic_root()
        self.addCleanup(shutil.rmtree, ai, ignore_errors=True)
        whole = whole_field(ai)
        # both arcs present in one graph
        self.assertEqual(set(whole["arcs"]), {"epic.alpha", "epic.beta"})
        # altitude preserved: each arc keeps all seven rungs (not flattened)
        for eid, ladder in whole["arcs"].items():
            self.assertIsNotNone(ladder)
            self.assertEqual(tuple(r["rung"] for r in ladder["rungs"]), RUNGS)

    def test_agenda_rung_names_each_arc_with_its_confirm_state(self):
        ai = _two_epic_root()
        self.addCleanup(shutil.rmtree, ai, ignore_errors=True)
        agenda = {it["subject"]: it for it in whole_field(ai)["agenda"]}
        self.assertEqual(agenda["epic.alpha"]["state"], "confirmed")
        self.assertEqual(agenda["epic.alpha"]["evidence"], ["adm.conf"])
        self.assertEqual(agenda["epic.beta"]["state"], "unconfirmed")


class HolographicRuleHasTeeth(unittest.TestCase):
    def test_a_clean_whole_field_has_no_route_violations(self):
        ai = _two_epic_root()
        self.addCleanup(shutil.rmtree, ai, ignore_errors=True)
        whole = whole_field(ai)
        known = _known_ids(ai, Fold(ai))
        self.assertEqual(route_audit(whole, known), [])

    def test_a_routeless_node_asserted_as_fact_is_caught(self):
        # a ghost: a non-gap state, no evidence, subject resolves to nothing
        ghost = {"agenda": [{"subject": "phantom.node",
                             "state": "settled (pipeline: confirmed)",
                             "evidence": [], "next_safe_move": "m"}],
                 "arcs": {}}
        self.assertEqual(len(route_audit(ghost, set())), 1)

    def test_an_honest_absence_is_a_surfaced_gap_not_a_violation(self):
        # the bug this done-line had to fix: an `absent` piece points
        # nowhere by design and must NOT read as a ghost
        gap = {"agenda": [{"subject": "atom.unbuilt.v0", "state": "absent",
                           "evidence": [], "next_safe_move": "m"}],
               "arcs": {}}
        self.assertEqual(route_audit(gap, set()), [])

    def test_known_ids_resolve_a_subject_without_evidence(self):
        # a node whose subject is a real on-disk id carries its own route
        ai = _two_epic_root()
        self.addCleanup(shutil.rmtree, ai, ignore_errors=True)
        known = _known_ids(ai, Fold(ai))
        self.assertIn("epic.alpha", known)
        self.assertIn("atom.a.v0", known)
        carried = {"agenda": [{"subject": "epic.alpha", "state": "settled",
                               "evidence": [], "next_safe_move": "m"}],
                   "arcs": {}}
        self.assertEqual(route_audit(carried, known), [])


class ProjectionCannotDrift(unittest.TestCase):
    def test_the_whole_field_folds_byte_for_byte_the_same(self):
        ai = _two_epic_root()
        self.addCleanup(shutil.rmtree, ai, ignore_errors=True)
        a = json.dumps(whole_field(ai), sort_keys=True).encode("utf-8")
        b = json.dumps(whole_field(ai), sort_keys=True).encode("utf-8")
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()

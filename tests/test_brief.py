"""Tests for the bdo-brief node (done-line 0104) — the §10 teeth of the surface
that packages owner-bound work as an inference construct instead of a ticket.

The teeth are the point. A discharged ask must NOT surface (the loop drops what
is settled, and a confirmed arc's piece is the loop's to carry, not his). A
recommendation that cites nothing resolvable must be refused as grounded — a
*fabricated* citation that looks like evidence is exactly what a check doing its
job catches. And the over-bulk surface must FOLD: several pieces under one arc
collapse to one group, never a 1:1 echo. A version that surfaced a settled item,
trusted an uncited recommendation, or echoed one row per piece would be doing
nothing."""

import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import brief


class StubFold:
    """Enough of a Fold for the pure functions: the two log slices they read."""
    def __init__(self, receipts=(), admissions=()):
        self.receipts = list(receipts)
        self.admissions = list(admissions)


def atom(aid, serves=()):
    return {"id": aid, "incidence": {"serves": list(serves)},
            "story": {"text": f"story for {aid}"}, "briefing": {}}


class DischargedDoesNotSurface(unittest.TestCase):
    def test_only_owner_items_kept(self):
        human = "owner-stamp.bdo.v1"
        actions = [
            (atom("a.settled"), "h1", None),                   # discharged
            (atom("a.mine"), "h2", ("await", human)),          # on bdo
            (atom("a.other"), "h3", ("await", "value-gate")),  # another node's
            (atom("a.parked"), "h4", ("parked", None)),        # bdo's to amend
            (atom("a.loop"), "h5", ("judge", human)),          # confirmed-arc piece
        ]
        kept = brief.classify_owner_items(actions, human)
        ids = {a["id"] for a, _, _ in kept}
        self.assertEqual(ids, {"a.mine", "a.parked"})
        # the teeth: a settled item is gone, and a loop-owned `judge` step
        # (a confirmed arc's piece) never lands on him
        self.assertNotIn("a.settled", ids)
        self.assertNotIn("a.loop", ids)
        self.assertNotIn("a.other", ids)


class UncitedIsRefused(unittest.TestCase):
    def test_fabricated_citation_is_caught(self):
        fold = StubFold(receipts=[{"id": "rcp.real"}])
        epics = [{"id": "epic.x"}]
        atom_ids = {"atom.y"}
        # looks grounded — has a cite — but it points at nothing on the log
        ghost = {"text": "stamp it", "reasoning": "trust me", "cites": ["rcp.nope"]}
        self.assertTrue(brief.uncited(ghost, fold, epics, atom_ids))
        # real records resolve, by each kind of citation
        self.assertFalse(brief.uncited({"cites": ["rcp.real"]}, fold, epics, atom_ids))
        self.assertFalse(brief.uncited({"cites": ["epic.x"]}, fold, epics, atom_ids))
        self.assertFalse(brief.uncited({"cites": ["atom:atom.y"]}, fold, epics, atom_ids))
        # an empty citation list is uncited too — no evidence, no mint
        self.assertTrue(brief.uncited({"cites": []}, fold, epics, atom_ids))


class DigestAggregates(unittest.TestCase):
    def test_pieces_under_one_arc_fold_to_one_group(self):
        epics = [{"id": "epic.a", "value": "A"}, {"id": "epic.b", "value": "B"}]
        items = [
            {"id": "a1", "atom": atom("a1", ["epic.a"])},
            {"id": "a2", "atom": atom("a2", ["epic.a"])},
            {"id": "a3", "atom": atom("a3", ["epic.a"])},
            {"id": "b1", "atom": atom("b1", ["epic.b"])},
            {"id": "u1", "atom": atom("u1", [])},  # unfiled
        ]
        groups = brief.group_by_arc(items, epics)
        by_id = {gid: its for gid, _, its in groups}
        # three pieces under epic.a collapse to ONE group — not three top rows
        self.assertEqual(len(by_id["epic.a"]), 3)
        self.assertEqual(len(by_id["epic.b"]), 1)
        # five items fold to three groups (aggregation, not a 1:1 echo)
        self.assertEqual(len(groups), 3)
        # the unfiled group sorts last
        self.assertEqual(groups[-1][0], brief.UNFILED)


class RecommendationFromRecords(unittest.TestCase):
    def test_refused_piece_recommends_hold_not_stamp(self):
        fold = StubFold(receipts=[{
            "id": "rcp.held", "artifact_hash": "h",
            "node": "value-confirm.claude.v1", "verdict": "missed",
            "reason": "the build never happened", "next_suggested_event": None,
        }])
        epics = [{"id": "epic.x"}]
        rec = brief.recommendation_for(atom("atom.z", ["epic.x"]), "h", fold, epics)
        self.assertTrue(rec["text"].startswith("hold"))
        self.assertNotIn("confirm the arc", rec["text"])  # a refusal is not a stamp
        self.assertEqual(rec["cites"], ["rcp.held"])
        self.assertFalse(brief.uncited(rec, fold, epics, {"atom.z"}))

    def test_accepted_under_unconfirmed_arc_recommends_confirm(self):
        fold = StubFold(receipts=[{
            "id": "rcp.acc", "artifact_hash": "h", "node": "value-gate.claude.v1",
            "verdict": "accept", "reason": "value is sound",
        }])  # no arc_confirmed admission → the arc is unconfirmed
        epics = [{"id": "epic.x"}]
        rec = brief.recommendation_for(atom("atom.z", ["epic.x"]), "h", fold, epics)
        self.assertIn("confirm the arc", rec["text"])
        self.assertIn("epic.x", rec["cites"])
        self.assertIn("rcp.acc", rec["cites"])
        self.assertFalse(brief.uncited(rec, fold, epics, {"atom.z"}))

    def test_confirmed_arc_piece_is_not_recommended_for_confirm(self):
        # if the arc is already confirmed, the confirm recommendation must not
        # fire — that would re-offer a gesture he already made
        fold = StubFold(
            receipts=[{"id": "rcp.acc", "artifact_hash": "h",
                       "node": "value-gate.claude.v1", "verdict": "accept",
                       "reason": "sound"}],
            admissions=[{"type": "arc_confirmed", "epic": "epic.x", "enabled": True}],
        )
        epics = [{"id": "epic.x"}]
        rec = brief.recommendation_for(atom("atom.z", ["epic.x"]), "h", fold, epics)
        self.assertNotIn("confirm the arc", rec["text"])


if __name__ == "__main__":
    unittest.main()

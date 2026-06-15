#!/usr/bin/env python3
"""§10 test for Impact as settling (done-line 0081) — the first assay pan.

The teeth, each from the done-line's bar:

  1. settling tracks the field — a heavier subject settles above a lighter one
     (a constant / fabricated weigher would fail this);
  2. a surfaced gap with no record reads UNMEASURED, never weight-zero tailings
     (absence is not lightness); a gap that DOES carry records is in the pan;
  3. a flat field (floor == ceiling) cannot calibrate a position — settled is
     None, and nothing divides;
  4. calibration is RELATIVE to the population — adding a heavier subject shifts
     the others' settled positions (a position between anchors, not an absolute);
  5. BLACK SAND — a subject that settled by a single signal is flagged, not
     silently ranked as gold; a subject heavy in both signals is not flagged;
  6. an empty field weighs nothing (absence, not a crash);
  7. over the repo's own whole field the fold weighs real, routed subjects.
"""

import unittest
from pathlib import Path

from loop.impact import impact, settle, weigh

REPO_ROOT = Path(__file__).resolve().parent.parent / ".ai-native"


def _story(arc_items):
    """A minimal whole-field: one story rung per arc, no agenda."""
    return {"agenda": [],
            "arcs": {eid: {"rungs": [{"rung": "story", "items": items}]}
                     for eid, items in arc_items.items()}}


def _item(subject, evidence=(), state="settled", why=None):
    it = {"subject": subject, "state": state, "evidence": list(evidence)}
    if why:
        it["why"] = why
    return it


class SettlingTracksTheField(unittest.TestCase):
    """Weight follows the records, not a constant (teeth 1)."""

    def test_heavier_subject_settles_above_lighter(self):
        whole = _story({"epic.a": [
            _item("heavy", ["r1", "r2", "r3"]),
            _item("light", []),
        ]})
        r = settle(whole)
        self.assertEqual(r["concentrate"][0]["subject"], "heavy")
        self.assertIn("light", [t["subject"] for t in r["tailings"]])

    def test_weight_is_evidence_plus_reach_not_a_constant(self):
        whole = _story({"epic.a": [_item("x", ["r1", "r2"])]})
        s = weigh(whole)
        self.assertEqual(len(s["x"]["evidence"]), 2)
        self.assertEqual(s["x"]["arcs"], {"epic.a"})


class GapIsUnmeasuredNotLight(unittest.TestCase):
    """A hole is not light material (teeth 2)."""

    def test_evidenceless_gap_is_unmeasured(self):
        whole = _story({"epic.a": [
            _item("hole", [], state="MOCK (seam value)"),
            _item("real", ["r1"]),
        ]})
        r = settle(whole)
        self.assertIn("hole", [u["subject"] for u in r["unmeasured"]])
        self.assertNotIn("hole", [x["subject"] for x in r["rows"]])

    def test_gap_with_records_is_still_in_the_pan(self):
        # an UN-AUTHORISED occupant carries a `why` (a gap) AND evidence — it is
        # real material, weighable, not a hole.
        whole = _story({"epic.a": [
            _item("ghostnode", ["e1", "e2"], state="UN-AUTHORISED",
                  why="self-asserted identity"),
        ]})
        r = settle(whole)
        self.assertIn("ghostnode", [x["subject"] for x in r["rows"]])
        self.assertEqual(r["unmeasured"], [])


class FlatFieldCannotCalibrate(unittest.TestCase):
    """No spread, no position — and never a divide (teeth 3)."""

    def test_single_subject_is_flat_settled_none(self):
        whole = _story({"epic.a": [_item("only", ["r1"])]})
        r = settle(whole)
        self.assertTrue(r["flat"])
        self.assertIsNone(r["rows"][0]["settled"])

    def test_uniform_weights_are_flat(self):
        whole = _story({"epic.a": [_item("a", ["r1"]), _item("b", ["r2"])]})
        r = settle(whole)  # both weight 2 (1 evidence + 1 reach)
        self.assertTrue(r["flat"])
        for row in r["rows"]:
            self.assertIsNone(row["settled"])


class CalibrationIsRelative(unittest.TestCase):
    """A settled position is between the population's own anchors (teeth 4)."""

    def test_adding_a_heavier_subject_shifts_the_others(self):
        small = settle(_story({"epic.a": [
            _item("A", ["r1", "r2"]), _item("B", [])]}))
        pos_a_small = next(r["settled"] for r in small["rows"]
                           if r["subject"] == "A")
        big = settle(_story({"epic.a": [
            _item("A", ["r1", "r2"]), _item("B", []),
            _item("C", ["c1", "c2", "c3", "c4", "c5"])]}))
        pos_a_big = next(r["settled"] for r in big["rows"]
                         if r["subject"] == "A")
        self.assertEqual(pos_a_small, 1.0)        # A was the ceiling
        self.assertLess(pos_a_big, 1.0)           # C raised the ceiling past A
        self.assertNotEqual(pos_a_small, pos_a_big)


class BlackSand(unittest.TestCase):
    """A single-signal settler is named, not passed off as gold (teeth 5)."""

    def _field(self):
        # sand: heavy in evidence only (reach 1). gold: heavy in BOTH (reach 2).
        # base: floor on both. (gold spans two arcs -> reach 2.)
        return {"agenda": [],
                "arcs": {
                    "epic.a": {"rungs": [{"rung": "story", "items": [
                        _item("sand", ["r1", "r2", "r3"]),
                        _item("gold", ["g1", "g2", "g3"]),
                        _item("base", []),
                    ]}]},
                    "epic.b": {"rungs": [{"rung": "story", "items": [
                        _item("gold", ["g4"]),
                    ]}]}}}

    def test_single_signal_settler_is_black_sand(self):
        r = settle(self._field())
        bs = [x["subject"] for x in r["black_sand"]]
        self.assertIn("sand", bs)

    def test_two_signal_settler_is_not_black_sand(self):
        r = settle(self._field())
        bs = [x["subject"] for x in r["black_sand"]]
        self.assertNotIn("gold", bs)
        # and gold, heavy in both, is the heaviest settler
        self.assertEqual(r["concentrate"][0]["subject"], "gold")

    def test_black_sand_is_still_in_the_concentrate_just_flagged(self):
        r = settle(self._field())
        conc = [x["subject"] for x in r["concentrate"]]
        self.assertIn("sand", conc)  # it settled; it is just not trusted as gold


class EmptyField(unittest.TestCase):
    """The pan weighs what is there (teeth 6)."""

    def test_empty_field_weighs_nothing(self):
        r = settle({"agenda": [], "arcs": {}})
        self.assertEqual(r["weighed"], 0)
        self.assertEqual(r["concentrate"], [])
        self.assertIsNone(r["floor"])

    def test_none_ladder_is_skipped(self):
        r = settle({"agenda": [], "arcs": {"epic.x": None}})
        self.assertEqual(r["weighed"], 0)


class RealWholeField(unittest.TestCase):
    """Over the repo's own field the pan weighs real, routed subjects (teeth
    7): every weighed subject is a non-empty id, the concentrate is non-empty,
    and the invariants hold on real data, not a fixture."""

    def test_pan_runs_over_the_real_field(self):
        r = impact(root=REPO_ROOT)
        self.assertGreater(r["weighed"], 0)
        self.assertTrue(r["concentrate"])
        for row in r["rows"]:
            self.assertIsInstance(row["subject"], str)
            self.assertTrue(row["subject"])
            self.assertEqual(row["weight"], row["evidence_mass"] + row["reach"])
        # consistency: every black-sand row is a settled (concentrate) row
        conc = {x["subject"] for x in r["concentrate"]}
        for x in r["black_sand"]:
            self.assertIn(x["subject"], conc)
        # every unmeasured subject is a genuine hole (named why)
        for u in r["unmeasured"]:
            self.assertTrue(u.get("why"))
        if not r["flat"]:
            self.assertLessEqual(r["floor"], r["ceiling"])


if __name__ == "__main__":
    unittest.main()

"""Tests for the bounded-run fold against done-line 0087: cited evidence becomes
a person's world as PROPOSED bounded-run candidates, clustered by locality, with
the declared-input slots (purpose/anima/control_surface) left unset and any
ghost-only locality refused.

The teeth: (1) a real multi-directory corpus yields >=2 proposed candidates each
backed by resolvable evidence; (2) the purpose/anima/control_surface slots are
unset on every candidate — the fold never tells the person who they are; (3) a
locality whose evidence are all ghosts is refused, not emitted as a candidate."""

import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from causality import cited_sensor
from causality.bounded_run_fold import DECLARED_SLOTS, fold


class BoundedRunFoldTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / "games").mkdir()
        (self.root / "games" / "MyGame-Setup.txt").write_text(
            "GameInstaller v3.2\n", encoding="utf-8")
        (self.root / "games" / "save.dat").write_text("slot1\n", encoding="utf-8")
        (self.root / "company").mkdir()
        (self.root / "company" / "invoice.csv").write_text(
            "date,amount\n2026-06-15,42.00\n", encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    # --- the happy fold ---------------------------------------------------

    def test_clusters_localities_into_proposed_bounds(self):
        candidates, refused = fold(self.root)
        by_id = {c["id"]: c for c in candidates}
        self.assertEqual(set(by_id), {"bound/games", "bound/company"})
        self.assertEqual(refused, [])
        self.assertEqual(by_id["bound/games"]["members"], 2)
        self.assertEqual(by_id["bound/company"]["members"], 1)

    def test_every_candidate_is_proposed_not_minted(self):
        candidates, _ = fold(self.root)
        self.assertTrue(candidates)
        for c in candidates:
            self.assertEqual(c["status"], "proposed")

    def test_declared_slots_are_present_but_unset(self):
        """The §10 'never tells you who you are' check: purpose/anima/
        control_surface exist on every candidate but the fold leaves them None
        — they are the person's to declare (D-4), never inferred."""
        candidates, _ = fold(self.root)
        for c in candidates:
            for slot in DECLARED_SLOTS:
                self.assertIn(slot, c)
                self.assertIsNone(c[slot])

    def test_candidate_evidence_all_resolve(self):
        candidates, _ = fold(self.root)
        for c in candidates:
            for ev in c["evidence"]:
                self.assertFalse(cited_sensor.is_ghost(self.root, ev))

    # --- the teeth: a ghost-only locality is refused ----------------------

    def test_ghost_only_locality_is_refused(self):
        # a real 'games' record plus a 'phantom' locality whose only evidence
        # cites a path that does not exist — the phantom bound must be refused
        real = {"file": "games/MyGame-Setup.txt", "stratum": "file",
                "kind": "txt", "size": 19, "contains": "GameInstaller v3.2"}
        phantom = {"file": "phantom/ghost.exe", "stratum": "file",
                   "kind": "exe", "size": 99, "contains": "nope"}
        candidates, refused = fold(self.root, evidence=[real, phantom])
        ids = {c["id"] for c in candidates}
        self.assertEqual(ids, {"bound/games"})
        self.assertEqual([r["locality"] for r in refused], ["phantom"])

    def test_empty_surface_folds_to_nothing(self):
        empty = Path(self._tmp.name) / "empty"
        empty.mkdir()
        candidates, refused = fold(empty)
        self.assertEqual(candidates, [])
        self.assertEqual(refused, [])


if __name__ == "__main__":
    unittest.main()

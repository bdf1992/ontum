"""Tests for the loop-maker against done-line 0084: the Plan seam of the loop's
MAPE-K cycle derives the next increment for an epic from current state, braided
to prior loops through the on-disk done-line ties (the log/records as K).

The §10 teeth: a locally-fine call must *refuse to fabricate* a next step when
state says there is none. (1) a partial fixture yields the expected next piece;
(2) a fully-tied fixture returns Stop("converged") rather than inventing a
piece; (3) the braid — adding a tie for the current piece advances a re-run to
the following piece, proving the connection is the disk fold and not memory;
plus (4) a blocked next piece returns Stop("stuck") and (5) an unknown arc
returns Stop("no-epic")."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import loopmaker
from loop.loopmaker import Increment, Stop, next_increment


class LoopMakerTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / ".ai-native"
        (self.root / "epics").mkdir(parents=True)
        (self.root / "done").mkdir(parents=True)

    def tearDown(self):
        self._tmp.cleanup()

    # --- fixtures ---------------------------------------------------------

    def _epic(self, pieces, epic_id="epic.test"):
        body = {"epic": {"id": epic_id, "owner": "test", "pieces": pieces}}
        (self.root / "epics" / f"{epic_id}.json").write_text(
            json.dumps(body), encoding="utf-8")

    def _piece(self, atom, glue="glue.", depends=None):
        p = {"atom": atom, "status": "test", "glue": glue}
        if depends is not None:
            p["depends"] = depends
        return p

    def _land(self, idnum, slug, piece_atom):
        """Write a landed done-line carrying the `> **Piece:**` tie — the braid
        surface the next derivation folds over."""
        (self.root / "done" / f"{idnum:04d}-{slug}.md").write_text(
            f"# Done-line {idnum:04d} — {slug}\n\n"
            f"> **Piece:** {piece_atom}\n\n"
            f"> **Done when:** the test bar is met.\n",
            encoding="utf-8")

    # --- teeth ------------------------------------------------------------

    def test_partial_yields_next_unlanded_piece(self):
        self._epic([self._piece("atom.alpha.v0"),
                    self._piece("atom.beta.v0"),
                    self._piece("atom.gamma.v0")])
        self._land(1, "alpha", "atom.alpha.v0")
        result = next_increment("epic.test", root=self.root)
        self.assertIsInstance(result, Increment)
        self.assertEqual(result.atom, "atom.beta.v0")
        self.assertEqual(result.slug, "beta")
        self.assertEqual(result.title, "Beta")

    def test_converged_refuses_to_fabricate_a_next_step(self):
        """The §10 refusal: every piece landed → Stop, never a made-up piece."""
        self._epic([self._piece("atom.alpha.v0"),
                    self._piece("atom.beta.v0")])
        self._land(1, "alpha", "atom.alpha.v0")
        self._land(2, "beta", "atom.beta.v0")
        result = next_increment("epic.test", root=self.root)
        self.assertIsInstance(result, Stop)
        self.assertEqual(result.reason, "converged")

    def test_braid_is_via_disk_not_memory(self):
        """Adding a tie on disk between two calls must change the derivation —
        proof the loop folds the records, not session state."""
        self._epic([self._piece("atom.alpha.v0"),
                    self._piece("atom.beta.v0"),
                    self._piece("atom.gamma.v0")])
        self._land(1, "alpha", "atom.alpha.v0")
        first = next_increment("epic.test", root=self.root)
        self.assertEqual(first.atom, "atom.beta.v0")
        # loop N+1: beta's done-line lands, tying it back
        self._land(2, "beta", "atom.beta.v0")
        second = next_increment("epic.test", root=self.root)
        self.assertIsInstance(second, Increment)
        self.assertEqual(second.atom, "atom.gamma.v0")

    def test_stuck_on_unmet_dependency(self):
        """A blocked next piece halts the loop rather than skipping ahead."""
        self._epic([self._piece("atom.alpha.v0"),
                    self._piece("atom.beta.v0", depends=["atom.zeta.v0"])])
        self._land(1, "alpha", "atom.alpha.v0")
        result = next_increment("epic.test", root=self.root)
        self.assertIsInstance(result, Stop)
        self.assertEqual(result.reason, "stuck")
        self.assertIn("atom.zeta.v0", result.detail)

    def test_unknown_epic_stops_cleanly(self):
        result = next_increment("epic.nope", root=self.root)
        self.assertIsInstance(result, Stop)
        self.assertEqual(result.reason, "no-epic")

    # --- the fold itself --------------------------------------------------

    def test_landed_pieces_reads_ties_across_files(self):
        self._land(1, "alpha", "atom.alpha.v0")
        self._land(2, "beta", "atom.beta.v0")
        self.assertEqual(loopmaker.landed_pieces(self.root),
                         {"atom.alpha.v0", "atom.beta.v0"})

    def test_no_pieces_landed_returns_first(self):
        self._epic([self._piece("atom.alpha.v0"),
                    self._piece("atom.beta.v0")])
        result = next_increment("epic.test", root=self.root)
        self.assertIsInstance(result, Increment)
        self.assertEqual(result.atom, "atom.alpha.v0")

    def test_slug_derivation_strips_atom_prefix_and_version(self):
        self.assertEqual(loopmaker._slug_of("atom.cited-sensor.v0"),
                         "cited-sensor")
        self.assertEqual(loopmaker._title_of("atom.cited-sensor.v0"),
                         "Cited sensor")


if __name__ == "__main__":
    unittest.main()

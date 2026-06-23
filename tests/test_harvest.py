"""Tests for harvest against done-line 0094: a stopping point becomes a harvest —
recorded teeth-signals sorted by generativity into grain (consumed) and seed
(banked proposed), and never planted.

The teeth: (1) a recurring-kind signal is banked as seed and reads `proposed`
(a generative shape is not consumed as mere grain — seed not eaten); (2) a
one-off signal is grain, NOT banked (no noise in the bank); (3) harvest NEVER
plants — every banked seed stays `proposed`; (4) an empty field harvests to
nothing."""

import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import seedbank, signals
from loop.harvest import harvest


class HarvestTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / ".ai-native"
        (self.root / "log").mkdir(parents=True)

    def tearDown(self):
        self._tmp.cleanup()

    def _signal(self, kind, subject, why="because"):
        signals.mark(self.root, kind, subject, why)

    def test_recurring_kind_is_banked_as_seed(self):
        # two cited-ghosts on distinct subjects -> a recurring shape
        self._signal("cited-ghost", "a.exe")
        self._signal("cited-ghost", "b.exe")
        h = harvest("epic.test", self.root, by="harvest")
        self.assertIn("cited-ghost", h["seed"])
        # and it reads proposed in the bank, never eaten as grain
        state = {s["slug"]: s for s in seedbank.seeds(self.root)}
        self.assertIn("cited-ghost", state)
        self.assertEqual(state["cited-ghost"]["state"], "proposed")
        self.assertNotIn("cited-ghost", [g["kind"] for g in h["grain"]])

    def test_one_off_is_grain_not_seed(self):
        self._signal("loop-stop:converged", "epic.test", "all landed")
        h = harvest("epic.test", self.root, by="harvest")
        self.assertEqual([g["kind"] for g in h["grain"]], ["loop-stop:converged"])
        self.assertEqual(h["seed"], [])
        # nothing banked
        self.assertEqual(seedbank.seeds(self.root), [])

    def test_harvest_never_plants(self):
        self._signal("gate-block:irreversible", "delete")
        self._signal("gate-block:irreversible", "send")
        h = harvest("epic.test", self.root, by="harvest")
        self.assertEqual(h["planted"], [])
        # every banked seed is proposed, none planted
        for s in seedbank.seeds(self.root):
            self.assertEqual(s["state"], "proposed")

    def test_empty_field_harvests_to_nothing(self):
        h = harvest("epic.test", self.root, by="harvest")
        self.assertEqual(h, {"grain": [], "seed": [], "planted": []})

    def test_banked_seed_then_planted_by_other_hand(self):
        # the full lifecycle: harvest banks (proposed), a deliberate hand plants
        self._signal("cited-ghost", "a.exe")
        self._signal("cited-ghost", "b.exe")
        harvest("epic.test", self.root, by="harvest")
        seedbank.plant(self.root, "cited-ghost", by="bdo")
        state = {s["slug"]: s for s in seedbank.seeds(self.root)}
        self.assertEqual(state["cited-ghost"]["state"], "planted")
        self.assertEqual(state["cited-ghost"]["planted_by"], "bdo")


if __name__ == "__main__":
    unittest.main()

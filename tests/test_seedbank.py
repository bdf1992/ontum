"""Tests for the seed bank against done-line 0093: harvested shapes are banked as
PROPOSED patterns and planted only by a deliberate, separate hand (D-4).

The teeth: (1) a banked seed reads `proposed`; (2) a different hand plants it →
`planted`; (3) planting is refused unsigned (not automatic), unbanked (never
planted what was never banked), and by the proposer (no one plants their own
seed); (4) the fold is idempotent — re-banking a slug folds to one."""

import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import seedbank
from loop.seedbank import SeedRefused, bank, plant, seeds


class SeedBankTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / ".ai-native"
        (self.root / "log").mkdir(parents=True)

    def tearDown(self):
        self._tmp.cleanup()

    def test_banked_seed_reads_proposed(self):
        bank(self.root, "absence-refusal",
             "refuse on absence — the refusal is the signal",
             provenance="loops 1-4", by="claude")
        state = seeds(self.root)
        self.assertEqual(len(state), 1)
        self.assertEqual(state[0]["slug"], "absence-refusal")
        self.assertEqual(state[0]["state"], "proposed")
        self.assertEqual(state[0]["proposed_by"], "claude")

    def test_a_different_hand_plants_it(self):
        bank(self.root, "absence-refusal", "shape", by="claude")
        plant(self.root, "absence-refusal", by="bdo")
        state = {s["slug"]: s for s in seeds(self.root)}
        self.assertEqual(state["absence-refusal"]["state"], "planted")
        self.assertEqual(state["absence-refusal"]["planted_by"], "bdo")

    # --- the teeth: planting refused three ways ---------------------------

    def test_unsigned_plant_is_refused(self):
        bank(self.root, "s", "shape", by="claude")
        with self.assertRaises(SeedRefused):
            plant(self.root, "s", by="")

    def test_unbanked_plant_is_refused(self):
        with self.assertRaises(SeedRefused):
            plant(self.root, "never-banked", by="bdo")

    def test_self_plant_is_refused(self):
        bank(self.root, "s", "shape", by="claude")
        with self.assertRaises(SeedRefused) as cm:
            plant(self.root, "s", by="claude")
        self.assertIn("own seed", str(cm.exception))
        # and it stays proposed
        self.assertEqual(seeds(self.root)[0]["state"], "proposed")

    def test_bank_refuses_unslugged_or_unsigned(self):
        with self.assertRaises(SeedRefused):
            bank(self.root, "", "shape", by="claude")
        with self.assertRaises(SeedRefused):
            bank(self.root, "s", "shape", by="")

    # --- idempotent fold --------------------------------------------------

    def test_rebank_folds_to_one(self):
        bank(self.root, "s", "shape v1", by="claude")
        bank(self.root, "s", "shape v2", by="claude")
        state = seeds(self.root)
        self.assertEqual(len(state), 1)
        self.assertEqual(state[0]["shape"], "shape v2")  # latest wins

    def test_empty_bank_folds_to_nothing(self):
        self.assertEqual(seeds(self.root), [])


if __name__ == "__main__":
    unittest.main()

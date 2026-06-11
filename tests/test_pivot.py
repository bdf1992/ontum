"""Pivot instrument tests (done-line 0031).

The test that matters (§10): a recovery can be locally plausible — every
word in a believable cell — and still refuse to fit, because together the
placements do not tile the cube. The grader must notice, not score it fine.
"""
import unittest

from glyphs.knoll import ternary_cells, cell_kind
from pivot import instrument as ins


class TestContainer(unittest.TestCase):
    def test_incidence_laws_hold(self):
        laws = ins.verify_container()  # raises SystemExit on drift
        self.assertEqual(laws["status"], "DERIVED")

    def test_reference_frame_census(self):
        frame = ins.reference_frame()
        self.assertEqual(len(frame), 27)
        census = {}
        for kind in frame.values():
            census[kind] = census.get(kind, 0) + 1
        self.assertEqual(census, ins.LAWFUL_CENSUS)

    def test_chance_floor(self):
        # Σ n_k² / 27² = (64+144+36+1)/729
        self.assertAlmostEqual(ins.chance_kind_match(), 245 / 729)


class TestPopulations(unittest.TestCase):
    def test_each_population_is_a_lawful_tiling(self):
        for name, build in ins.POPULATIONS.items():
            pop = build()
            self.assertEqual(len(pop), 27, name)
            # the truth placements themselves must tile the cube
            ins.assert_lawful_tiling(pop)

    def test_surface_truth_is_transparent(self):
        # the ceiling token encodes its own coord — the cube's Pilish analog
        pop = ins.surface_population()
        self.assertEqual(pop["x-neg_y-zero_z-pos"], (-1, 0, 1))
        self.assertEqual(pop["x-zero_y-zero_z-zero"], (0, 0, 0))


class TestGrader(unittest.TestCase):
    def setUp(self):
        self.truth = ins.surface_population()

    def test_perfect_recovery_scores_one(self):
        score = ins.grade(dict(self.truth), self.truth)
        self.assertEqual(score["kind_match"], 1.0)
        self.assertEqual(score["exact_match"], 1.0)

    def test_kind_match_ignores_axis_symmetry(self):
        # swap two corners: exact drops, but both are corners so kind holds
        rec = dict(self.truth)
        a, b = (-1, -1, -1), (1, 1, 1)
        wa = next(w for w, c in self.truth.items() if c == a)
        wb = next(w for w, c in self.truth.items() if c == b)
        rec[wa], rec[wb] = b, a
        score = ins.grade(rec, self.truth)
        self.assertEqual(score["kind_match"], 1.0)      # corner<->corner
        self.assertLess(score["exact_match"], 1.0)      # but positions moved

    def test_refuses_a_collision(self):
        # §10: each word sits in a believable cell, but two claim one cell —
        # the placement refuses to fit, and the gate notices.
        rec = dict(self.truth)
        victim = next(w for w, c in self.truth.items() if c == (0, 0, 0))
        rec[victim] = (1, 1, 1)  # now two occupants at (1,1,1), center empty
        with self.assertRaises(ins.RefusedToFit):
            ins.grade(rec, self.truth)

    def test_refuses_a_non_cell(self):
        rec = dict(self.truth)
        victim = next(iter(rec))
        rec[victim] = (2, 0, 0)  # off the lattice
        with self.assertRaises(ins.RefusedToFit):
            ins.grade(rec, self.truth)

    def test_refuses_mismatched_occupants(self):
        rec = dict(self.truth)
        rec["a-word-not-in-the-set"] = rec.pop(next(iter(rec)))
        with self.assertRaises(ins.RefusedToFit):
            ins.grade(rec, self.truth)


class TestPrompt(unittest.TestCase):
    def test_question_withholds_the_truth(self):
        truth = ins.s_frame_population()
        prompt = ins.recovery_prompt(sorted(truth))
        # every occupant is named (they are the question)...
        for word in truth:
            self.assertIn(word, prompt)
        # ...but no occupant's coord is paired to it, and no rationale leaks.
        for word, coord in truth.items():
            self.assertNotIn("%s: %s" % (word, list(coord)), prompt)
        self.assertNotIn("predicted pivot", prompt)   # an s-frame rationale
        self.assertNotIn("rationale", prompt.lower())


if __name__ == "__main__":
    unittest.main()

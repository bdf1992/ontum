"""Measurement-battery tests (done-line 0031, the inverted measurement).

Each case plants a *known* tension and checks the battery reads it back:
identical (no tension), the same cube rotated (convention slack), a
kind-preserving swap (orientation slack), and disjoint vocabularies.
"""
import unittest

from glyphs.knoll import cell_kind, ternary_cells
from pivot import instrument as ins
from pivot import measure as m


class TestSymmetries(unittest.TestCase):
    def test_there_are_48_and_all_preserve_kind(self):
        syms = m.cube_symmetries()
        self.assertEqual(len(syms), 48)
        for c in ternary_cells():
            for s in syms:
                img = m.apply_symmetry(c, s)
                self.assertIn(img, set(ternary_cells()))
                self.assertEqual(cell_kind(img), cell_kind(c))


class TestBattery(unittest.TestCase):
    def setUp(self):
        self.base = ins.surface_population()  # a lawful tiling, term -> coord

    def test_identical_has_no_tension(self):
        b = m.measure([self.base, dict(self.base)])
        self.assertEqual(b["placement"]["exact"], 1.0)
        self.assertEqual(b["placement"]["kind"], 1.0)
        self.assertEqual(b["pairwise"]["raw"], 1.0)
        self.assertEqual(b["tensions"]["orientation_slack"], 0.0)
        self.assertEqual(b["tensions"]["convention_slack"], 0.0)
        self.assertTrue(all(v == 1.0 for v in b["per_grade"].values()))

    def test_same_cube_rotated_is_convention_slack(self):
        # apply a real symmetry: the two cubes are identical up to rotation
        sym = ((1, 0, 2), (1, 1, 1))  # swap the x and y axes
        rotated = {t: m.apply_symmetry(c, sym) for t, c in self.base.items()}
        b = m.measure([self.base, rotated])
        self.assertLess(b["pairwise"]["raw"], 1.0)          # raw disagrees
        self.assertEqual(b["pairwise"]["best_aligned"], 1.0)  # ...but it's a rotation
        self.assertGreater(b["tensions"]["convention_slack"], 0.0)

    def test_kind_preserving_swap_is_orientation_slack(self):
        # swap two corners: same kind, different coord
        swapped = dict(self.base)
        c1 = next(t for t, c in self.base.items() if c == (-1, -1, -1))
        c2 = next(t for t, c in self.base.items() if c == (1, 1, 1))
        swapped[c1], swapped[c2] = self.base[c2], self.base[c1]
        b = m.measure([self.base, swapped])
        self.assertEqual(b["placement"]["kind"], 1.0)       # corner <-> corner
        self.assertLess(b["placement"]["exact"], 1.0)       # but they moved
        self.assertGreater(b["tensions"]["orientation_slack"], 0.0)

    def test_disjoint_vocab_reads_zero_overlap(self):
        alt = {"alt-%d" % i: c for i, c in enumerate(ternary_cells())}
        b = m.measure([self.base, alt])
        self.assertEqual(b["vocabulary"]["mean_pairwise_jaccard"], 0.0)
        self.assertEqual(b["placement"]["n_terms"], 0)
        self.assertIsNone(b["placement"]["exact"])          # nothing shared to place
        # vocab tension is undefined when placement has no shared terms
        self.assertIsNone(b["tensions"]["vocab_minus_placement"])

    def test_refuses_too_few_and_unlawful(self):
        with self.assertRaises(ValueError):
            m.measure([self.base])
        unlawful = dict(self.base)
        victim = next(t for t, c in self.base.items() if c == (0, 0, 0))
        unlawful[victim] = (1, 1, 1)  # collision: two at (1,1,1)
        with self.assertRaises(ins.RefusedToFit):
            m.measure([self.base, unlawful])

    def test_rows_flatten_to_a_dataset(self):
        b = m.measure([self.base, dict(self.base)])
        rows = m.rows(b, seed_id="s.test")
        self.assertTrue(all(set(r) == {"seed", "scope", "grade", "metric",
                                       "value"} for r in rows))
        self.assertTrue(any(r["metric"] == "orientation_slack" for r in rows))
        self.assertTrue(all(r["seed"] == "s.test" for r in rows))


if __name__ == "__main__":
    unittest.main()

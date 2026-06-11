"""Seed / generation-prompt tests (done-line 0031, the inverted generation).

The seed is the minimal compressed element; the prompt must carry its
three axes and anchor and ask for a JSON placement — and must NOT leak
any particular vocabulary (the words are the generator's to invent).
"""
import unittest

from pivot import seed as sd


class TestSeed(unittest.TestCase):
    def test_seed_shape(self):
        self.assertEqual(len(sd.SEED_S["axes"]), 3)
        for ax in sd.SEED_S["axes"]:
            self.assertEqual(set(ax), {"name", "neg", "zero", "pos"})

    def test_prompt_carries_the_seed_not_a_vocabulary(self):
        p = sd.generation_prompt(sd.SEED_S)
        self.assertIn(sd.SEED_S["anchor"], p)
        for ax in sd.SEED_S["axes"]:
            self.assertIn(ax["name"], p)
            self.assertIn(ax["neg"], p)
        self.assertIn("JSON", p)
        # the generator invents the words — no candidate terms are handed in
        self.assertNotIn("reservoir", p.lower())
        self.assertNotIn("interface", p.lower())


if __name__ == "__main__":
    unittest.main()

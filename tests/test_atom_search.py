"""Tests for done-line 0113: Causality's read-only atom search projection."""

import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from causality import atom_search
from loop import reconcile


class AtomSearchProjection(unittest.TestCase):
    def setUp(self):
        self.root = REPO / ".ai-native"

    def test_search_matches_real_atom_records(self):
        projection = atom_search.build_projection("causality welcome", self.root)
        ids = {r["id"] for r in projection["results"]}
        self.assertIn("atom.causality-welcome-mat.v0", ids)
        self.assertIn("atom.causality-term-economy.v0", ids)
        for result in projection["results"]:
            self.assertEqual(result["record_kind"], "projected")
            self.assertTrue(result["matches"])

    def test_lifecycle_state_comes_from_reconcile_fold(self):
        projection = atom_search.build_projection("causality welcome", self.root)
        by_id = {r["id"]: r for r in projection["results"]}
        atoms = {a["id"]: (a, h) for a, h in reconcile.load_atoms(self.root)}
        _, ahash = atoms["atom.causality-welcome-mat.v0"]
        self.assertEqual(
            by_id["atom.causality-welcome-mat.v0"]["state"],
            reconcile.atom_state(reconcile.Fold(self.root), ahash))
        self.assertEqual(by_id["atom.causality-welcome-mat.v0"]["artifact_hash"], ahash)

    def test_no_match_is_named_as_a_gap_not_fabricated(self):
        projection = atom_search.build_projection("not-a-real-atom-token-xyz", self.root)
        self.assertEqual(projection["result_count"], 0)
        self.assertEqual(projection["results"], [])
        self.assertEqual(projection["gaps"][0]["kind"], "no-match")

    def test_empty_query_is_refused(self):
        projection = atom_search.build_projection("   ", self.root)
        self.assertEqual(projection["result_count"], 0)
        self.assertEqual(projection["gaps"][0]["kind"], "empty-query")

    def test_search_writes_nothing_and_serializes_deterministically(self):
        before = {
            p.name: p.read_bytes()
            for p in (self.root / "log").glob("*.jsonl")
        }
        first = atom_search.dumps(atom_search.build_projection("causality", self.root))
        second = atom_search.dumps(atom_search.build_projection("causality", self.root))
        after = {
            p.name: p.read_bytes()
            for p in (self.root / "log").glob("*.jsonl")
        }
        self.assertEqual(first, second)
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()

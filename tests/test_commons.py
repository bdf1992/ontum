"""test_commons.py — the §10 check for done-line 0097: the Pattern Commons is
DERIVED from the repo's common patterns (not authored), graded against committed
bytes, and served curl-first over HTTP — with teeth: an unresolvable etymon is
held `proposed`/`ghost`, never minted.

Drives both the fold (`causality/commons.py`) and the HTTP router
(`causality/api.py`) in-process. Joins the main suite (`python -m unittest
discover -s tests`).
"""
import json
import unittest
from pathlib import Path

from causality import commons, api

REPO = Path(__file__).resolve().parent.parent


class DeriveCommons(unittest.TestCase):
    def setUp(self):
        self.result = commons.derive(REPO)
        self.by_id = {p["id"]: p for p in self.result["patterns"]}

    def test_derived_from_real_patterns_not_a_catalog(self):
        # the node patterns are mined from canvas.js's own SCHEMA kinds — so the
        # Commons tracks the engine's real vocabulary, not a hand list.
        kinds = commons._schema_kinds(REPO)
        self.assertIn("gate", kinds)
        self.assertIn("inference", kinds)
        for k in kinds:
            self.assertIn(f"node:{k}", self.by_id,
                          f"node kind {k} in canvas SCHEMA must derive a Commons pattern")

    def test_grounded_subset_is_present(self):
        for fam in ("node:gate", "edge", "site", "fundamental", "derived",
                    "learned", "divergence"):
            self.assertIn(fam, self.by_id, f"{fam} must be in the grounded subset")

    def test_grounded_patterns_resolve_against_real_bytes(self):
        # a grounded pattern's etymon really resolves on disk (file + substring).
        for p in self.result["patterns"]:
            if p["grounded"]:
                ok, _ = commons._resolve(p["etymon"], REPO)
                self.assertTrue(ok, f"{p['id']} claims grounded but does not resolve")
                self.assertEqual(p["grade"], "minted-eligible")

    def test_teeth_learned_is_not_minted(self):
        # the REAL tooth: `learned` has no on-disk oracle surface yet
        # (display-system C3 hole), so it must NOT be minted-eligible. A fold that
        # minted it anyway would fail here.
        learned = self.by_id["learned"]
        self.assertFalse(learned["grounded"])
        self.assertIn(learned["grade"], ("proposed", "ghost"))
        self.assertNotEqual(learned["grade"], "minted-eligible")

    def test_teeth_a_fabricated_etymon_cannot_ground_itself(self):
        # negative control: a candidate that asserts a backing the bytes do not
        # carry stays un-grounded. The bytes win, never the claim.
        ok, why = commons._resolve(
            {"file": "causality/canvas.js", "contains": "this-string-is-not-in-canvas"},
            REPO)
        self.assertFalse(ok, "a false `contains` must not resolve")
        # and an absent file is a ghost, not a silent pass
        ok2, _ = commons._resolve({"file": "causality/nope.py", "contains": ""}, REPO)
        self.assertFalse(ok2)

    def test_reproducible(self):
        again = commons.derive(REPO)
        self.assertEqual(self.result, again, "the derivation must be deterministic")


class CurlFirstApi(unittest.TestCase):
    def test_commons_route_serves_the_derivation(self):
        status, ctype, body = api.route("/commons")
        self.assertEqual(status, 200)
        self.assertEqual(ctype, "application/json")
        data = json.loads(body)
        self.assertEqual(data, commons.derive(REPO),
                         "the curl surface and the fold are one source (I-4)")

    def test_projection_route_serves_committed_bytes(self):
        status, ctype, body = api.route("/projection")
        self.assertEqual(status, 200)
        data = json.loads(body)
        self.assertIn("terms", data)
        self.assertIn("evidence_edges", data)
        # verbatim committed bytes — the projection property
        self.assertEqual(body, api.PROJECTION.read_bytes())

    def test_health_and_index(self):
        self.assertEqual(api.route("/health")[0], 200)
        self.assertEqual(api.route("/")[0], 200)

    def test_unknown_path_404(self):
        status, _, body = api.route("/not-a-route")
        self.assertEqual(status, 404)
        self.assertIn("routes", json.loads(body))

    def test_trailing_slash_and_query_are_normalized(self):
        self.assertEqual(api.route("/commons/")[0], 200)
        self.assertEqual(api.route("/projection?x=1")[0], 200)


if __name__ == "__main__":
    unittest.main()

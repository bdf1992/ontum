"""Tests for the term-economy fold (done-line 0060) — Causality's witness slice.

The §10 bar is the whole point here: the audit must be able to *refuse*. Four
locally-fine-looking terms each fail to fit their claim, and the fold must
notice rather than wave them through:

  (a) a term with no resolvable evidence can never be `minted` — no evidence
      is not a license to mint;
  (b) a term whose claimed code citation points at bytes that are not on disk
      is a `ghost`, not a real node;
  (c) a term carrying two incompatible senses that each resolve is
      `overloaded` — proven on the REAL `seam` and `arc` overloads already on
      the record, not a synthetic case;
  (d) the committed projection is reproducible from the committed seed
      byte-for-byte (asserted as bytes, per tests/CLAUDE.md).

And the gate is not vacuous: a fabricated constant classifier (`always
minted-runtime`) is shown to violate (a)–(c). A classifier that does not read
the evidence fails this suite.
"""

import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from causality import term_economy as te


def _resolved(term):
    return [te.resolve_evidence(te.ROOT, e) for e in term.get("evidence", [])]


class TermEconomyClassify(unittest.TestCase):
    """The classifier discriminates on resolved evidence — the refusals."""

    def test_no_evidence_is_never_minted(self):
        # (a) a term that claims nothing cannot be minted by appearing here.
        term = {"term": "vibes", "evidence": []}
        klass = te.classify(term, _resolved(term))
        self.assertNotIn("minted", klass)
        self.assertEqual(klass, "proposed")

    def test_unresolvable_citation_is_ghost(self):
        # (b) a citation that points at bytes not on disk is a ghost backing.
        term = {"term": "phantom", "evidence": [
            {"stratum": "code", "file": "loop/does-not-exist.py",
             "contains": "def imaginary()", "claim": "claims a function nobody wrote"},
        ]}
        evs = _resolved(term)
        self.assertFalse(evs[0]["file_exists"])
        self.assertFalse(evs[0]["resolved"])
        self.assertEqual(te.classify(term, evs), "ghost")

    def test_real_code_term_is_minted_runtime(self):
        # the positive case: doctrine + code + log all resolve.
        term = {"term": "atom", "evidence": [
            {"stratum": "code", "file": "loop/reconcile.py",
             "contains": "def load_atoms(root)", "claim": "code folds atoms"},
            {"stratum": "log", "file": ".ai-native/log/events.jsonl",
             "contains": "atom.created", "claim": "real event kind"},
        ]}
        self.assertEqual(te.classify(term, _resolved(term)), "minted-runtime")

    def test_two_incompatible_senses_is_overloaded(self):
        # (c) the real seam overload — loop event-surface vs phase-2 primitive.
        term = {"term": "seam", "evidence": [
            {"stratum": "code", "file": "loop/reconcile.py",
             "contains": '"seam": "author-to-value"', "sense": "loop-event-surface",
             "claim": "the loop's event surface"},
            {"stratum": "doctrine", "file": "glyphs/knolling.md",
             "contains": "**Seam** | SETTLED | A primitive that is a join",
             "sense": "phase2-site-primitive", "incompatible": True,
             "claim": "the phase-2 geometric primitive — a different object"},
        ]}
        self.assertEqual(te.classify(term, _resolved(term)), "overloaded")

    def test_lone_doctrine_definition_is_orphaned(self):
        # a definition with no economy around it is orphaned, not minted.
        term = {"term": "lonely", "evidence": [
            {"stratum": "doctrine", "file": "ai-native-loop-substrate.md",
             "contains": "**Atom** (the story is the value part",
             "claim": "borrows a real doctrine line, but claims no usage anywhere"},
        ]}
        self.assertEqual(te.classify(term, _resolved(term)), "orphaned")


class TermEconomyProjection(unittest.TestCase):
    """The committed example projects honestly and reproduces byte-for-byte."""

    def setUp(self):
        self.seed = te.load_seed(te.DEFAULT_SEED)
        self.projection = te.build_projection(te.ROOT, self.seed)

    def test_five_canonical_terms_present(self):
        names = {t["term"] for t in self.projection["terms"]}
        self.assertLessEqual({"atom", "receipt", "seam", "node", "arc"}, names)

    def test_sites_are_first_class_projected_records(self):
        sites = {s["id"]: s for s in self.projection["sites"]}
        self.assertEqual(self.projection["site_count"], len(sites))
        self.assertIn(te.site_id("loop/reconcile.py"), sites)
        self.assertEqual(sites[te.site_id("loop/reconcile.py")]["kind"], "code")
        self.assertTrue(sites[te.site_id("loop/reconcile.py")]["exists"])
        self.assertEqual(sites[te.site_id(".ai-native/log/events.jsonl")]["kind"], "log")
        self.assertEqual(sites[te.site_id("ai-native-loop-substrate.md")]["kind"], "doctrine")
        for site in sites.values():
            self.assertEqual(site["record_kind"], "projected")
            self.assertNotIn("contains", site, "sites index addresses, not citation claims")

    def test_evidence_edges_target_sites(self):
        site_ids = {s["id"] for s in self.projection["sites"]}
        for edge in self.projection["evidence_edges"]:
            self.assertIn(edge["to"], site_ids)
            self.assertEqual(edge["to"], te.site_id(edge["ref"]["file"]))

    def test_site_inbound_counts_distinct_terms(self):
        expected = {}
        for edge in self.projection["evidence_edges"]:
            expected.setdefault(edge["to"], set()).add(edge["from"])
        sites = {s["id"]: s for s in self.projection["sites"]}
        for sid, terms in expected.items():
            self.assertEqual(sites[sid]["inbound_term_count"], len(terms))

    def test_mermaid_renders_shared_sites_once(self):
        graph = te.mermaid(self.projection)
        reconcile_site = te._nid(te.site_id("loop/reconcile.py"))
        self.assertEqual(
            graph.count(f'{reconcile_site}["loop/reconcile.py :: code"]'), 1)
        self.assertIn(f"term_arc -->|code/arc-as-confirmed-admission| {reconcile_site}", graph)
        self.assertIn(f"term_atom -->|code| {reconcile_site}", graph)
        self.assertIn(f"term_receipt -->|code| {reconcile_site}", graph)

    def test_every_term_carries_a_must_not_mean_guard(self):
        for t in self.projection["terms"]:
            self.assertTrue(t["must_not_mean"],
                            f"{t['term']} has no must-not-mean guard")

    def test_seam_and_arc_surface_as_overloaded(self):
        by_name = {t["term"]: t for t in self.projection["terms"]}
        self.assertEqual(by_name["seam"]["class"], "overloaded")
        self.assertEqual(by_name["arc"]["class"], "overloaded")
        # and the audit names them as gaps, not silently passes them
        overload_gaps = {g["term"] for g in self.projection["gaps"]
                         if g["kind"] == "overloaded-term"}
        self.assertEqual(overload_gaps, {"seam", "arc"})

    def test_no_unresolved_evidence_in_the_committed_seed(self):
        # the example's citations are real; a stale one would be a finding
        unresolved = [g for g in self.projection["gaps"]
                      if g["kind"] == "unresolved-evidence"]
        self.assertEqual(unresolved, [], f"stale citations: {unresolved}")

    def test_projection_reproduces_byte_for_byte(self):
        # (d) re-running the fold over the committed seed yields the committed
        # projection exactly — asserted as bytes (tests/CLAUDE.md).
        committed = te.DEFAULT_PROJECTION.read_bytes()
        fresh = te.dumps(self.projection).encode("utf-8")
        self.assertEqual(fresh, committed,
                         "projection drifted — regenerate with "
                         "`python causality/term_economy.py project --write`")


class GateIsNotVacuous(unittest.TestCase):
    """A fabricated constant classifier must fail (a)-(c): the suite has teeth."""

    def test_constant_classifier_would_be_caught(self):
        constant = lambda term, evs: "minted-runtime"  # noqa: E731 — the strawman
        no_ev = {"term": "vibes", "evidence": []}
        ghost = {"term": "phantom", "evidence": [
            {"stratum": "code", "file": "loop/does-not-exist.py",
             "contains": "x", "claim": "nope"}]}
        seam = te.load_seed(te.DEFAULT_SEED)
        seam_term = next(t for t in seam["terms"] if t["term"] == "seam")

        # the honest classifier discriminates...
        self.assertEqual(te.classify(no_ev, _resolved(no_ev)), "proposed")
        self.assertEqual(te.classify(ghost, _resolved(ghost)), "ghost")
        self.assertEqual(te.classify(seam_term, _resolved(seam_term)), "overloaded")
        # ...where the constant would lie on every one of them.
        self.assertNotEqual(constant(no_ev, []), "proposed")
        self.assertNotEqual(constant(ghost, []), "ghost")
        self.assertNotEqual(constant(seam_term, []), "overloaded")


if __name__ == "__main__":
    unittest.main()

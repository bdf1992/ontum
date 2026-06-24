"""Done-line 0139: epic.diagram wave 1 — the deterministic floor and the
refusing gate.

The §10 bar (tests/CLAUDE.md): prefer a test where a locally-fine artifact
*refuses to fit* over one that confirms the happy path. Here the honest
pipeline state-machine renders and PASSES the gate, while a locally-fine but
dishonest variant (an orphan node) is REFUSED with its canon principle named —
the two specs differ by exactly one node.

What this pins:
  - compose.py is byte-deterministic: the same spec renders identical bytes on
    repeated runs, and the committed SVG equals a fresh render (asserted as
    bytes, not text — diagrams/CLAUDE.md byte-deterministic grain).
  - qa.py is a refusing gate: exit 0 on the honest spec, exit 2 on the
    dishonest one with the violated canon principle on stderr, and fail-open
    (exit 0) on its own internal error.
  - the individual canon teeth actually bite (a rule with no refusal is
    decoration — canon.md's discipline).
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DIAGRAMS = REPO / "diagrams"
EXAMPLES = DIAGRAMS / "examples"
HONEST = EXAMPLES / "pipeline-state-machine.json"
DISHONEST = EXAMPLES / "pipeline-dishonest.json"
REGIONED = EXAMPLES / "pipeline-regioned.json"
REGION_BROKEN = EXAMPLES / "pipeline-region-broken.json"
LAYERED = EXAMPLES / "pipeline-layered.json"
LAYER_ORPHAN = EXAMPLES / "pipeline-layer-orphan.json"

sys.path.insert(0, str(DIAGRAMS))
sys.path.insert(0, str(REPO))
import compose  # noqa: E402
import qa  # noqa: E402
from causality import term_economy as te  # noqa: E402

# done-line 0173: the from-truth diagram projection, folded INTO term_economy.
GW_SEED = REPO / "causality" / "examples" / "gateway-topology.seed.json"
GW_SPEC = REPO / "causality" / "examples" / "gateway-topology.spec.json"
GW_SVG = REPO / "causality" / "examples" / "gateway-topology.spec.svg"
GW_PROJECTION = REPO / "causality" / "examples" / "gateway-topology.projection.json"


def _run_qa(spec_path):
    """Run the gate as a subprocess; the contract is exit code + streams."""
    return subprocess.run(
        [sys.executable, str(DIAGRAMS / "qa.py"), str(spec_path)],
        capture_output=True, text=True,
    )


class TestDeterminism(unittest.TestCase):
    def test_same_spec_renders_identical_bytes_twice(self):
        spec = json.loads(HONEST.read_text(encoding="utf-8"))
        first = compose.render(spec).encode("utf-8")
        second = compose.render(spec).encode("utf-8")
        self.assertEqual(first, second, "render is not byte-deterministic")

    def test_committed_svg_equals_a_fresh_render(self):
        spec = json.loads(HONEST.read_text(encoding="utf-8"))
        committed = (EXAMPLES / "pipeline-state-machine.svg").read_bytes()
        fresh = compose.render(spec).encode("utf-8")
        self.assertEqual(
            committed, fresh,
            "the committed SVG drifted from compose.py — re-render it")

    def test_cli_writes_byte_identical_output(self):
        with tempfile.TemporaryDirectory() as d:
            a = Path(d) / "a.svg"
            b = Path(d) / "b.svg"
            compose.main([str(HONEST), "--out", str(a)])
            compose.main([str(HONEST), "--out", str(b)])
            self.assertEqual(a.read_bytes(), b.read_bytes())


class TestTheGate(unittest.TestCase):
    """The §10 pair: honest passes, dishonest refuses with the cited canon."""

    def test_honest_spec_passes(self):
        r = _run_qa(HONEST)
        self.assertEqual(r.returncode, 0, f"honest spec was refused:\n{r.stderr}")

    def test_dishonest_spec_is_refused_with_cited_principle(self):
        r = _run_qa(DISHONEST)
        self.assertNotEqual(r.returncode, 0, "the dishonest spec passed the gate")
        self.assertEqual(r.returncode, 2, "deny must be exit 2 (the guard convention)")
        # the refusal names the violated canon principle by name
        self.assertIn("no orphans", r.stderr.lower())
        self.assertIn("audit", r.stderr.lower())

    def test_the_pair_differs_by_exactly_one_node(self):
        honest = json.loads(HONEST.read_text(encoding="utf-8"))
        dishonest = json.loads(DISHONEST.read_text(encoding="utf-8"))
        h_ids = {n["id"] for n in honest["nodes"]}
        d_ids = {n["id"] for n in dishonest["nodes"]}
        self.assertEqual(d_ids - h_ids, {"audit"},
                         "the dishonest variant must be locally-fine + one defect")
        self.assertEqual(honest["edges"], dishonest["edges"],
                         "the topology is otherwise identical")


class TestFailOpen(unittest.TestCase):
    """A gate that cannot parse its input must not block honest work."""

    def test_malformed_spec_fails_open(self):
        with tempfile.TemporaryDirectory() as d:
            bad = Path(d) / "bad.json"
            bad.write_text("{ not json", encoding="utf-8")
            r = _run_qa(bad)
            self.assertEqual(r.returncode, 0,
                             "internal error must fail open (exit 0), not deny")
            self.assertIn("failing open", r.stderr.lower())


class TestEachToothBites(unittest.TestCase):
    """canon.md's discipline: a rule with no refusal is decoration. Each canon
    tooth is exercised on a minimal spec that trips exactly it."""

    def _principles(self, spec):
        return {p for sev, p, _m, _c in qa.evaluate(spec) if sev == "error"}

    def test_semiotic_clarity_unknown_type(self):
        spec = {"size": [400, 200], "nodes": [
            {"id": "a", "type": "trapezoid", "x": 20, "y": 20, "w": 100, "h": 50, "label": "a"},
            {"id": "b", "type": "rect", "x": 200, "y": 20, "w": 100, "h": 50, "label": "b"}],
            "edges": [{"from": "a", "to": "b"}]}
        self.assertIn("semiotic clarity", self._principles(spec))

    def test_perceptual_discriminability_three_accents(self):
        spec = {"size": [600, 200], "nodes": [
            {"id": "a", "type": "rect", "x": 20, "y": 20, "w": 100, "h": 50, "label": "a", "accent": "cool"},
            {"id": "b", "type": "rect", "x": 200, "y": 20, "w": 100, "h": 50, "label": "b", "accent": "warm"},
            {"id": "c", "type": "rect", "x": 400, "y": 20, "w": 100, "h": 50, "label": "c", "accent": "purple"}],
            "edges": [{"from": "a", "to": "b"}, {"from": "b", "to": "c"}]}
        self.assertIn("perceptual discriminability", self._principles(spec))

    def test_dual_coding_unlabeled_node(self):
        spec = {"size": [400, 200], "nodes": [
            {"id": "a", "type": "rect", "x": 20, "y": 20, "w": 100, "h": 50, "label": ""},
            {"id": "b", "type": "rect", "x": 200, "y": 20, "w": 100, "h": 50, "label": "b"}],
            "edges": [{"from": "a", "to": "b"}]}
        self.assertIn("dual coding", self._principles(spec))

    def test_no_orphans(self):
        spec = {"size": [400, 200], "nodes": [
            {"id": "a", "type": "rect", "x": 20, "y": 20, "w": 100, "h": 50, "label": "a"},
            {"id": "b", "type": "rect", "x": 200, "y": 20, "w": 100, "h": 50, "label": "b"},
            {"id": "lonely", "type": "rect", "x": 20, "y": 120, "w": 100, "h": 50, "label": "lonely"}],
            "edges": [{"from": "a", "to": "b"}]}
        self.assertIn("graph-drawing: no orphans", self._principles(spec))

    def test_reachability_beyond_four_hops(self):
        # a connected chain longer than 4 hops from its single hub
        nodes, edges = [], []
        for i in range(7):
            nodes.append({"id": f"n{i}", "type": "rect",
                          "x": 20 + i * 90, "y": 20, "w": 80, "h": 50, "label": f"n{i}"})
            if i:
                edges.append({"from": f"n{i-1}", "to": f"n{i}"})
        # mark the first node as the hub so n6 sits 6 hops away
        nodes[0]["hub"] = True
        spec = {"size": [700, 120], "nodes": nodes, "edges": edges}
        self.assertIn("graph-drawing: reachability / cognitive load", self._principles(spec))

    def test_graphic_economy_too_many_siblings(self):
        nodes = [{"id": f"n{i}", "type": "rect", "x": 20 + i * 70, "y": 20,
                  "w": 60, "h": 50, "label": f"n{i}"} for i in range(9)]
        edges = [{"from": f"n{i}", "to": f"n{i+1}"} for i in range(8)]
        spec = {"size": [1000, 120], "nodes": nodes, "edges": edges}
        self.assertIn("graphic economy / complexity management", self._principles(spec))

    def test_semantic_transparency_invented_genre(self):
        spec = {"size": [400, 200], "genre": "membrane-cross-section", "nodes": [
            {"id": "a", "type": "rect", "x": 20, "y": 20, "w": 100, "h": 50, "label": "a"},
            {"id": "b", "type": "rect", "x": 200, "y": 20, "w": 100, "h": 50, "label": "b"}],
            "edges": [{"from": "a", "to": "b"}]}
        self.assertIn("semantic transparency", self._principles(spec))

    def test_edge_through_unrelated_node(self):
        spec = {"size": [700, 160], "nodes": [
            {"id": "a", "type": "rect", "x": 20, "y": 50, "w": 100, "h": 50, "label": "a"},
            {"id": "mid", "type": "rect", "x": 300, "y": 50, "w": 100, "h": 50, "label": "mid"},
            {"id": "b", "type": "rect", "x": 560, "y": 50, "w": 100, "h": 50, "label": "b"}],
            "edges": [{"from": "a", "to": "b"}, {"from": "a", "to": "mid"}]}
        self.assertIn("graph-drawing: minimize edge crossings", self._principles(spec))

    def test_honest_spec_trips_no_tooth(self):
        spec = json.loads(HONEST.read_text(encoding="utf-8"))
        self.assertEqual(self._principles(spec), set(),
                         "the honest spec must trip no canon tooth")


class TestRegionsAreStructure(unittest.TestCase):
    """Done-line 0151: regions are first-class declared structure — a node
    belongs to a boundary by declaration, not geometry. The §10 pair: an honest
    regioned diagram passes; a variant differing by exactly one field (one
    node's `region`) where that node claims a boundary that does not exist is
    REFUSED with the C4 containment principle named."""

    def _principles(self, spec):
        return {p for sev, p, _m, _c in qa.evaluate(spec) if sev == "error"}

    def test_honest_regioned_passes(self):
        r = _run_qa(REGIONED)
        self.assertEqual(r.returncode, 0, f"honest regioned spec was refused:\n{r.stderr}")

    def test_committed_regioned_svg_equals_fresh_render(self):
        spec = json.loads(REGIONED.read_text(encoding="utf-8"))
        committed = (EXAMPLES / "pipeline-regioned.svg").read_bytes()
        fresh = compose.render(spec).encode("utf-8")
        self.assertEqual(committed, fresh,
                         "the committed regioned SVG drifted — re-render it")

    def test_broken_region_refused_with_cited_principle(self):
        r = _run_qa(REGION_BROKEN)
        self.assertEqual(r.returncode, 2, "the broken-region spec passed the gate")
        self.assertIn("c4 containment", r.stderr.lower())
        self.assertIn("does not exist", r.stderr.lower())

    def test_the_region_pair_differs_by_one_field(self):
        honest = json.loads(REGIONED.read_text(encoding="utf-8"))
        broken = json.loads(REGION_BROKEN.read_text(encoding="utf-8"))
        diffs = [(h["id"], h.get("region"), b.get("region"))
                 for h, b in zip(honest["nodes"], broken["nodes"])
                 if h.get("region") != b.get("region")]
        self.assertEqual(len(diffs), 1,
                         "the broken variant must be locally-fine + one bad region declaration")
        self.assertEqual(honest["regions"], broken["regions"],
                         "the declared regions are otherwise identical")

    def test_node_outside_its_region_is_refused(self):
        # a node declares a region it sits geometrically outside → deny
        spec = {"size": [400, 400],
                "regions": [{"id": "r", "label": "r", "x": 20, "y": 20, "w": 150, "h": 150}],
                "nodes": [
                    {"id": "out", "type": "rect", "region": "r", "x": 220, "y": 220, "w": 80, "h": 50, "label": "out"},
                    {"id": "ok", "type": "rect", "region": "r", "x": 40, "y": 40, "w": 80, "h": 50, "label": "ok"}],
                "edges": [{"from": "out", "to": "ok"}]}
        self.assertIn("C4 containment / cognitive integration", self._principles(spec))

    def test_no_regions_is_backward_compatible(self):
        # the floor's honest spec has no `regions`/`region` → the tooth never bites
        spec = json.loads(HONEST.read_text(encoding="utf-8"))
        self.assertNotIn("C4 containment / cognitive integration", self._principles(spec))
        self.assertEqual(qa.check_region_membership.__name__, "check_region_membership")


class TestDiagramProjectionFromTruth(unittest.TestCase):
    """Done-line 0173 (epic.diagram wave 3): a diagram is a FOLD over truth,
    folded INTO causality/term_economy.py (never a parallel module, §10).
    Realness is DERIVED from records — and a layer whose citation resolves
    nowhere is REFUSED, dropped not drawn (term_economy's existing teeth).

    The §10 pair is the non-vacuous ghost tooth: a fixture seed of two locally
    -fine terms, one citing real committed bytes and one citing bytes that are
    not on disk; diagram_spec draws the real one and DROPS the ghost — proven by
    asserting the real id is present, the ghost id is absent, and the ghost is
    surfaced as a gap. The drop is selective (it does not wipe the diagram), so
    the test FAILS on a fold that draws unresolved citations or drops everything.
    """

    # one resolving citation reused across fixtures (it really exists on disk).
    REAL_EV = {"stratum": "code", "file": "loop/node.py",
               "contains": "def judge", "claim": "the one pen"}
    GHOST_EV = {"stratum": "code", "file": "loop/does-not-exist.py",
                "contains": "def imaginary", "claim": "cites bytes nobody wrote"}

    def _fixture(self):
        """A 2-term seed: `real` resolves, `phantom` resolves nowhere; both are
        placed and on the flow, so the flow runs real -> phantom."""
        return {
            "seed": "fixture",
            "terms": [
                {"term": "real", "claimed_class": "minted-runtime",
                 "evidence": [dict(self.REAL_EV)]},
                {"term": "phantom", "claimed_class": "minted-runtime",
                 "evidence": [dict(self.GHOST_EV)]},
            ],
            "diagram": {
                "size": [600, 240],
                "title": "fixture",
                "regions": [{"id": "r", "label": "r", "x": 20, "y": 60,
                             "w": 560, "h": 140, "row_y": 110, "col_x0": 60,
                             "col_step": 240}],
                "place": {"real": {"region": "r", "col": 0},
                          "phantom": {"region": "r", "col": 1}},
                "flow": ["real", "phantom"],
            },
        }

    def test_spec_is_byte_deterministic_on_a_fixed_fixture(self):
        seed = self._fixture()
        layout = seed["diagram"]
        spec_a = te.diagram_spec(te.build_projection(te.ROOT, seed), layout)
        spec_b = te.diagram_spec(te.build_projection(te.ROOT, seed), layout)
        self.assertEqual(te.dumps(spec_a), te.dumps(spec_b),
                         "diagram_spec is not byte-deterministic")
        self.assertEqual(compose.render(spec_a).encode("utf-8"),
                         compose.render(spec_b).encode("utf-8"),
                         "the rendered SVG is not byte-deterministic")

    def test_ghost_citation_is_dropped_not_drawn_and_surfaced_as_a_gap(self):
        seed = self._fixture()
        layout = seed["diagram"]
        projection = te.build_projection(te.ROOT, seed)
        spec = te.diagram_spec(projection, layout)
        ids = {n["id"] for n in spec["nodes"]}

        # selective: the resolving term is drawn...
        self.assertIn("real", ids, "the resolving term must be drawn")
        # ...and the ghost (cites bytes not on disk) is REFUSED — dropped.
        self.assertNotIn("phantom", ids,
                         "a citation that resolves nowhere must not be drawn")

        # the refusal is reported, not silent: a projection gap + a named drop.
        ghost_gaps = [g for g in projection["gaps"] if g["term"] == "phantom"]
        self.assertTrue(ghost_gaps,
                        "the dropped node must be surfaced as a projection gap")
        self.assertIn("ghost-term", {g["kind"] for g in ghost_gaps})
        self.assertEqual({d["term"] for d in te.diagram_drops(projection, layout)},
                         {"phantom"})

        # the flow edge THROUGH the dropped node is dropped with it — no edge
        # may reference a node that was refused.
        for e in spec["edges"]:
            self.assertNotIn("phantom", (e["from"], e["to"]),
                             "an edge cannot route through a refused node")

    def test_the_tooth_is_non_vacuous_a_resolving_twin_is_kept(self):
        # swap the ghost's citation for a resolving one: now BOTH draw. This is
        # the control that proves the drop is caused by non-resolution, not by
        # the term's name or position (the tooth bites the right thing).
        seed = self._fixture()
        seed["terms"][1]["evidence"] = [dict(self.REAL_EV)]
        spec = te.diagram_spec(te.build_projection(te.ROOT, seed), seed["diagram"])
        ids = {n["id"] for n in spec["nodes"]}
        self.assertEqual(ids, {"real", "phantom"},
                         "with a resolving citation the twin is kept — so the "
                         "earlier drop was the non-resolution, not the node")


class TestGatewayTopologyCommittedArtifacts(unittest.TestCase):
    """The real-data demonstration: the gateway stack, classified from records
    and emitted as a spec that the gate (qa.py) accepts. The committed spec,
    SVG, and projection are byte-deterministic regenerations of the fold."""

    def setUp(self):
        self.seed = te.load_seed(GW_SEED)
        self.layout = self.seed["diagram"]
        self.projection = te.build_projection(te.ROOT, self.seed)
        self.spec = te.diagram_spec(self.projection, self.layout)

    def test_gateway_spec_passes_the_gate(self):
        r = _run_qa(GW_SPEC)
        self.assertEqual(r.returncode, 0,
                         f"the gateway spec was refused by qa:\n{r.stderr}")

    def test_committed_spec_equals_a_fresh_fold(self):
        self.assertEqual(GW_SPEC.read_bytes(),
                         te.dumps(self.spec).encode("utf-8"),
                         "the committed gateway spec drifted — regenerate with "
                         "`term_economy.py diagram --seed ... --write`")

    def test_committed_svg_equals_a_fresh_render(self):
        self.assertEqual(GW_SVG.read_bytes(),
                         compose.render(self.spec).encode("utf-8"),
                         "the committed gateway SVG drifted — re-render it")

    def test_committed_projection_reproduces_byte_for_byte(self):
        self.assertEqual(GW_PROJECTION.read_bytes(),
                         te.dumps(self.projection).encode("utf-8"),
                         "the committed gateway projection drifted — "
                         "`term_economy.py project --seed ... --write`")

    def test_threshold_is_refused_on_real_data(self):
        # the named-only layer cites loop/threshold.py, which resolves nowhere.
        ids = {n["id"] for n in self.spec["nodes"]}
        self.assertNotIn("threshold", ids,
                         "the named-only threshold layer must be dropped")
        self.assertIn("threshold",
                      {g["term"] for g in self.projection["gaps"]})
        self.assertEqual({d["term"] for d in
                          te.diagram_drops(self.projection, self.layout)},
                         {"threshold"})

    def test_every_drawn_layer_resolves_to_real_code(self):
        # honesty: every node actually drawn is a minted-runtime layer (its
        # shape, rect, is its realness class — never hand-asserted).
        by_name = {t["term"]: t for t in self.projection["terms"]}
        for n in self.spec["nodes"]:
            self.assertEqual(by_name[n["id"]]["class"], "minted-runtime")
            self.assertEqual(n["type"], "rect")
            self.assertGreater(by_name[n["id"]]["resolved_count"], 0)

    def test_no_container_exceeds_eight_siblings(self):
        # the layout reason regions exist: ~10 layers > the 8-sibling cap, so
        # the gate would refuse one row — split across two regions keeps it legal.
        self.assertEqual(qa.evaluate(self.spec), [],
                         "the gateway spec trips a canon tooth")


class TestLayersAreStructure(unittest.TestCase):
    """Done-line 0192 (the editable diagram canvas, first cut): layers are
    first-class declared bands — the structural sibling of regions. A part
    belongs to a band by declaration (`part.layer == layer.id`), not by where
    it is drawn. The §10 pair, non-vacuous: an honest layered diagram passes
    the gate and renders; a variant differing by exactly one field (one node's
    `layer`) where that node claims a band the `layers` array never declared is
    REFUSED with the C4 containment principle named. A constant 'pass' fails the
    negative case; a constant 'deny' fails the positive."""

    def _principles(self, spec):
        return {p for sev, p, _m, _c in qa.evaluate(spec) if sev == "error"}

    def test_honest_layered_passes(self):
        r = _run_qa(LAYERED)
        self.assertEqual(r.returncode, 0, f"honest layered spec was refused:\n{r.stderr}")

    def test_honest_layered_renders_and_committed_svg_matches(self):
        spec = json.loads(LAYERED.read_text(encoding="utf-8"))
        committed = (EXAMPLES / "pipeline-layered.svg").read_bytes()
        fresh = compose.render(spec).encode("utf-8")
        self.assertEqual(committed, fresh,
                         "the committed layered SVG drifted — re-render it")

    def test_layer_orphan_refused_with_cited_principle(self):
        r = _run_qa(LAYER_ORPHAN)
        self.assertEqual(r.returncode, 2, "the layer-orphan spec passed the gate")
        self.assertIn("c4 containment", r.stderr.lower())
        self.assertIn("does not exist", r.stderr.lower())
        self.assertIn("overlay", r.stderr.lower())

    def test_the_layer_pair_differs_by_one_field(self):
        honest = json.loads(LAYERED.read_text(encoding="utf-8"))
        orphan = json.loads(LAYER_ORPHAN.read_text(encoding="utf-8"))
        diffs = [(h["id"], h.get("layer"), o.get("layer"))
                 for h, o in zip(honest["nodes"], orphan["nodes"])
                 if h.get("layer") != o.get("layer")]
        self.assertEqual(len(diffs), 1,
                         "the orphan variant must be locally-fine + one bad layer declaration")
        self.assertEqual(honest["layers"], orphan["layers"],
                         "the declared layers are otherwise identical")

    def test_edge_or_region_on_undeclared_layer_is_refused(self):
        # not just nodes: an edge (and a region/subgraph) declaring a missing
        # band is refused too — the rule covers every kind of part.
        spec = {"size": [400, 200],
                "layers": [{"id": "base", "label": "base", "z": 0}],
                "nodes": [
                    {"id": "a", "type": "rect", "layer": "base", "x": 20, "y": 20, "w": 100, "h": 50, "label": "a"},
                    {"id": "b", "type": "rect", "layer": "base", "x": 200, "y": 20, "w": 100, "h": 50, "label": "b"}],
                "edges": [{"from": "a", "to": "b", "layer": "ghost-band"}]}
        self.assertIn("C4 containment / cognitive integration", self._principles(spec))

    def test_no_layers_is_backward_compatible(self):
        # the floor's honest spec declares no `layers`/`layer` → the tooth never bites
        spec = json.loads(HONEST.read_text(encoding="utf-8"))
        self.assertNotIn("C4 containment / cognitive integration", self._principles(spec))
        self.assertEqual(qa.check_layer_membership.__name__, "check_layer_membership")

    def test_layer_visibility_and_zorder_in_render(self):
        # compose.py honors a declared band: a hidden layer's node is omitted,
        # and a higher-z node draws after (on top of) a lower-z one. A no-op
        # layer set must not perturb a spec's draw order (backward-compat).
        spec = {"size": [400, 200],
                "layers": [
                    {"id": "base", "label": "base", "z": 0, "visible": True},
                    {"id": "top", "label": "top", "z": 5, "visible": True},
                    {"id": "hidden", "label": "hidden", "z": 1, "visible": False}],
                "nodes": [
                    {"id": "ontop", "type": "rect", "layer": "top", "x": 20, "y": 20, "w": 100, "h": 50, "label": "ontop"},
                    {"id": "base1", "type": "rect", "layer": "base", "x": 200, "y": 20, "w": 100, "h": 50, "label": "base1"},
                    {"id": "gone", "type": "rect", "layer": "hidden", "x": 20, "y": 120, "w": 100, "h": 50, "label": "gone"}],
                "edges": [{"from": "ontop", "to": "base1"}]}
        svg = compose.render(spec)
        self.assertNotIn(">gone<", svg, "a node on a hidden layer must be omitted")
        # ascending-z draw order: base1 (z=0) is emitted before ontop (z=5)
        self.assertLess(svg.index(">base1<"), svg.index(">ontop<"),
                        "parts must be drawn in ascending layer z")


if __name__ == "__main__":
    unittest.main()

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


class TestGatewayNodeMeaningIsDerived(unittest.TestCase):
    """Done-line 0179 (epic.diagram, stacks on 0173): each drawn gateway node
    carries its real ontum MEANING, DERIVED from the term's first resolving
    citation `claim` in the projection — never prose authored on the node. The
    fix for a cold reader who confabulated `fence` as IP-whitelisting, `heal` as
    generic recovery, and `pen` as a sandbox: the shape carried realness but the
    name carried a generic-gateway trope, so the meaning had to land on the node.

    The §10 teeth are derivation and non-vacuity: a hand-written constant would
    pass a 'the label is non-empty' check but FAIL here, because the meaning is
    asserted EQUAL to the projection's resolved claim and is shown to CHANGE when
    the seed's evidence changes.
    """

    def setUp(self):
        self.seed = te.load_seed(GW_SEED)
        self.layout = self.seed["diagram"]
        self.projection = te.build_projection(te.ROOT, self.seed)
        self.spec = te.diagram_spec(self.projection, self.layout)

    def _first_resolved_claim(self, projection, name):
        """Independently (not via te's helper) read the first resolving
        citation's claim from the projection's evidence edges — so the assertion
        proves the node meaning tracks the projection, not a shared code path."""
        src = f"term:{name}"
        for e in projection["evidence_edges"]:
            if e["from"] == src and e["resolved"]:
                return e["claim"]
        return None

    def _node_meaning(self, node):
        """The meaning the node carries: every label line below the name. The
        wrap joins back to the claim with single spaces (no word is split)."""
        lines = node["label"].split("\n")
        self.assertEqual(lines[0], node["id"],
                         "the first label line must be the layer name")
        return " ".join(lines[1:])

    def test_every_drawn_node_meaning_equals_its_resolved_claim(self):
        # (a) derived: each drawn node's meaning IS the projection's first
        # resolving citation claim — not a string authored on the node.
        for n in self.spec["nodes"]:
            claim = self._first_resolved_claim(self.projection, n["id"])
            self.assertTrue(claim, f"{n['id']} has no resolving claim to draw")
            self.assertEqual(self._node_meaning(n), claim,
                             f"{n['id']} meaning is not its derived evidence claim")

    def test_fence_heal_pen_read_truthfully(self):
        # (b) the three confabulated layers now carry their ground truth.
        meanings = {n["id"]: self._node_meaning(n) for n in self.spec["nodes"]}
        self.assertEqual(
            meanings["fence"],
            "the registry carries forbidden-decision rules (e.g. raw git push)")
        self.assertEqual(
            meanings["heal"],
            "the healing fold detects a stale-park bite and proposes the heal")
        self.assertEqual(
            meanings["pen"],
            "judge() is the one pen by which a summoned node writes its verdict")
        # and each is the actual projection claim (the generic-gateway reading is
        # nowhere on the node).
        for layer in ("fence", "heal", "pen"):
            self.assertEqual(
                meanings[layer],
                self._first_resolved_claim(self.projection, layer))

    def test_spec_is_byte_deterministic_with_meaning(self):
        # (c) byte-determinism survives the meaning-bearing label.
        spec_b = te.diagram_spec(te.build_projection(te.ROOT, self.seed), self.layout)
        self.assertEqual(te.dumps(self.spec), te.dumps(spec_b))
        self.assertEqual(compose.render(self.spec).encode("utf-8"),
                         compose.render(spec_b).encode("utf-8"))

    def test_meaning_bearing_spec_passes_the_gate(self):
        # (d) the wrapped meaning still fits every node — qa stays clean.
        self.assertEqual(qa.evaluate(self.spec), [],
                         "the meaning-bearing gateway spec trips a canon tooth")

    def test_meaning_is_non_vacuous_it_changes_with_the_evidence(self):
        # the load-bearing §10 leg: the meaning is PULLED from evidence, so
        # editing the seed's claim changes the node's meaning. A hand-written
        # constant would not move — this test FAILS on that mistake.
        real_ev = {"stratum": "code", "file": "loop/node.py",
                   "contains": "def judge", "claim": "the one pen — original claim"}
        seed = {
            "seed": "fixture",
            "terms": [{"term": "real", "claimed_class": "minted-runtime",
                       "evidence": [dict(real_ev)]}],
            "diagram": {
                "size": [600, 240], "title": "fixture",
                "node": {"w": 220, "h": 140},
                "regions": [{"id": "r", "label": "r", "x": 20, "y": 60,
                             "w": 560, "h": 160, "row_y": 90, "col_x0": 40,
                             "col_step": 240}],
                "place": {"real": {"region": "r", "col": 0}},
                "flow": ["real"],
            },
        }
        spec1 = te.diagram_spec(te.build_projection(te.ROOT, seed), seed["diagram"])
        meaning1 = " ".join(spec1["nodes"][0]["label"].split("\n")[1:])
        self.assertEqual(meaning1, "the one pen — original claim")

        # change ONLY the cited claim; the node meaning must follow it.
        seed["terms"][0]["evidence"][0]["claim"] = "a totally different grounding"
        spec2 = te.diagram_spec(te.build_projection(te.ROOT, seed), seed["diagram"])
        meaning2 = " ".join(spec2["nodes"][0]["label"].split("\n")[1:])
        self.assertEqual(meaning2, "a totally different grounding")
        self.assertNotEqual(meaning1, meaning2,
                            "the meaning did not change with the evidence — it is "
                            "hand-written, not derived")


class TestLabelMetricParity(unittest.TestCase):
    """Done-line 0179: term_economy wraps the node meaning to the node's usable
    width so the spec it emits passes qa.py's label-fit check. That only holds
    if the fold and the gate measure with the SAME font metrics. The metrics
    live in both places (a core fold should not put diagrams/ on sys.path for the
    whole suite), so this test is the teeth that refuse drift: if qa's mono char
    width or side padding ever changes, the fold's mirror must follow or this
    fails — the parity is checked, never trusted."""

    def test_fold_label_metrics_equal_the_gate(self):
        self.assertEqual(te._LABEL_MONO_CHAR_W, qa.MONO_CHAR_W_AT_16,
                         "the fold's mono char width drifted from qa's gate")
        self.assertEqual(te._LABEL_SIDE_PAD, qa.NODE_SIDE_PADDING,
                         "the fold's node side padding drifted from qa's gate")

    def test_fold_char_budget_matches_qa_usable_width(self):
        # the budget the fold wraps to must not exceed what the gate calls
        # usable, at the real gateway node width — a max-length line must pass
        # qa's own text_width check.
        node_w = 220
        max_chars = te._label_max_chars(node_w)
        usable = node_w - 2 * qa.NODE_SIDE_PADDING
        self.assertLessEqual(qa.text_width("X" * max_chars), usable,
                             "a max-budget line overflows qa's usable width")
        self.assertGreater(qa.text_width("X" * (max_chars + 1)), usable,
                           "the budget is needlessly conservative (off by one)")


if __name__ == "__main__":
    unittest.main()

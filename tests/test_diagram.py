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
import compose  # noqa: E402
import qa  # noqa: E402


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


class TestCaptionContainment(unittest.TestCase):
    """The caption-containment tooth: `compose.render_caption` wraps the foot
    caption to the canvas width (it can no longer clip off the right edge), and
    `qa.check_caption` is the deterministic FLOOR that refuses a caption that —
    even wrapped — runs off the top of the foot into the diagram body.

    The §10 pair: a normal multi-word caption that WRAPS still renders fully and
    PASSES the gate; an absurdly long caption on a tiny canvas, which even
    wrapped cannot fit, is REFUSED with the 'dual coding' principle named. The
    renderer and the gate share one wrap definition (`compose.wrap_caption`,
    I-4), so the gate counts exactly the lines that render."""

    def _principles(self, spec):
        return {p for sev, p, _m, _c in qa.evaluate(spec) if sev == "error"}

    def test_wrapping_caption_renders_fully_and_passes(self):
        caption = ("This panel deliberately omits the metabolism loop and the "
                   "tier stack so the reader sees only the floor organs and the "
                   "one dimension everything is measured on.")
        spec = {"size": [520, 400], "title": "wrap demo", "nodes": [
            {"id": "a", "type": "rect", "x": 40, "y": 40, "w": 150, "h": 60, "label": "alpha"},
            {"id": "b", "type": "rect", "x": 320, "y": 40, "w": 150, "h": 60, "label": "beta"}],
            "edges": [{"from": "a", "to": "b"}], "caption": caption}

        usable = 520 - 32 - 8
        lines = compose.wrap_caption(caption, usable)
        self.assertGreater(len(lines), 1, "the caption must actually wrap for this test to mean anything")

        # renders fully: every wrapped line's text is in the SVG (nothing dropped)
        svg = compose.render(spec)
        for line in lines:
            self.assertIn(__import__("html").escape(line), svg,
                          "a wrapped caption line did not render")
        # the last line's baseline is unchanged at height-18 (the foot anchor)
        self.assertIn('y="382"', svg)

        # and the gate passes it — wrapping fits within the foot
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "wrap.json"
            p.write_text(json.dumps(spec), encoding="utf-8")
            r = _run_qa(p)
        self.assertEqual(r.returncode, 0, f"a wrapping-but-fitting caption was refused:\n{r.stderr}")
        self.assertEqual(self._principles(spec), set(), "a fitting wrapped caption must trip no tooth")

    def test_overflowing_caption_is_refused_with_cited_principle(self):
        # absurdly long caption on a tiny canvas: even wrapped it runs off the
        # top of the foot into the body and off the canvas.
        caption = ("overflow " * 60).strip()
        spec = {"size": [200, 140], "nodes": [
            {"id": "a", "type": "rect", "x": 20, "y": 20, "w": 70, "h": 40, "label": "a"},
            {"id": "b", "type": "rect", "x": 110, "y": 20, "w": 70, "h": 40, "label": "b"}],
            "edges": [{"from": "a", "to": "b"}], "caption": caption}

        # the tooth bites in isolation: check_caption alone denies with dual coding
        issues = []
        qa.check_caption(spec, issues)
        deny_principles = {p for sev, p, _m, c in issues if sev == "error" and c == "caption"}
        self.assertIn("dual coding", deny_principles,
                      "check_caption must refuse an un-fittable caption, citing dual coding")

        # and the full gate refuses it (exit 2)
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "overflow.json"
            p.write_text(json.dumps(spec), encoding="utf-8")
            r = _run_qa(p)
        self.assertEqual(r.returncode, 2, "the un-fittable caption passed the gate")
        self.assertIn("dual coding", r.stderr.lower())
        self.assertIn("caption", r.stderr.lower())

    def test_single_line_caption_is_byte_identical_to_unwrapped(self):
        # a caption that already fits on one line must render exactly as the
        # pre-wrap form did (keeps short-caption fixtures unchanged).
        spec = {"size": [1200, 360], "caption": "short caption that fits on one line"}
        rendered = compose.render_caption(spec)
        expected = (
            '<text x="32" y="342" '
            "font-family='" + compose.FONT_STACK + "' font-size=\"12\" "
            "fill=\"" + compose.PALETTE["muted"] + "\">"
            "short caption that fits on one line</text>"
        )
        self.assertEqual(rendered, expected,
                         "a single-line caption must be byte-identical to the un-wrapped output")


if __name__ == "__main__":
    unittest.main()

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


if __name__ == "__main__":
    unittest.main()

"""Tests for the viewer's cube mathematics against the group's own laws:
each generator has order 4, the sexy move has order 6, F/B flip exactly the
four edges they move while U/D/L/R flip none, the EO/CO parity invariants
hold along random words, and any word followed by its inverse returns to
the solved state string from cube-alphabet.md §7.

The cube math lives in a pure block (CUBE_MATH markers) inside
glyphs/viewer.html — no DOM, no registry — so it can be extracted and run
under node. Skipped when node is unavailable."""

import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from glyphs import knoll

VIEWER = REPO / "glyphs" / "viewer.html"

ASSERTIONS = """
function assert(c, msg){ if(!c){ console.error("FAIL: " + msg); process.exit(1); } }
let ps = newPieces();
assert(stateStringOf(ps) === SOLVED_STRING, "solved at start");
assert(SOLVED_STRING === "GHIJKLMNOPQR | 000000000000 | STUVWXYZ | 00000000",
       "solved string matches cube-alphabet.md section 7");
for (const f of ["U","D","L","R","F","B"]) {
  ps = newPieces();
  for (let i = 0; i < 4; i++) applyMoveTo(ps, f, 1);
  assert(stateStringOf(ps) === SOLVED_STRING, f + "^4 = identity");
}
ps = newPieces();
for (let i = 0; i < 6; i++) { applyMoveTo(ps,"R",1); applyMoveTo(ps,"U",1);
                              applyMoveTo(ps,"R",-1); applyMoveTo(ps,"U",-1); }
assert(stateStringOf(ps) === SOLVED_STRING, "(R U R' U')^6 = identity");
for (const f of ["F","B"]) {
  ps = newPieces(); applyMoveTo(ps, f, 1);
  assert(stateStringOf(ps).split(" | ")[1].split("").filter(b => b === "1").length === 4,
         f + " flips exactly 4 edges");
}
for (const f of ["U","D","L","R"]) {
  ps = newPieces(); applyMoveTo(ps, f, 1);
  assert(stateStringOf(ps).split(" | ")[1] === "000000000000",
         f + " preserves edge orientation");
}
ps = newPieces(); const word = [];
for (let i = 0; i < 300; i++) {
  const f = "UDLRFB"[Math.floor(Math.random() * 6)], d = Math.random() < .5 ? 1 : -1;
  word.push([f, d]); applyMoveTo(ps, f, d);
  const parts = stateStringOf(ps).split(" | ");
  assert(parts[1].split("").reduce((a, b) => a + +b, 0) % 2 === 0, "EO sum even");
  assert(parts[3].split("").reduce((a, b) => a + +b, 0) % 3 === 0, "CO sum divisible by 3");
}
for (const [f, d] of word.reverse()) applyMoveTo(ps, f, -d);
assert(stateStringOf(ps) === SOLVED_STRING, "inverse word returns to solved");
console.log("ok");
"""


def cube_math_block():
    html = VIEWER.read_text(encoding="utf-8")
    m = re.search(r"/\*CUBE_MATH_START\*/(.*?)/\*CUBE_MATH_END\*/", html, re.S)
    return m.group(1) if m else None


class CubeMathSyncTest(unittest.TestCase):
    """Pure-Python checks: the JS block exists and its piece tables match
    the generator's (single source of truth is cube-alphabet.md §7)."""

    def test_block_present_and_pure(self):
        block = cube_math_block()
        self.assertIsNotNone(block, "CUBE_MATH block missing from viewer.html")
        for forbidden in ("document.", "REGISTRY", "window."):
            self.assertNotIn(forbidden, block)

    def test_js_tables_match_knoll(self):
        block = cube_math_block()
        e = re.search(r"CUBIES_E = \[(.*?)\]", block).group(1)
        c = re.search(r"CUBIES_C = \[(.*?)\]", block).group(1)
        self.assertEqual(re.findall(r'"(\w+)"', e), knoll.CUBE_EDGES)
        self.assertEqual(re.findall(r'"(\w+)"', c), knoll.CUBE_CORNERS)


@unittest.skipUnless(shutil.which("node"), "node not available")
class CubeGroupLawTest(unittest.TestCase):
    def test_group_laws_under_node(self):
        block = cube_math_block()
        self.assertIsNotNone(block)
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
            f.write(block + ASSERTIONS)
            path = f.name
        r = subprocess.run(["node", path], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr or r.stdout)
        self.assertIn("ok", r.stdout)


# --------------------------------------------------------- descent (0029)

def frame_math_block():
    html = VIEWER.read_text(encoding="utf-8")
    m = re.search(r"/\*FRAME_MATH_START\*/(.*?)/\*FRAME_MATH_END\*/", html, re.S)
    return m.group(1) if m else None


FRAME_ASSERTIONS = """
function assert(c, msg){ if(!c){ console.error("FAIL: " + msg); process.exit(1); } }
const reg = {
  placements: { S: { status: "PROPOSED, every score MODEL-GUESSED", cells: {
    Seam:  { coord: [0,0,0],  cell: "center", rationale: "boundary in all three" },
    State: { coord: [1,1,1],  cell: "corner", rationale: "as the outside reads it" } } } },
  term_frames: { frames: { B: [
    { d: [0,0,0],  slot: "center", kind: "self", label: "B", gloss: "the keystone" },
    { d: [1,0,0],  slot: "face",   kind: "decided", label: "x+", gloss: "held" } ] } },
  lexicon: {
    frames: { B: { pivot_candidate: "Basis", pivot_status: "OPEN" } },
    interstitial: { pivot_candidate: "Interstice",
                    kinds: { corner: { terms: ["Centroid"] } } } },
};
// a placed frame: words land by coordinate, status PROPOSED
const s = frameVocabOf(reg, "S");
assert(s.byHome["0,0,0"].text === "Seam", "S center carries Seam");
assert(s.byHome["1,1,1"].text === "State", "S corner carries State");
assert(s.byHome["1,1,1"].status === "PROPOSED", "placed words stay PROPOSED");
// a letter frame: term slots by offset; the basin pivot rides the center
// as a named hole, never a settled occupant
const b = frameVocabOf(reg, "B");
assert(b.byHome["0,0,0"].text === "Basis", "B center carries the pivot candidate");
assert(b.byHome["0,0,0"].status === "OPEN", "pivot candidate is OPEN");
assert(b.byHome["1,0,0"].text === "x+", "term slots ride their offsets");
// the void: interstitial — only the center speaks; cell assignment is OPEN
const v = frameVocabOf(reg, "\\u2298");
assert(v.byHome["0,0,0"].text === "Interstice", "void center carries Interstice");
assert(Object.keys(v.byHome).length === 1, "interstitial cells stay unassigned");
assert(v.pools.corner.terms[0] === "Centroid", "kind pools surface in the panel");
// displacement is counted from the pairing, not invented
const ps = [{ home: [0,0,1], cell: [0,0,1] }, { home: [1,0,0], cell: [0,1,0] }];
assert(displacedOf(ps) === 1, "one piece away from home");
console.log("ok");
"""


def shell_only():
    html = VIEWER.read_text(encoding="utf-8")
    return re.sub(r"/\*GLYPH_DATA_START\*/.*?/\*GLYPH_DATA_END\*/", "",
                  html, flags=re.S)


class FrameMathSyncTest(unittest.TestCase):
    """The descent vocabulary lives in its own pure block; the viewer shell
    honors the spec: placements come from the registry (never hardcoded),
    the conversation-invalidated features are gone, the index exists."""

    def test_block_present_and_pure(self):
        block = frame_math_block()
        self.assertIsNotNone(block, "FRAME_MATH block missing from viewer.html")
        for forbidden in ("document.", "window.", "REGISTRY."):
            self.assertNotIn(forbidden, block)

    def test_no_hardcoded_placements_in_shell(self):
        shell = shell_only()
        # placed words may appear only via the data block; the shell reads
        # them through the registry's placements section
        self.assertNotIn('"Substrate"', shell)
        self.assertIn("reg.placements", shell)

    def test_invalidated_features_removed_and_spec_features_present(self):
        shell = shell_only()
        for gone in ("bTrioSpot", "bCascade", "cascadeStages", "pTrioBody"):
            self.assertNotIn(gone, shell, gone)
        for present in ("bOntabet", "indexOntabetHTML", "indexBasinHTML",
                        "ontSyllables", "renderIndex", "function descend",
                        "function ascend", "renderCrumbs", "frameVocabOf",
                        "displacedOf", "max-width: 700px"):
            self.assertIn(present, shell, present)


@unittest.skipUnless(shutil.which("node"), "node not available")
class FrameVocabLawTest(unittest.TestCase):
    def test_frame_vocab_under_node(self):
        block = frame_math_block()
        self.assertIsNotNone(block)
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False,
                                         encoding="utf-8") as f:
            f.write(block + FRAME_ASSERTIONS)
            path = f.name
        r = subprocess.run(["node", path], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr or r.stdout)
        self.assertIn("ok", r.stdout)

    def test_syllabary_is_48(self):
        # the 48-word syllabary derives in-browser: 8 corners × 3! axis
        # orders, each spelling a 6→5→4→3 bit staircase
        letters = knoll.derive_polysheaf_lettering()
        corners = [c for c in letters if knoll.cell_kind(c) == "corner"]
        self.assertEqual(len(corners) * 6, 48)


if __name__ == "__main__":
    unittest.main()

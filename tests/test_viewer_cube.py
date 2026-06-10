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


if __name__ == "__main__":
    unittest.main()

"""Tests for the glyph knolling generator against its own discipline:
the derivation reproduces every doc-pinned letter; both letterings are
bijections over the 27-cell solid; outputs are idempotent; the viewer's
data block stays in sync with registry.json; the grip ledger parses live."""

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from glyphs import knoll


class LetteringTest(unittest.TestCase):
    def setUp(self):
        self.letters = knoll.derive_polysheaf_lettering()
        self.by_letter = {v: k for k, v in self.letters.items()}

    def test_doc_pins_reproduced(self):
        # the six letters the worked example states outright
        self.assertEqual(self.by_letter["A"], (-1, -1, -1))
        self.assertEqual(self.by_letter["E"], (1, -1, -1))
        self.assertEqual(self.by_letter["H"], (1, 1, 1))
        self.assertEqual(self.by_letter["I"], (0, -1, -1))
        self.assertEqual(self.by_letter["M"], (-1, 0, -1))
        self.assertEqual(self.by_letter["Q"], (-1, -1, 0))

    def test_bijection_26_letters_center_unlettered(self):
        self.assertEqual(len(self.letters), 26)
        self.assertEqual(sorted(self.letters.values()),
                         [chr(ord("A") + i) for i in range(26)])
        self.assertNotIn((0, 0, 0), self.letters)

    def test_kind_bands(self):
        # corners A-H, edges I-T, faces U-Z
        for letter, kind in [("A", "corner"), ("H", "corner"),
                             ("I", "edge"), ("T", "edge"),
                             ("U", "face"), ("Z", "face")]:
            self.assertEqual(knoll.cell_kind(self.by_letter[letter]), kind)

    def test_antipode_is_involution(self):
        # letter -> antipode letter -> antipode letter lands back home,
        # with no fixed points among the 26 (only the center is its own)
        anti = {letter: self.letters[tuple(-v for v in c)]
                for c, letter in self.letters.items()}
        for letter in self.letters.values():
            self.assertEqual(anti[anti[letter]], letter)
            self.assertNotEqual(anti[letter], letter)
        # the doc's named pair: global antipode of A is H
        self.assertEqual(anti["A"], "H")

    def test_edge_I_is_seam_A_E(self):
        # the doc's load-bearing example: edge I = seam(A, E)
        seam = [self.letters[s] for s in knoll.seam_of((0, -1, -1))]
        self.assertEqual(seam, ["A", "E"])

    def test_corner_A_requests_I_M_Q_in_axis_order(self):
        req = [self.letters[r] for r in knoll.requests((-1, -1, -1))]
        self.assertEqual(req, ["I", "M", "Q"])

    def test_trio_is_the_seam_star_of_corner_E(self):
        # the registry's derived reading: S, I, O are exactly the three
        # seams corner E = (+,−,−) requests — one per axis
        req = [self.letters[r] for r in knoll.requests((1, -1, -1))]
        self.assertEqual(req, ["I", "O", "S"])

    def test_cascade_terminates_at_center(self):
        # center requests nothing; everything else requests something
        self.assertEqual(knoll.requests((0, 0, 0)), [])
        for c in knoll.ternary_cells():
            if c != (0, 0, 0):
                self.assertTrue(knoll.requests(c))


class CubeAlphabetTest(unittest.TestCase):
    def test_table_matches_doc_section_7(self):
        # spot-check the pinned rows of the bijection table
        table = (knoll.CUBE_CENTERS + knoll.CUBE_EDGES + knoll.CUBE_CORNERS)
        self.assertEqual(len(table), 26)
        self.assertEqual(table[0], "U")        # A
        self.assertEqual(table[8], "UB")       # I
        self.assertEqual(table[14], "FR")      # O
        self.assertEqual(table[18], "UFR")     # S

    def test_face_colors_match_doc_table(self):
        # §7 pins them in prose: Up (white), Down (yellow), Left (orange),
        # Right (red), Front (green), Back (blue)
        self.assertEqual(knoll.CUBE_FACE_COLORS,
                         {"U": "white", "D": "yellow", "L": "orange",
                          "R": "red", "F": "green", "B": "blue"})
        text = (REPO / "docs/phase-2/cube-alphabet.md").read_text(encoding="utf-8")
        for face, color in knoll.CUBE_FACE_COLORS.items():
            self.assertIn(f"({color})", text)

    def test_home_slots_cover_the_27_cell_solid(self):
        coords = {knoll.cubie_coord(n) for n in
                  knoll.CUBE_CENTERS + knoll.CUBE_EDGES + knoll.CUBE_CORNERS}
        self.assertEqual(len(coords), 26)
        self.assertNotIn((0, 0, 0), coords)  # the spindle is not a piece


class RegistryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reg = knoll.build_registry()

    def test_pins_still_present_in_docs(self):
        # build_registry() raises on drift; reaching here is the assertion,
        # but check one source citation is a real line of the live doc
        a = next(c for c in self.reg["letterings"]["polysheaf"]["cells"]
                 if c["letter"] == "A")
        doc, line = a["source"].rsplit(":", 1)
        text = (REPO / doc).read_text(encoding="utf-8").splitlines()
        self.assertIn("A = (−,−,−)", text[int(line) - 1])

    def test_every_entry_carries_provenance(self):
        statuses = {"PINNED", "DERIVED", "MINTED", "OPEN", "SETTLED", "DEAD"}
        for lettering in self.reg["letterings"].values():
            for cell in lettering["cells"]:
                self.assertIn(cell["status"], statuses)
                self.assertTrue(cell["source"])
        for term in self.reg["terms"]:
            self.assertIn(term["status"], statuses)
            self.assertTrue(term["source"])

    def test_grip_ledger_parsed_live(self):
        names = {t["term"] for t in self.reg["terms"]}
        for expected in ("Ontum", "onta", "Keystone", "Cant", "Drift",
                         "Site", "Seam", "Atlas", "Ontogram"):
            self.assertIn(expected, names)

    def test_trio_is_open_with_three_readings(self):
        trio = self.reg["trio"]
        self.assertEqual(trio["status"], "OPEN")
        self.assertEqual(len(trio["readings"]), 3)
        # the derived reading spans the basis: one seam per axis
        poly = {c["letter"]: c for c in
                self.reg["letterings"]["polysheaf"]["cells"]}
        self.assertEqual({poly[g]["axis"] for g in ("S", "I", "O")},
                         {"x", "y", "z"})

    def test_core27_inventory(self):
        c27 = self.reg["core27"]
        self.assertEqual(c27["status"], "MINTED")
        self.assertTrue(c27["non_example"])
        self.assertEqual(len(c27["terms"]), 27)
        # the openness gradient: corner 7/19, edge 11/15, face 17/9, ⊘ 26/0
        expect = {"corner": (7, 19), "edge": (11, 15),
                  "face": (17, 9), "center": (26, 0)}
        for t in c27["terms"]:
            inf, opn = expect[t["global_role"]]
            self.assertEqual(t["neighbors_in_frame"], inf, t["glyph"])
            self.assertEqual(t["open_slots"], opn, t["glyph"])
        # the root closes completely: its frame is the whole specimen
        root = next(t for t in c27["terms"] if t["glyph"] == "⊘")
        self.assertEqual(root["open_slots"], 0)

    def test_dim_codim_split_recorded(self):
        # finding seam.codim-wording: both numbers kept per cell
        for cell in self.reg["letterings"]["polysheaf"]["cells"]:
            self.assertEqual(cell["dim"] + cell["codim"], 3)
            self.assertEqual(cell["dim"],
                             sum(1 for v in cell["coord"] if v == 0))


class OutputTest(unittest.TestCase):
    def run_knoll(self):
        return subprocess.run(
            [sys.executable, str(REPO / "glyphs" / "knoll.py")],
            capture_output=True, text=True)

    def test_idempotent_and_synced(self):
        first = self.run_knoll()
        self.assertEqual(first.returncode, 0, first.stderr)
        before = {p: (REPO / "glyphs" / p).read_bytes()
                  for p in ("registry.json", "knolling.md", "viewer.html")}
        second = self.run_knoll()
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertIn("byte-identical", second.stdout)
        for p, data in before.items():
            self.assertEqual((REPO / "glyphs" / p).read_bytes(), data, p)

    def test_viewer_data_block_equals_registry(self):
        html = (REPO / "glyphs" / "viewer.html").read_text(encoding="utf-8")
        m = re.search(r"const REGISTRY = (.*?);\n/\*GLYPH_DATA_END\*/",
                      html, re.S)
        self.assertIsNotNone(m, "GLYPH_DATA block missing from viewer.html")
        embedded = json.loads(m.group(1))
        on_disk = json.loads(
            (REPO / "glyphs" / "registry.json").read_text(encoding="utf-8"))
        self.assertEqual(embedded, on_disk)


if __name__ == "__main__":
    unittest.main()

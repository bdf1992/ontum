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

    def test_term_frames_contract_v0(self):
        tf = self.reg["term_frames"]["frames"]
        self.assertEqual(len(tf), 27)
        for letter, slots in tf.items():
            self.assertEqual(len(slots), 27, letter)
            kinds = {tuple(s["d"]): s for s in slots}
            self.assertEqual(kinds[(0, 0, 0)]["kind"], "self")
        # the worked example: S (+,−,0)
        s = {tuple(sl["d"]): sl for sl in tf["S"]}
        self.assertEqual((s[(0, 0, -1)]["kind"], s[(0, 0, -1)]["label"]), ("seam", "E"))
        self.assertEqual((s[(0, 0, 1)]["kind"], s[(0, 0, 1)]["label"]), ("seam", "F"))
        self.assertEqual((s[(-1, 0, 0)]["kind"], s[(-1, 0, 0)]["label"]), ("request", "W"))
        self.assertEqual((s[(0, 1, 0)]["kind"], s[(0, 1, 0)]["label"]), ("request", "V"))
        self.assertEqual(s[(1, 0, 0)]["kind"], "decided")
        self.assertEqual(s[(0, -1, 0)]["kind"], "decided")
        # corners are settled facts; edges carry relations then open slots
        self.assertEqual(
            sum(1 for sl in tf["S"] if sl["slot"] == "corner" and sl["kind"] == "fact"), 8)
        glosses = " ".join(sl["gloss"] for sl in tf["S"] if sl["slot"] == "edge")
        self.assertIn("antipode", glosses)
        self.assertIn("occupant", glosses)
        self.assertIn("trio", glosses)
        self.assertIn("open", glosses)
        # the root: all six faces are seams, nothing decided, no antipode
        root_faces = [sl for sl in tf["⊘"] if sl["slot"] == "face"]
        self.assertTrue(all(sl["kind"] == "seam" for sl in root_faces))
        self.assertNotIn("antipode",
                         " ".join(sl["gloss"] for sl in tf["⊘"]))

    def test_dim_codim_split_recorded(self):
        # finding seam.codim-wording: both numbers kept per cell
        for cell in self.reg["letterings"]["polysheaf"]["cells"]:
            self.assertEqual(cell["dim"] + cell["codim"], 3)
            self.assertEqual(cell["dim"],
                             sum(1 for v in cell["coord"] if v == 0))


class IncidenceLawTest(unittest.TestCase):
    """Basin v1's two graded fans, recomputed here independently of the
    generator's own verification."""

    def test_sizes_by_kind(self):
        for c in knoll.ternary_cells():
            dim = sum(1 for v in c if v == 0)
            self.assertEqual(len(knoll.closure_of(c)), 3 ** dim, c)
            self.assertEqual(len(knoll.star_of(c)), 2 ** (3 - dim), c)

    def test_graded_census_is_125_both_ways(self):
        cells = knoll.ternary_cells()
        self.assertEqual(sum(len(knoll.closure_of(c)) for c in cells), 125)
        self.assertEqual(sum(len(knoll.star_of(c)) for c in cells), 125)

    def test_closure_star_duality(self):
        for c in knoll.ternary_cells():
            for d in knoll.closure_of(c):
                self.assertIn(c, knoll.star_of(d))
            for u in knoll.star_of(c):
                self.assertIn(c, knoll.closure_of(u))

    def test_worked_example_S(self):
        # the basin's own worked utterance: S in full is E·F·S; S's star
        # opens to W (x), V (y), and the void
        letters = knoll.derive_polysheaf_lettering()
        s = next(c for c, l in letters.items() if l == "S")
        name = lambda c: letters.get(c, knoll.CENTER_GLYPH)
        self.assertEqual({name(d) for d in knoll.closure_of(s)},
                         {"E", "F", "S"})
        self.assertEqual({name(d) for d in knoll.star_of(s)},
                         {"S", "W", "V", "⊘"})

    def test_axis_code_is_complete_prefix_code(self):
        # memo P8: Kraft sum exactly 1; spelling sheds one bit per open-step
        bits = [knoll.axis_code_bits(c) for c in knoll.ternary_cells()]
        self.assertEqual(sum(2 ** -b for b in bits), 1.0)
        for c in knoll.ternary_cells():
            for r in knoll.requests(c):
                self.assertEqual(knoll.axis_code_bits(r),
                                 knoll.axis_code_bits(c) - 1)


class LexiconTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lex = knoll.build_lexicon()

    def test_basin_frames_parsed(self):
        # 23 letter frames (S, I, O are bdo's, not restated) + the parent ⊘
        frames = self.lex["frames"]
        self.assertEqual(len(frames), 24)
        for absent in ("S", "I", "O"):
            self.assertNotIn(absent, frames)
        self.assertEqual(frames["A"]["pivot_candidate"], "Anchor")
        self.assertEqual(frames["⊘"]["pivot_candidate"], "Basis")
        self.assertIsNone(frames["X"]["pivot_candidate"])
        # pivots ride as named holes, never pre-stamped
        for fr in frames.values():
            self.assertEqual(fr["pivot_status"], "OPEN")

    def test_census_measured_against_claim(self):
        # the artifact claims 588/60; the document itself holds 583/65 —
        # the divergence is a recorded finding, never an edit
        cen = self.lex["census"]
        self.assertEqual(cen["claimed"], {"filled": 588, "open": 60})
        self.assertEqual(cen["measured"], {"filled": 583, "open": 65})
        ids = {f["id"] for f in self.lex["findings"]}
        self.assertIn("basin.census-arithmetic", ids)
        self.assertIn("basin.sio-not-restated", ids)

    def test_density_is_measured_fill_rate(self):
        x = self.lex["frames"]["X"]
        self.assertEqual(x["filled"], 5)
        self.assertEqual(x["density"]["rate"], round(5 / 27, 4))
        self.assertEqual(x["density"]["status"], "MEASURED")
        self.assertEqual(self.lex["frames"]["W"]["filled"], 27)

    def test_collisions_knolled_not_deduped(self):
        col = self.lex["collisions"]
        self.assertEqual(col["Basis"], ["B", "⊘"])
        self.assertEqual(col["Frame"], ["F", "⊘"])
        self.assertIn("interstitial", col["Keystone"])

    def test_schema_columns_exist_and_are_honestly_open(self):
        # BUILD-2: the columns the measures will fill — present, unfilled
        for fr in self.lex["frames"].values():
            self.assertIsNone(fr["placements"])
            self.assertEqual(fr["attestations"], [])
            self.assertIsNone(fr["chips"])
            self.assertIsNone(fr["sc"])
            self.assertIn("PIN-6", fr["empties"]["typing"])

    def test_interstitial_27(self):
        kinds = self.lex["interstitial"]["kinds"]
        self.assertEqual({k: len(v["terms"]) for k, v in kinds.items()},
                         {"corner": 8, "edge": 12, "face": 6, "center": 1})
        self.assertEqual(kinds["center"]["terms"], ["Interstice"])
        self.assertIn("Cant", kinds["edge"]["terms"])


class PlacementGateTest(unittest.TestCase):
    """The §10 test at the placements layer: two locally-fine placements
    refuse to fit, and the gate notices — loudly, with a receipt."""

    @classmethod
    def setUpClass(cls):
        cls.placed = json.loads(
            (REPO / "language" / "s-frame-placements.json")
            .read_text(encoding="utf-8"))["placements"]

    def test_real_artifact_passes(self):
        by_coord = knoll.validate_placements(self.placed)
        self.assertEqual(len(by_coord), 27)

    def test_address_collision_refused(self):
        # Span and Semantics each sit fine alone; both claiming Span's cell
        # must refuse (this is the falsifier's one live refusal, frozen)
        tampered = json.loads(json.dumps(self.placed))
        tampered["Semantics"]["coord"] = tampered["Span"]["coord"]
        tampered["Semantics"]["cell"] = tampered["Span"]["cell"]
        with self.assertRaises(SystemExit) as ctx:
            knoll.validate_placements(tampered)
        self.assertIn("address collision", str(ctx.exception))
        self.assertIn("Span", str(ctx.exception))

    def test_kind_mismatch_refused(self):
        tampered = json.loads(json.dumps(self.placed))
        tampered["State"]["cell"] = "edge"  # (+,+,+) is a corner
        with self.assertRaises(SystemExit) as ctx:
            knoll.validate_placements(tampered)
        self.assertIn("State", str(ctx.exception))

    def test_short_frame_refused(self):
        tampered = json.loads(json.dumps(self.placed))
        del tampered["Shadow"]
        with self.assertRaises(SystemExit):
            knoll.validate_placements(tampered)

    def test_loaded_as_proposed_with_seed_chips(self):
        letters = knoll.derive_polysheaf_lettering()
        s = knoll.build_placements(letters)["S"]
        self.assertEqual(s["census"],
                         {"corner": 8, "edge": 12, "face": 6, "center": 1})
        self.assertEqual(s["chips"]["seed_total"], 64)
        self.assertIsNone(s["chips"]["tally"])  # three columns, never fused
        self.assertIsNone(s["sc"])
        seam = s["cells"]["Seam"]
        self.assertEqual(seam["coord"], [0, 0, 0])
        self.assertEqual(seam["local_letter"], "⊘")
        for p in s["cells"].values():
            self.assertIn("MODEL-GUESSED", p["status"])


class DemotionTest(unittest.TestCase):
    def test_minted_without_non_example_renders_open(self):
        terms = [
            {"term": "grounded", "status": "MINTED", "non_example": "a real one"},
            {"term": "hole-in-disguise", "status": "MINTED", "non_example": None},
            {"term": "settled", "status": "SETTLED", "non_example": None},
        ]
        demoted = knoll.demote_unfalsified(terms)
        self.assertEqual(demoted, ["hole-in-disguise"])
        self.assertEqual(terms[0]["status"], "MINTED")
        self.assertEqual(terms[1]["status"], "OPEN")
        self.assertEqual(terms[2]["status"], "SETTLED")

    def test_live_ledger_carries_no_unfalsified_minted_terms(self):
        # the registry's demotions list is empty today; if a future ledger
        # edit mints without a falsifier, the demotion shows up visibly
        reg = knoll.build_registry()
        self.assertEqual(reg["demotions"], [])
        for t in reg["terms"]:
            if t["status"] == "MINTED":
                self.assertTrue(t.get("non_example"), t["term"])


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

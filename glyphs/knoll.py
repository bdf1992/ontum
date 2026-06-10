#!/usr/bin/env python3
"""Knoll the glyph systems: derive, validate, and lay out the repo's semiotics.

Reads docs/phase-2/ as source material (the vault stays read-only — this
script never writes there) and regenerates the knolled inventory:

  - glyphs/registry.json   the machine-readable inventory; every entry
                           carries a provenance status (etymontoken style)
  - glyphs/knolling.md     the human-readable flat-lay
  - glyphs/viewer.html     data block refreshed between GLYPH_DATA markers

Provenance statuses, in the grip-ledger's own discipline:

  PINNED   — quoted verbatim from a phase-2 doc; the source line is cited and
             re-checked on every run (doc drift fails loudly, not silently).
  DERIVED  — produced by a stated rule from pinned anchors; the rule is
             recorded next to the value.
  MINTED   — coined by a knolling session; provisional until bdo pins it
             with a non-example.
  OPEN     — a named hole; the slot exists, the referent does not yet.

Stdlib only. Idempotent: re-running over unchanged docs is byte-identical.
"""

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DOCS = REPO / "docs" / "phase-2"
GLYPHS = REPO / "glyphs"

POLYSHEAF_DOC = "docs/phase-2/autojective-polysheaf.md"
CUBE_DOC = "docs/phase-2/cube-alphabet.md"
LEDGER_DOC = "docs/phase-2/ontum-evolution.md"
ONTOGRAM_DOC = "docs/phase-2/ontogrammatic-systems.md"

# Unicode minus, as the phase-2 docs write it.
MINUS = "−"
SIGN = {-1: MINUS, 0: "0", 1: "+"}
AXES = ("x", "y", "z")
CENTER_GLYPH = "⊘"  # ⊘ — the obscured wildcard / null slot
SPINDLE_GLYPH = "∅"  # ∅ — the spindle: not a piece at all


def coord_str(c):
    return "(" + ",".join(SIGN[v] for v in c) + ")"


# ---------------------------------------------------------------------------
# Pins: anchors quoted from the docs. Each pin is (letter, must-co-occur
# substring, doc). validate_pins() re-checks them against the live doc text
# every run, so the derivation can never drift silently away from the vault.
# ---------------------------------------------------------------------------

POLYSHEAF_PINS = [
    ("A", "A = (−,−,−)", POLYSHEAF_DOC),
    ("E", "(+,−,−) = E", POLYSHEAF_DOC),
    ("H", "H = (+,+,+)", POLYSHEAF_DOC),
    ("I", "(0,−,−)", POLYSHEAF_DOC),
    ("M", "(−,0,−)", POLYSHEAF_DOC),
    ("Q", "(−,−,0)", POLYSHEAF_DOC),
]

CUBE_PINS = [
    ("A", "| A | U center |", CUBE_DOC),
    ("I", "| I | UB |", CUBE_DOC),
    ("O", "| O | FR |", CUBE_DOC),
    ("S", "| S | UFR |", CUBE_DOC),
    ("solved", "GHIJKLMNOPQR | 000000000000 | STUVWXYZ | 00000000", CUBE_DOC),
]


def read_doc(rel):
    return (REPO / rel).read_text(encoding="utf-8")


def find_line(text, needle):
    """1-based line number of the first line containing needle, or None."""
    for i, line in enumerate(text.splitlines(), 1):
        if needle in line:
            return i
    return None


def validate_pins(doc_texts):
    """Every pin must still exist in its doc. Drift is reported, not papered."""
    missing = []
    pin_lines = {}
    for letter, needle, doc in POLYSHEAF_PINS + CUBE_PINS:
        n = find_line(doc_texts[doc], needle)
        if n is None:
            missing.append(f"  {doc}: pin {letter!r} ({needle!r}) not found")
        else:
            pin_lines[(doc, letter)] = n
    if missing:
        raise SystemExit(
            "doc drift — pinned anchors no longer present:\n"
            + "\n".join(missing)
            + "\nThe vault changed under the derivation. Re-read the doc, "
            "update PINS to the new anchors, and re-run."
        )
    return pin_lines


# ---------------------------------------------------------------------------
# Lettering 1 — polysheaf ternary lettering (addresses).
# The worked example pins A,E,H (corners), I,M,Q (first edge per axis).
# Stated rule, DERIVED for the rest: cells grouped by kind (corners, edges,
# faces), edges and faces grouped by their open/decided axis in x,y,z order,
# ties broken by natural sign order (− < 0 < +) on the remaining coordinates.
# This rule reproduces all six pins; everything else inherits DERIVED status.
# ---------------------------------------------------------------------------

POLYSHEAF_RULE = (
    "corners A–H, edges I–T, faces U–Z; edges grouped by open "
    "axis (x, then y, then z), faces by their normal axis; within a group, "
    "natural sign order (− < 0 < +) on the remaining coordinates; the "
    "all-zeros center is the obscured wildcard ⊘, letterless"
)


def ternary_cells():
    return [(x, y, z) for x in (-1, 0, 1) for y in (-1, 0, 1) for z in (-1, 0, 1)]


def cell_kind(c):
    zeros = sum(1 for v in c if v == 0)
    return {0: "corner", 1: "edge", 2: "face", 3: "center"}[zeros]


def open_axes(c):
    return [AXES[i] for i, v in enumerate(c) if v == 0]


def derive_polysheaf_lettering():
    """coord -> letter for the 26 lettered cells, by the stated rule."""
    corners = sorted(c for c in ternary_cells() if cell_kind(c) == "corner")
    edges = sorted(
        (c for c in ternary_cells() if cell_kind(c) == "edge"),
        key=lambda c: ([i for i, v in enumerate(c) if v == 0][0], c),
    )
    faces = sorted(
        (c for c in ternary_cells() if cell_kind(c) == "face"),
        key=lambda c: ([i for i, v in enumerate(c) if v != 0][0], c),
    )
    letters = {}
    for i, c in enumerate(corners):
        letters[c] = chr(ord("A") + i)  # A–H
    for i, c in enumerate(edges):
        letters[c] = chr(ord("I") + i)  # I–T
    for i, c in enumerate(faces):
        letters[c] = chr(ord("U") + i)  # U–Z
    return letters


def check_polysheaf_pins(letters):
    expect = {
        "A": (-1, -1, -1), "E": (1, -1, -1), "H": (1, 1, 1),
        "I": (0, -1, -1), "M": (-1, 0, -1), "Q": (-1, -1, 0),
    }
    by_letter = {v: k for k, v in letters.items()}
    bad = [
        f"  {l}: derived {coord_str(by_letter[l])}, doc pins {coord_str(c)}"
        for l, c in expect.items() if by_letter[l] != c
    ]
    if bad:
        raise SystemExit(
            "derivation no longer matches the doc's pinned letters:\n"
            + "\n".join(bad)
        )


def seam_of(c):
    """Cells reached by DECIDING one open axis — an edge's two endpoint
    corners, a face's four boundary edges, the center's six faces. The doc's
    move: 'an edge's own boundary is the two cells that decide its open
    axis'."""
    out = []
    for i, v in enumerate(c):  # axis order x, y, z — the doc's own ordering
        if v == 0:
            for s in (-1, 1):
                out.append(tuple(s if j == i else w for j, w in enumerate(c)))
    return out


def requests(c):
    """Cells reached by OPENING one decided axis — what this cell's
    seam-logic asks for next. Corner → 3 edges, edge → 2 faces, face →
    center, center → nothing (the loop closes at the void)."""
    out = []
    for i, v in enumerate(c):  # axis order x, y, z, so A requests I, M, Q
        if v != 0:
            out.append(tuple(0 if j == i else w for j, w in enumerate(c)))
    return out


def polysheaf_cells(letters, pin_lines):
    pinned = {"A", "E", "H", "I", "M", "Q"}
    cells = []
    for c, letter in sorted(letters.items(), key=lambda kv: kv[1]):
        kind = cell_kind(c)
        zeros = sum(1 for v in c if v == 0)
        axis = None
        if kind == "edge":
            axis = open_axes(c)[0]
        elif kind == "face":
            axis = [AXES[i] for i, v in enumerate(c) if v != 0][0]
        entry = {
            "letter": letter,
            "coord": list(c),
            "coord_str": coord_str(c),
            "cell": kind,
            "dim": zeros,           # count of zeros = open/undecided axes
            "codim": 3 - zeros,     # decided axes (see finding seam.codim-wording)
            "axis": axis,
            "antipode": letters[tuple(-v for v in c)],
            "seam_of": [letters[s] for s in seam_of(c)],
            "requests": [
                letters.get(r, CENTER_GLYPH) for r in requests(c)
            ],
            "status": "PINNED" if letter in pinned else "DERIVED",
        }
        if letter in pinned:
            entry["source"] = (
                f"{POLYSHEAF_DOC}:{pin_lines[(POLYSHEAF_DOC, letter)]}"
            )
        else:
            entry["source"] = "rule (see lettering.rule), anchored on the six pins"
        cells.append(entry)
    center = (0, 0, 0)
    cells.append({
        "letter": CENTER_GLYPH,
        "coord": [0, 0, 0],
        "coord_str": coord_str(center),
        "cell": "center",
        "dim": 3,
        "codim": 0,
        "axis": None,
        "antipode": CENTER_GLYPH,  # its own antipode: the fixed point
        "seam_of": [letters[s] for s in seam_of(center)],
        "requests": [],
        "status": "PINNED",
        "source": f"{POLYSHEAF_DOC}:111",
        "note": "the obscured wildcard — anchored by no pin, requests nothing; "
                "the null/generative slot where the cascade terminates",
    })
    return cells


# ---------------------------------------------------------------------------
# Lettering 2 — cube-alphabet piece lettering (occupants).
# cube-alphabet.md §7: centers A–F, edges G–R, corners S–Z, by piece type
# then standard face order U D L R F B. These letters name MOBILE PIECES,
# not fixed cells; the 3D placement below is each piece's home (solved) slot
# under the axis convention x: L−/R+, y: D−/U+, z: B−/F+ (a DERIVED choice).
# ---------------------------------------------------------------------------

CUBE_CENTERS = ["U", "D", "L", "R", "F", "B"]                      # A–F
# face colors as the §7 table pins them: "Up (white)", "Down (yellow)" …
CUBE_FACE_COLORS = {"U": "white", "D": "yellow", "L": "orange",
                    "R": "red", "F": "green", "B": "blue"}
CUBE_EDGES = ["UF", "UR", "UB", "UL", "DF", "DR", "DB", "DL",
              "FR", "FL", "BR", "BL"]                               # G–R
CUBE_CORNERS = ["UFR", "UFL", "UBR", "UBL", "DFR", "DFL", "DBR", "DBL"]  # S–Z

FACE_VECTOR = {
    "U": (0, 1, 0), "D": (0, -1, 0),
    "L": (-1, 0, 0), "R": (1, 0, 0),
    "F": (0, 0, 1), "B": (0, 0, -1),
}


def cubie_coord(name):
    x = y = z = 0
    for f in name:
        fx, fy, fz = FACE_VECTOR[f]
        x, y, z = x + fx, y + fy, z + fz
    return (x, y, z)


def cube_alphabet_cells(pin_lines):
    cells = []
    table = (
        [("center", n, 0) for n in CUBE_CENTERS]
        + [("edge", n, 2) for n in CUBE_EDGES]
        + [("corner", n, 3) for n in CUBE_CORNERS]
    )
    cube_pin_letters = {"A", "I", "O", "S"}
    for i, (piece, cubie, orientations) in enumerate(table):
        letter = chr(ord("A") + i)
        entry = {
            "letter": letter,
            "cubie": cubie,
            "piece": piece,
            "coord": list(cubie_coord(cubie)),
            "carries_state": piece != "center",
            "orientation_states": orientations,
            "status": "PINNED",
            "source": (
                f"{CUBE_DOC}:{pin_lines[(CUBE_DOC, letter)]}"
                if letter in cube_pin_letters
                else f"{CUBE_DOC} §7 (bijection table)"
            ),
        }
        if piece == "center":
            entry["face_color"] = CUBE_FACE_COLORS[cubie]
        cells.append(entry)
    cells.append({
        "letter": SPINDLE_GLYPH,
        "cubie": "spindle",
        "piece": "spindle",
        "coord": [0, 0, 0],
        "carries_state": False,
        "orientation_states": 0,
        "status": "PINNED",
        "source": f"{CUBE_DOC}:73",
        "note": "not a piece — the mechanism is a void with an axis through "
                "it; what enables rotation is the absence of a cubie",
    })
    return cells


# ---------------------------------------------------------------------------
# Terms — the semantic wing. The grip ledger is parsed live from
# ontum-evolution.md §8 so doc edits flow into the registry on re-run;
# the polysheaf/ontogrammatic primitives are quoted with cited lines.
# ---------------------------------------------------------------------------

def parse_grip_ledger(text):
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.startswith("## 8. Grip ledger"):
            start = i
            break
    if start is None:
        raise SystemExit(f"doc drift: grip ledger heading not found in {LEDGER_DOC}")
    terms = []
    for n in range(start + 1, len(lines)):
        line = lines[n]
        if line.startswith("## ") or line.startswith("---"):
            if terms:
                break
            continue
        if not line.startswith("|"):
            continue
        cols = [c.strip().strip("*") for c in line.strip("|").split("|")]
        if len(cols) < 4 or cols[0] in ("Term", "") or set(cols[0]) <= {"-"}:
            continue
        terms.append({
            "term": cols[0],
            "status": cols[1],
            "referent": cols[2],
            "non_example": cols[3].replace("—", "").strip() or None,
            "source": f"{LEDGER_DOC}:{n + 1}",
        })
    if not terms:
        raise SystemExit(f"doc drift: grip ledger table parsed empty in {LEDGER_DOC}")
    return terms


PRIMITIVES = [
    {
        "term": "Site",
        "status": "SETTLED",
        "referent": "A primitive treated as a local frame; holds its local "
                    "stalk (with dynamics), an inward encoding, axis/antipode "
                    "structure, and outgoing maps. Simultaneously a whole and a part.",
        "non_example": "A global object authored as its own file",
        "source": f"{POLYSHEAF_DOC}:37",
    },
    {
        "term": "Seam",
        "status": "SETTLED",
        "referent": "A primitive that is a join. Connects Sites and carries "
                    "the comparison between them as a cocycle. A Seam that "
                    "does not close is not a bug; it is data.",
        "non_example": "A boolean joined/not-joined flag",
        "source": f"{POLYSHEAF_DOC}:39",
    },
    {
        "term": "Atlas",
        "status": "SETTLED",
        "referent": "Not authored. The emergent index: the collection of "
                    "Sites and Seams plus their incidence. The whole is read "
                    "off the Atlas, never written as its own file.",
        "non_example": "A hand-maintained global map",
        "source": f"{POLYSHEAF_DOC}:41",
    },
    {
        "term": "Autojective",
        "status": "SETTLED",
        "referent": "Self-casting (thrown-by-itself): a structure that "
                    "generates its own slots and the constraint that shapes "
                    "what may fill them.",
        "non_example": "A projection with an external observer role",
        "source": f"{POLYSHEAF_DOC}:52",
    },
    {
        "term": "Spindle",
        "status": "SETTLED",
        "referent": "The 27th grid position, dead center: not a piece. A void "
                    "with an axis through it — what enables rotation is the "
                    "absence of a cubie.",
        "non_example": "A 27th cubie",
        "source": f"{CUBE_DOC}:73",
    },
    {
        "term": "The empty-center law",
        "status": "SETTLED",
        "referent": "Symbol systems work because their center is empty. The "
                    "mechanism is the negative space. Structure rotates "
                    "around an absence.",
        "non_example": "A token system whose semantics live inside one privileged symbol",
        "source": f"{CUBE_DOC}:81",
    },
    {
        "term": "Ontogram",
        "status": "SETTLED",
        "referent": "A typed form whose source, structure, and downstream "
                    "effects are all inspectable — the atomic unit of trust.",
        "non_example": "A generated artifact whose formation chain died in the conversation",
        "source": f"{ONTOGRAM_DOC}:107",
    },
    {
        "term": "The Machine",
        "status": "SETTLED",
        "referent": "The gating mechanism: certifies (never generates) "
                    "ontograms; six checks, three verdicts — admit, refuse, "
                    "instrumentation-needed.",
        "non_example": "A generator that grades its own output",
        "source": f"{ONTOGRAM_DOC}:166",
    },
]


# ---------------------------------------------------------------------------
# The S·I·O trio — the requested glyph review. No phase-2 doc defines the
# trio AS a trio; each lettering gives it a different referent, and the
# letterforms themselves suggest a third. All three readings are laid out;
# the pin (with non-example) is bdo's to place. Until then: OPEN.
# ---------------------------------------------------------------------------

def build_trio(poly_cells, cube_cells):
    poly = {c["letter"]: c for c in poly_cells}
    cube = {c["letter"]: c for c in cube_cells}
    return {
        "glyphs": ["S", "I", "O"],
        "status": "OPEN",
        "note": "Three candidate readings, knolled side by side. A grip needs "
                "a non-example; until bdo pins one reading (or mints a fourth), "
                "the trio is a named hole, not a referent.",
        "readings": [
            {
                "frame": "polysheaf (addresses)",
                "status": "DERIVED",
                "reading": {
                    "I": f"x-seam {poly['I']['coord_str']} = "
                         f"seam({','.join(poly['I']['seam_of'])})",
                    "O": f"y-seam {poly['O']['coord_str']} = "
                         f"seam({','.join(poly['O']['seam_of'])})",
                    "S": f"z-seam {poly['S']['coord_str']} = "
                         f"seam({','.join(poly['S']['seam_of'])})",
                },
                "gloss": "One seam per axis — I on x, O on y, S on z — and "
                         "all three share the corner E = (+,−,−): S·I·O is "
                         "exactly the request set of one Self, E's seam-star. "
                         "(The worked example's corner A requests I, M, Q; "
                         "the corner that requests I, O, S is E.) A seam "
                         "basis for the compression frame, issued by a "
                         "single point.",
            },
            {
                "frame": "cube-alphabet (occupants)",
                "status": "PINNED",
                "reading": {
                    "S": f"corner {cube['S']['cubie']} — the first corner, the "
                         "canonical home piece",
                    "I": f"edge {cube['I']['cubie']}",
                    "O": f"edge {cube['O']['cubie']}",
                },
                "gloss": "S leads the corner octave (S–Z); I and O are "
                         "edges. All three carry state — none is a stateless "
                         "anchor.",
            },
            {
                "frame": "letterform (semiotic)",
                "status": "MINTED",
                "reading": {
                    "O": "the ring: a stroke enclosing a void — the empty "
                         "center made visible; the spindle/wildcard drawn as "
                         "a glyph",
                    "I": "the stroke: one decided axis — a line, the minimal "
                         "edge; the unit presence",
                    "S": "the seam: one curve crossing between two lobes — "
                         "the join drawn as a glyph; also the initial of "
                         "Site, Seam, Self, settle, spindle",
                },
                "gloss": "I/O is additionally the binary pair — 1 and 0, two "
                         "stickers around a void (cube-alphabet §5) — and "
                         "S is the path between them. Ontology (O), "
                         "instance (I), seam (S): the fabric, a fiber, and "
                         "the stitch.",
            },
        ],
    }


# ---------------------------------------------------------------------------
# The Core 27 — bdo's leap (session 0009): "one term of those 27 glyphs ends
# up being the S/Void term for each letter; these are like our CORE 27
# operational terms." Each glyph, opened as its own local frame, occupies
# that frame's void — the keystone. Globally one void; locally every glyph
# voids its own center. Scale-recursive restatement of the cube principle:
# every Feature is the Token of its own subtree.
# ---------------------------------------------------------------------------

def build_core27(poly_cells):
    terms = []
    for c in poly_cells:
        in_frame = 1
        for v in c["coord"]:
            in_frame *= 3 if v == 0 else 2
        in_frame -= 1  # neighbors of the cell that stay inside {−,0,+}³
        entry = {
            "glyph": c["letter"],
            "coord_str": c["coord_str"],
            "global_role": c["cell"],
            "local_role": "keystone — the Self/void term of its own frame",
            "neighbors_in_frame": in_frame,
            "open_slots": 26 - in_frame,
        }
        if c["letter"] == CENTER_GLYPH:
            entry["note"] = ("the root: zero open slots — its local frame is "
                             "the entire specimen")
        terms.append(entry)
    return {
        "name": "Core 27",
        "status": "MINTED",
        "coined_by": "bdo — 'one term of those 27 glyphs ends up being the "
                     "S/Void term for each letter; these are like our CORE "
                     "27 operational terms' (glyph-knolling session 0009)",
        "principle": "Every glyph of the 27 is the Self/void term of its own "
                     "local frame: globally a cell among cells, locally the "
                     "keystone occupying its frame's empty center. The 27 "
                     "glyphs are therefore the system's core operational "
                     "terms — 26 letters and ⊘, each one anchoring a "
                     "neighborhood. Globally there is one void; locally, "
                     "every glyph voids its own center.",
        "gradient": "openness by kind — corner frames hold 7 neighbors (19 "
                    "slots open), edges 11/15, faces 17/9, and ⊘ 26/0: the "
                    "root's frame is the whole specimen and closes "
                    "completely.",
        "non_example": "A grip-ledger word without an address — cant, drift, "
                       "jective: operational vocabulary, but not core-27; "
                       "they have no cell and anchor no local frame.",
        "terms": terms,
    }


# ---------------------------------------------------------------------------
# Findings — seams between the docs that do not close. Per the polysheaf's
# own doctrine these are preserved as comparison structs, not "fixed":
# the vault is read-only, so findings are reported, never patched around.
# ---------------------------------------------------------------------------

FINDINGS = [
    {
        "id": "seam.lettering-collision",
        "kind": "non-closing seam, resolved as complementarity",
        "status": "MINTED",
        "between": [f"{CUBE_DOC} §7", f"{POLYSHEAF_DOC} (worked example)"],
        "observation": "The same 26 letters are assigned twice, incompatibly: "
                       "cube-alphabet gives A = U center / S = corner UFR; the "
                       "polysheaf gives A = corner (−,−,−) / "
                       "S = a z-edge. I and O are edges in both; A and S "
                       "change kind entirely.",
        "resolution": "Read as the (position, value) split both docs already "
                      "name (cube-alphabet §3): polysheaf letters name "
                      "fixed CELLS (addresses), cube-alphabet letters name "
                      "mobile PIECES (occupants). One alphabet for where, one "
                      "for what. A full state is a pairing of the two; the "
                      "solved cube is the canonical pairing. Held MINTED "
                      "until bdo admits or refuses the reading.",
    },
    {
        "id": "seam.codim-wording",
        "kind": "internal inconsistency (wording)",
        "status": "PINNED",
        "between": [f"{POLYSHEAF_DOC}:111", f"{POLYSHEAF_DOC}:115"],
        "observation": "Line 111 says 'the count of zeros in a cell's "
                       "coordinate is its codimension', but line 115 calls "
                       "corner (−,−,−) — zero zeros — 'codim 3'. "
                       "Count-of-zeros is the cell's DIMENSION (open axes); "
                       "codimension is 3 minus that (decided axes). One of "
                       "the two lines is mis-worded.",
        "resolution": "Vault is read-only for this stream: reported, not "
                      "patched. The registry records both numbers per cell "
                      "(dim = zeros, codim = decided) so either fix leaves "
                      "the data correct.",
    },
    {
        "id": "note.two-voids",
        "kind": "alignment worth keeping",
        "status": "PINNED",
        "between": [f"{CUBE_DOC}:73", f"{POLYSHEAF_DOC}:146"],
        "observation": "Both letterings leave (0,0,0) letterless, for "
                       "different reasons: the spindle ∅ is the mechanism "
                       "void (absence enables rotation); the obscured wildcard "
                       "⊘ is the generative null (requests nothing, "
                       "terminates the cascade). Two readings of one empty "
                       "center — the system's load-bearing absence.",
        "resolution": "No action; knolled here so the alignment stays visible.",
    },
]


# ---------------------------------------------------------------------------
# Output writers
# ---------------------------------------------------------------------------

def build_registry():
    doc_texts = {d: read_doc(d) for d in
                 (POLYSHEAF_DOC, CUBE_DOC, LEDGER_DOC, ONTOGRAM_DOC)}
    pin_lines = validate_pins(doc_texts)
    letters = derive_polysheaf_lettering()
    check_polysheaf_pins(letters)
    poly_cells = polysheaf_cells(letters, pin_lines)
    cube_cells = cube_alphabet_cells(pin_lines)
    terms = parse_grip_ledger(doc_texts[LEDGER_DOC]) + PRIMITIVES
    return {
        "generated_by": "glyphs/knoll.py — do not edit registry.json or the "
                        "viewer data block by hand; re-run the generator",
        "discipline": "every entry carries a provenance status: PINNED "
                      "(quoted, source cited) | DERIVED (stated rule from "
                      "pins) | MINTED (coined, provisional) | OPEN (named hole)",
        "letterings": {
            "polysheaf": {
                "name": "Polysheaf ternary lettering",
                "names_what": "addresses — fixed cells of {−,0,+}³",
                "rule": POLYSHEAF_RULE,
                "source": f"{POLYSHEAF_DOC} (worked example)",
                "cells": poly_cells,
            },
            "cube_alphabet": {
                "name": "Cube-alphabet piece lettering",
                "names_what": "occupants — mobile pieces; coords are home "
                              "(solved) slots under x:L−/R+, y:D−/U+, "
                              "z:B−/F+ (a derived convention)",
                "rule": "piece type (centers, edges, corners), then standard "
                        "face order U D L R F B",
                "source": f"{CUBE_DOC} §7",
                "cells": cube_cells,
            },
        },
        "terms": terms,
        "trio": build_trio(poly_cells, cube_cells),
        "core27": build_core27(poly_cells),
        "findings": FINDINGS,
    }


def render_knolling_md(reg):
    poly = reg["letterings"]["polysheaf"]["cells"]
    cube = reg["letterings"]["cube_alphabet"]["cells"]
    poly_by = {c["letter"]: c for c in poly}
    cube_by = {c["letter"]: c for c in cube}
    out = []
    w = out.append
    w("# The Knolling — glyphs and terms, laid flat")
    w("")
    w("*Generated by `glyphs/knoll.py` from the read-only phase-2 vault. Do "
      "not edit by hand; re-run the generator. 3D view: open "
      "`glyphs/viewer.html`.*")
    w("")
    w("Knolling: everything out of the drawer, sorted by kind, laid at right "
      "angles, labeled. Two alphabets share the same 27-cell solid — one "
      "names **addresses** (polysheaf cells), one names **occupants** "
      "(cube-alphabet pieces). Both leave the center letterless.")
    w("")
    w("Provenance legend: **PINNED** quoted from a doc (line cited) · "
      "**DERIVED** by a stated rule from pins · **MINTED** coined, "
      "provisional · **OPEN** a named hole.")
    w("")
    w("---")
    w("")
    w("## 1. The 26 letters, both frames")
    w("")
    w("| Letter | Polysheaf address | cell | axis | seam of | requests | st | Cube-alphabet occupant | piece | st |")
    w("|---|---|---|---|---|---|---|---|---|---|")
    for i in range(26):
        l = chr(ord("A") + i)
        p, c = poly_by[l], cube_by[l]
        w("| **{}** | `{}` | {} | {} | {} | {} | {} | {} | {} | {} |".format(
            l, p["coord_str"], p["cell"], p["axis"] or "—",
            ",".join(p["seam_of"]) or "—",
            ",".join(p["requests"]) or "—",
            p["status"][0], c["cubie"], c["piece"], c["status"][0]))
    pc, cc = poly_by[CENTER_GLYPH], cube_by[SPINDLE_GLYPH]
    w("| **{}/{}** | `{}` | {} | — | {} | none — the loop closes here | P "
      "| {} | {} | P |".format(
          CENTER_GLYPH, SPINDLE_GLYPH, pc["coord_str"], pc["cell"],
          ",".join(pc["seam_of"]), cc["cubie"], cc["piece"]))
    w("")
    w("Cube-alphabet state note: centers A–F stay fixed, so **only 20 of "
      "26 letters carry state** ({}). The other six are the spindle's "
      "retinue.".format(f"{CUBE_DOC}:153"))
    w("")
    w("---")
    w("")
    w("## 2. The S·I·O trio")
    w("")
    trio = reg["trio"]
    w(f"Status: **{trio['status']}** — {trio['note']}")
    w("")
    for r in trio["readings"]:
        w(f"### {r['frame']}  [{r['status']}]")
        w("")
        for g in ("S", "I", "O"):
            if g in r["reading"]:
                w(f"- **{g}** — {r['reading'][g]}")
        w("")
        w(f"> {r['gloss']}")
        w("")
    w("---")
    w("")
    w("## 3. The Core 27")
    w("")
    c27 = reg["core27"]
    w(f"Status: **{c27['status']}** — coined by {c27['coined_by']}")
    w("")
    w(c27["principle"])
    w("")
    w(f"*{c27['gradient']}*")
    w("")
    w(f"Non-example: {c27['non_example']}")
    w("")
    w("| Glyph | Address | Global role | Local role | In frame | Open slots |")
    w("|---|---|---|---|---|---|")
    for t in c27["terms"]:
        w("| **{}** | `{}` | {} | {} | {} | {} |".format(
            t["glyph"], t["coord_str"], t["global_role"],
            t["local_role"], t["neighbors_in_frame"], t["open_slots"]))
    w("")
    w("---")
    w("")
    w("## 4. Terms (grip ledger + primitives)")
    w("")
    w("| Term | Status | Referent | Non-example | Source |")
    w("|---|---|---|---|---|")
    for t in reg["terms"]:
        w("| **{}** | {} | {} | {} | `{}` |".format(
            t["term"], t["status"], t["referent"],
            t["non_example"] or "—", t["source"]))
    w("")
    w("---")
    w("")
    w("## 5. Findings — seams that do not close")
    w("")
    for f in reg["findings"]:
        w(f"### `{f['id']}` — {f['kind']}  [{f['status']}]")
        w("")
        w(f"- **Between:** {' ↔ '.join(f['between'])}")
        w(f"- **Observation:** {f['observation']}")
        w(f"- **Disposition:** {f['resolution']}")
        w("")
    return "\n".join(out) + "\n"


VIEWER_START = "/*GLYPH_DATA_START*/"
VIEWER_END = "/*GLYPH_DATA_END*/"


def inject_viewer(reg):
    viewer = GLYPHS / "viewer.html"
    if not viewer.exists():
        raise SystemExit("glyphs/viewer.html missing — restore it from git "
                         "before re-knolling (the data block is generated, "
                         "the app around it is authored).")
    text = viewer.read_text(encoding="utf-8")
    i, j = text.find(VIEWER_START), text.find(VIEWER_END)
    if i < 0 or j < 0:
        raise SystemExit("viewer.html data markers not found — the authored "
                         "app must keep the GLYPH_DATA markers intact.")
    payload = (VIEWER_START + "\nconst REGISTRY = "
               + json.dumps(reg, indent=2, ensure_ascii=False)
               + ";\n" + VIEWER_END)
    new = text[:i] + payload + text[j + len(VIEWER_END):]
    if new != text:
        viewer.write_text(new, encoding="utf-8")
        return True
    return False


def main():
    reg = build_registry()
    registry_path = GLYPHS / "registry.json"
    knolling_path = GLYPHS / "knolling.md"
    reg_bytes = json.dumps(reg, indent=2, ensure_ascii=False) + "\n"
    changed = []
    if not registry_path.exists() or registry_path.read_text(encoding="utf-8") != reg_bytes:
        registry_path.write_text(reg_bytes, encoding="utf-8")
        changed.append("registry.json")
    md = render_knolling_md(reg)
    if not knolling_path.exists() or knolling_path.read_text(encoding="utf-8") != md:
        knolling_path.write_text(md, encoding="utf-8")
        changed.append("knolling.md")
    if inject_viewer(reg):
        changed.append("viewer.html (data block)")
    n_cells = sum(len(l["cells"]) for l in reg["letterings"].values())
    print(f"knolled: {n_cells} cells across 2 letterings, "
          f"{len(reg['terms'])} terms, {len(reg['findings'])} findings, "
          f"trio status {reg['trio']['status']}")
    print("changed: " + (", ".join(changed) if changed else
                         "nothing (byte-identical — idempotent re-run)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())

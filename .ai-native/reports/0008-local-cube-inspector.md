# Session report 0008 — the cubie as its own Site: the local-cube inspector

- **Date:** 2026-06-10
- **Session:** continuation of 0007, bdo: "S as a cube has many
  elements/glyphs we can place and see when we select this cube …
  eventually we can even make this cubie its OWN local rubik's cube on a
  global rubik's, so then nest … and the center spindle contains that
  letter and its elements land where needed … this might require
  re-arranging as we make more connections and relationships to
  terms/glyphs and that's the point"
- **Branch:** `claude/busy-feynman-4hd46k`
- **End-state:** `done`, one OPEN target named below

## What landed

Selecting a cubie now opens it as **its own local 3×3×3 frame** — the §4
scale-recursion (onta → ontum, Feature → Token) made interactive:

- **The keystone holds the glyph.** The local spindle position — empty at
  the global scale — carries the selected letter at the local scale. The
  Self sits at its own origin: "I move, but I do not move."
- **Elements land where needed, by geometry, not by hand.** The 26
  surrounding slots are the cell's actual global neighborhood at true
  relative offsets: its **seams** glow teal along its open axes, its
  **requests** glow white along its decided axes, diagonal kin sit dimmed,
  and neighbors that fall outside the global frame render as **open
  dashed slots** — holes the structure has not filled yet, ready for
  future term placements.
- **Placement is computed from the registry relations** (`seam_of`,
  `requests`, coordinates), never authored. When the term graph grows or
  changes, re-arrangement is recomputation — exactly the autojective
  shaper discipline: author the constraint, let the fill be derived.
- **Click a neighbor to re-root.** The inspector walks the atlas: declare
  a Site → survey its neighborhood → promote a neighbor to Site and
  recurse. Drag rotates the local frame; the view direction persists
  across hops so the walk feels continuous.
- **The closing consistency:** the local cube of ⊘ (the global center) is
  the *entire global cube* — every neighbor in-bounds, no open slots. The
  root Token is the Feature whose subtree is the whole specimen; the
  recursion closes by itself, with no special-casing in the code.
- The occupant wing, facelet chips, and address wing remain beneath the
  local cube; the inspector still re-renders on every committed turn.

## Named OPEN target (the nesting)

**In-place nesting on the global cube** — expanding a cubie *in situ* into
its own rubik's cube (and recursing), rather than inspecting it in a side
panel. That requires: (a) a level-of-detail renderer (cubie → 27
sub-cubies under zoom), (b) a placement contract for which glyphs/terms
fill a sub-cube's 26 slots at each depth — the obvious candidate is the
relative-neighborhood rule landed here, which generalizes; and (c) a
re-arranging pass when relationships change — already the knoll
discipline. Named now so it is a target rather than a vibe.

## Discipline notes

- No registry change; knoll re-run byte-identical; CUBE_MATH untouched;
  suite 27/27.
- The neighborhood/seam/request classification in the inspector reads the
  same registry fields the tests pin (`seam_of`, `requests`), so the
  derivation tested in `tests/test_knoll.py` is the one rendered.

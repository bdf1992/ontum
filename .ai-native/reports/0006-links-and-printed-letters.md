# Session report 0006 — the links web + letters on the facelets

- **Date:** 2026-06-10
- **Session:** continuation of 0005, bdo request: relationship lines in the
  knoll that respond to turning/scrambling ("see the impact of
  configurations on the knoll"), then the 27 terms placed onto the cubie
  faces themselves.
- **Branch:** `claude/busy-feynman-4hd46k`
- **End-state:** `done`, one naming flag below

## What landed

### 1. The links web (`links` button: off → seams → drift)

- **seams** — the incidence skeleton, straight from the registry's
  `seam_of` relation (edge → its two corners, face → its four edges,
  faces → ⊘), drawn between the **pieces currently occupying** the related
  cells and colored by source-cell kind. The cell relation is fixed; which
  pieces the web lands on is configuration. Scramble and the same skeleton
  threads through different occupants.
- **drift** — each displaced piece tied to the piece squatting its home
  cell. That is the permutation's cycle structure drawn as chords: solved
  shows no chords; a single quarter-turn shows two 4-cycles (corners +
  edges); a scramble shows the full tangle. Colored by piece kind, so
  corner-cycles and edge-cycles read separately.
- Both modes follow pieces live through turn animations and through the
  knolled flat-lay — in the knoll, seams becomes the face-lattice diagram
  drawn between the sorted rows, and drift draws the configuration's
  chords across the rows. This is the requested "impact of configurations
  on the knoll", as geometry.

### 2. The 27 terms on the faces

- The 26 letters now print **on the facelets**, in each facelet's own text
  frame (`TANG`, one frame per face direction, chosen so `tu × tv = −n` —
  stickers read correctly from outside, never mirrored, upright in the
  solved pose). Ink color flips dark/light per sticker color.
- **Occupant letters are glued:** the home-face text frame is transported
  by the piece's rotation matrix, so a flipped edge wears its letter
  flipped and a twisted corner wears it turned — orientation made visible
  through typography, matching the sticker derivation.
- **Address letters print upright always** — they label fixed space, and
  mid-turn they ride the layer then snap back at commit: the
  address/occupant split, again demonstrated rather than asserted.
- The void ⊘/∅ keeps its billboard glyph (the 27th term has no faces).
  Billboard letters otherwise appear only in the knolled flat-lay, where
  box faces go edge-on; sublabels and group captions unchanged.

## Needs-you (naming)

- The displacement view is labeled **drift** — a loose borrow of the grip
  ledger's word (where Drift is the trajectory of the cant over updates,
  not piece displacement). The viewer caption flags the borrow. Admit,
  refuse, or rename (candidate alternatives: *away*, *squat*, *chords*).

## Discipline notes

- No registry change; knoll re-run byte-identical. `CUBE_MATH` untouched
  and still pure. Suite 27/27; loop tests untouched.

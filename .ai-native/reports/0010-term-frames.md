# Session report 0010 — the term frame: S's cube has its TERMS mapped on it

- **Date:** 2026-06-10
- **Session:** continuation of 0009, bdo: "S has 27 terms associated with
  it. Those terms could EACH go on a cubie of S if it's self-similar to
  THIS rubik's cube. AKA S's cube has its TERMS mapped on it." And: "there
  CAN and SHOULD be a neighborhood view AT SOME point so it's GOOD you
  built it, but I want the LOCAL/self view first."
- **Branch:** `claude/busy-feynman-4hd46k`
- **End-state:** `done` — contract v0 is MINTED-by-construction; expected
  to be re-arranged as the term graph grows (that is the point)

## The term-frame contract (v0)

Each core term's own cube carries **its 27 terms mapped on its cubies**,
typed self-similarly to the solid itself, derived entirely in `knoll.py`
(registry section `term_frames`; never hand-authored):

- **center** — the Self/void term: the glyph. The keystone holds it.
- **faces (6)** — the directional relations, forced by pure geometry:
  in-bounds unit neighbors are this cell's **seams** (they decide one of
  its open axes) or **requests** (they open one of its decided axes);
  out-of-bounds directions carry the cell's own **decisions** — `x+` sits
  on the +x face because *x = + is why no neighbor lies that way*.
- **corners (8)** — fully decided slots take fully decided terms: the
  settled facts (cell kind, dim, codim, axis, status, frame capacity,
  wing, home piece), in lex slot order.
- **edges (12)** — relations, because a Seam is a primitive that is a
  join: antipode, the **live occupant** (the viewer fills it from the
  current configuration each frame), trio membership for S·I·O. Unfilled
  edge slots stay **OPEN** — drawn dashed, the measured capacity for
  future relationships.

Worked example, S `(+,−,0)`: center S; faces −z/+z = seams E, F; faces
−x/+y = requests W, V; faces +x/−y = decisions `x+`, `y−`; corners =
its eight facts; edges = R (antipode), @ (live occupant), S·I·O; nine
edge slots open.

## The inspector: LOCAL/self first

- The panel now has two tabs: **terms** (default — the term frame) and
  **neighborhood** (the true-offset view from 0008, kept; wanted again
  later for the in-place nesting).
- Hover any cubie for its gloss ("seam — E decides z = −", "decided —
  x = + is why no neighbor lies this way", "occupant — L is the piece
  currently at this address"); click any letter to re-root and walk.
- The live-occupant slot updates with scrambles; the rest of the frame is
  registry truth.

## Where it landed

- `knoll.py` — `build_term_frames()` + `TERM_FRAME_CONTRACT`; registry
  gains `term_frames` (contract + all 27 frames × 27 slots).
- `knolling.md` — contract documented under the Core 27 with the S
  worked example.
- Viewer — two-mode inspector, terms first.
- Tests — `test_term_frames_contract_v0`: 27 frames × 27 slots, the S
  example exact (E/F/W/V placements, the two decisions), 8 facts on
  corners, antipode/occupant/trio/open on edges, the root's six faces
  all seams and no antipode. Suite 29/29.

## Needs-you

- The contract itself is the pin to place: face/corner/edge typing
  (relations-on-edges, facts-on-corners) is an argued choice, not a
  settled one. Re-arranging is one function away.
- Which terms deserve the open edge slots next? cant/drift/jective want
  addresses *within frames* before they want global cells.

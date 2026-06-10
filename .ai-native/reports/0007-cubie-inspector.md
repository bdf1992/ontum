# Session report 0007 — the cubie inspector

- **Date:** 2026-06-10
- **Session:** continuation of 0006, bdo: "I should be able to inspect a
  cubie to see its glyphs"
- **Branch:** `claude/busy-feynman-4hd46k`
- **End-state:** `done`

## What landed

Clicking a cubie now opens a full glyph inspection instead of the
mode-dependent card. One panel, everything the piece carries:

- **A live mini render** of the piece itself — its plastic, its stickers,
  its glued letters — slowly rotating in the panel, true to the piece's
  current rotation matrix (a flipped edge spins past wearing its letter
  flipped). The void renders as its dashed ⊘ ring; the 27th term has no
  faces.
- **The dual glyph header:** occupant letter @ address letter (e.g.
  `S @ T` — piece S sitting in cell T), with home/away status.
- **The occupant wing:** glyph + cubie name, carries-state, orientation
  (edge flip) or twist (corner), home address.
- **The facelet breakdown:** one chip per sticker in its pinned §7 color
  (names read live from the registry's `face_color`), each saying which
  home face it is and which direction it currently faces — `U sticker
  (white) → facing B`.
- **The address wing:** the cell it currently sits in — glyph, coords,
  dim/codim, axis, antipode, seam-of, requests — with provenance badges
  and both source citations.
- The inspector **tracks the live configuration**: while it's open, every
  committed turn (manual, scramble, unwind, reset) re-renders it, so you
  can watch a single piece's facing-directions and twist change as the
  cube moves around it.

## Discipline notes

- No registry change; knoll re-run byte-identical; CUBE_MATH untouched;
  suite 27/27.
- The panel no longer depends on the active lettering — inspection shows
  both wings at once. The lettering toggle still drives what is printed
  on the cube itself.

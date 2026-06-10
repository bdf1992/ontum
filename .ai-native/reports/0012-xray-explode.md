# Session report 0012 — x-ray and explode

- **Date:** 2026-06-10
- **Session:** continuation of 0011, bdo: "1. Xray mode 2. Explode mode —
  Xray show only the colored facelets, and explode expands the cube, but
  still keeps things connected so the inside can be seen"
- **Branch:** `claude/busy-feynman-4hd46k`
- **End-state:** `done`

## What landed

- **x-ray** — the plastic bodies vanish; only the 54 colored facelets
  render. Front tiles bright with their printed letters; back tiles
  dimmed to 30%, so the cube reads as a hollow shell you can see
  through. The ⊘ ring at the center — invisible inside the solid cube —
  shows through the shell: the void rendered in its place for the first
  time in the main view. Works in every mode (turns, scramble, knolled,
  spotlight, cascade).
- **explode** — the pieces lift radially apart (animated smoothstep,
  ×2.25 spread at full lift, camera eases back to compensate), with
  **struts** drawn between cell-adjacent pieces so the structure stays
  visibly connected — 54 thin lines, the lattice skeleton itself. The
  empty center sits visibly at the middle of the lifted assembly. Turns
  still work exploded: the layer rotates at its lifted radius and the
  struts stretch and follow.
- x-ray + explode compose: the value layer floating in space on its
  skeleton, void at the center. Knolled and exploded are mutually
  exclusive (the flat-lay owns its own geometry); engaging one releases
  the other.
- Internals: the printed-letter pass was extracted to a shared
  `printFaceLetter()` used by both the solid renderer and the x-ray
  facelet renderer — one code path for typography, no drift between
  modes.

## Discipline notes

- Rendering-only change; registry untouched (knoll re-run
  byte-identical); CUBE_MATH untouched; suite 29/29.

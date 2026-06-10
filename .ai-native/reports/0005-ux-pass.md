# Session report 0005 — UX pass: colors, cubies, facelets, drag, sound, rendering

- **Date:** 2026-06-10
- **Session:** continuation of 0004, bdo request: UX before any solvers —
  "1. Colors 2. Cubies 3. facelets 4. virtual mouse interaction
  5. sound/clicks" + "and a rendering pass"
- **Branch:** `claude/busy-feynman-4hd46k`
- **End-state:** `done`

## What landed, by item

1. **Colors.** The §7 table pins the face colors in prose — Up (white),
   Down (yellow), Left (orange), Right (red), Front (green), Back (blue).
   They are now registry data: `face_color` on the six center entries
   (PINNED), with a test asserting the names against the live doc text.
   The hexes are the authored rendering layer (`FACE_HEX` in the viewer).
2. **Cubies.** Bigger pieces (half-size 0.42 → 0.53), tight gaps, dark
   plastic body, rounded bevel edges (thick round-join strokes). The void
   keeps its dashed ⊘ ring.
3. **Facelets.** Real stickers, inset on each face. Not painted on:
   derived per frame from each piece's rotation matrix — `Mᵀ·n` pulls the
   world-facing normal back into the piece's home frame, so a flipped edge
   *shows* its flip and a twisted corner *shows* its twist. The orientation
   dots from 0004 became redundant and were removed; the state string's
   EO/CO digits now have a visible referent on the cube itself.
4. **Virtual mouse.** Drag a facelet to turn its layer: the grabbed face's
   normal fixes the candidate axes, the drag direction is matched against
   each candidate turn's screen-projected tangent, and the best-aligned
   axis fires the move (≥0.35 cosine, else falls through to orbit).
   Middle slices are not in the generator set and fall through. Left-drag
   on space orbits; right-drag always orbits; a still click selects.
5. **Sound.** Synthesized Web Audio, no assets: bandpass noise tick + low
   triangle thunk on every commit snap, a soft C-E-G triad when the cube
   comes home (with the Pilish line). Context unlocked inside the user
   gesture; `sound` toggle to mute.
6. **Rendering pass.** Radial vignette background, soft ground shadow
   (fades out in knolled mode), per-facelet specular gradient keyed to the
   light direction, slight ease-out-back overshoot on manual turns (fast
   replays stay cubic), letters re-rendered white with dark outline for
   contrast over stickers, `letters` toggle for the clean-cube look.

## Discipline notes

- Face-color names live in the registry as PINNED entries; hex values are
  authored viewer code. The split keeps the vault the source of truth for
  *what* the colors are and the viewer responsible only for *how* they look.
- `CUBE_MATH` block unchanged and still pure; 27/27 tests (new:
  `test_face_colors_match_doc_table`), loop suite untouched.
- knoll.py re-run regenerates registry + viewer data block; idempotent on
  the second run.

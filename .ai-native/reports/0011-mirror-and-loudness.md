# Session report 0011 — mirror fix + the related glyphs made loud

- **Date:** 2026-06-10
- **Session:** continuation of 0010, bdo (with screenshots): "This is
  incorrect — I don't even see the glyphs/tokens related to that letter
  as discussed."
- **Branch:** `claude/busy-feynman-4hd46k`
- **End-state:** `done`

## Two defects, both real

1. **The world was mirrored.** The projection had the camera on the
   left-handed side; geometry hides a mirror but typography exposes it —
   the printed facelet letters rendered backwards (the screenshots' Ǝ
   and Ɔ were the tell). Fixed by flipping the camera to a right-handed
   view (`zc = dist − z`, visibility `rn·z > 0`) in both the main
   renderer and the inspector. Side benefit: apparent turn directions
   now match the physical cube (a CW move *looks* CW from the front).
2. **The related glyphs were buried.** In the terms view, fact and meta
   cubies rendered as loudly as the actual related glyph tokens. Fixed
   the hierarchy:
   - seams / requests / antipode / live occupant render **large, bright,
     glowing, with relation sublabels** ("seam", "request", "antipode",
     "@ occupant") — the loud layer;
   - facts and decisions render small and dim (brightening on hover);
   - wider slot spacing to cut occlusion; compact fact labels
     ("codim 2", "dim 1", "addr") with verbose glosses on hover.
3. **Related glyphs strip** — new panel section listing the letter's
   tokens as clickable chips regardless of 3D occlusion: seams, requests,
   antipode, and the live occupant. Click a chip to re-root. The tokens
   of a letter are now impossible to miss.

## Discipline notes

- Fact labels compacted in `build_term_frames()` (knoll.py) — registry
  regenerated; glosses keep the verbose text. Suite 29/29; CUBE_MATH
  untouched (the mirror was in rendering, not in the group math — the
  state math was always correct, which is why the tests never caught it:
  they test the algebra, not the optics).

# Session report 0003 — glyph review + the knolling

- **Date:** 2026-06-10
- **Session:** glyph review and creation, requested by bdo directly
  ("semantic and syntactic knolling of our semiotics in place", 3D viewer
  inspired by Rubik's-solver visualizations)
- **Branch:** `claude/busy-feynman-4hd46k`
- **End-state:** `done`, with three `needs-you` pins listed below
- **Scope note:** this is a new stream over the phase-2 vault as *source
  material*, authorized by bdo's request. It does not touch `loop/`, does
  not import phase-2 into the loop, and does not edit the read-only vault.
  `tests.test_loop` still 6/6.

## What landed

- `glyphs/knoll.py` — stdlib-only generator. Derives the polysheaf ternary
  lettering from the six letters the worked example pins (A, E, H, I, M, Q),
  validates every pin against the live doc text (doc drift fails loudly),
  hard-codes the cube-alphabet §7 bijection, parses the grip ledger
  (ontum-evolution.md §8) live, and emits the three generated surfaces.
  Idempotent: re-run on an unchanged vault is byte-identical.
- `glyphs/registry.json` — the knolled inventory. Every entry carries a
  provenance status (PINNED / DERIVED / MINTED / OPEN) and a cited source —
  the registry is made of etymontokens.
- `glyphs/knolling.md` — the human-readable flat-lay: both alphabets side
  by side per letter, the S·I·O trio readings, all terms, all findings.
- `glyphs/viewer.html` — single-file, zero-dependency 3D viewer (canvas,
  no CDN, works from `file://`). Orbit/zoom; lettering toggle
  (addresses ⊘ / occupants ∅); animated **knolled** flat-lay; **S·I·O**
  spotlight; the polysheaf worked example as an animated **cascade**
  (A → I,M,Q → E → faces → ⊘); click any cell for its registry entry.
- `.claude/skills/glyph-knolling/SKILL.md` — the repeatable skill: the
  discipline (vault read-only, provenance statuses, grips need
  non-examples), the pass, and the extension points.
- `tests/test_knoll.py` — 16 tests: pins reproduced, bijections, antipode
  involution, edge I = seam(A,E), A requests I,M,Q in axis order, cascade
  terminates at the center, idempotence, viewer/registry sync, ledger parse.

## Findings (seams that do not close — recorded, not patched)

1. **`seam.lettering-collision`** — the same 26 letters are assigned twice,
   incompatibly: cube-alphabet §7 (A = U center, S = corner UFR) vs the
   polysheaf worked example (A = corner (−,−,−), S = a z-edge). Read as
   complementarity, not conflict: polysheaf letters name fixed **cells**
   (addresses), cube-alphabet letters name mobile **pieces** (occupants) —
   the (position, value) split cube-alphabet §3 already names. MINTED.
2. **`seam.codim-wording`** — autojective-polysheaf.md:111 ("count of zeros
   … is its codimension") contradicts :115 (corner (−,−,−), zero zeros,
   "codim 3"). Count-of-zeros is the dimension; codimension is 3 minus it.
   One line is mis-worded. Vault read-only → reported here. PINNED.
3. **`note.two-voids`** — both alphabets leave (0,0,0) letterless for
   different reasons: spindle ∅ (mechanism void) vs obscured wildcard ⊘
   (generative null). Kept visible in the knolling.

## Needs-you (open pins, bdo's cut)

1. **The S·I·O trio.** No doc defines the trio as a trio. Three readings
   are knolled side by side (registry `trio`, viewer **trio** panel):
   *addresses* — one seam per axis (I on x, O on y, S on z), and all three
   share corner E = (+,−,−): S·I·O is exactly the request set of one Self,
   E's seam-star (tested);
   *occupants* — S = corner UFR, I = edge UB, O = edge FR;
   *letterform* — O the ring around a void, I the single stroke, S the seam
   between two lobes (and I/O as the binary pair). Status stays OPEN until
   one reading gets a pin **with a non-example** — or a fourth is minted.
2. **The lettering collision** — admit or refuse the
   address-alphabet/occupant-alphabet reading (finding 1).
3. **The codim wording** — which of the two vault lines is the intended
   one (finding 2). The registry stores both numbers per cell, so either
   fix leaves the data correct.

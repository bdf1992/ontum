# Report 0075 — Overnight loop: Causality's canvas design system + phrase portfolio + live Story-demo renderer

Overnight-loop run on **epic.causality-surface**, branch `claude/canvas-home-reshape`,
done-line **0103**. Stop reason: **done-line satisfied** (all three deliverables met,
live, tested) before the 08:00 stop.

## End-state — done-line 0103 met

1. **Canvas design system framed** — `causality/canvas-system.js` is the single
   schema-driven source of tokens + primitives: `COLOR · FACET · SHAPE · LINE ·
   EASE · ANIM · PHYSICS · INTERACT · LENS`, with an **ASCII fallback** per facet.
   `validate(table,key)` is the §10 teeth — a fabricated/hand-rolled primitive is
   refused. Documented in `canvas-system.md`. Test `canvas-system.test.js`: **12/12**.
2. **Phrase portfolio** — `causality/phrases.json`: **8** cute-but-mechanically-rich
   phrases, each with glyphs, **facet compositions** (type-by-composition), relations
   (facet→facet across glyphs), and cross-membrane links, modelled with *correct*
   mechanics (the cat chain is `shadow blocks warmth → warmth fades → wakes cat`, per
   bdo's caveat). Test `phrases.test.js`: **8/8** — the no-dangling teeth caught two
   real dangling glyphs (`village`, `tree`) on the first run; fixed.
3. **Story-demo renderer, live** — `causality/story.html` renders a phrase the full
   way: the **sentence skin** (key words tinted to their glyph), the **membrane**,
   glyph **holons** with composed **facet chips**, **labelled facet→facet relations**
   (solid + dashed feedback), a working **Lens** (glyph → facets + connected-through;
   relation → endpoints + explain/invert/stitch; membrane → counts + ask-box), the
   bottom toolbar, and an **8-phrase switcher**. Reads `canvas-system.js` + `phrases.json`
   (the deterministic floor; gateway enrichment is the seam behind the same node spec,
   iterations 0006). Served as the landing at **https://bdf1992.github.io/ontum/**
   (branch preview via the `claude/*` Pages policy).

Tests: JS suites (design-system, portfolio, inspector, persistence) green; python
handoff suite green (untouched by this JS work).

## Earlier this session (pre-loop, same branch)

The all-canvas reshape (iter1) → minimalist strip (iter2, inspector confirmed
working) → GitHub Pages serving stood up (`pages.yml`, Pages enabled via bdo's gh
creds, `claude/*` preview policy added) → the **story-demo model locked** through
screenshot proofs bdo confirmed (iterations.md **0001–0006**: membranes, type-by-
composition, compress-to-enrich vs headroom, each-node-through-the-gateway).

## needs-you

None blocking. bdo's surfaces are untouched; nothing waits on a stamp.

## Resumable next (session/merge-node work, named — not bdo's)

- **Land `claude/canvas-home-reshape` → main** (atom + PR + independent merge-node)
  so `main` == live; the live URL is currently a branch preview, not yet on trunk.
- **Renderer polish toward the exact mockup**: facet-label crowding near dense
  glyphs, relation/membrane Lens depth, the figurative glyph icons (cat/sun/cloud),
  real toolbar/zoom/minimap behaviour.
- **Sliders** acting on the membrane (complexity/length/twists/weirdness/colors as
  world-physics controls, iterations 0003).
- **Gateway composition seam** (iterations 0006): route a node's typing through the
  governed inference gateway, deterministic compiler as the bounded fallback; the
  "ask this membrane" Lens box is the first inference surface.
- Fold the membrane renderer into the editable/saveable canvas (one surface, two modes).

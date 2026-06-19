# Causality — the canvas design system

The single, schema-driven vocabulary the canvas renders from (done-line 0103,
iterations 0001–0005). One source — [`canvas-system.js`](canvas-system.js) — so a
new primitive ships as a **table entry, not bespoke render code**. The §10 teeth
live in [`canvas-system.test.js`](canvas-system.test.js): `validate(table, key)`
**refuses** any primitive absent from these tables (a fabricated or hand-rolled
one fails), every facet is fully specified, every animation names a real easing
curve.

Truth-discipline (causality/CLAUDE.md): this is a *display vocabulary*, never a
second source of meaning. It styles; it does not decide.

## The tables

| table | what it governs |
|---|---|
| `COLOR` | semantic roles — paper/ink/dim, positive(teal)/strain(rust)/inference(purple)/pulse(amber), + the glyph pigment ring. The established cream look-and-feel; no dark mode. |
| `FACET` | the **type-by-composition** vocabulary (iterations 0004): `actor, objective, source, sink, signal, state, place, action, memory, time, gate` — each with an icon, an **ASCII fallback**, a color role, and a one-line read. A glyph is a *bundle* of facets. |
| `SHAPE` | node shapes — `holon` (a glyph, composes facets), `facet` (a chip), `membrane` (a phrase boundary blob), `card`, `readout`. |
| `LINE` | relation edge styles — `relation`, `feedback`(loop/interrupt), `cross-membrane`(shared glyph), `facet`(glyph→facet), `proportional`. dash + width + hand-ink wobble. |
| `EASE` | named curves — `linear, easeInOut, easeOut, spring, breath`. |
| `ANIM` | named motions — `wobble, water-fill, pulse-travel, ring, membrane-breath, entrance-fade`; each names an `EASE`. |
| `PHYSICS` | field params — drift, damping, baseline, energy-coupling, repulsion. |
| `INTERACT` | gesture → act — `hover→reveal, click→select(Lens), double-click→add/zoom, drag-rim→wire, drag-body→move, right-click→erase, pan, lasso, voice`. |
| `LENS` | what the inspector becomes per selection — `glyph` (facets + connected-through), `relation` (endpoints + explain/invert/stitch), `membrane` (counts + ask). |

## The discipline

- **Add a primitive = add a table entry.** Never hand-roll a one-off in render
  code; `validate()` is the gate and the test fails an undeclared token.
- **ASCII is a first-class render target**, not an afterthought — every facet
  carries its ASCII glyph so the whole surface degrades to text.
- **The look is fixed**: cream paper, Fraunces / Caveat / IBM Plex Mono / Space
  Grotesk, hand-drawn ink. A new skin is a non-example (see
  [[causality-look-and-feel]] / done-line 0103).

## Reading order

`canvas-system.js` (the tokens) → `canvas.js` (the engine that renders them) →
`iterations.md` (why the shape is what it is) → `display-system.md` (the broader
display target this serves).

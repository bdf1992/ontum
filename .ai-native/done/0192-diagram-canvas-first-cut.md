# Done-line 0192 — The editable diagram canvas — first cut: schema-driven component model, edit-and-save, declared layers, export-through-the-gate

Written before code, per §9.4. When this line is met, stop.

> **Done when:** the editable diagram canvas first cut lives in `diagrams/`
> (reusing `causality/canvas.js`'s schema/persistence DISCIPLINE by pattern, not
> the artifact — `causality/` untouched), and all four things are true:
>
> 1. **A diagram SCHEMA** (a JS object in `diagrams/canvas.js`, in canvas.js's
>    spirit) declares the part-types `compose.py` renders (pill · rect · rounded ·
>    dashed · subroutine · hex · rhombus · chips), per-part config, and the
>    holonic attribute fields (`sites` / `space` / `strata{fundamental,derived,
>    learned}` / `anima{strength,tempo}`) — one table driving defaults + inspector
>    + persistence; a new part-type is a SCHEMA entry, not new code.
> 2. **An editable canvas** `diagrams/canvas.html` + `diagrams/canvas.js` loads a
>    `compose.py` spec (JSON), renders the parts (HTML/SVG/2D — need not be
>    byte-identical to compose.py), lets the user SELECT a part, MOVE it (drag
>    writes explicit x/y back — no auto-layout), INSPECT/EDIT it via a
>    schema-driven inspector (relabel + edit attributes), and round-trips the whole
>    diagram through `toJSON`/`fromJSON` to localStorage (autosave) + file
>    export/import. The spec is the truth; the canvas is an editor over it.
> 3. **Layers**: a `layers` array on the spec (`{id,label,z,visible,locked}`) and a
>    declared `layer` field on parts; a layer panel in the canvas (show/hide, lock,
>    reorder). `compose.py` renders parts in ascending layer z and omits parts on
>    `visible:false` layers — BACKWARD-COMPATIBLE (a spec with no `layers` behaves
>    exactly as today). `qa.py` gains `check_layer_membership`: a part on a layer
>    not in `layers` → deny (exit 2) citing the canon's containment principle (the
>    structural analog of an orphan — the region-membership shape).
> 4. **Export → gate → render**: an export path that runs the edited spec through
>    `qa.py` then `compose.py`; the canvas cannot ship a picture the gate refuses.
>
> And the §10 pair, non-vacuous, with teeth:
>
> - In the python suite (`tests/test_diagram_canvas.py` or `test_diagram.py`): an
>   honest spec with declared layers PASSES `qa.py` (exit 0) and renders; a
>   one-variant with a part on an UNDECLARED layer is REFUSED (exit 2) citing the
>   canon principle — proven non-vacuous (a constant "pass" fails the negative).
> - A canvas persistence round-trip (in the grain of
>   `causality/canvas.persist.test.js`): build a diagram in-memory, `toJSON` →
>   `fromJSON`, assert structural identity including layers and a moved part's
>   x/y; a dropped field is detectably lost (the negative control).
> - The FULL existing suite (`python -m unittest discover -s tests -v`) stays
>   green and `compose.py`'s committed example SVGs still render byte-identically
>   (the layers change is backward-compatible).
>
> The work is atom-backed; it claims no arc — `diagram-canvas.proposal.md` (CTA-A
> = A1, bdo-stamped) is the blueprint. Save-states beyond autosave+file (C4 full)
> and generation wiring (C6) are NOT in scope — named, deferred to later cells.

## Why

bdo, 2026-06-23 (ask-surface stamp on `diagram-canvas.proposal.md`, CTA-A = A1):
*"let's upgrade our diagramming tool"* — make each generated part a component, put
parts on an editable, layered, save-stated canvas, carry past requirements
forward, take Miro as the quality bar only. The diagrammer today has two halves
that don't touch: the deterministic renderer + refusing gate (`diagrams/`) and an
editable schema-driven graph engine (`causality/canvas.js`). This first cut is the
bridge's smallest real piece: the component tier proving the gesture on a real
shape, with the carried-forward rigor (the gate judges the edited spec) intact.

## In scope (this cut — the proposal's "smallest first cut")

- `diagrams/canvas.html` + `diagrams/canvas.js` — the editable canvas + diagram
  SCHEMA + schema-driven inspector + layer panel + toJSON/fromJSON persistence +
  the export-through-the-gate path.
- `diagrams/compose.py` — layers honored (ascending z, hidden omitted),
  backward-compatible.
- `diagrams/qa.py` — `check_layer_membership` (declared-layer teeth).
- `diagrams/canon.md` — the layer rule cited under C4 containment, with its
  non-example (the canon discipline: a rule lands before it bites).
- `diagrams/examples/` — an honest layered spec + a layer-orphan variant.
- `tests/test_diagram.py` (or a sibling) — the §10 layer pair.
- `diagrams/canvas.persist.test.js` (sibling, diagrams home) — the round-trip.
- `diagrams/CLAUDE.md` — the canvas-surface + layers module rules.
- The backing atom (no arc claimed).

## Not in scope (named, not invented away)

- **Named/versioned save-states (C4 full)** — autosave-to-localStorage + named
  spec-file export only; a versioned in-repo save-state store is a later cell.
- **Generation wiring (C6)** — `authoring.js` (describe→draft) and
  `term_economy.py diagram` (truth→draft) seeding the canvas; later cell.
- **Grouping / piece-as-component (CTA-B)** — one part = one component first.
- **A shared canvas-kit (CTA-A / A3)** — deferred until a second consumer proves
  it; the discipline is reused by pattern, not the artifact.
- **Miro-bar visual finish** — the canvas is a working editor, not the polished
  served skin (`atom.diagram-experience.v0`); a later cell.
- **Connect/edge authoring on the canvas** — edges round-trip and render but the
  first cut edits parts (select/move/inspect/relabel/re-layer), not edge drawing.

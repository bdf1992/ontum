# The diagram canvas — parts · components · pieces (PROPOSED)

> Status: **PROPOSED** — a blueprint for bdo to address, authored 2026-06-23 at
> his request ("let's upgrade our diagramming tool"). This is the *bundle*, not an
> increment: full shape → the holonic ladder → carried-forward requirements →
> the new systems → calls-to-action against a purpose. Nothing here is built. It
> is the structure to decide *before* building (the blueprint-before-build hard
> rule, #348/CTA-3).
>
> This **extends the confirmed `epic.diagram`** (bdo, named 2026-06-19). It does
> not replace it: it pulls the served, editable surface forward and names the one
> constraint of that epic this direction puts in tension (see CTA-A).

## DECISIONS (bdo, 2026-06-23 — ask-surface stamp)

- **CTA-A — A1.** The editable canvas lives in **`diagrams/`**, reusing
  `canvas.js`'s schema/inspector/persistence *discipline* by pattern (not the
  artifact). The live causality board stays untouched; the diagram canvas edits
  the `compose.py` spec and exports through the `qa.py` gate. A shared canvas-kit
  (A3) is deferred until a real second consumer proves it's needed. The epic's
  "sibling, not extension" constraint is **honored**, not reversed.
- **CTA-D — confirmed by his own words** ("only in quality and bar"): Miro
  inspires the interaction *finish* only; ontum keeps declared structure, the
  deterministic spec, and the refusing gate.
- **CTA-B / CTA-C / CTA-E — proceeding on the recommended defaults** (one-part =
  one-component first; localStorage autosave + named spec-file save-states; both
  generation paths seed the editable canvas). Each default forecloses nothing —
  grouping and a versioned save-state store are later cells. bdo may retune any.

## What bdo asked for (verbatim intent, 2026-06-23)

1. Make each **generated part a component**.
2. Put those parts **on a canvas**.
3. A **layering system**.
4. **Carry past requirements forward** (don't lose what the tool already is).
5. Generate the **parts, components, and canvas/pieces** of a diagram.
6. Each component and part that *should be* interactable/editable **is**.
7. The user can **edit the canvas and save their edits**.
8. Support **save states**.
9. Take **Miro** as inspiration — **only in quality and bar**, not its model.

## The REAL target: one-shot (bdo, 2026-06-23)

bdo's correction, on the record: *"Your REAL task is to one-shot it. And define
how to make that possible."* The remake-until-approve loop is **scaffolding, not
the product** — a loop you can run forever is a place to hide never nailing it.
The target is the first generation landing inside the acceptance region with no
edit; the deliverable is the **environment that makes one-shot the expected
outcome**, not luck.

**One-shot, defined.** The first generation passes the encoded bar and needs no
edit — "approved" becomes *"passes the gate"* (a thing you check, not faith). It
is possible **exactly when the acceptance region is fully encoded in the
environment before generation, and the generator is bound to that environment.**
The miss-rate is a property of the environment, not the model.

**The environment that makes it possible (each checkable):**
1. **The bar *as* the gate** — every dimension bdo would reject on is a `qa.py`
   check citing the canon. A rejection reason that is not a check is the gap that
   forces a loop. (Gate-completeness.)
2. **An exemplar + notoriety library** (the Pattern Commons) — approved exemplars
   to imitate, recorded refusals to avoid; the generator composes from proven
   patterns, never from scratch. One-shot reliability scales with its coverage.
3. **The schema** — output valid by construction (`validateSpec` refuses
   malformed before render).
4. **The deterministic body** (`compose.py`) — zero render variance; the only
   variance left is in the authored spec, which 1–3 pin.
5. **A bound generative pole** — bounded inference handed the description + the
   live schema + the relevant exemplars + the canon checks, so the draft is born
   inside the acceptance region.

**The move that makes it possible.** The accept/reject loop is the *calibration
run* that builds (1) and (2), not "try again and hope." Each rejection is
harvested **once** — into a new gate tooth or an exemplar/notoriety deposit — so
it can never recur. One-shot becomes possible the moment the loop stops teaching
the gate anything new: the gate's acceptance region has converged onto bdo's
taste. That convergence collapses the two acceptances to one — "passes the gate"
≡ "bdo approves" — bdo still the last stop, rarely overturning.

**The discriminator (the §10 test for one-shot).** Take a subject bdo has never
seen, generate once, gate it, show him. Accept unchanged → one-shot achieved for
that class. Reject → the rejection is a gate gap; encode it. The metric:
**gate-missed-rejections per fresh generation → 0.** Reliably 0 across diverse
subjects = one-shot is real, and the loop retires.

This reframes the whole arc: the carried-forward gate, the Pattern Commons, the
schema, and the generative pole are not separate features — they are the four
walls of the acceptance region that make one-shot possible. The build below is
those walls; the success measure is the discriminator above.

## The why (one line)

The diagrammer today has two strong halves that don't touch: a deterministic
renderer + refusing gate (`diagrams/`, the **quality** half) and an editable,
schema-driven, persisted graph engine (`causality/canvas.js`, the **edit** half).
bdo's request is the bridge — an **editable, layered, save-stated canvas whose
parts are first-class components**, with the refusing gate kept as the rigor and
Miro's polish as the bar. The diagram stops being a one-shot render and becomes a
surface you compose, edit, layer, and keep.

## The holonic ladder (bdo's own vocabulary, defined)

bdo named three tiers — "the **parts**, **components**, and **canvas/pieces**."
Read as a holonic ladder, each tier contains the one below:

- **PART** — one generated primitive: a node (pill · rect · rounded · hex ·
  rhombus · subroutine · chips), an edge, or a region. The atom of a diagram. It
  is what `diagrams/compose.py` already renders deterministically. *(carries
  forward: the closed `NODE_TYPES`, explicit-position, byte-determinism.)*
- **COMPONENT** — a part made **interactable, editable, and addressable**, and
  authorized to **hold its attributes** (per-type config + the holonic fields
  `sites` / `space` / `strata{fundamental,derived,learned}` / `anima{strength,
  tempo}`). A component is a part you can select, inspect, edit, move, layer, and
  group. *(carries forward: `atom.diagram-attribute-model.v0`, and the
  schema-driven inspector discipline from `canvas.js`.)*
- **PIECE / CANVAS** — the board where components live: placed, layered, edited,
  saved. A **piece** is a saved composition — a named save-state, and (the
  holonic move) a reusable *component-of-components*: a piece can be dropped onto
  another canvas as one component. *(carries forward: `toJSON`/`fromJSON`,
  localStorage + file export/import; new: layers + named save-states.)*

The spec is the truth; the canvas is an **editor over the spec**. compose.py
already gives every node an explicit `x/y`, so dragging a part writes `x/y` back
into the spec — editing stays diff-stable and deterministic, and the gate still
judges the spec. The canvas is a richer *authoring pole*, never a second source
of truth (it fits the epic's membrane: generative pole → gate-with-teeth →
deterministic body → truth).

```
  describe / drag / infer ──► [ editable canvas: parts→components→pieces ]
        (the authoring pole)            │  edits write back into ▼
                                  ┌─────────────────────────────┐
                                  │   the diagram SPEC (JSON)     │  ◄── truth
                                  │  nodes·edges·regions·LAYERS   │      (byte-
                                  └─────────────────────────────┘       stable)
                                          │            │
                          [ qa.py: refusing gate ]  [ compose.py: spec→SVG ]
                            (the Miro-quality            (the deterministic
                             RIGOR, canon-cited)          render, unchanged)
```

## Carry past requirements forward (the explicit map)

bdo asked that nothing the tool already is be lost. Every standing requirement
and where it lives in this shape:

| Carried-forward requirement | Source | Where it lives here |
|---|---|---|
| Deterministic spec→SVG, explicit-position, byte-stable | done-0139, `compose.py` | **unchanged** — the canvas edits the spec; compose.py stays the renderer |
| Refusing gate, every refusal cites the named canon | done-0139, `qa.py`, `canon.md` | **unchanged** — gate judges the edited spec on export; the canvas cannot ship a picture the gate refuses |
| Auto-layout is REFUSED (diff-stability) | epic.diagram context (2) | held — drag writes explicit `x/y`; the only aid stays tier→grid-snap (`atom.diagram-gridsnap.v0`) |
| Regions = first-class **declared** membership (not geometric) | done-0151 | the **layer** model copies this discipline exactly (declared, not bounding-box) |
| Hold attributes (per-type + holonic fields) | `atom.diagram-attribute-model.v0` | the **component** tier — the inspector edits exactly these |
| Schema-driven: one SCHEMA drives defaults + inspector + persistence | done-0082, `canvas.js` | the **discipline** is reused (a new part-type ships as a SCHEMA entry, not new code) |
| Generative authoring: describe → validate → render, refuse malformed | done-0083, `authoring.js` | the **generation** path (CTA-E); reuses `validateSpec` |
| Projection-from-truth, folded into `term_economy`, never parallel | `atom.diagram-projection.v0` | the **generation** path can seed a canvas from a truth-fold; still folds into `term_economy.py` |
| No double-build; reuse discipline not artifact | epic.diagram context (3) | **the open fork** — see CTA-A |
| Causality look (cream paper, hand-drawn, anima), served live | `atom.diagram-experience.v0` | the **Miro-bar** skin (CTA-D) |

## The concept-list (categories · description · today · the gap)

**C1 — The component model.** *A part you can select, edit, move, layer, group —
holding its attributes.*
- Today: `compose.py` parts are render-only (no identity beyond `id`, no
  interaction). `canvas.js` has the editable-component machinery but for the
  causality vocabulary, not diagram parts.
- Gap: the diagram **part** has no **component** wrapper — no inspector, no
  selection, no attribute-holding. (`atom.diagram-attribute-model.v0` is the slot
  for this; it's planned, not built.)

**C2 — The editable canvas surface.** *Place, move, connect, and direct-manipulate
components in a browser, Miro-bar polish.*
- Today: no editable diagram canvas exists. `compose.py` emits a static SVG;
  `canvas.js` is the causality board.
- Gap: the whole interactive surface for diagrams. **This is the new build.**

**C3 — The layering system.** *Named, ordered layers; show/hide, lock, reorder;
membership declared, not geometric.*
- Today: nonexistent for diagrams. Regions exist (declared membership) and are
  the discipline to copy.
- Gap: a `layers` array on the spec + a `layer` field on parts (declared, like
  `region`); compose.py renders layers in z-order and omits hidden ones; the
  canvas shows a layer panel (toggle/lock/reorder). Deterministic and diff-stable.

**C4 — Save states.** *Name, keep, and restore versions of a canvas; the spec
file is itself a save-state.*
- Today: `canvas.js` has a single localStorage slot + file export/import — one
  state, not many.
- Gap: **named** save-states (snapshots a user can title and restore), in-progress
  autosave to localStorage, durable export to a spec file. A "piece" is a saved
  composition; a save-state is a titled spec snapshot.

**C5 — Edit-and-persist.** *Every edit (move, relabel, retype, re-attribute,
re-layer) is captured and survives reload.*
- Today: `canvas.js` round-trips through `toJSON`/`fromJSON`; the diagram surface
  has none of it.
- Gap: the inspector + direct-manipulation, persisted — the schema-driven
  discipline applied to the diagram SCHEMA.

**C6 — Generation (parts · components · pieces).** *Generate any tier: from a
description, or from truth.*
- Today: `authoring.js` (describe→schema-valid graph) and
  `term_economy.py diagram` (truth→spec) both exist but emit into their own
  surfaces, not an editable diagram canvas.
- Gap: wire both to **seed a canvas** — generate a part, a component, or a whole
  piece into the editable surface, where the user then edits and saves it. NL
  produces a *draft the gate judges*, never truth (carried-forward §10 teeth).

**C7 — The quality bar (Miro, only the bar).** *Miro-grade interaction polish and
finish; Miro's freeform-whiteboard model is explicitly NOT adopted.*
- Today: the rigor lives in `qa.py` (refusing gate); the polish target is the
  causality look (`atom.diagram-experience.v0`), unbuilt for diagrams.
- Gap: the served, polished, interactive surface — smooth select/drag/connect,
  the inspector, the layer panel, save-state UI — at Miro's *finish*, while the
  *rigor* stays in the gate and the *model* stays ontum's (declared structure,
  deterministic spec, refusing gate). Miro inspires the bar, not the architecture.

## The new systems, in detail

**Layering** extends the spec, it does not bolt on:
```jsonc
"layers": [ {"id":"base","label":"base","z":0,"visible":true,"locked":false},
            {"id":"annotations","label":"annotations","z":1,"visible":true} ],
// on a node/edge/region:  "layer": "annotations"     // declared membership
```
compose.py renders by ascending `z`, skips `visible:false` layers, and a part's
membership is **declared** (the region discipline, done-0151) — never inferred
from geometry. qa.py gains a `check_layer_membership` (a part on a layer not
declared → deny, the structural analog of an orphan).

**Save states** are titled spec snapshots:
- in-progress → autosave to `localStorage['diagram.canvas.v1']` (survives reload),
- durable → export a named spec `.json` (the save-state *is* the file),
- a **piece** = a saved composition; a piece can be re-imported as one component
  (the holonic move — composition is structure, `atom.diagram-composition.v0`).

**Edit-and-persist** is the schema-driven discipline applied to a diagram SCHEMA:
one table drives part defaults, the inspector panel, and `toJSON`/`fromJSON`. A
new part-type ships as a SCHEMA entry, not new code (carried from `canvas.js`).

## The calls-to-action (the forks — bdo steers, §10/D-4)

**CTA-A — Where does the editable canvas live? (the headline fork.)** The epic
says *"diagrams/ sibling to causality/, never an extension of canvas.js — reuse
the discipline, not the artifact."* bdo's ask (parts on an editable, persisted,
layered canvas) is exactly what `canvas.js` already does. Three roads:
- **A1 (recommended) — new editable canvas in `diagrams/`, reusing canvas.js's
  schema/persistence discipline by *pattern*.** Honors the epic's letter; keeps
  the causality board uncluttered; the diagram canvas edits the compose.py spec
  and exports through qa.py. Defer extracting a shared "canvas-kit" until a second
  consumer proves it's needed (don't pre-abstract). *Most code, cleanest doctrine.*
- **A2 — one engine: add a diagram *preset* to `causality/canvas.js`.** Least
  code; layers + save-states built once, shared by both presets. **Requires bdo
  to relax the epic's no-extension constraint** (and accept risk to the live
  causality preset). *Fastest, but reverses a prior stamp.*
- **A3 — bridge: extract the reusable mechanics (persistence, layers,
  save-states) into a small shared kit both canvases consume.** Most faithful to
  "reuse the discipline," but the most up-front structure. *Right only if a second
  consumer is certain.*

**CTA-B — Component granularity.** Is a **component** exactly "a part + its
attributes + interaction" (recommended — one part = one component), or also a
**group** of parts treated as one (a sub-piece)? Recommend: start one-part =
one-component; add grouping when `atom.diagram-composition.v0` lands (groups are
the holonic/nesting move, already a planned cell).

**CTA-C — Save-state model.** Recommend: autosave-to-localStorage (in-progress) +
named spec-file export (durable) + the spec file IS the save-state. Confirm, or
do you want a versioned in-repo save-state store (snapshots committed as records)?

**CTA-D — Miro scope.** Confirm the read: Miro inspires **only the interaction
finish/bar** (smooth select/drag/connect, inspector, layer panel) — ontum keeps
declared structure, the deterministic spec, and the refusing gate. *Not* adopted:
infinite freeform canvas, geometric-only grouping, auto-layout.

**CTA-E — Generation reuse.** Confirm both generation paths seed the *editable
canvas* (not separate surfaces): `authoring.js` (describe→draft) and
`term_economy.py diagram` (truth→draft), each producing a draft the gate judges.

## The smallest first cut (once CTA-A is stamped)

One done-line, the component tier proving the gesture on a real shape:

1. A diagram SCHEMA (part-types + holonic attribute fields) — the **component**
   model, inheriting `atom.diagram-attribute-model.v0`'s slots.
2. An editable canvas (per CTA-A) that loads a `compose.py` spec, lets you
   select/move/inspect/relabel a part, and round-trips through `toJSON`/`fromJSON`
   to localStorage + file (the **edit-and-save** core).
3. Layers as a declared field + one layer panel (show/hide/reorder) — the
   **layering** core, on the region discipline.
4. **Export → qa.py gate → compose.py render**: the canvas cannot ship a picture
   the gate refuses (the carried-forward rigor, proven by a §10 pair: an honest
   edited diagram exports; a layer-orphan variant is refused with the cited
   principle).

Save-states (C4 full) and generation wiring (C6) follow as their own cells.
Everything stands on truth (the spec), is gated (qa.py), and renders
deterministically (compose.py) — the carried-forward grain, intact.

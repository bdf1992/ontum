# Causality reality audit — presentation vs. living surface

*Deliverable #1, done-line 0060. A read of what Causality actually is in
ontum today, naming the gap between Causality-as-presentation and
Causality-as-living-term-surface. Every claim cites a real file or record;
where something is absent, that absence is named, not filled (hard rule).*

## The one finding

Causality today is a **sealed demonstration of a grammar**, not a surface
ontum operates. The grammar it proved is real and right — typed nodes, typed
routes, pulses, real local inference, receipts — but it lives **outside this
repo**, mutates nothing here, and is fed by nobody. The terminology-economy
slice this done-line builds is the first piece that is *inside* the repo,
*reads* repo truth, and *refuses* on bad evidence. It is one narrow vertical,
deliberately not the app.

## What is real

- **The grammar, proven, foundry-side.** A working typed pulse machine exists
  at `c:\Users\bdf19\experience-foundry\` (NOT in ontum git) — engine
  (`lib/causality.js`), canvas (`canvas.html`), real local inference bridge
  (`infer-bridge.py`, ollama/`claude -p`, never a cloud API). The end-to-end
  success story (input → code → inference → pen → receipt) ran. Source:
  report 0047 §"What exists in the foundry", `.ai-native/reports/0047-causality-surface-and-field-handoff.md`.
- **The arc, on the record.** `epic.causality-surface` is committed
  (`.ai-native/epics/epic.causality-surface.json`) with eight pieces across
  four waves — the witness/request/simulation registers, the virtual request
  node, schema/persistence, the API-first layer, the graph-authoring skill,
  the register UX discipline.
- **The disclosure, sealed.** The prototype is packaged as a sealed envoy
  (`exports/causality-envoy/`, 8 files, receipt on `exports/log.jsonl`). Its
  own `06-seams.md` is an honest self-audit — the source for much of the gap
  below.
- **This slice, real and tested.** `causality/term_economy.py` +
  `tests/test_term_economy.py` (11 tests, byte-reproducible projection, the
  §10 refusals). It reads the doctrine, `loop/*.py`, the log, `glyphs/`, and
  classifies five real terms with resolved evidence.

## What is mocked, demo-only, or disconnected — the gap

Drawn from the prototype's own seam audit (`exports/causality-envoy/06-seams.md`)
and the epic's piece statuses:

| Gap | Where it bites | Evidence |
| --- | --- | --- |
| **No persistence.** Every node carries the config fields for all ten types as inert properties — a flat bag that "will not survive a database." | No saved patterns, no versioned graphs, no reload. | `exports/causality-envoy/06-seams.md` §3; epic piece `atom.causality-schema.v0` (wave 2, unbuilt) |
| **No API-first paths.** The browser IS the authority; there is no read/request/projection/test API the canvas is merely one client of. | Not drivable by CLI, DevTools, Playwright, or NL against one contract. | epic piece `atom.causality-api-layer.v0` (wave 4, unbuilt); seams §8 |
| **No canvas interaction for config.** You cycle a node's type by clicking a badge; there is no click-node → config panel, click-route → config. | The immediate UX gap bdo named. | `exports/causality-envoy/02-vision.md` piece 5; seams §9 |
| **No graph semantics that survive scale.** "The diagram IS the system" has no principled answer for what the fold should *omit* to stay a useful abstraction. | A busy system renders an unreadable canvas. | seams §1 (named the make-or-break) |
| **Informal concurrency.** A pulse mid-think is dropped; no parked/resumed pulse, no backpressure, no cancellation. | No honest long-running node. | seams §5; epic piece `atom.long-running-exec.v0` (wave 3, unbuilt) |
| **`new Function()` for code/gate bodies.** A prototype-only shortcut; an injection surface in any shared context. | Not yet the governed pen model. | seams §4 |
| **Disconnected from repo truth.** The foundry canvas is fed by hand templates, not by a fold over `.ai-native/log/`. It is a *reflection* (drifts), not a *projection* (cannot drift). | It shows a picture, not the system. | `02-vision.md` §"The load-bearing idea"; the prototype is foundry-side, touches no ontum record |

## The category-error guard (the prototype flagged it on itself)

`exports/causality-envoy/06-seams.md` §10 names the live risk: "Causality
visualizes ontum" can quietly make the *visualization* the point when the
substrate exists to build something else (report 0004's harness-vs-fabric
correction). This slice answers that risk concretely: it is **read-only**, it
**writes no record**, it **mints nothing**, and its whole job is to make the
*language* — a thing ontum genuinely needs to keep honest — inspectable. It
is metabolism (watch your machine run), not a second building.

## Where this slice sits in the gap

It closes exactly one square of the table — *disconnected from repo truth* —
for one data type (terminology) on one narrow path (resolve declared
citations → classify → project), and proves the projection property (a fold
that reproduces byte-for-byte, cannot drift) on real terms. It does **not**
touch persistence, the API layer, canvas interaction, concurrency, or the
`new Function` surface. Those stay named here and owned by their epic pieces.

## Verdict

Causality-as-presentation is a **proven grammar with no body in ontum**.
Causality-as-living-surface begins where a fold over real repo bytes refuses
to lie about what a term means. This audit is the floor that increment stands
on; the term-fold audit (`term-fold-audit.md`) is the method it runs.

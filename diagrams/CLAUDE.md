# diagrams/ — the diagram part

A governed diagramming surface for ontum: it captures subject-matter
intent and renders **honest** architecture diagrams, and it can
**refuse** a dishonest one with a cited reason — the thing a generic
drawing tool (draw.io, raw Mermaid) structurally cannot be. Arc:
[`epic.diagram`](../.ai-native/epics/epic.diagram.json). First bar:
[done-line 0139](../.ai-native/done/0139-diagram-floor-and-gate.md).

Ported and turned up from the `diagram-author` skill that lived in the
SubProtocol vault (`_theme/svg/compose.py` + `skills/diagram-author/`);
this is its ontum home, rebuilt in the repo's grain.

## What it is (the shape)

Built *as* the membrane architecture this repo designed, not bolted onto
it: a **generative pole** (a description / gesture, later bounded
inference) feeds an **ingress gate with teeth** (the named canon,
refusing), which gates a **deterministic body** (`compose.py`: spec →
SVG, the fold), standing on **truth** (the repo, in projection mode).
Read [`canon.md`](canon.md) for the SME the gate enforces.

## Hard rules

- **Stdlib, local-first.** Same law as `loop/` — no network at runtime,
  no daemon; a named offline dependency only where it earns its place
  (a real graph-layout library, if auto-routing is ever built — not a
  hand-rolled Sugiyama). The renderer is pure stdlib.
- **Explicit-position, not auto-layout.** `compose.py` places nodes at
  declared coordinates *by design* — it protects diff-stability (one
  node added → one diff), which is `.ai-native`'s byte-deterministic
  grain. The only admitted layout aid is **tier-declaration → grid-snap**
  (you declare the rank, the tool does the arithmetic). A constraint
  solver / orthogonal router is **refused** at this layer (see the
  SubProtocol taste: "auto-layout produces unpredictable diffs").
- **The canon governs, with teeth.** Every gate refusal cites a named
  principle in [`canon.md`](canon.md) (Moody · graph-drawing aesthetics ·
  C4) — never taste-by-assertion. The `data-visualizer` advisor is a
  **sub-advisor for quantitative genres only** (e.g. sankey), **not** the
  governor: it is the *charts* canon (it ranks encodings of magnitude),
  and an architecture diagram encodes connection and type, no magnitude.
- **Projection, never a second truth (§10).** A diagram drawn from the
  repo is a **fold over evidence**; it resolves every node/edge against
  committed bytes and refuses what does not resolve. It does **not**
  build a parallel fold: any from-truth projection folds **into**
  [`causality/term_economy.py`](../causality/term_economy.py), never a
  sibling `diagram_economy.py`.
- **No double-build (§10).** This module is a **sibling to `causality/`**,
  never an extension of [`causality/canvas.js`](../causality/canvas.js)
  (a schema change there would break the live causality preset). Reuse
  the schema-driven *discipline* and the generative-authoring *pattern*
  ([`causality/authoring.js`](../causality/authoring.js)), not the
  artifacts. Consult the live Pattern Commons
  (`causality/patterns/pattern-commons.v1.json`) before inventing a
  pattern; deposit, do not free-style.
- **A genre earns its place by the §10 test.** Add a genre only when two
  real diagrams *refuse to fit* the existing ones. The "membrane
  cross-section" is **not** a genre — it is invented notation (refused by
  graphic economy / semantic transparency); it stands only as a one-off
  authored diagram.

## Commands (as pieces land)

```sh
python diagrams/compose.py <spec.json> [--out OUT.svg]   # the deterministic floor: spec → SVG
python diagrams/qa.py <spec.json>                        # the refusing gate: deny + cited principle on stderr
python -m unittest tests.test_diagram -v                 # the §10 test: honest passes, dishonest refused
```

## Layout (as pieces land)

- `compose.py` — the deterministic spec→SVG renderer (explicit-position;
  ported from the SubProtocol `_theme/svg/compose.py`).
- `qa.py` — the gate: was a checklist-runner, promoted to a refusing gate
  in the off-log-gate / mock-shame grain (nonzero + reason on stderr,
  fail-open on its own error).
- [`canon.md`](canon.md) — the named architecture-diagramming SME; every
  gate rule cites a principle here.
- `examples/` — committed spec + rendered SVG, byte-deterministic.
- the pieces and their waves live in
  [`epic.diagram`](../.ai-native/epics/epic.diagram.json).

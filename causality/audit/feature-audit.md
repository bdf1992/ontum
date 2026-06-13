# Causality feature audit — launched, driven, and scored

*A hands-on quality scan and feature audit of the Causality canvas
(`experience-foundry/canvas.html` + `lib/causality.js` + `infer-bridge.py`,
and the `04-causality` showcase), run in a real browser (agent-browser/CDP)
against bdo's three questions: does it have the **editing**, **data**, and
**persistence** to be a usable tool, or is it still a toy? Every finding below
is grounded in observed browser behavior, not a code read. Companion to
`reality-audit.md` (the desk read) — this is the same gap, confirmed live.*

## How it was run

- Served the foundry on `:8080`, started `infer-bridge.py` on `:8378` (real
  local inference, ollama `mistral:latest` / `qwen3`), opened
  `canvas.html` in a pinned 1280×720 browser, drove it through the engine's
  own debug handle `window.__cz` (API-first; the handle IS the surface's API).
- Screenshots: `experience-foundry/shots/audit-01..05-*.png`. Console clean
  on every round (`window.__pageErr` → "no page errors").

## The three intents (read before the verdict)

- **Code's intent:** `canvas.html` is a typed-pulse *authoring machine* —
  typed nodes (stock/source/sink/code/inference/gate/pen/…), routes that
  refuse incompatible wires, pulses carrying data, real local inference, a
  live latency-vs-expectation fold. `04-causality` is an *essay showcase*
  ("More of This, Less of That") that loads the real ontum log for
  illustration.
- **User's intent:** bdo and a managing AI session who need to *compose and
  operate real ontum work as a graph*, watch the system move, and trust what
  they save. bdo acts by gesture, never CLI.
- **Use-case's intent:** a returning **work hub** (compose → save → reload →
  operate). That register *demands* persistence, deep editing, and real data.
  Today the surface is built at the **arrival/demo register** — beautiful,
  instant, and ephemeral. The register mismatch is the whole finding.

## Verdict

**Causality is a proven grammar with a beautiful demo body and no working
memory. Today it is a toy — an extraordinary one, but a toy.** It fails all
three of bdo's tests *in the editable surface*: you cannot deeply edit a node,
you cannot point it at the real system's data, and you cannot save anything.
The pulse machine and the typed-node idea are real and right, and real local
inference genuinely works — which is exactly why the missing tool-grade
capabilities are worth building, not abandoning.

## Finding 1 — EDITING: shallow (label + geometry only)

**Observed.** A node carries real, load-bearing config. Live read of the
inference node:

```
backend: "ollama"
prompt:  "You are a research assistant. Give 3 concise bullet leads
          for this search, no preamble:\n{{data}}"
model:   null
```

But a full DOM scan returned `configPanels: []` — there is **no inspector,
form, or config UI anywhere**. The only inputs on the page are the template
dropdown, the poke selector, and the inject text box. The only editable node
property is its **label** (double-click → rename). Route editing is
geometry-only (click a wire to flip its sign or cycle its kind).

**So:** the *prompt* — the thing that defines what an inference node actually
does — is set by the template and is invisible and uneditable in the UI. To
author a real graph you must edit JS template functions or type into the
browser console. That is a toy's editing surface. The fix bdo already named is
the **per-element config panel** (click node → config for its type; click
route → its config), which the envoy seam audit also flagged (§9).

## Finding 2 — DATA: real inference, no real-system ingress

**Observed.** Inference is genuinely real, not mocked. A direct bridge POST
returned in mistral (`{"result":"Alive","ms":6880,...}`), and firing the
search-agent pipeline through the engine produced a real result and a receipt:

```
inferenceOut: "1. Recursive Feedback Loops: Key regulatory mechanisms in
               biological systems… 2. Positive and Negative Feedback Loops…"
receipts: 1   inflight: 0   busy: false
```

**But** the editable canvas has **no ingress of the real ontum system**: no
atom search, no log load — only hand-typed inputs and code-defined templates.
The engine's API (`window.__cz`) exposes `node/link/clear/inject/step/stats/
render/…` and no `load`/`import` verb. The *only* place the real ontum log is
ingested is the `04-causality` essay (`window.LOOP_LOG` present, 7 canvases),
and that surface is a scrolling narrative with `rename/clear/preset/pulse`
controls — an illustration, not an operable tool.

**So:** data flows *through* the machine, but the machine cannot *see* the real
system, and the one surface that loads real data isn't editable. The "real
data" and "editable tool" halves live in different files. Unifying them is the
wave-1 `atom.atom-search-request-node.v0` slice; the new
`causality/term_economy.py` fold is one read-only projection such a canvas
could render.

## Finding 3 — PERSISTENCE: absent (the decisive gap)

**Observed.** The engine API has **no `save`, no `load`, no `export`** — all
three are `undefined`; the full verb list carries none. There is no
localStorage, IndexedDB, or file export anywhere. Proven by the reload test:

```
added node "AUDIT-PERSIST-TEST"        → nodes: 5
reload                                 → nodes: 4, auditNodeSurvived: false
                                         (canvas reset to template default,
                                          receipts back to 0)
```

**So:** every reload is a total wipe. Nothing you make survives — you cannot
save a graph, name it, reload it, version it, or share it. This single gap is
enough to keep Causality a toy regardless of how good the canvas is, and it is
the highest-leverage thing to fix. It maps to wave-2
`atom.causality-schema.v0` and the flat-bag-won't-survive-a-database seam the
envoy audit named (§3).

## What's missing to cross the toy → tool line (prioritized)

1. **Persistence (P0)** — `toJSON`/`fromJSON` over the whole graph
   (nodes + routes + config), a named/versioned saved record, reload, and
   import/export. The single biggest lever. *(epic wave-2
   `atom.causality-schema.v0`.)*
2. **Per-element config panel (P0)** — click a node → an inspector for its
   type (prompt / code body / backend / model / latency / required fields);
   click a route → its config (sign / kind / delay / compatibility). Turns
   editing from rename-only into authoring. *(the immediate UX gap, envoy
   §9; epic wave-4 `atom.register-ux-discipline.v0`.)*
3. **Real data ingress in the editable canvas (P1)** — load the real ontum
   log / search atoms in the *tool*, not only the essay; unify the two
   surfaces. *(wave-1 `atom.atom-search-request-node.v0`.)*
4. **A real API + governed authoring (P1–P2)** — promote the `window.__cz`
   debug handle to a documented read/request/projection API with the
   persistence verbs, and route any authoring that touches real ontum through
   pens + trust rungs (the `new Function` body, envoy §4, becomes a vetted pen
   body). *(waves 3–4: `atom.virtual-request-node.v0`,
   `atom.causality-api-layer.v0`.)*

The punch list is not a new plan — it confirms and prioritizes
`epic.causality-surface`'s own waves against what the launched surface
actually does today. P0 (persistence + a config panel) is the smallest change
that flips the verdict from toy to tool.

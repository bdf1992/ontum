---
name: recommend
description: >-
  /ask expanded into a generative branching tree. Where /ask raises one
  panel and asks "which of these?", /recommend composes a routed TREE of
  panels — each AskUserQuestion call is up to 4 tabs x <=4 options, and a
  route selected in one tab GENERATES the next set of checkboxes, composed
  live from that route + bdo's gesture. The ~20 options across several
  routes are the tree's leaves, walked branch by branch; the recommended
  path is marked at every panel. Use when bdo hands a loose or complex
  design prompt whose honest response is a composed recommendation across
  several routes, or on "/recommend". It is GENERATIVE by necessity (the
  branches cannot be pre-authored — inference composes each next panel)
  and BOUNDED (compose.py's refusal check runs on every generated panel
  before it renders). It composes /ask's whole law (../ask/policy.md is
  the floor; policy.md here adds the tree rules) and is the concrete form
  of the captured design-conversation meta-skill. The living discipline
  persists in the shared registered memory `ontum-ask-surface-discipline`.
version: 0.2.0
owner: bdo
changelog:
  - version: 0.1.0
    note: >-
      First form. bdo asked for a /ask variant that "composes a complex
      and informed recommendation with options, mostly multi-select and
      themes with routing decisions… 20 options and several routes… until
      we have a generative compositum."
  - version: 0.2.0
    note: >-
      bdo, 2026-06-18, corrected the v0.1 render: NOT a document +
      decision-pens, and NOT an "inverse ask / confirm-not-select" (my
      mis-read). The real shape: "multiple tabs of 4 options with routing,
      so one route might prompt a second set of checkboxes" — a GENERATIVE
      BRANCHING TREE of panels. He chose "build the generative step now".
      This version rewrites the render to the tree, adds the code bound
      (compose.py), and drops the inverse framing.
---

# /recommend — a generative branching tree of routed panels

`/ask` raises **one** panel at a fork and asks "which of these?".
`/recommend` composes a **tree**: a routed sequence of panels where the
answer to one **generates** the next.

- A panel is one `AskUserQuestion` call: up to **4 tabs (questions)**,
  each with **≤4 options**.
- **Routing is the mechanism.** A route selected in a tab *prompts a
  second set of checkboxes* — the next panel, composed **live** from the
  route taken plus bdo's gesture. Routes branch; the tree grows as he
  walks it.
- The **~20 options across several routes** are the tree's leaves. They
  are never crammed into one modal (the 4×4 cap forbids it); they are
  reached by walking the branches.
- Every panel is **recommendation-first** (`/ask` R1): the recommended
  route/subset is marked at each step, with the reasoning in the
  description and routes narrated in `preview` (R2). The tree does not
  withhold the pick; it composes a *path* of picks.

```
gesture
  │  compose (inference, bounded)
  ▼
Panel 1  ──tab A: route X* | Y | Z      (recommend X, narrated)
         └─tab B: theme checklist [≤4]
  │  bdo selects X
  ▼  compose NEXT from X  (the routing → second set of checkboxes)
Panel 2  ──tab A: checklist generated for X [≤4]
         └─tab B: route X1* | X2          (recommend X1)
  │  bdo selects …
  ▼  … walk until the space is resolved
Composed recommendation  (+ trace recorded for re-read / audit)
```

## Generative by necessity, bounded by the floor

The branches **cannot be pre-authored** — which next checkboxes a route
prompts depends on the route taken and the gesture. So each next panel is
**composed by inference** (the session is the composer — see the
architectural note). That is the "generative compositum" bdo named: the
tree generated as it is walked.

It is **bounded**. Before any generated panel renders, it passes the
refusal check in [`compose.py`](compose.py) — the deterministic floor of
`/ask`'s law: ≤4 tabs × ≤4 options, a single-select route tab carries a
`(Recommended)` option (R1) and narrated `preview`s (R2), headers ≤12
chars. A generated panel that fails the bound is **refused before bdo
ever sees it** — reshape and recompose, never render the unbounded panel.
This is inference-as-composition (`ontum-inference-as-composition-layer`):
the settled-safe floor is code, the fresh composition is inference.

## Architectural note: the composer is the session

`AskUserQuestion` is a **session tool** — only the live session can
render a tab. So recommend's generative step is **prompt-as-code, not a
headless pen**: this skill instructs the session (the inference) to
compose each next panel from the prior route, and the session calls
[`compose.py`](compose.py) to enforce the bound before rendering. The
code's job is the *bound and the trace*; the session's job is the
*composition*. (This is why there is no `loop/compose.py` rendering
panels in a subprocess — it could not reach the tool.)

## The loop (how a session runs recommend)

1. **Read the gesture** and the priors it touches (proposals, memory,
   code) — the design-conversation move: connect bdo's half-formed intent
   to what already exists.
2. **Compose Panel 1** — a routing tab (recommendation-first, narrated)
   plus any theme checklists. Run it through `compose.py`'s bound. Render.
3. **On each answer, compose the next panel** from the route taken +
   gesture. Bound, render. A route *prompts* its own next checkboxes —
   that is the branching.
4. **Resolve** when the space is walked: state the composed
   recommendation in prose, and record the walked tree as a trace (a
   `*.recommend.md` when it should persist) for re-read and the audit
   fold.
5. **Refuse** at any step the bound bites, or if the space turns out to
   be no real decision-space (see policy RC5 / the offloading rule) —
   then make the call yourself and proceed.

## Compose, don't double-build (§10)

recommend does **not** re-author `/ask`'s law. The shape (R1–R7, the
refusal teeth) lives in [`../ask/policy.md`](../ask/policy.md); recommend
adds only the tree rules in [`policy.md`](policy.md) beside this file. The
living discipline and learnings stay in the **shared** registered memory
`ontum-ask-surface-discipline` — one home for both. recommend is one
render of that discipline; `/ask` and the bdo-brief digest are others.

## The honest limit (inherited)

The `AskUserQuestion` **modal chrome** is the harness's, not ours to
reskin (R6). recommend's lever is the composition, the bound, the trace,
the affordances inside the call, the policy, and the shared memory.

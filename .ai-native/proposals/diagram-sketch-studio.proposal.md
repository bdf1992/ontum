# Proposal — The hand-drawn sketch studio: a physical, NL-driven authoring surface

*Captured 2026-06-23/24, bdo iterating live. A built-ahead **probe** (working
code in the `handdrawn-diagram` worktree, branch `worktree-handdrawn-diagram`),
written for bdo to react to and to decide its home and priority. **PROPOSED** —
a session proposes; the arc and its rank are bdo's (D-4).*

## Where it came from

Started as "what if we got a good local image model and wired it to our
diagrams." Corrected twice in conversation: (1) the right lineage is **vector
(SVG) + a thin raster slot**, not diffusion-for-everything — vector composes,
validates, scales, and banks into a stable library, which diffusion cannot; (2)
the first cut (a **dials control panel**) bdo rated **1/5, "does not pass the
bar."** Rebuilt under the `experience` skill against the Pattern Commons.

## What is built (the probe)

A served, offline, local-first **sketch studio** — `diagrams/sketch-studio.html`
+ an owner-run localhost bridge `diagrams/sketch_studio.py`:

- **Physical canvas** (Commons: `direct-manipulation`): place / select / move
  (with inertia) / resize / marquee, real mass and springs, born-ease, hand-drawn
  seeded-deterministic vector (Commons: `sketch-permission`).
- **NL is the control panel** (Commons: `ml-duet`): a command bar over **local
  inference** (ollama; default `mistral:latest` — qwen3 collapses under
  forced-JSON) composes objects from a sentence; output is **validated against an
  op schema before it draws** (the authoring.js discipline).
- **Simple settings, not dials**: small GLOBAL toggles (theme/snap/clear) + a
  per-object LOCAL mini-bar (recolor/shape/duplicate/delete) for **repeated ops
  only** — never NL.
- **Logs + undo/redo**: append-only activity log panel; snapshot history with
  Ctrl+Z / Ctrl+Shift+Z (the fold-over-a-log shape, on the canvas).
- **Images**: place / size, saved server-side as real files.
- **Canvas → session loop**: select parts → note → button → a **requisition** the
  session reads. **Session-bound link** (`?to=token`) so the session that hands
  you the link is auto-addressed — no picker; tabs = bound workspaces.

## The honest shape: this is two of epic.diagram's waves, missing its rigor

Mapped against [`epic.diagram`](../epics/epic.diagram.json):

| this probe | epic.diagram piece | gap |
|---|---|---|
| NL command bar → validated spec | `atom.diagram-generative.v0` (wave 2) | epic wants it feeding the **gate**; the probe has no gate |
| hand-drawn look, served live; physical canvas | `atom.diagram-experience.v0` (wave 4) | epic says experience is **skin, never rigor** |
| logs, undo/redo, session-requisition loop, session-bound links | *(none — new)* | not in the epic at all |

The tension to resolve, plainly: epic.diagram's organ is a **governed,
deterministic renderer with a refusing gate** (compose.py spec→SVG + qa.py canon,
explicit-position, projection-from-truth). This probe is a **freehand authoring
editor** with **no gate, no canon, not folded from truth**. It is the epic's
*front door* (generative + experience) built before its *spine* (the gate). Left
as-is it would **double-build** the renderer and skip the rigor — exactly what
epic.diagram's context section forbids (§10).

## The fork for bdo (this is the priority decision)

1. **Fold into `epic.diagram`** as the realization of waves 2+4, and reconcile
   it with the spine: the studio authors a **spec** that `compose.py` renders and
   `qa.py` gates — the canvas becomes the *generative + experience* surface over
   the existing deterministic floor, not a parallel renderer. *(Recommended — it
   keeps the rigor and avoids the double-build.)*
2. **A sibling arc** (`epic.authoring-studio`) — if the *direct-manipulation
   editor + canvas→session loop + session-bound surfaces* are a bigger thing than
   diagramming (they touch the authoring-platform vision and the session-gateway),
   give them their own home and let epic.diagram stay the governed renderer.
3. **Hold** — keep it a probe in the worktree; bank the learnings; don't rank it
   yet.

The deeper design question under (1)/(2): **how much governance does a *sketch*
surface carry?** epic.diagram's whole thesis is "a diagram is an act on the
record that can refuse a lie." A freehand canvas is the opposite — a *pencil*,
provisional. (The `sketch-ink-paint` proposal's frame fits here: this canvas is a
**sketch** stage; it earns **ink** only when it emits a gated spec.)

## Calls to action (against the purpose: make visual assets we can trust + see fast)

- **CTA-1 (decision):** pick the home — fold into epic.diagram (rec.), sibling
  arc, or hold. This sets the priority; until then the work is **unranked in the
  loop** (its priority lives only in attention + the `ontum-handdrawn-sketch-studio`
  memory).
- **CTA-2 (the bridge to rigor, if folded):** the studio's "export" emits a
  `compose.py` **spec**, run through `qa.py` — so a hand-drawn sketch can be
  *inked* into a gated, deterministic, projectable diagram. This is the single
  move that reconciles the probe with the epic.
- **CTA-3 (the asset library):** banked, validated reusable components (the
  original "stable libraries of validated assets" ask) — a sketch becomes a
  Commons/asset deposit once gated.
- **CTA-4 (the session loop as substrate):** the requisition + session-bound link
  is an instance of the session-gateway's *live injection / registered-addressable
  sessions* (#534) — if it grows, it belongs to that arc, governed by deny-by-default
  authz, not reinvented here.

## What it does not do (yet) / honest gaps

No gate, no canon, no projection-from-truth (CTA-2). The raster/asset-library
idea (the original ask) is present only as the concept, not built. bdo has not
yet driven the studio to approval; nothing here is landed.

---

*Decisions are bdo's (D-4). On a confirm/fold, this proposal stays as the record
of where the arc was born and notes "REALIZED → see epic.<id>" at its head.*

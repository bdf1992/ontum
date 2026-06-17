# Causality — iterations log

The shared place where refinements to the **design** and the **system** land —
so a change of shape or feel is a recorded decision a later session can read,
not a message lost in a chat. Newest at the top. Each entry says what was asked,
why, and where it landed.

Status: 🔴 open · 🟡 in progress · 🟢 landed

---

## 0003 — The story demo: cute skin, mechanical body, sliders steer both 🟡
**2026-06-17 · bdo**

The homepage's purpose: **tiny natural-language stories that are cute on the
surface but mechanically rich underneath.** "The little robot waters the plant
when the leaves droop, then checks tomorrow to see if it helped" reads casual,
but the system hears `actor → desire → signal → action → state-change →
evaluation → loop`. The proof: *natural language is a compressible interface to
a working system.*

> A tiny story is the visible skin. The graph is the hidden body. The sliders
> alter both at once — they are **world-physics controls**, not "AI story
> controls." Moving one changes the cute sentence *and* the underlying mesh.

**Sliders = translation pressure:**
- **Complexity** → node density + relationship variety (how much structure is extracted)
- **Length** → timeline depth (how many temporal frames unfold)
- **Twists** → how often causal assumptions invert (observer becomes observed, hidden parent loop)
- **Colors** → palette + emotional/semantic register + node styling
- **Weirdness (arbitrary inclusion)** → how aggressively odd objects must be integrated — and each object must *earn a relationship* (a key → lock/secret, a bell → signal/alert, a mushroom → growth/memory), not just decorate.

**Random** → a *seed card* (creature, desire, world-signal, arbitrary object,
twist, palette, complexity, length), which compiles to a story + a mesh.
**Epic mode** → many time-series episodes from one world model: `local loop →
learned rule → inherited behavior → world memory` (recursive teaching / network
growth).

**Three panes:** Story (the sentence) · Mesh (the animated canvas) · System
(events, states, rules, loops, unresolved tensions).

The five-seed first pack (covers observer/signal/state/memory/path/resource/
recursion): owl+stars (observation), robot+plant (feedback), mouse+crumbs
(path/memory), cat+sunbeam (moving attractor), caterpillar+leaf (growth/consumption).

**Architecture call (mine):** the served site is static — no LLM backend — so the
generator is a **deterministic local story-compiler** (seed + sliders →
sentence + mesh, plain JS, instant, works for everyone, on-brand: real structure
not a hallucination). Open-ended LLM authoring returns as a local-only mode when
the inference bridge runs.

Lands in: _(in progress — `causality/stories.js` compiler + a clean control
strip + story pane on the minimal canvas; slice 1 = the five seeds + complexity/
length/weirdness + Random + Generate; twists-matrix, epic mode, and the System
pane follow.)_

---

## 0002 — Minimalist: remove before adding 🟢
**2026-06-16 · bdo**

Iteration 0001 put the canvas as the home but kept all the tool chrome
(describe-bar, template/poke/inject bar, help text, legend, system panel).
**Too much. Remove before adding.** Strip to **just the canvas** and perfect the
basic design-system patterns first: **canvas, size, color, lines.**

- Strip the chrome to near-nothing — quiet `Causality` wordmark, and a faint
  `+ New` / `Save` cluster that comes up on hover. Everything else removed for now.
- **Hover tooltips, not always-on labels** — node metadata (type / latency)
  appears on hover; the canvas stays clean.
- Keep the **animations** (the living ink — wobble, water, pulses).
- Perfect the fundamentals before re-adding any tool: node **size** + spacing,
  the **color** application, and the hand-drawn **line** weight (fine-tipped
  marker). Re-introduce tools deliberately, one clean affordance at a time.

Lands in: _(in progress — strip canvas.html chrome; node sublabels hover-only.)_

---

## 0001 — The whole app is the canvas 🟡
**2026-06-16 · bdo**

The served surface shipped as *two* things: a welcome-mat HTML page that links to
the canvas. **Wrong shape.**

**Hard requirement: the entire app takes place on the canvas — one surface,
nothing else.**

- The **home screen itself is built from nodes on the canvas** — not a separate
  page. The `Causality` wordmark, the felt-field, all of it lives as nodes.
- Minimal chrome only: a **+ New** button (clears the canvas) and a **Save**
  button.
- A person can **edit their home-screen canvas and save it** — the home is just
  a saved canvas document like any other.
- **Feel:** the `Causality` wordmark, nice typography, easy on the eyes (keep the
  current cream palette and fonts), clean lines — almost **hand-drawn with a
  fine-tipped marker**.
- **No-compromise experience FIRST — not phone-first.** The surface is judged by
  the best experience the canvas can be; phone / web / desktop are incidental
  access points to the same served surface, never the constraint that narrows the
  design. (bdo's correction — don't optimize for the small screen.)

Why: Causality is one canvas where witness / request / simulation share a single
surface (`epic.causality-surface`). A separate home page is a *second* surface —
it breaks the one-canvas premise. The felt-field welcome mat becomes a canvas
**document** (nodes folded from the log), openable, editable, saveable.

Lands in: _(in progress — reshape the canvas to the single surface; the welcome
mat becomes the default home canvas document; add + New / Save chrome.)_

---

## 0000 — Causality's surface is served 🟢
**2026-06-16 · done-line 0099 · PR #175 (rcp.merge.175)**

The canvas + welcome mat reach a public URL the owner can open from his phone:
**https://bdf1992.github.io/ontum/**, deployed by `.github/workflows/pages.yml`
on push to `main`. The diagnosis that started it: the canvas kept "failing to
land" only because the one judge with taste had never *seen* it — it lived behind
a `localhost` command. Serving it closed the seeing loop. The hard rule held: the
loop stays local-first; only the experience layer is published at build time.

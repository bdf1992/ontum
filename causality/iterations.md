# Causality — iterations log

The shared place where refinements to the **design** and the **system** land —
so a change of shape or feel is a recorded decision a later session can read,
not a message lost in a chat. Newest at the top. Each entry says what was asked,
why, and where it landed.

Status: 🔴 open · 🟡 in progress · 🟢 landed

---

## 0013 — The pattern named: Auditable Intent Mesh (AIM) — the gesture→AI→response loop, formalized 🟡
**2026-06-18 · bdo** — generalize to the *intent of the pattern*, then make it executable

The bake-off climb (a winner → a recipe book → "bake our experience" → *both* →
the general pattern → its Pattern Commons) bottomed out where bdo named it: the
move is **not** "a fancier graph." It is **name the actual pattern and make it
executable.** He handed the full formalization brief and the working name.

**Auditable Intent Mesh (AIM)** — the formal pattern under the surface, the **open
heart** 0012 left unturned (the gesture→AI→response loop), now specified instead of
guessed. The load-bearing correction: *a gesture is not the command — it is evidence
of possible intent*; the system compiles gesture + selected context + source
evidence into a normalized **intent packet**, then routes it proposal → gate →
admitted pen → audit event → projection refresh. It is **ontum's own loop**
(log-is-truth → pen → gate → receipt → fold) pointed at the interaction surface —
not new machinery. Four registers (**Record / Runtime / Request / Simulation**) and
the clean law: *infer/simulate/request freely; commit only through an admitted pen.*
Six sub-graphs (source / witness / request / execution / audit / projection), 15
primitives (reusing the display-system C1–C18 witness half), 7 failure modes each
with teeth, 7 invariants + the §10 fit-refusal test.

Recommended name: **AIM** over the native **WIM (Witnessed Intent Mesh)** — *audit*
and *execution* are the missing requirements; *witness* names only the half already
built. Status **PROPOSED**; the mint and the home in the Pattern Commons
(`causality/patterns/`, PR #174) are bdo's (D-4).

Lands in: [`auditable-intent-mesh.md`](auditable-intent-mesh.md) — the formal spec.
Open holes named there (OH1 gesture→packet compile table, OH2 the gesture-pen, OH3
virtual request-nodes, OH4 membrane scope, OH5 the mint). Next: bdo blesses the name
+ seeds OH1's compile table, *or* we pressure-test the spec via the diverge-judge
panel (dogfooding AIM's own §3) before building the smallest executable slice.

---

## 0012 — Causality is a spatial-graph RepoPrompt: the narrative is the directory (defined by negation) 🟡
**2026-06-17 · bdo** — the frame, set before anyone cooks again

The hunt for the home surface's *shape* converged here. A 4-chef bake-off
(full-live, on-canvas, both-axes — orchestrated as a workflow) cooked a
"minimal element zoo," and bdo named the result exactly: *"this is like the
ingredients… not quite the right shape to even enter the context yet."* A
**catalog** frame can only ever produce ingredients; the missing things —
editing, flavor, animation, nuance, usability, **narrative** — are properties
of an *experience with an arc*, which a specimen sheet structurally cannot
have. The bake-off's keep: the **decomposition vocabulary** (3-strata: word →
mortar/glyph → facets → real engine channels, the editorial chef's, judged
best) and a harvested plating (naturalist's, judged best surface). The four
candidate pages live in `causality/zoo-*.html` + the synthesis `zoo.html` as
the **pantry, not the dish** — kept, not landed.

**The reference (bdo): RepoPrompt** (`github.com/repoprompt/repoprompt-ce`) —
a native **context-engineering** tool: point it at a repo → index → curate
files / line-ranges / CodeMaps / git-diffs → assemble a dense, reviewable
**context package** for an AI agent. **We are making the spatial-graph,
AI-native version: point Causality at a directory and the narrative is
*generated from the files* you pointed it at.** The living graph *is* the
curated context; you shape it by gesture, not checkboxes. It dogfoods on day
one — point it at `ontum`, get ontum's own story.

**Defined by negation first (bdo's framing — non-examples do the heavy
lifting). What it shouldn't be:**
1. **Not RepoPrompt's file-tree redrawn as a graph** — folder-nesting-as-edges
   is a reskin; the narrative is the *relationships and meaning*, not the
   hierarchy with prettier lines.
2. **Not a static architecture diagram** — not a dead Mermaid/dependency
   picture; it moves, it's alive, you edit it by touching it (instrument, not
   render).
3. **Not a zoo / catalog of file-nodes** — the exact failure above; ingredients
   laid out, no arc.
4. **Not a token-budget spreadsheet** — meaning leads; the budget is a quiet
   consequence of what you've selected, never the hero.
5. **Not a chatbot with a graph sidebar** — the conversation happens *through*
   the graph (selection zones, gestures), not a bolted-on chat panel (the
   Interface-as-AI anti-pattern named in `display-system.md`).
6. **Not click-ops** — gesture-native (select-patterns, move, recolor, draw),
   no checkbox tree or menu-of-buttons.
7. **Not a second source of truth** — the graph is a *witness* of the directory
   (Causality's one hard rule), never the authority over the files it reads.

**What it therefore is (the one line):** *a living, gesture-native spatial
graph that generates a navigable story from a directory, and lets a person
build AI context and steer their AI by playing it.*

**The experience (bdo, painted):** you open on the canvas; a **simple cut
story** is alive in nodes / connections / pulses, moving and dynamic; you
**read it by scrolling and zooming, and that act edits it** (no separate
mode); zoom a node and you find **its own story** on the same page;
**interacting is the animation and the authoring**; **NL-collection zones**
open from your selection/click *patterns*; every gesture — a node moved, a
color changed, a line drawn — is **collected as interaction data**, so you talk
to your AI about what you're doing and **steer it by gesture**.

**The open heart (still bdo's to turn):** the **gesture → AI → response
loop** — does a gesture (a) interpret-and-propose (you draw, the AI guesses
intent and shows a change you accept/reject), (b) become context for a
conversation, or (c) act directly (the gesture *is* the command)? That loop is
the difference between a pretty canvas and the thing described; it is named
here as the next decision, not guessed.

Lands in: _(the frame only — no build yet. The bake-off's vocabulary + plating
are the harvested ingredients; the next slice re-aims at the
narrative-from-a-directory experience once the gesture→AI loop is chosen.)_

---

## 0011 — The construction flag (game-dev missing-texture rule) + the Complexity slider on one three-word phrase 🟢
**2026-06-17 · bdo · done-line 0106** — built on `claude/canvas-home-reshape`, screenshot-verified

bdo, at the Story demo: *"I need a rule used in game dev. Anything that is mock or
not done, get a special flag so I can see the state of construction. I want to
bring in the slider now, and start with just one phrase, three words. The Cat Naps."*

Three moves, landed together:

1. **The game-dev rule = the missing-texture convention.** The oldest convention
   in the trade: an unfinished or placeholder asset renders in a deliberately
   glaring magenta (the Source-engine purple/black checker) so it can never be
   mistaken for finished or silently ship. It is **ontum's mock-shame made visual
   on the canvas** — a mock that moves fake work cannot hide behind a clean
   surface. Now a first-class, schema-driven token: `BUILD` in `canvas-system.js`
   (`real` / `mock` / `wip` / `todo`); `real` renders in its own color, every
   flagged state wears the magenta hazard + a tag. §10 teeth in
   `canvas-system.test.js`: a fabricated build state is refused; every flagged
   state must carry a color + a tag (it cannot be mistaken for finished).

2. **The Complexity slider, live, on one three-word phrase.** The demo reduces to
   the single cat seed (no phrase-picker) and opens at the three words **"The cat
   naps"** — one glyph. The **Complexity** slider grows the sentence *and* the
   mesh together (3 words → `+ sunbeam, warmth` → the full
   cat·sunbeam·shadow·warmth mesh): glyphs carry a `stage`, the slider filters by
   level, the sentence comes from `stages.texts`. This is the first of bdo's five
   reference sliders (0005) made real — and the perturbation axis the
   story-benchmark wants (matched pairs by complexity).

3. **The flag, applied honestly.** The four not-yet-built sliders (Length, Twists,
   Weirdness, Colors) wear the magenta hatch + a `MOCK` tag — so the construction
   state of the *slider feature itself* is legible. And every relation edge renders
   magenta with a `MOCK` tag, because relations are still **hand-authored, not yet
   composition-generated** (iterations 0008): the glyphs read as built (their own
   colors), the wiring reads as mock. A legend names the rule on the surface.

Engineering: the staging/build fields are **additive** on the cat phrase in
`phrases.json` — the benchmark mesh (glyphs/facets/relations) is untouched, so the
recovery-scorer corpus still round-trips. `?c=<n>` deep-links a level (verification
+ sharing). All causality node tests green (canvas-system 16, phrases 11, scorer 11).

Lands in: `causality/canvas-system.js` (+ test), `causality/phrases.json` (cat
phrase, additive), `causality/story.html`. To reach the live URL it must land to
`main` (only `main` deploys via `pages.yml`); branch work is screenshot-verified.

---

## 0010 — The canvas is a chunked coordinate volume (API-first spatial substrate) 🟡
**2026-06-17 · bdo**

bdo: *"the nodes, canvas position and such should be API first, chunked,
coordinate based — think like Minecraft. A 100×100×100 volume of subcubes, each
with an xyz grid projected to the surface… almost like a game-engine screen but
capable of being subdivided (might also be 10×10×10). The seams could be left to
editor/dev mode."*

**Why:** the "connections are subpar" problem is a *substrate* problem — free
`x,y` floats give edges nothing to route through. A discrete, chunked coordinate
space makes routing a **solved grid problem** (lanes through free cells, no
crossings), makes nodes more interesting (volume, cells, subdivision), and gives a
better canvas.

**The model:**
- A coordinate **volume** — `N×N×N` subcubes (start `10³`, can grow to `100³`),
  each carrying an xyz grid, **recursively subdividable** (chunk → subcubes, like
  Minecraft chunks).
- **Nodes have an address, not a float** — a coordinate (+ chunk path). This is
  ontum's *fundamental stratum = address* made literal; positions become
  serializable, API-first (the spatial contract lives in `canvas-system.js`, the
  renderer only *projects* it).
- **Edges route through free cells** — orthogonal/lane pathfinding between occupied
  cubes → deterministic, crossing-free, controllable routing.
- **Chunks = holons / membranes** — a phrase is a chunk; its glyphs are subcubes;
  a glyph's facets are sub-subcubes. The recursion (0004) gets a spatial home.
- **Seams in dev mode** — grid/chunk lines show in editor/dev view; the normal
  reading view is clean (the "seams to dev mode" rule).

This **supersedes the float-overlap polish** (0007's "remaining") — don't hack
overlap avoidance on floats; build the substrate and routing falls out.

**Open fork (bdo to pick):** the default *projection*. (a) clean **2D top-down
grid** for the reading view + a **3D/iso dev view** that shows the volume + seams
(recommended — matches "seams to dev mode", keeps nodes legible); or (b) full
**isometric Minecraft view** as the default. Start size: `10³` (subdivide as
needed). API-first regardless.

Lands in: _(next — the coordinate/chunk contract in `canvas-system.js`, an
address→surface projection, grid-cell edge routing; then re-home the Story-demo
on it.)_

---

## 0009 — The hero comes alive: the four idle ANIM tokens wired, motion folded from the mesh 🟡
**2026-06-17 · bdo (animations & polish pass)** — built on `claude/canvas-home-reshape`, screenshot-verified, eyeball-pending

bdo: *"let's work on animations and polish for this canvas."* The design system
(`canvas-system.js`) **declared** six motions but the Story-demo renderer only ever
used `wobble` + `membrane-breath` — four were **declared-but-idle**. This pass wires
all four and grounds motion in the phrase's own structure (three layers, hero first):

1. **Idle ANIM tokens, now real** (in `story.html`):
   - `water-fill` → glyph holons are **water-level discs** (the look-and-feel
     signature), the level **folded from the glyph's degree in the mesh** (central
     glyphs sit fuller) — folded, not painted.
   - `pulse-travel` → an amber pulse **travels each relation edge** (the beat of an
     act); strain-rust on feedback edges.
   - `ring` → an **activation ripple** fires when a glyph opens.
   - `entrance-fade` → glyphs **scale+fade in**, staggered, on phrase switch.
2. **Interaction feel & easing** — hover→open **eases the facets growing out** of the
   glyph (not popping); facet-level edges re-anchor to the animated facet positions;
   the Lens panel slides in.
3. **Anima-driven (folded)** — since the served floor has no live log, `energy`
   (ink-wobble amplitude) and `tempo` (pulse speed) are **folded per-phrase from the
   mesh** (edge density, loop count). A denser phrase visibly runs more alive — the
   felt field emerges from structure, paint-free (honors the anima "fold not paint").

Engineering note: the clock is now **real-time-driven** and entrance/water are
**closed-form in `t`** (frame-rate independent; also what made deterministic
headless-screenshot verification possible). No new tokens invented — every motion
is an existing `canvas-system.js` ANIM entry finally rendered.

Lands in: `causality/story.html` (the served `index.html`). Carrying the same
primitives into the editable `canvas.html` is the next slice. **To reach the live
URL it must land to `main`** (only `main` deploys via `pages.yml`); branch work is
screenshot-verified meanwhile.

---

## 0008 — Relations are typed by composition too: generative ends, perspective-flip is a type 🟡
**2026-06-17 · bdo**

bdo, on the cat demo: *"`warmth.state blocks shadow.signal` / `shadow.signal blocks
warmth.state` — this isn't true… the perspective flip on the relationship is a
type, so the ends are generative too."*

A relation is **not a hand-picked label**. Three consequences:

1. **The ends are generative.** A relation's *type* is **generated by the
   composition of its endpoint facets** — exactly as a glyph's type is generated
   by its facets (0004), now extended from **nodes to edges**. `signal` on `state`
   generates a *modulation* (trigger if `+`, block if `−`); `state` on `objective`
   generates *satisfies*; `source` on `state` generates *feeds*. You never pick
   "blocks" — it falls out of `(signal, state, −)`.
2. **Perspective is typed.** "A blocks B" ≠ "B blocks A". The direction carries the
   claim; the relation owns its perspective. (This is how the hand-authored cat
   "blocks" got reversed — authoring direction by hand is the bug.)
3. **The flip is a type.** `invert` is not a reversed arrow — it is a **generative
   transform** producing the typed *dual* (`blocks` ⟷ `is-blocked-by`/`yields-to`),
   with `flip(flip(r)) == r`. The Lens's `invert` becomes a real operation.

**Build:** a relation-composition table in the design system —
`(fromFacet × toFacet × valence) → { type, label, inverse }`. Phrases declare
`(fromGlyph.facet, toGlyph.facet, valence)`; **label + perspective are derived**,
never authored. §10 teeth: a relation's label must be *generated* (a fabricated
hand-label is refused), and `flip(flip(r)) == r`. Regenerate the portfolio's
relations through it (fixes the cat-chain: `(shadow.signal, warmth.state, −) →
blocks`, `(warmth.state, cat.objective, +) → satisfies`, `(warmth.state, cat.actor,
fades) → wakes`).

Lands in: _(next increment — `RELATION` table in canvas-system.js + the generator;
portfolio relations refactored to `(facet, facet, valence)`.)_

---

## 0007 — Progressive discovery: smooth surface, detailed graph 🟢
**2026-06-17 · bdo** — live on the branch preview

*"The nodes under cat only show after selection/interaction, so the surface is
very smooth and simple but the true graph is detailed."* Default view is now
**glyph-level only** — glyphs + the sentence skin + glyph-level rim-anchored edges
+ the membrane. A glyph's **facets and facet-level edges unfold only on
hover/select** (the holon zoom = the CCR reversibility of 0004). This killed the
all-at-once clutter and is the "connections subpar" fix's first half (rim
anchoring + labels drawn on paper for legibility). Remaining: edges still need
overlap avoidance and the relation-composition of 0008.

---

## 0006 — Each node goes through the gateway (governed composition) 🟡
**2026-06-17 · bdo**

bdo: *"Each node should technically go through the gateway."* Confirmed — and it
unifies the canvas with `epic.inference-gateway` and the inference-as-composition
layer.

A node's **composition is an inference act** — the composition router deciding
"this word → `{actor, objective}`" *is* inference filtered through logic + register
+ learned patterns. So it must not be a free, ungoverned LLM call; it routes
through **the gateway**: policy-gated, affirmed, fallback-on-failure, **receipted**
(every node's typing attributable to a record), on local minds at zero disclosure
— the same governance the rest of the loop carries.

This reconciles with the deterministic-compiler call (0003) as exactly the
**inference-as-composition** pattern:
- **The deterministic compiler is the bounded FLOOR** — always works, offline,
  on the static served site (the settled-safe baseline).
- **The gateway is the ENRICHMENT** — when the local inference plane is up, a node
  routes through it for richer/looser composition, governed and receipted.
- **The gateway's fallback IS the deterministic compiler.** So a node always
  resolves: gateway when present (enriched), floor when not. Bounded floor +
  governed inference = no settling-drift, no hallucination-drift.

So: every glyph's typing is a **governed, receipted composition with a
deterministic floor under it.** The render layer is agnostic to which produced the
composition (it reads the same node spec either way).

Lands in: _(the composition router is built floor-first; the gateway seam is the
enrichment layer behind the same node spec — built/wired when the local plane is
the host, never required for the static served floor.)_

---

## 0005 — The design target + overnight mandate: frame the canvas design system 🟡
**2026-06-17 · bdo** (with reference mockups)

bdo supplied polished reference mockups that lock the visual + interaction
language, and set an **overnight-loop mandate**: *build a portfolio of phrases and
loop until the canvas design system is framed* — supporting **ASCII, colors,
shapes, connections, line-types, animations, easing, nodes, physics, hover &
click interaction, gestures, and more.**

**The reference (the "Story demo" hero + four Lens states):**
- **Hero / Story physics:** the phrase sentence as skin (key words highlighted in
  glyph colors) over a dashed **phrase membrane**. Inside: glyph holons drawn with
  *figurative icons* (cat face, sun, cloud) over the water-fill, each composing
  **facet sub-nodes with their own icons** (actor=person, objective=heart "warmth",
  source=waves "warmth", time=clock "drift", signal=bell). Relations are **labelled
  hand-ink edges** (`wants`, `moves`, `satisfies`) with a dashed **`interrupts`**
  feedback loop spanning the membrane. A slider strip — **Complexity · Length ·
  Twists · Weirdness · Colors** (swatches) — and complexity reveals an extra glyph
  (`moves`).
- **Glyph selected:** a right **Lens** panel — the glyph, its facet chips, and
  *Connected through* (`sunbeam.source → cat.objective`, `shadow.signal →
  cat.actor`). Selection shows a sparkle.
- **Relation selected:** Lens shows the facet edge + actions **explain · invert ·
  stitch**.
- **Membrane selected:** Lens shows **counts** (glyphs · loops · facet-edges) and
  an **"Ask this membrane…"** inference box (e.g. "what interrupts the cat?").
- **Chrome:** top bar `Causality · Story demo · + New · Save · ⋯`; bottom
  toolbar **Select · Pan · Lasso · Voice**; **zoom** (100 % − +) bottom-left;
  **minimap** bottom-right.

**Caveat (bdo):** the cat/shadow/warmth example is *logically wrong on purpose* —
the real chain is `warmth → holds cat`, `shadow → blocks warmth (−)`, `loss of
warmth → signals cat` (not `shadow.signal → cat` directly). It is an **idea
collection**, not a correct model; the design system must NOT hardcode this chain
— the portfolio should aim for correct mechanics, the demo proves the *capabilities*.

**Deliverables of the overnight loop:**
1. A **portfolio of phrases** (many cute-but-mechanically-rich seeds, each with its
   glyph set, facet compositions, relations, membrane, and cross-membrane links).
2. A **framed canvas design system** — the token + primitive system behind the
   reference, covering every capability above (ASCII fallback included), so a node
   type / line type / interaction / animation ships as a *spec entry*, not new code
   (the schema-driven discipline of `canvas.js`), in the established look-and-feel.

Lands in: _(overnight loop on `epic.causality-surface`; slices pushed to the live
URL as `claude/*` previews; this entry + 0001–0004 are the brief.)_

---

## 0004 — Type by composition + compress-to-enrich (the governing principle) 🟡
**2026-06-17 · bdo**

Two locked decisions that govern the story demo's engine:

**Type by composition.** A glyph is not one primitive type — it is a **bundle of
typed facets**, and that bundle *is* a small system. `cat` = `actor` +
`objective`(warmth); `sunbeam` = `source`(warmth) + `time`(its drift is a clock);
`shadow` = `signal` + `time`. Zoomed in, a glyph is a network of facets; zoomed
out, one node in the phrase-membrane. Relations connect **facets across glyphs**
(sunbeam's `source` → cat's `objective`; shadow's `signal` → cat's `actor`), which
is where the mechanical richness lives. (Proven: `concept-compose` shot.)

**Compress to enrich, not to fit (vs. headroom).** Ref:
`github.com/chopratejas/headroom` — content-aware context compression for "60–95%
fewer tokens, same answers," reversible (CCR: cache the original, expand on
demand), routed by a `ContentRouter` (code→AST, json→structure, text→trained
model). It compresses **to fit a budget**. We invert the *objective*, keep the
*mechanism*:

> The glyph is the compression (intelligence densified into a holon, reversible
> the same way CCR is — zoom it open to its facets). But the budget we win is
> **reinvested into relationships** — facet-to-facet edges, membranes, the
> network. The dividend from compressing meaning buys the *edges*. The context
> gets **richer, not smaller**. We don't compress to save; we compress to enrich.

Borrowed concretely: headroom's `ContentRouter` ≈ the missing **composition
router** — the "filter through logic + register + learned patterns (Pattern
Commons)" that maps a word to its facet-bundle (a creature → `{actor, objective}`;
a moving light → `{source, time}`). Their router picks a compressor; ours picks a
composition. CCR reversibility ≈ glyph zoom-open.

Lands in: _(governs 0003's build — the composition router + the facet vocabulary.)_

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

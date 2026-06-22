# The platform portal — the blueprint bundle (PROPOSED)

> Status: **PROPOSED** — bdo's direction, 2026-06-21 (this design conversation),
> his to steer; a session's only to propose (D-4). This is the *bundle*, not an
> increment: full shape → categorized, labelled concept-list → a fixed generative
> concept-list → calls-to-action against a purpose. **No code is implied as
> done.** It is the structure we would agree *before* building, per the
> *blueprint-before-build* hard rule (CLAUDE.md; #348, CTA-3). Every mechanism
> below is mapped to a primitive that already exists, an existing proposal, or
> named as a hole — it **composes**, it does not re-derive (§10).

## The why (the friction it names)

bdo wants a **platform portal** in ontum. The portal is not a feature list to
pick from — its **primary job is *derived* from the grammar composition of the
configured model we discover, consequently** (bdo, this conversation). That is
the derived-primaries frame ([memory `ontum-derived-primaries-rgb`](../../README.md)):
there is no universal set of primaries — RGB is right for screens, CMYK for print;
primaries *fall out of* the medium and its constraints, never picked. So the
portal's function falls out of the perspective a user registers, not out of a
designer's box of containers.

The first walk through the portal, in bdo's words (this conversation):

1. **Register / sign up** — a profile **generated** from working with an inferred
   process in NL, steered by **deterministic gestures**. *"Basically it's a
   registration of a **blanket over a perspective**."*
2. **See the corpus.**
3. **Author volumes** to fill with **slots of grammar and structure**, each
   **pointed at a registered bound of data**.

> **One interpretation flagged for your correction (the riskiest read, per the
> Taster's Clause / D-14).** I read *"a blanket over a perspective"* as a
> **boundary in the Markov-blanket sense** — the interface that separates what is
> *inside* a view (its own states, its grammar) from the world it draws on (the
> registered bound of data). Registration registers that boundary; the profile
> *is* the registered blanket. If you meant *blanket* more plainly (a covering /
> a template / a claim laid over a domain), the bundle's spine still holds — only
> the P1 framing below changes. This is the one place I am interpreting rather
> than quoting; everything else is yours verbatim.

The purpose every CTA below serves:

> **ontum becomes a platform anyone can enter: a user registers a blanket over
> their perspective, sees the accrued corpus, and authors volumes of grammar
> pointed at their own bound of data — the portal's function *derived from that
> grammar*, never pre-decided. The owner is a *parameter*, not hardwired to bdo;
> ontum is instance #1, pointed at itself.**

## The full shape — register a blanket, derive a grammar, author into it

```
  register ─► [P1 blanket over a perspective] ─► [P2 generated profile]
                        │  inferred NL × deterministic gestures
                        ▼
              [P3 configured model] ──derives──► grammar (its own primaries / RGB)
                        │
                        ▼
              the portal's JOB  (a consequence of the grammar, not a box)
                        │
            ┌───────────┴────────────┐
            ▼                         ▼
     [P4 see the CORPUS]      [P5 author VOLUMES]
     the accrued vocabulary   └─ slots of grammar + structure
     (already accounted)         └─ [P6 pointed at a registered BOUND of data]
            └────────────┬────────────┘
                         ▼
              [P7 the served portal — the one door; owner = parameter]
```

## The categories (label · description · today · the gap)

**P1 — The registration seam (the blanket over a perspective).** *How a user
enters: registering a bounded perspective, not filling a form.*
- Today: the **herald** registers open-set agents (`herald introduce` → a
  content-hash credential at the trust floor — `loop/herald.py`); the **trust
  ladder** (`loop/trust.py`) gates what a class may do; the **session-gateway**
  proposal names the three A's (authenticated · authorized · attributed) as the
  birth ritual. The **gallery** built a worked sibling — a genesis owner
  registration on an OPEN registry (`gallery/lib/`, the typed-graph relay).
- Gap: none of these registers a **blanket over a perspective** — a *bounded
  vantage* with its own scope, the thing the rest of the portal derives from.
  Registration today mints an identity, not a perspective + its bound.

**P2 — The profile generation (inferred process + deterministic gestures).**
*How the profile is **generated** by a conversation, not typed into fields.*
- Today: the **/ask** and **/recommend** surfaces are the typed gesture rail
  (AskUserQuestion as a faithful projection, not a menu — `.claude/skills/ask`);
  **gesture-as-a-typed-consequence-scaled-act** is proposed (`gesture.proposal`
  / PR #387). **Inference-as-composition** (memory) is the principle: bounded
  config generated just-in-time from a description.
- Gap: nothing wires *inferred NL + deterministic gestures → a generated
  profile*. The gesture primitives exist; the onboarding *journey* that composes
  them into a registered profile does not.

**P3 — The configured model & its derived grammar (the RGB primaries).** *The
heart: the perspective's grammar is **derived** (its own primaries), and the
portal's job is a consequence of it.*
- Today: the **accounting-attributing organ** is the named home — accounting
  (`causality/corpus_terms.py`, built: the literal terms fold) ⇄ attributing
  (decompose each unit onto *derived* primaries as coordinates + onto
  cause/consequence/owner). `accounting-attributing-organ.proposal.md` carries
  it; the first installable increment is the attributing step on `corpus_terms`.
- Gap: the **derive-not-pick** organ is proposed but not built past accounting,
  and it is not yet *pointed at a registered perspective* (P1) to produce *that
  perspective's* grammar. Derive-not-pick is **what makes the portal general**
  (owner = parameter).

**P4 — The corpus surface (see the accrued vocabulary).** *How a registered user
**sees the corpus** their volumes will be authored from.*
- Today: `causality/corpus_terms.py` already accounts the whole corpus (4806
  files, ~30 spine terms = the empirical type system, the id-citation network =
  the genuine latent graph — memory `ontum-corpus-terms-accounting`). The
  **canvas** (`causality/canvas.html`) is the witness lens for a typed graph.
- Gap: there is **no served view** that shows a user the corpus *through their
  registered blanket* — scoped to their perspective and bound. The fold exists;
  the surfaced, perspective-scoped read does not.

**P5 — The volume authoring (volumes filled with slots of grammar/structure).**
*How a user **authors volumes** — containers of typed grammar/structure slots.*
- Today: the closest worked primitive is the **attributed workflow** (gallery
  `workflow.py`: id·name·description·phases·requirements·**attributes**, with a
  deterministic `lint` that studies inherent requirements and an `arm` gate that
  refuses an unlinted one — *study-before-run*). ontum's own **author-workflow /
  review-workflow** skills are the Claude-Code-surface analogue. **"Interface as
  AI"** (`causality/display-system.md`) is the authoring front door: describe it,
  AI composes a *schema-valid* shape, validated before it renders. The **glyphs**
  layer is the generative-language organ (the closed loop with P3).
- Gap: no **volume** primitive — a container whose **slots** are typed grammar +
  structure blanks, authored conversationally, validated against the *derived*
  grammar (P3) before it stands. The workflow is a near-sibling, not the thing.

**P6 — The registered bound of data (what a volume/slot points at).** *How a
volume/slot is **scoped to a registered dataset boundary**.*
- Today: **registered surfaces** (`loop/reflect.py register --surface`) are the
  one existing "register a bound" primitive; the **corpus** itself is a de-facto
  bound. The **blanket** of P1 is the natural home of a bound (the boundary *is*
  the data scope).
- Gap: there is no first-class **registered bound of data** a slot can point at —
  a named, scoped dataset the grammar draws on. P1's blanket and P6's bound are
  likely **the same primitive seen twice** (the boundary and what it encloses);
  the bundle should decide whether to unify them.

**P7 — The served portal itself (the one door).** *The surface all of the above
is reached through — and the owner is a **parameter**.*
- Today: `loop/web.py` is the only **served** surface (`python -m loop.web serve`
  — the owner inbox with real verdict forms, one write path). `loop/surface.py`
  is the **active-surface control plane** (a live fold over digest+gaps+setpoint,
  not a prerender). The **gallery `site.py`** is the worked sibling: API-first
  (a *guiding* orientation surface for AI-native sessions; HTML projection for
  humans), content-negotiated, one gateway door, writes loop back through it.
- Gap: ontum has no **single served door** that composes P1–P6 into one portal,
  and `loop/web.py` is hardwired to bdo-the-owner — P7 must make **owner a
  parameter** (the portable-stamp / three-A's generalization, from "any surface"
  to "any instance").

## The fixed generative concept-list (what to ponder)

1. Is the **blanket over a perspective** one new first-class record (registered,
   bounded, attributed), and is the **profile** its rendered face? (P1 + P2)
2. Are **P1's blanket** and **P6's bound of data** the *same primitive* — the
   boundary and what it encloses — or two? (P1 + P6)
3. Does the **derived-grammar organ** (P3) get pointed at a registered
   perspective to produce *that perspective's* primaries — and is that the build
   that turns the accounting fold into the portal's engine? (P3 + P4)
4. What is a **volume**, exactly — a schema-driven container (like the attributed
   workflow) whose **slots** validate against the derived grammar before standing?
   (P5)
5. Is authoring a volume **conversational** (Interface-as-AI: describe → AI
   composes → validate → render) end-to-end, never bespoke fields? (P2 + P5)
6. Does the portal (P7) make **owner a parameter** from day one (so instance #1 =
   bdo is *a* case, not *the* case)? (P7)
7. Is the corpus view (P4) **scoped through the registered blanket** — you see the
   corpus *as your perspective frames it*, not the whole undifferentiated heap?
   (P1 + P4)

## Calls to action (against the purpose)

| # | CTA | Kind | Serves |
|---|-----|------|--------|
| CTA-1 | Decide the **blanket-over-a-perspective** primitive: one registered, bounded, attributed record; whether it unifies with P6's bound of data; what the *generated profile* is as its face. | bdo decides → build | P1, P2, P6 |
| CTA-2 | Build the **attributing step** on `corpus_terms` (derive a perspective's primaries by inference, express real terms as mixes/coordinates, record coords+cause+owner) — the engine that makes the portal's job derivable. | build (composes accounting-attributing organ) | P3 |
| CTA-3 | Define the **volume** primitive — a schema-driven container whose **slots** are typed grammar/structure blanks, validated against the derived grammar before standing (the attributed-workflow grain, generalized). | bdo decides → build | P5 |
| CTA-4 | Define the **registered bound of data** a slot points at (likely the same record as CTA-1's blanket) — named, scoped, attributed. | bdo decides → build | P6 |
| CTA-5 | Build the **served portal door** (P7) composing `loop/web.py` + `loop/surface.py`, **owner as a parameter**, one gateway write path — the corpus view (P4) and the registration journey (P1/P2) as its first two rooms. | build | P4, P7 |
| CTA-6 | The **first vertical slice** when you say build: registration journey (P1/P2 → a generated profile/blanket) → corpus view scoped through it (P4) → author one volume of slots pointed at the bound (P5/P6). One walk, end to end, thin. | build | the instance |
| CTA-7 | Stamp **owner = parameter** as the portal's law (the portable-stamp generalization), so the platform is general from birth, not retrofitted. | bdo's stamp | P7 |

## Whose move

- **bdo decides** (the shape, not a session's to set): CTA-1, CTA-3, CTA-4,
  CTA-7, and whether this graduates into `epic.platform-portal`.
- **Session-buildable** once a decision points the way: CTA-2, CTA-5, CTA-6.

## The first buildable slice (when bdo says build)

Per *one real node at a time* and *witness before actuator*: the smallest real,
non-double-building increment is **CTA-2 — the attributing step on
`corpus_terms`**. It is the engine the whole portal's "job is derived"
(P3) rests on, it composes an organ that is already proposed and half-built
(accounting runs; attributing is the named next increment), and it is read-only
/ propose-grain (the cut stays bdo's, D-4). With derive-not-pick real, the portal
has something to *derive a job from*; without it, P7 is a shell. The served door
(CTA-5) and the volume primitive (CTA-3) ride later increments, gated on CTA-1's
shape decision.

## Composition note (no second truth, no double-build — §10)

- This document **cites** the organs and proposals it composes; it copies or
  supersedes none. It adds one thing none held: the **portal as a single shape**,
  and the **registration-of-a-blanket-over-a-perspective** spine bdo named.
- **The gallery is the worked sibling, not the build.** The gallery
  (`C:\Users\bdf19\gallery`, a different repo) already built this fractal —
  registration on an open registry, the attributed workflow, the typed graph, the
  API-first served door (`graph.py`/`workflow.py`/`site.py`/`triage.py`). It is
  *"one fractal scale of ontum itself"* (memory `gallery-website-typed-graph-relay`).
  ontum's portal is **ontum pointed at itself** — built over **ontum's own
  organs** in **ontum's own tree** (bdo: only this directory). The gallery is a
  pattern to learn from, never material to copy in.
- **The closed loop holds:** the accounting-attributing / derived-primaries organ
  (P3) ⇄ the generative-language layer (`glyphs/`); the portal feeds the graph and
  the inference re-enters as proposed typed nodes (the ratchet). The log stays
  truth; the portal is a faithful surface over it, one gateway write path.
- When bdo names it, it graduates to `epic.platform-portal` and this proposal
  stays as the record of where that arc was born (the proposals-dir contract).

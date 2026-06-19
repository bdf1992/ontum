# The structured-communication channel — proposal

*Status: PROPOSED. Author: a session, 2026-06-19, with bdo, from the `/recommend`
thread. The build is incremental; this document is the worked-through design, not
a mandate to build it all. Naming and mint are bdo's (D-4).*

## What this is

A typed, two-way, user↔agent **communication channel** built from the basic
`AskUserQuestion` primitives (radio / checkbox / title / tabs) used as a
*structured-input instrument*. The owner's framing, across the thread:

- A **selection is evidence-of-intent, not a command** — inference reads what it
  *means* in context (this is AIM, `causality/auditable-intent-mesh.md`).
- The primitives express many shapes: **scales, pickers** (color/tone/format/
  gesture/action), **routers**, **multi-tab forms**, **chained wizards** —
  collected as structured **data**.
- An option **picked → deterministic code** auto-runs; **"Other"/NL → inference**
  interprets. "Other"-breakouts are the highest-signal learning (the next rail).
- It carries **typed speech-acts both ways** and can **survey/configure** a
  moment before diving in, or **connect to deterministic code** to auto-run.
- bdo's governing rule: **"it's also a tool for those shapes, not if the
  situation doesn't fit."**

`/recommend` (`.claude/skills/recommend/`) is the **first instance** — one
speech-act (request-for-decision). This proposal is the frame it serves.

## The design pass (three lenses)

This was worked through by three independent analyses (risks, architecture,
conformance). Their convergent conclusions are the constraints below.

### The corrected thesis (the unification claim was overstated)

The claim "ontum already has this channel five-plus times" is **mercury** — only
two organs are genuine two-way channels. The honest map:

| Organ | What it really is |
|---|---|
| `web.py` inbox | **genuine two-way** (verdict POST → same `judge()`; "no second write path") |
| `ask` / `recommend` | **genuine two-way, synchronous** (the proposed primitive) |
| `reflect.py` → GitHub | **one-way outbound engine** (mirror, never back — D-4) |
| `digest.py`, `brief.py` | **one-way producers** (no return leg) |
| summon hook | **agent-*inbound*** (loop→agent, wrong counterparty) |

The defensible claim: *the message grammar recurs; one surface-agnostic outbound
engine (`reflect`) and one synchronous two-way surface (`ask`) already exist; the
abstraction names the grammar so the next organ stops re-deriving it.* The
`brief ↔ ask` pair is the one proven "one shape, two render targets" (the ask
skill already declares this at `SKILL.md`).

### The constraints (the priors the build must honor)

1. **Situational (RC6).** The instrument scales at the exact angle the
   ask-discipline fights (the "form-filling prison" — the top risk). It is
   subordinate to R4: reach for it only when the moment fits its shapes;
   otherwise prose / `/ask` / just act. *This is the answer to the top risk.*
2. **Auto-run is read-class only (RC7).** A pick fires deterministic code only
   for a read; a change/authority act becomes a proposal → gate. A pick that
   writes is self-signing (AIM: gesture ≠ command; D-4; no-self-sign). Enforced
   in `compose.py autorun_refusals()`.
3. **"Other"/NL proposes, never commits.** The NL escape is `ambiguous` by
   construction — inference reads it, a pen commits. It is the anti-prison
   safeguard *and* the learning signal, but never a write path.
4. **No second write path (§10).** Every user→agent act routes through an
   **existing pen** (`node.judge`, confirm-arc, the git/PR pens, `inference
   set_policy`). The grammar types over pens; it is not a new writer.
5. **Two irreducible render classes.** `AskUserQuestion` is a **session tool** —
   only the live session can render a panel (RC4). So there is no single
   "surface-agnostic render": there is **session-sync** (ask/recommend, two-way
   in one turn) and **headless-async** (reflect/web, one-way + pen-return). One
   grammar, two render mechanisms.
6. **Grammar stays PROPOSED until ≥2 real renders.** Derive the abstraction from
   instances; never author the surface-agnostic layer top-down (§12 tripwire;
   the 5-confirmed-arcs-0-landings sprawl this method exists to prevent).
7. **The owner's surfaces are protected.** Default-deny on the phone; only
   `escalate`-class acts may render there (the "bdo steers arcs, not tickets"
   hard rule). Everything else folds into the digest.

## Architecture & topology

The channel sits **above the gateway and pen, below the per-surface render**; it
holds no authority of its own (an AIM node — a witness and a handle, never a
writer). Bottom-up:

```
Record   (log)          append-only truth — events / receipts / admissions
Gateway  (PDP)          authority: inference.authorize + fence/policy + the SHAPE pdp
Pen      (commit)       the only writers; no second write path
CHANNEL  (this)         typed speech-acts; composes / bounds / classifies / routes
Render   (per-surface)  session-sync (modal) | headless-async (web, issue, digest)
```

**Two gate points, never more:** (a) a **SHAPE** gate on agent→user asks — is the
ask well-formed (`ask_guard.shape_problems`, fail-open, contextual); (b) an
**AUTHORITY** gate on the answer — may this answer write (`inference.authorize` /
fence / confirm-arc, bright-line fail-closed at the pen).

**The pipeline** (AIM's, made concrete):
`gesture → IntentPacket (evidence, verbatim) → classify (read→deterministic |
change/Other→inference→proposal) → AUTHORITY gate → admitted pen → receipt →
projection refresh.`

**The speech-act grammar** (PROPOSED; names what is scattered):
- agent→user: `report`, `recommend`, `ask`, `propose`, `escalate`
- user→agent: `configure`, `message`, `request`, `summon`, `gesture`
Each binds `{schema, route, existing-pen}` and a preferred render class. Mapping
to live code: `recommend` skill = `recommend`; `/ask` = `ask`; `brief.py` =
`report`+`recommend` async; `inference policy` = `configure`; `gesture_surface`
reads `gesture`; `summon.py` = `summon`.

**Data model — no second source of truth.** The shape-sensor stays on the
gitignored `tool-use.jsonl` ("a sensor, not truth"); a tap that *writes* is
recorded by the pen it routes to, in the existing kind (admission / receipt /
event); a durable `exchange` event is **deferred** (OD1) until a second surface
needs to re-read past exchanges.

## Conformance — how the channel earns itself (not a sixth surface)

The first slices **absorb** existing duplication rather than add a parallel
surface:

- **Absorb `brief ↔ ask` into one construct.** `brief.py`'s
  considered-context → recommendation → divergence (with the `uncited` refusal)
  *is* the construct; `/ask` re-states it in prose. Make the synchronous surface
  import `recommendation_for` / `considered_context` rather than re-derive it —
  the one place the §10 risk is concrete and the thesis is already declared.
- **Outbound async speech-acts become `reflect` `RULE_KINDS`**, riding the
  existing beat — not a parallel enum or surface registry.
- **`compose.refusal_check` + `ask_guard.shape_problems`** stay the one shared
  bound (I-4).

## Built now (this increment)

- `compose.py autorun_refusals()` — the **RC7 bound** in code, with `--selftest`
  teeth (read auto-runs; a change-class auto-run is refused; reuses the tags.py
  verb→intent classifier, I-4).
- `recommend/policy.md` — **RC6** (situational use, the answer to the top risk)
  and **RC7** (the auto-run constraint), each with its own refusal teeth.
- `recommend/SKILL.md` — "reach for it only when the situation fits," the RC7
  bound, and the channel framing (PROPOSED), pointing here.
- this proposal.

## Deferred — named next slices (each its own done-line)

1. The **SessionStart `configure` tap-form** — the first *new* speech-act
   instance: a read-only composer (panel_spec + routing_table) reusing the bound,
   configuring only the session's **own bounded binding** (never a global dial —
   that would self-sign), with "Other"→inference. (The architecture's smallest
   viable slice; deferred so the grammar earns itself from a second instance.)
2. **Absorb `brief ↔ ask`** into the shared `recommend`/`report` construct.
3. **Wire `ask_guard`** as the channel's SHAPE PEP (built but unwired — the
   gateway-spine's named first migration). Until then the floor is willpower.
4. The **audit fold** (shared with `/ask`, done-line 0119's named next): reads
   the exchange trace for genuine-fit vs offloaded use and for "Other"-breakouts
   (the next rail). The conformance surface over these expectations.

## Open design decisions (bdo / follow-up)

- **OD1** A durable `exchange` event on `events.jsonl` (replayability) vs the
  gitignored sensor only? *Recommend defer.*
- **OD2** Wire `ask_guard` now (lowest-blast-radius PEP — gates the agent, never
  bdo) or wait for the spine?
- **OD3** The gesture→`intent_class` compile table (AIM OH1) — the *shape* is
  fixed; the *entries* are bdo's to seed.
- **OD4** A gesture-pen for `propose-change`/`mutate-source` taps (AIM OH2), or
  escalate-by-default (conservative, correct)?
- **OD5** Which render classes beyond the modal are in scope?
- **OD6** Does a `request` speech-act compile into a policy-governed work-queue
  (the spine's 5th branch), against `gaps.py` + `trust.py` (don't double-build)?
- **OD7** Confirm the "Other"-breakout → next-rail self-improvement loop and home
  the audit fold accordingly.
- **OD8** Name and mint: "AIM's Request register made real," or its own organ?

## A ghost to fix (found in the pass)

`ask_guard.py` and the ask skill cite `.claude/skills/ask/exemplars.md`, which
**does not exist** — a cited backing that doesn't resolve. Either create it or
drop the citation (out of scope here; named so it isn't lost).

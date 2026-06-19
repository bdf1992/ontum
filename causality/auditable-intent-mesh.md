# Auditable Intent Mesh (AIM) — the pattern

> The formal pattern under the Causality surface. **Not** "a graph UI," **not**
> "RepoPrompt redrawn spatially," **not** "execution bolted onto a canvas." The
> pattern named, pressure-tested, and specified: primitives, contracts, lifecycle,
> invariants, and acceptance tests. Analogy is used once for orientation, then
> replaced by primitives.
>
> **Status: PROPOSED** (grip discipline). The name and the mint are bdo's (D-4).
> Working name **AIM — Auditable Intent Mesh**; the Causality-native variant is
> **WIM — Witnessed Intent Mesh**. Recommendation: keep **AIM** — *audit* and
> *execution* are the load-bearing, currently-missing requirements; *witness* names
> only the half the display system already has. Authored 2026-06-18 from bdo's
> formalization brief; destined for the Pattern Commons (`causality/patterns/`,
> PR #174) once it lands.

---

## 0. Orientation (the only analogy, then discarded)

RepoPrompt assembles a static context package from a repo by checkbox-curation.
Causality is the spatial, AI-native, *executable* generalization: point it at a
source substrate, and a living graph of **witnessed claims** becomes the control
surface — you shape context and steer your system by **gesture**, and authorized
gestures **commit actions** back through governed seams.

That sentence is taste, not spec. Drop it now. The pattern is:

```text
source evidence
→ witnessed graph claims          (a claim cites evidence or is flagged inference/mock)
→ user gesture / selection        (typed interaction events — evidence of possible intent)
→ intent packet                   (normalized: gesture + selected context + source evidence)
→ proposed execution              (a draft action, simulated, reversible by construction)
→ authority gate                  (intent-class × reversibility × authorization)
→ admitted action                 (only through a named pen — D-4)
→ append-only audit event         (a receipt: who, what, from which packet, citing which evidence)
→ graph projection refresh        (a deterministic fold over records — never a side-write)
→ next loop
```

**The one-sentence pattern.** *Auditable Intent Mesh: a distributed, replayable
graph system where source-backed claims become a live spatial control surface,
user gestures compile into typed intent packets, and only authorized seams can
turn those packets into committed, receipted actions.*

**The load-bearing correction (the thing the whole pattern protects):**

> A gesture is **not** the command.
> A gesture is **evidence of possible intent**.
> The system converts gesture + selected context + source evidence into an
> **intent packet**, then routes that packet through proposal → validation →
> authority → execution → witness → replay.

This is not new machinery. It is **ontum's loop** — log-is-truth → pen → gate →
receipt → level-triggered fold — pointed at the interaction surface. AIM inherits
the doctrine's invariants wholesale (no self-signing, the owner is the last stop,
realness is an admitted record, history is append-only). What AIM adds is the
*front half*: how a gesture becomes a candidate action without ever becoming an
unaudited one.

---

## 1. Core primitives

Each primitive: **what it is · contract (required fields) · register it lives in
· its firm invariant.** Primitives that already exist in `display-system.md` or
`canvas.js` are marked `(extends C#)` and reused, not re-invented.

### Substrate & witness

**P1 · SourceEvidence** *(extends C1 FundamentalDatum)*
- *Is:* a durable, append-only given the mesh may read but never own.
- *Contract:* `address` (`file:line` | log-record id | commit sha | source span),
  `hash` (sha256 of the bytes), `append_only: true`.
- *Register:* **Record.**
- *Invariant:* the mesh never writes here except through an admitted pen producing
  an audit event. Source bytes are identity (editing them is a new version).

**P2 · WitnessedClaim**
- *Is:* an assertion the graph makes *about* the substrate ("this file is the
  value gate," "this term is overloaded"). The atomic content of a node or edge.
- *Contract:* `statement`, `backing` (≥1 `SourceEvidence` ref **or** a declared
  `DerivedStep`), `confidence_class` ∈ {`minted-*`, `projected`, `proposed`,
  `poetic`} (the term-economy taxonomy), `build_state` ∈ {`real`, `mock`, `wip`,
  `todo`} (the construction flag).
- *Register:* **Runtime** (displayed), grounded in **Record**.
- *Invariant:* **a claim with no resolvable backing can never be `minted` or
  `real`** — it renders `proposed`/magenta-flagged or it is a `ghost`. (Same
  refusal as `term_economy.classify` and the `BUILD` flag.) *This is the audit
  floor; everything else rests on it.*

**P3 · Node** *(extends C5 TypedNode)*
- *Is:* a typed unit carrying one or more WitnessedClaims; a place in the mesh.
- *Contract:* C5's (`id`, `type`, `label`, `config`, `sites[]`, `space`,
  `strata{fundamental,derived,learned}`, `divergence`) **+** `claims[]` (P2),
  `anima{strength,tempo}` (C18).
- *Register:* **Runtime.**
- *Invariant:* a node holds no authority of its own — it is a witness and a
  handle, never a writer.

**P4 · Edge** *(extends C10 TypedConnection / C11 TypedIteration)*
- *Is:* a typed relation between nodes (sync intra-cluster, or async cross-cluster).
- *Contract:* C10/C11's (`from`, `to`, `kind`, `sign`, `port_compat`, `stratum`)
  **+** `backing` (P2 — an edge is itself a claim and must cite or be flagged).
- *Register:* **Runtime.**
- *Invariant:* an incompatible wire is refused at the seam (the port contract);
  an unbacked edge renders as inference/mock, never as fact.

**P5 · Membrane**
- *Is:* a bounded region grouping nodes into one context (a phrase's mesh; a
  directory's story; a cluster). The unit of *selection* and *scope*.
- *Contract:* `id`, `members[]` (node/edge refs), `boundary` (the selection
  predicate or hand-drawn region that defines it), `scope` (what intent packets
  raised inside it default to).
- *Register:* **Runtime.**
- *Invariant:* a membrane is a lens, not a container of truth — dissolving it
  changes no record. (Resolves the iterations-0012 "phrase = mesh in a membrane.")

**P6 · Pulse** *(extends C8 TypedPulse)*
- *Is:* a message flowing along an edge; its internal *is* a sub-mesh (recurse).
- *Contract:* C8's (`id`, `data`, `internal_graph`, `route`, `stratum`).
- *Register:* **Runtime.**
- *Invariant:* a pulse animates and carries; it commits nothing. (A pulse that
  writes is a category error — writes go through P12.)

### Intent & execution

**P7 · GestureEvent**
- *Is:* one typed interaction — move, recolor, draw, lasso, zoom, scroll-as-read,
  connect, dwell. The raw signal.
- *Contract:* `kind`, `target` (node/edge/membrane/region refs), `params`
  (vector, color, path…), `t` (timestamp), `actor`.
- *Register:* **Request** (raw, pre-normalization).
- *Invariant:* **a GestureEvent is evidence, never a command.** It is appended to
  the interaction trace and may be folded into an IntentPacket; it triggers no
  action by itself.

**P8 · SelectionRegion**
- *Is:* the context a gesture points at — a set of nodes/edges/membranes/source
  spans gathered by a select-pattern or a drawn boundary.
- *Contract:* `members[]`, `derivation` (the pattern/region that produced it),
  `source_spans[]` (the SourceEvidence the selection resolves to).
- *Register:* **Request.**
- *Invariant:* a selection carries its *derivation* so the resulting packet is
  explainable ("you selected these because…").

**P9 · IntentPacket** — *the normalization point; the heart of the pattern.*
- *Is:* a normalized, replayable statement of *possible* intent compiled from
  GestureEvents + SelectionRegion + SourceEvidence. The unit everything downstream
  routes.
- *Contract:* `id`, `gestures[]` (P7, preserved verbatim), `selection` (P8),
  `evidence[]` (P1 refs), `intent_class` (see §3 — e.g. `read`, `annotate`,
  `propose-change`, `mutate-source`), `ambiguity` ∈ {`unambiguous`, `ambiguous`},
  `reversible` (bool), `authority_required` (bool, derived from class).
- *Register:* **Request.**
- *Invariant:* **a packet preserves the gesture and context that produced it**
  (replayability). It is a *request*, not a decision — it has no power until a
  gate rules on it. A packet whose `intent_class` cannot be resolved is
  `ambiguous` and **cannot** auto-execute (§3).

**P10 · Proposal**
- *Is:* a concrete, simulated draft action a packet would perform — a dry-run with
  a preview the user can accept/reject.
- *Contract:* `id`, `packet` (P9 ref), `effect` (the would-be change, as data),
  `preview` (the projected post-state), `target_pen` (which P12 it would route
  to), `reversal` (how to undo, or `irreversible: true`).
- *Register:* **Simulation.**
- *Invariant:* a proposal **mutates nothing** — it lives in Simulation. A rejected
  proposal still leaves an audit event (the rejected path is recorded, never
  silently dropped — history keeps questions).

**P11 · Gate** *(the loop's gates — value/owner-stamp/placement/handoff/confirm)*
- *Is:* the authority check: may this proposal become an admitted action?
- *Contract:* `kind`, `decision` ∈ {`admit`, `refuse`, `escalate`}, `policy` (the
  rule applied: intent-class × reversibility × authorization), `authorized_by`
  (the standing stamp or owner gesture it executes), `reason`.
- *Register:* the seam between **Request/Simulation** and **Record.**
- *Invariant:* **no gate signs its own line; the owner is the last stop (D-4).**
  An irreversible or unauthorized class **must** `escalate` to an owner gesture —
  it can never self-admit. A confirmed arc is the standing stamp the gate
  *executes* (it does not invent authority).

**P12 · AdmittedPen**
- *Is:* the *only* path from a proposal to a committed action — a named, branded
  writer (the git pen, the PR pen, `loop.node`, the records pen, a future
  gesture-pen).
- *Contract:* `id`, `verbs[]` (what it may write), `produces` (the audit event
  shape), `guard` (the precondition it enforces).
- *Register:* the write seam into **Record.**
- *Invariant:* **the mesh may infer freely, simulate freely, request freely — it
  may only commit through an admitted pen.** There is deliberately no second write
  path. A write that bypasses a pen is the cardinal failure (§6).

**P13 · CommittedAction**
- *Is:* the durable effect once a pen has run — a log append, a file written via
  pen, a PR opened, a verdict recorded.
- *Contract:* `id`, `pen` (P12), `packet` (P9 — the intent it realized),
  `effect`, `reversible` (bool), `reversal_ref` (if undone later).
- *Register:* **Record.**
- *Invariant:* a committed action is append-only history — superseded, never
  erased.

**P14 · AuditEvent** *(the loop's receipt/event)*
- *Is:* the append-only record of *any* mesh act worth witnessing — a packet
  raised, a proposal previewed, a gate decision, a committed action, a refusal.
- *Contract:* `id`, `t`, `actor`, `kind`, `packet_ref`, `evidence_refs[]`,
  `decision`/`effect`, `prior_hash` (chain link).
- *Register:* **Record.**
- *Invariant:* **every action produces a receipt; every projection is replayable
  from these events.** The audit graph is the truth of *what the mesh did*, the
  way the loop's log is the truth of *what the system did*.

**P15 · ProjectionRefresh**
- *Is:* the re-derivation of the Runtime graph from Record after any change.
- *Contract:* `inputs` (the Record span folded), `fold` (the deterministic
  function), `output` (the Runtime graph + claims + anima).
- *Register:* **Record → Runtime.**
- *Invariant:* **level-triggered, never push.** The projection is a *pure fold*
  over records (cache, rebuildable, deletable) — it holds no authoritative state.
  The moment Runtime keeps state Record doesn't, the pattern is broken.

---

## 2. The four operating registers

The mesh is partitioned into four registers. Every primitive lives in exactly
one; crossing between them is the entire discipline.

| Register | What it holds | Mutability | Maps to (ontum) |
|---|---|---|---|
| **Record** | source bytes, logs, atoms, commits, receipts, committed actions, audit events | append-only, **truth** | `.ai-native/log/*`, source, the doctrine |
| **Runtime** | the live projection: nodes, edges, membranes, pulses, selections, anima, UI state | ephemeral, **derived** | the canvas / a fold |
| **Request** | gesture events, selection regions, intent packets, virtual request-nodes | proposed, **powerless** | atoms/announcements pre-gate |
| **Simulation** | proposals, previews, inferred intent, dry-runs, rejected paths | sandboxed, **never commits** | the slow-loop *proposer*, dry-runs |

**The clean law (the whole pattern in one line):**

> The mesh may **infer freely** (Simulation), **simulate freely** (Simulation),
> and **request freely** (Request).
> It may only **commit** through an **admitted pen** (Record).

Execution happens **only** when a **Request** becomes a **CommittedAction** by
passing a **Gate** and running through an **AdmittedPen**. Runtime and Simulation
have no write authority over Record — ever.

---

## 3. Execution semantics

The lifecycle of intent, with the exact thresholds at each transition.

**When a gesture is only evidence.** Always, at emission. A GestureEvent (P7)
appended to the interaction trace is evidence. It triggers nothing. Reading,
scrolling, zooming, recoloring-for-view, moving-for-layout are *Runtime-local*
gestures that never leave Request as packets unless the user composes them into
one.

**When a gesture becomes a request.** When gestures + a SelectionRegion are folded
into an **IntentPacket** (P9) — explicitly (the user opens an NL-collection zone
on a selection) or by a declared compile rule (a drawn connect-gesture compiles to
a `propose-edge` packet). The packet preserves its gestures and context.

**When a request becomes a proposal.** When the packet's `intent_class` implies a
*change* (not pure `read`/`annotate-runtime`), the mesh simulates it into a
**Proposal** (P10) with a preview and a reversal. Pure-read packets never become
proposals; they refresh Runtime selection only.

**When a proposal may execute.** Only when a **Gate** (P11) returns `admit`. The
gate's policy is `intent_class × reversibility × authorization`:

| Intent class | Reversible? | Auto-execute? | Path |
|---|---|---|---|
| `read` / `annotate-runtime` | n/a (no Record write) | yes | Runtime-local, no pen |
| `propose-change` (unambiguous, reversible, authorized) | yes | yes, via pen | pen → audit event |
| `propose-change` (ambiguous) | — | **no** — show preview, require accept | escalate to user |
| `mutate-source` / irreversible / unauthorized | — | **never** | **escalate to owner gesture (D-4)** |

**What must remain reversible.** Every auto-executed `propose-change`. If a
proposal cannot state its `reversal`, it is treated as irreversible and escalates.
(The reversibility line from `[[ontum-inference-verified-prune-cut]]`: autonomy on
the reversible, an owner gesture on the irreversible.)

**What requires explicit owner authorization.** Any `mutate-source`, any
irreversible action, any action under an *unconfirmed* arc. A *confirmed arc* is a
standing owner stamp the gate executes for the reversible pieces under it; it does
**not** cover irreversible or out-of-scope acts.

**What can never mutate source directly.** The Runtime graph, a Proposal, an
IntentPacket, a Pulse, inference output. **Nothing in Runtime/Request/Simulation
holds a write to Record.** Source changes only as a CommittedAction through an
AdmittedPen producing an AuditEvent. This is the projection-is-not-a-second-source
hard rule, made mechanical.

---

## 4. The audit model

Four obligations, each with teeth:

1. **Every claim cites or is flagged.** A WitnessedClaim (P2) carries `backing`
   resolving to SourceEvidence/DerivedStep, **or** it wears a `build_state` of
   `mock`/`wip`/`todo` and a `confidence_class` no higher than `proposed`. An
   unbacked claim rendered as `real`/`minted` is a **ghost** and is refused.
2. **Every packet preserves its origin.** An IntentPacket (P9) holds its
   `gestures[]` and `selection` verbatim — the action is always explainable back
   to the gesture and context that produced it.
3. **Every action produces a receipt.** A CommittedAction (P13) — *and every gate
   refusal and rejected proposal* — appends an AuditEvent (P14). No silent acts,
   no silent drops.
4. **Every projection is replayable.** The Runtime graph is a pure fold (P15) over
   Record. Given the Record span, the projection re-derives byte-for-byte; given
   the audit chain, any past projection replays. Runtime holds no truth Record
   lacks.

The audit graph is itself a mesh (§5) — queryable, with a `prior_hash` chain so a
torn or forged tail is detectable and dropped on the next fold (the loop's
torn-tail tolerance).

---

## 5. The distributed mesh model

AIM is **not one graph.** Collapsing it into "the graph" is how provenance and
authority blur. It is six typed sub-graphs that communicate across seams; what
crosses a seam is explicit, the rest stays local.

| Sub-graph | Nodes are | Register | Authority |
|---|---|---|---|
| **Source graph** | files, log records, commits, spans (P1) | Record | truth; read-only to the mesh |
| **Witness graph** | WitnessedClaims (P2) over source — the projection | Runtime | derived; cites source |
| **Request graph** | gestures, selections, intent packets (P7–P9) | Request | powerless until gated |
| **Execution graph** | proposals, gates, pens, committed actions (P10–P13) | Sim → Record | the *only* writer |
| **Audit graph** | audit events (P14), chained | Record | the witness of acts |
| **Projection graph** | the rendered Runtime: nodes/edges/membranes/pulses/anima | Runtime | display only |

**What crosses seams (the only legal crossings):**

- Source → Witness: a **ProjectionRefresh** fold (P15). Deterministic. One-way.
- Witness + gesture → Request: an **IntentPacket** compile (P9). Carries evidence.
- Request → Execution: a **Proposal** (P10), then a **Gate** decision (P11).
- Execution → Source/Record: a **CommittedAction** through an **AdmittedPen**
  (P12/P13). The single write seam.
- Execution/Request/Witness → Audit: an **AuditEvent** (P14) per act.
- Record (any change) → Projection: a **ProjectionRefresh** (P15). Closes the loop.

**What stays local (never crosses):** Runtime layout/UI state stays in the
Projection graph. Simulation previews stay in the Execution graph until admitted.
Raw gestures stay in the Request graph unless folded into a packet. A sub-graph
that reaches *across* a non-listed seam (e.g. Projection writing Source) is a
violation, not a feature.

This is the same shape as the loop's organs (reconcile/orchestrate/node/summon
each a fold or a pen over the one log) — six lenses, one truth, no second write
path.

---

## 6. Failure modes (anti-patterns, each a test in §7)

| # | Failure | The mechanism that catches it |
|---|---|---|
| F1 | **Graph becomes decorative** (pretty, witnesses nothing) | every node/edge must carry a backed P2 claim; the mock-census DQs a surface over a mock-ratio threshold (the `BUILD` flag fold) |
| F2 | **Gesture becomes ambiguous command** | `ambiguous` packets cannot auto-execute (§3); they require an accepted preview |
| F3 | **AI invents authority** | a gate executes only a *standing stamp* or owner gesture; an unauthorized/irreversible class **escalates** — it cannot self-admit (D-4) |
| F4 | **Projection becomes source of truth** | Runtime holds no state Record lacks; ProjectionRefresh is a pure deletable fold; the replay test re-derives it |
| F5 | **Narrative hides provenance** | every claim resolves to evidence or is flagged `proposed`/magenta; a `real` claim with no backing is a `ghost`, refused |
| F6 | **Audit log becomes unreadable** | audit events are typed + chained + queryable as the audit graph; the digest/retro folds read it (no prose-only audit) |
| F7 | **Execution bypasses admitted pens** | the *only* Record-write crossing is Execution→Pen; the command-guard/write-guard refuse a raw write; no second write path exists |

---

## 7. Invariants & acceptance tests (the teeth, §10)

A spec without teeth is taste. These are the firm laws and the tests that refuse
their violation — each with a **negative control** (the thing that *must* fail).

**I1 · Backed-or-flagged.** *Test:* a claim with a non-resolving `backing` and
`build_state: real` is rejected as `ghost`; the same claim with `build_state: mock`
renders (magenta, `proposed`). *Negative control:* a fabricated citation classified
`minted` fails the test.

**I2 · Gesture-is-not-command.** *Test:* a GestureEvent alone produces zero
CommittedActions and zero AuditEvents of kind `commit`; an `ambiguous` IntentPacket
routed at a gate returns `escalate`/preview, never `admit`. *Negative control:* a
draw-gesture that silently mutates source fails.

**I3 · One write seam.** *Test:* every CommittedAction's `pen` resolves to a
registered AdmittedPen; a Record write with no pen ref is refused by the guard.
*Negative control:* a Runtime/Simulation object holding a direct Record write
fails.

**I4 · Replayable projection.** *Test:* deleting the Runtime/cache and re-folding
Record yields a byte-identical Projection; replaying the audit chain to step *n*
reproduces the projection at step *n*. *Negative control:* a Projection carrying
state absent from Record fails (it cannot be re-derived).

**I5 · Receipted refusals.** *Test:* a refused proposal and a rejected preview each
append an AuditEvent. *Negative control:* a silently dropped intent (no audit
event) fails.

**I6 · Owner-last-stop.** *Test:* an irreversible or `mutate-source` packet under
an unconfirmed arc always `escalate`s; a confirmed arc admits only its reversible,
in-scope pieces. *Negative control:* a gate that self-admits an irreversible action
fails (self-signing).

**I7 · No second source of truth.** *Test:* mutating the Projection graph changes
no Source/Record byte; only a CommittedAction does. *Negative control:* a witness
edit that survives a ProjectionRefresh (i.e. was written to Record off-pen) fails.

**The §10 fit-refusal test (the one that matters):** two locally-fine packets —
each individually admissible — must be able to *refuse to fit* and the audit catch
it. Example: packet A commits a source edit; packet B's preview was simulated
against the *pre-A* projection. On refresh, B's `reversal` no longer resolves —
the gate must refuse B as stale, not admit it against a vanished base. If every
packet always fits on the first try, the gate isn't doing its job yet.

---

## 8. Lifecycle summary (the repeatable loop)

```text
RECORD        source bytes, logs (truth, append-only)
  │  ProjectionRefresh (pure fold, level-triggered)
  ▼
RUNTIME       witnessed claims rendered as nodes/edges/membranes/pulses + anima
  │  gesture + selection
  ▼
REQUEST       GestureEvents → SelectionRegion → IntentPacket (preserves origin)
  │  intent_class implies change
  ▼
SIMULATION    Proposal (preview + reversal) — mutates nothing
  │  Gate: intent_class × reversibility × authorization
  ▼
GATE ──refuse/escalate──► owner gesture (D-4) or rejected (still audited)
  │ admit
  ▼
ADMITTED PEN  the only write seam
  ▼
RECORD        CommittedAction + AuditEvent (receipt, chained)
  │  ProjectionRefresh
  ▼
RUNTIME       refreshed projection → next loop
```

**Where AIM meets the substrate already built:** the Witness graph is the
`display-system.md` projection (strata C1–C3, divergence C4, node/edge/pulse/glyph
C5–C11, anima C18). The Execution graph is the loop's gates + pens. The Audit graph
is `.ai-native/log/`. AIM is the **named seam** that joins the witness half (built)
to the execution half (the loop) through the intent packet — the "open heart" of
iterations 0012, formalized.

## 9. Open holes (grip discipline — named, not filled)

- **OH1 · The gesture→packet compile rules.** Which gesture kinds compile to which
  `intent_class` (and which stay Runtime-local) is a declared table not yet
  written. The *shape* is fixed (P7→P9); the *entries* are bdo's to seed.
- **OH2 · The gesture-pen.** A new AdmittedPen for gesture-originated source
  changes does not exist; today's pens (git/PR/node/records) cover their verbs.
  Until it exists, `mutate-source` packets escalate by default — correct, but
  conservative.
- **OH3 · Virtual request-nodes.** Intent packets raised by *nodes* (not humans) —
  the autojective/self-slotting case — are named in the Request register but their
  authority rung (the spawn-rail trust ladder) needs binding.
- **OH4 · Membrane scope inheritance.** Whether a packet raised inside a membrane
  inherits the membrane's confirmed-arc scope, or must re-authorize, is a fork.
- **OH5 · AIM is PROPOSED.** The name and the mint are bdo's (D-4). This file is the
  drafted pin awaiting his bless and its home in the Pattern Commons.

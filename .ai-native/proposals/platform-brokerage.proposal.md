# The platform layer: the brokerage, the witnessed mesh, and confirmation chains (PROPOSED — bdo's, 2026-06-20)

**Status:** PROPOSED — a **blueprint, not a build**. Naming and the arc are bdo's
(D-4); a session may only propose. This is durable foundation captured from a
live design conversation (2026-06-20), per bdo's directive that he wants
blueprint-first foundation, results as byproduct (issue #348). Nothing here is
built. The companion memories are `ontum-activity-accounting-gateway`,
`ontum-git-gh-gateway`, `ontum-platform-vision-gateway-economy`, and
`ontum-gateway-separation-of-powers`.

> **Deepening (2026-06-20, same conversation's continuation).** A second pass
> found the layer the five facets stand *on*: the **consequence tier** and the
> **generative ladder** that the platform exists to operate. The witnessed mesh
> (facet #2) is its **pentimento** channel; the Herald-brokerage (facet #4) is its
> **reputation economy**. The deep layer is the new section "The deeper layer: the
> consequence tier," below the facets — and it promotes the `exports/model-free-mode`
> package from a one-shot critique bundle to the **research spine of the measurement
> layer**.

## How this arc was found (the thread)

It began at "account for **all** activity, even the harness's own hooks, and
audit their data collection for a **shared gateway**" (→ organ 1 shipped, PR
#339, `loop/activity.py`). Pulling that thread surfaced four more facets that
are one arc:

1. **Naming** — what gets named, at what grain? ("how many atoms in a node / a
   skill / a grain of rice?")
2. **The holon** — a node's interior **is** an atom-graph; the structure already
   exists in the incidence data.
3. **The gateway** — that structure + the activity should be **witnessed as data
   streams** at platform/gateway level.
4. **The substrate** — to carry streams across an open set of agents we asked
   whether to add **internal networking** (still local), liftable to public.
5. **The institution** — the broker that fear forbade becomes a **branded,
   governed brokerage** — and the **Herald is already nearly one.**

The through-line: lift ontum from *file-local* to a *governed,
internally-networked platform* — **without the log ever stopping being truth.**

## The full shape (one picture)

```
            ┌─────────────────── the gateway (one-way glass) ───────────────────┐
            │  reads WITNESSED · writes AUTHORIZED · every act + structure       │
            │                    passes here and is seen                         │
            └───────────────────────────────────────────────────────────────────┘
                 ▲ witnesses                         ▲ witnesses
        ┌────────┴──────────┐              ┌─────────┴────────────┐
        │  STREAM 1: activity │            │  STREAM 2: holon-graph │
        │  (organ 2: every    │            │  atoms = vertices,     │
        │   hook firing → a    │            │  incidence = edges     │
        │   receipt)           │            │  (seam/collide/touch)  │
        └─────────┬───────────┘            └──────────┬─────────────┘
                  │   both are FOLDS / tails over the append-only log
                  ▼                                    ▼
        ┌──────────────────────── the internal mesh (transport) ────────────────┐
        │  local, not public · carries derived/transient data · NOT a truth-holder │
        └───────────────────────────────────────────────────────────────────────┘
                  ▲ governed by
        ┌─────────┴───────────────────── the BROKERAGE ─────────────────────────┐
        │  the Herald generalized: registration + reputation + ROUTING,          │
        │  all folds over the log · brokers ON THE RECORD · transports EPHEMERALLY │
        └───────────────────────────────────────────────────────────────────────┘
                  ▲ lifted internal → public by
        ┌─────────┴──────────────── confirmation chains ────────────────────────┐
        │  staged authorization: trust-ladder + arc-confirm + policy, composed    │
        │  into links · internal → internal-shared → public                       │
        └───────────────────────────────────────────────────────────────────────┘
```

## The five facets (bundle + label)

**1. Structure — the holon-graph.** A node is a holon; its **interior is an
atom-graph**. This is not a new model to build — it is **already encoded on
disk**: `epic.pieces` and `atom.incidence.serves` are the membership edges;
`hands_off_to` (the seam) is a directed edge between atoms; `must_not_collide_with`
is a constraint edge; `touches` is a shared-resource edge. The system today treats
a node as a *judge* (a function over atoms) and never as a *container whose
interior is that graph*. Surfacing it makes "how many atoms in a node" a real
query and gives a node a Merkle-style identity rolled up from its atoms.
*Atom = the floor* (the grain of rice — the indivisible leaf; nodes-all-the-way-down
stop at atoms). **Open:** the `node` term is overloaded — a **holon-node**
*contains* (interior = atoms) while a **gate/judge** *acts on* (a face, no
interior). One type seen two ways, or two types? (cut below.)

**2. Observation — the gateway witness.** The gateway witnesses both the activity
and the holon-graph as **data streams**. Load-bearing constraint: local-first
means a "data stream" is **the append-only log re-surfaced as a fold/tail**, not
a transport (no Kafka). The log *is* the stream; the gateway is the witness seam.
The asymmetry holds: reads witnessed, writes authorized (one-way glass).

**3. Substrate — the internal mesh.** A *local, internal* network (localhost/IPC
between agents) as a **new governed reach**, not a change to the pure core
(`loop/`). Justified only by **real-time, multi-agent coordination** — if the
driver is merely *surfacing*, folds-over-the-log already suffice and a mesh is
premature (cut below). Network and daemon clauses of local-first are *already
bent* in the reach layer (the inference gateway talks `http://localhost`; the
session-lifecycle watcher is an external cron). The mesh would extend that, not
breach the core.

**4. Institution — the brokerage (the keystone).** Instead of *forbidding* a
broker, **brand and govern it** — the same move ontum made for every raw seam
(raw git → the git pen, raw spawn → the spawn rail, raw model → the inference
gateway). The broker was the last wall. **The Herald already breached it:** it is
a broker-shaped thing that holds **no truth** — registration and reputation are
*folds over logged `herald_introduction` admissions, never a table*. A full
brokerage adds **routing / matchmaking** (connecting an agent that needs work to
one that can; dispatching a stream producer→consumer) on top of the Herald's
registration + reputation.

**5. Authorization — confirmation chains.** Lift internal → public by **staged
authorization**: the trust ladder, arc-confirm, and gateway policy are single
links today; a *chain* composes them (internal → internal-shared → public), each
link an owner-or-policy gesture. The core never trusts the outside; the gateway's
one-way glass scales up the chain.

## The deeper layer: the consequence tier (what the five facets stand on)

*Added from the design conversation's continuation (2026-06-20). The five facets
above are the **body** — gateway, mesh, brokerage. This is the **metabolism** they
serve: why the platform exists and what it operates on. It is the bridge to
`epic.model-free-mode-response` and the `exports/model-free-mode` package.*

**The shift (the higher tier).** Today's AI operates at the **action tier** — it
picks tokens/actions, and we gate the *actions* (a whitelist; brittle; routed-around
— the doctrine's T1). The platform lifts operation to the **consequence tier**: an
agent is given a *consequence to satisfy* (a volume to fill) and mashes freely toward
it, gated not on what it pressed but on what it **caused**. This is the new class
object's "higher tier," and it is the move that sidesteps today's AI traps —
hallucination, reward-hacking, metric-optimization, lost provenance — *by
construction* (each trap's antidote is named below).

**The generative ladder (how a consequence is born).** A unit of meaning is built by
climbing a dimensional ladder, each rung an act of **interpretation**, not
calculation:

> **fill a 0d point** (a *gesture* — dimensionless intent) → **interpret until
> measurable** (the gesture resolves into a handle) → **measurements make a surface**
> (a field) → **surface composed into an object** (a bounded volume / holon) →
> **object defined and molded** (identity, type, governed, versioned).

The molded object at one tier **is** the 0d point at the next — the ladder re-climbs,
holographically, at rising tiers ("all the way up"; bdo: "I could go on for days").
This is the holon-graph (facet #1) given its *generative* reading: not just a static
interior-graph, but the path by which that interior was filled.

**The four invariants = measure + contain.** The doctrine's gate (Reversible,
Bounded, Observable, Learning) splits cleanly along the ladder:

- **Measure the consequence** = **Observable + Learning** = **pentimento + sauce.**
  - **Pentimento** — the *observed* channel: the creator's process showing through,
    the real superseded bytes, attribution by construction. The append-only log *is*
    the pentimento; the witnessed mesh (facet #2 / STREAM 1) is it surfaced. *(It
    carries Reversible too: the prior mold never leaves, so walk-back is structural —
    you cannot forge a one-way door in a medium that keeps the earlier image in the
    paint.)*
  - **Sauce** — the *tasted* channel: the emergent, integrative quality — does the
    whole **cohere**, judged not by inspecting ingredients but by tasting the whole,
    **by a panel of peers** (the gate-panel, PR #338, + the §7 spawn rail). The tooth:
    **sauce is a measured coherence anchored to the pentimento** (relation-bucket
    coherence, val_bpb on the mesh) — never a vibes-verdict, or it becomes the
    confident-hallucination it exists to defeat.
- **Contain the consequence** = **Bounded + Reversible** = the mesh boundary + the
  pentimento.

**The measurement layer is load-bearing, and the model-free research is its spine.**
The doctrine's three open estimators *are* the measurement organs: the reversibility
classifier + blast-radius bound = the **contain** estimators; the in-stream
learning-progress signal = the **sauce**, made a number. So
`epic.model-free-mode-response` does not run *beside* the platform — it **is** the
platform's measurement engine. Wave-1's `observe.py` (Observable-as-gate),
`relation_ledger.py` (the relational middle band — meaning without mechanism), and
`over_containment.py` (the predictive-vs-trivial discriminator) are its first organs.

**The reputation economy (the brokerage's foundation).** Pentimento + sauce, composed
over a creator's history, *are* a reputation: **exemplars net against notorieties, per
credential, recomputed forward, never asserted** — exactly `herald.py`'s model. This
is what lets the consequence tier **scale without a central gate on every act**: the
front door opens *per-creator, in proportion to earned standing* (the trust ladder
allocates the rope). The doctrine's "maximally free *and* maximally interruptible"
becomes operable — freedom **allocated by reputation** rather than pre-cleared by
whitelist. The tooth (§10, one level up): a **herald earns a meta-reputation over the
standing of whom it vouched**, so a cartel is visible by construction — the vouching
graph is itself reputation-bearing. Facet #4 (the brokerage) is this economy's
*transport*; this layer is its *principle*.

**The holographic kill-test (the whole object's falsification).** "Holographic" is
testable: **cut the mesh anywhere, regenerate the whole from the fragment, measure the
reconstruction error** (val_bpb on the mesh itself). A pentimento that cannot
regenerate the whole from a fragment is decoration; one that can is real holographic
compression. This is the §10 teeth at platform scale — the wager with a test
attached, matching the doctrine's own.

**Self-defining domain (the anti-wirehead anchor).** The mesh emits its own rules —
the objective and the complex rules it fills against are generated *as it climbs*
(geometry emits chemistry…). The danger is self-reference collapse (the noisy-TV /
wireheading trap). Two anchors prevent it: the pentimento must be *actual* superseded
bytes (not a painted-on history effect), and Observable ties every node to a real
receipt. Self-defining, but **pinned to committed reality at every node**.

## The invariant that survives all of it (the one non-negotiable)

**Log-is-truth.** Every facet above is admissible **only** because truth never
leaves the log. Lifted to the brokerage, the test is:

> **The brokerage's knowledge is a FOLD; its transport is EPHEMERAL; truth never
> lives in transit.**

- The **brokering** — every match, vouch, and routing decision, with which
  credential and reputation — lands as an **admission** (foldable, auditable,
  witnessed). The *relationship* is on the record.
- The **payload transport** — the bytes flowing agent-to-agent over the mesh — is
  **ephemeral and explicitly NOT truth**: like a phone call, the *fact you
  connected* is logged, the *audio* never claims to be truth. If it mattered, it
  lands as a log append; if it is not on the log, it did not happen.

This is the `no broker` clause doing its real work (the `no network` / `no daemon`
clauses are already negotiable in the reach). The doctrine amendment:

> ~~`no broker`~~ → **"no broker holds truth; a *brokerage* brokers on the record
> and transports ephemerally."**

## Concept list (the new vocabulary — proposed, to be minted by evidence)

- **brokerage** — a branded, governed intermediary for the open set of agents:
  registration + reputation + routing, all folds over the log; brokers on the
  record, transports ephemerally. (The Herald generalized.)
- **internal mesh** — a local, non-public transport between agents; a governed
  reach, not a core change; carries derived/transient data, holds no truth.
- **data stream (here)** — the append-only log re-surfaced as a fold/tail; the
  log *is* the stream.
- **holon-graph** — a node's interior as a graph: atoms (vertices) + incidence
  (edges); already on disk, never surfaced.
- **confirmation chain** — staged authorization composing trust-ladder /
  arc-confirm / policy links to lift internal → public.
- **broker-on-record / transport-ephemeral** — the cut that keeps a broker
  log-truth-safe.
- **consequence tier** — operation on what an act *causes*, not which act; the higher
  tier that sidesteps action-gating's traps. The new class object lives here.
- **the generative ladder** — point → measure → surface → object → mold; a unit of
  meaning born by dimensional interpretation, the object becoming the next tier's point.
- **pentimento** — the *observed* measurement channel: the creator's process and
  superseded bytes showing through; the append-only log surfaced. Carries Observable
  *and* Reversible structurally.
- **sauce** — the *tasted* measurement channel: emergent coherence, peer-panel-judged,
  anchored to a number (val_bpb / relation-bucket coherence). Carries Learning.
- **measurement layer** — pentimento + sauce; the model-free research (the three
  estimators) is its spine.
- **reputation economy** — exemplars net notorieties per credential, recomputed
  forward; allocates the consequence tier's rope per creator. (The Herald, generalized
  — see facet #4.)
- **holographic kill-test** — cut the mesh anywhere, regenerate the whole from the
  fragment, measure the reconstruction error; the platform's own falsification.

## Open edges — NOT yet cut (preserved honestly, the owner's to resolve)

1. **The `node` overload** — holon-node (interior = atoms) vs gate/judge (a face,
   no interior): one type seen two ways, or two distinct types? *This is the
   hinge for whether christening/naming governs one kind of thing or two.*
2. **Real-time vs surfacing** — does the internal mesh earn its place (real-time
   multi-agent), or do folds-over-the-log already deliver the streams (mesh
   premature)? *Decides whether the substrate facet is built now or deferred.*
3. **What the brokerage routes first** — work, data-streams, or confirmations?
4. **Atom = floor** — confirmed as the indivisible leaf? (Read as yes; pin it.)
5. **The measure/contain 2×2** — does Observable+Learning = *measure* and
   Bounded+Reversible = *contain* hold, or is it too clean? Reversible is claimed on
   *both* sides (the pentimento gives it). One axis or two?
6. **Where the non-deterministic organ enters the pure fold** *(the determinant
   question, from the package's T3).* Sauce — the learning-progress signal, and any
   locality-sensitive/meaning hash over atoms — is inherently learned and predictive;
   the core is a deterministic fold ("the log is truth, everything else is a fold").
   Is the measurement layer a **gated reach** (like the inference gateway, admitted by
   the very consequence-gate this serves), or can the signal be expressed as a *fold
   over the log's own verdict history* and stay native? This decides whether
   model-free operation is *first-class* here or bolted on.
   - *Proposed resolution (a session's engineering cut, bdo to confirm —
     2026-06-20): **native fold first.*** Sauce starts as a pure fold over the log's
     own verdict/relation history — the rate at which verdicts stop flipping = the
     derivative of prediction-error = learning-progress — built in the exact grain of
     `retro.py` (churn), `heal.py`, and `relation_ledger.py`. Determinism and
     log-is-truth stay intact; model-free operation is *first-class*, not bolted on,
     and it is buildable in a single session. The locality-sensitive / meaning-hash
     **embedding** over atom content (T7's organ) is the more powerful but out-of-fold
     path — non-deterministic, via the inference gateway — preserved as a **named
     later reach, admitted by the very consequence-gate this layer serves**, and built
     *only if* the native fold provably cannot separate the regimes (the doctrine's
     deceptive-environment falsification). The cut points toward the substrate, not
     against it.

## CTAs (the first links, in order — none to build before the cuts above)

- **Cut edge #1 (node overload)** — it gates the naming/christening ritual and
  the holon-graph surface.
- **First buildable link: generalize the Herald.** It is already the proto-
  brokerage; the smallest real slice is to add *routing/matchmaking on the
  record* to its existing registration + reputation folds — proving
  broker-on-record / transport-ephemeral on the one organ that already passes the
  fold test.
- **Christening** (the naming ritual) rides facet #1 once the node overload is
  cut: confirm-arc-for-names — young names forgiven, relation-placed, christened
  by one owner gesture.
- **Doctrine amendment** (no-broker → brokerage) is bdo's to make when the
  brokerage slice proves the cut.
- **The measurement layer's spine: promote `exports/model-free-mode`.** The package
  stops being a one-shot critique bundle and becomes the research spine of the
  measurement layer; the doctrine's three estimators become its organs (`observe.py`,
  `relation_ledger.py`, `over_containment.py` are wave 1). The **existence proof** is
  to climb the ladder *once*, publicly, on the model-free-mode material, and run the
  **holographic kill-test** on the result — the smallest run that banks-or-falsifies
  the whole deep layer (the doctrine's own kill-criterion, lifted to platform scale).

## Connections (compose, do not double-build — §10)

- **The Herald** (`loop/herald.py`, epic.landing-throughput-response) — the seed
  of the brokerage; generalize it, do not rebuild it.
- **The git/gh gateway** and **inference gateway** — sibling governed reaches; the
  brokerage is the agent-to-agent reach in the same grain.
- **The activity-accounting** (PR #339, organ 2 = the runtime witness) — STREAM 1
  is organ 2 lifted to gateway level.
- **The gateway separation-of-powers** (memory) — the brokerage is an *enforcement*
  organ under the regulatory branch; its routing policy is *legislation*.
- **Causality / the canvas** — already renders typed graphs with a recursion lens;
  the holon-graph stream is its data, and the **pentimento (process visualized)** is
  the canvas pointed at provenance.
- **`epic.model-free-mode-response` + `exports/model-free-mode`** — the **measurement
  engine** of the deep layer; `observe.py` / `relation_ledger.py` / `over_containment.py`
  (wave 1, PR #351) are its first organs. Do not double-build — the platform's
  measurement layer *is* this epic, lifted to platform tier.
- **The gate-panel** (PR #338) + the **§7 spawn rail** — the **peer panel** that
  tastes the sauce; plural independent judges, not one model's verdict.

## Cautions

- **Blueprint, not build.** Per #348: capture the foundation; do not ship a result
  before the cuts are made.
- **The core stays pure.** Every network/daemon/mesh addition is a *reach*, never
  a change to `loop/` (the fold, where truth is derived).
- **Truth never enters transit.** The single failure mode that would break ontum:
  state leaking into the mesh until the log stops being truth. Every brokerage
  increment is tested against the fold/ephemeral split.

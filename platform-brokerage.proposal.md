# The platform layer: the brokerage, the witnessed mesh, and confirmation chains (PROPOSED — bdo's, 2026-06-20)

**Status:** PROPOSED — a **blueprint, not a build**. Naming and the arc are bdo's
(D-4); a session may only propose. This is durable foundation captured from a
live design conversation (2026-06-20), per bdo's directive that he wants
blueprint-first foundation, results as byproduct (issue #348). Nothing here is
built. The companion memories are `ontum-activity-accounting-gateway`,
`ontum-git-gh-gateway`, `ontum-platform-vision-gateway-economy`, and
`ontum-gateway-separation-of-powers`.

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

## Open edges — NOT yet cut (preserved honestly, the owner's to resolve)

1. **The `node` overload** — holon-node (interior = atoms) vs gate/judge (a face,
   no interior): one type seen two ways, or two distinct types? *This is the
   hinge for whether christening/naming governs one kind of thing or two.*
2. **Real-time vs surfacing** — does the internal mesh earn its place (real-time
   multi-agent), or do folds-over-the-log already deliver the streams (mesh
   premature)? *Decides whether the substrate facet is built now or deferred.*
3. **What the brokerage routes first** — work, data-streams, or confirmations?
4. **Atom = floor** — confirmed as the indivisible leaf? (Read as yes; pin it.)

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
  the holon-graph stream is its data.

## Cautions

- **Blueprint, not build.** Per #348: capture the foundation; do not ship a result
  before the cuts are made.
- **The core stays pure.** Every network/daemon/mesh addition is a *reach*, never
  a change to `loop/` (the fold, where truth is derived).
- **Truth never enters transit.** The single failure mode that would break ontum:
  state leaking into the mesh until the log stops being truth. Every brokerage
  increment is tested against the fold/ephemeral split.

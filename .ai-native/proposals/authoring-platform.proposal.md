# ontum as an agent-authoring platform — the one vision, and the bridge between its tiers (PROPOSED)

> **Status: PROPOSED** — bdo's direction, 2026-06-21 (this design conversation),
> his to steer. A **consolidation blueprint**, not a build: it gives a vision
> bdo has stated many times a single home, and answers the one open design
> question he handed back — *what is the bridge between the Owner, the
> Administrator, and the operator?* No code is implied as done. Every mechanism
> below is mapped to a primitive that already exists, an existing proposal, or
> named as a hole. It **composes** the scattered proposals; it does not
> re-derive them (§10).

---

## Why this exists (the friction it names)

bdo, this conversation: *"I really feel like if you give me an agent and
workflow authoring platform that allow me to author agents over the work we
would be closer… It's just so difficult to describe every part of it which is
why we have this canvas. But the vision should be within the repo, and quite
clear, I've stated the idea many times."*

The defect is **not a missing vision.** A sweep of the repo found the vision
stated, clearly and repeatedly, across ~12 documents. The defect is that it has
**no single home** — so each time bdo reaches for it he must re-assemble it from
memory and re-state it, and it never feels "quite clear" even though every piece
is written down. This document is that home. It is the umbrella the scattered
proposals hang from.

## The vision, in the words already on disk

ontum already says — almost verbatim what bdo just said — that it **is** an
agent-authoring platform:

> "ontum is a **meta-agentic, closed, user-configurable platform for authoring
> AI-worker systems** against a target environment and use case — ambient/
> scheduled/habitual workflows composed from primitives (agents, skills, tools,
> data sources), every act routed through the gateway… ontum is **instance #1,
> pointed at itself** (dogfood); the platform is meant to generalize."
> — [`session-gateway.proposal.md`](session-gateway.proposal.md) §13.7

And [`docs/culture/the-idea.md`](../../docs/culture/the-idea.md) (confirmed by
bdo, 2026-06-21) sets the ladder: *Agent → a staffed team (the one who works,
the one who independently checks, the owner who decides, the record that
proves it, kept separate); Automation → autonomy inside bounded authority;*
scaling up into *"governed agents and long-running autonomous projects."*

That **is** "author agents over the work." It is stated. It is just stated in
twelve places.

## Where the vision lives today (the map, folded into one place)

Each row is a real document already on the record. This blueprint does not
replace them; it is the index that was missing.

| Layer of the platform | Where it's stated | Status |
|---|---|---|
| **The vision / scope** | `session-gateway.proposal.md` §13.7; `docs/culture/the-idea.md` | PROPOSED / confirmed |
| **The authoring front door** ("Interface as AI" — describe in language, AI composes a schema-valid graph) | `causality/display-system.md` | PROPOSED |
| **Governance backbone** (policy → what's guarded; PEP/PDP/PIP; auditable by construction) | `gateway-policy-spine.proposal.md` | PROPOSED |
| **Routing / brokerage** (one pub/sub bus over the log; every hop a gateway crossing) | `gated-pubsub-brokerage.proposal.md`; platform-brokerage (PR #354) | PROPOSED |
| **The delivery seam** (writes authorized, reads witnessed; truth from local, not GitHub) | `git-gh-gateway.proposal.md` | PROPOSED |
| **Self-governing loop** (governs, provisions, staffs itself; insulated-not-isolated) | `anthology-self-governing-loop.proposal.md` | BLESSED |
| **The declarative workforce** (desired occupancy in admitted records; the loop staffs itself) | `epic.virtual-fleet.json` | confirmed epic |
| **Morphic agents** (an agent whose program is the surface it stands in) | `epic.experience-layer.json` | confirmed epic |
| **Three hands on a piece** (sketch / ink / paint — author ≠ reviewer ≠ surfacer) | `sketch-ink-paint.proposal.md`; `epic.three-marks.json` | resolved / confirmed |
| **Agent↔owner speech** (typed two-way channel from AskUserQuestion primitives) | `structured-communication-channel.proposal.md` | PROPOSED |
| **The fleet overseer** (the three-tier Administrator → Conductor → Agents) | report 0122; Administrator blueprint (PR #416) | PROPOSED |
| **The witness surface** (the canvas — render the structure too big for prose) | `causality/display-system.md`, `causality/canvas.js` | partly real |

## What "author agents over the work" means here

bdo composes and launches **governed agents over the atoms and arcs**, and the
workforce stays **declarative** — desired occupancy lives in admitted records
(which seats fill under which conditions), not in runtime heroics
(`epic.virtual-fleet.json`). Authoring is **conversational** (describe it; the
AI composes a schema-valid shape; the canvas shows it back —
`display-system.md`), never bespoke buttons. The **canvas is the witness lens**
— how bdo *sees and steers* a structure too large to hold in prose (his "hard to
describe every part") — not the place he hand-builds each agent. Language
authors; the canvas witnesses; the gateway governs; the log remembers.

---

## The bridge question (bdo's, and the spine of this blueprint)

bdo, this conversation:

> *"Who does the Administrator get help and assistance from in administering
> their work? What's the bridge between Owner→Administrator and
> Administrator→operator? Controller? Something else? Vices? Managers?
> Departments? Joins? A crease/fold?"*

This is the load-bearing question, because it decides whether the platform grows
a **staffed org chart** (managers, VPs, departments as standing processes) or
stays true to ontum's spine: **summoned, not staffed** (D-10), and *the loop
staffs itself* (`epic.virtual-fleet.json`).

### The proposed answer: the bridge is a *crease*; the staff are *folds*

**A tier is not a role. A bridge is not a manager. The bridge is a crease — a
witnessed fold — and the Administrator's "help" is the per-axis sensor folds
it already has.** Using bdo's own vocabulary (the gateway grammar: *cross =
authorized, look = witnessed*; origami: *a crease is a witnessed fold logged*):

| bdo's candidate word | The ontum primitive it maps to | Exists today? |
|---|---|---|
| **Owner** | bdo — the last stop (D-4), `confirm-arc` | ✅ |
| bridge **Owner ↔ Administrator** | the **confirm-arc / digest crease** — bdo stamps arcs; the digest is the read back. Authorized crossing, witnessed look. | ✅ `confirm-arc` + `digest` |
| **Administrator** | the **join over the sensor folds** — reads the whole fleet, dispatches one governed launch per unit | ❌ **the one missing part** (report 0122) |
| **Vices / Managers / Departments** | the **per-axis sensor folds**: `digest` · `census` · `heal` · `gaps` · `activity` · `watcher` · `retro`. Each one *manages* one axis of fleet-state. These are the Administrator's staff. | ✅ all built |
| **Joins** | fold-joins over the one log surface (e.g. `atoms_on_main`; the fleet-read itself is a join of the sensor folds) | ✅ join is a known primitive |
| bridge **Administrator ↔ Conductor** | the **dispatch crease** — a governed launch per unit, bounded by an authority dial (what may launch unattended vs what escalates) | ◐ spawn rail exists; dispatch + dial missing |
| **Conductor** | controls **one unit** of the fleet (one arc/department) | ❌ also missing (report 0122) |
| bridge **Conductor ↔ Agent** | the **spawn-rail crease** — branded `ontum-node:<id>`, the §7 prompt pinned, the trust rung checked before the node acts | ✅ spawn rail |
| **Agents** | the workforce — mortal sessions, branded judges, landers, model backings | ✅ |

So the answers, plainly:

- **Who helps the Administrator?** Not lieutenants — the **sensor folds are its
  staff**. `digest` reports what landed/refused/awaits; `census` reports which
  parts carry weight; `heal` reports where a tooth bit wrong; `gaps` reports the
  backlog; `activity` reports what the hooks collected; `watcher` reports which
  sessions idle. The Administrator does not re-sense any of it — it is the
  **join** that folds those reads into one fleet-state and acts on the diff.
- **What is the bridge between tiers?** A **crease** — a witnessed fold — at each
  crossing: confirm-arc/digest (Owner↔Administrator), dispatch (Administrator↔
  Conductor), spawn-rail (Conductor↔Agent). Each crossing is *authorized*; each
  look is *witnessed* (one-way glass — you see through the gate, the patrol sees
  you). The bridges are not new agents; they are **creases over the one log
  surface.**
- **A "department" is an arc/epic.** The fleet is already organized by epic; a
  Conductor steers one epic's slice of the workforce. No new org primitive is
  needed.

### The risk this answer refuses (flagged, per the Taster's Clause / D-14)

The tempting wrong turn — and the one to **not** take — is a literal corporate
org chart: standing "manager" / "VP" / "department-head" agents as long-lived
processes between the Owner and the workers. That violates **summoned, not
staffed** (D-10): such a role would hold state between places, babysat, a
process on a roster. It also manufactures middle-management the loop would then
have to feed. The whole of `epic.virtual-fleet.json` says the opposite: the
workforce is **declarative records + folds**, not staffed seats. If the
Administrator ever *feels* like a manager-of-managers, that is the smell that it
has stopped being a join-over-folds and become a second authority — which D-4
forbids. **The Administrator projects and dispatches; it never authorizes.**

---

## What exists vs what's missing (the honest inventory)

The substrate for authoring agents over the work is **mostly built**:

- ✅ **Agent launcher** — the branded spawn rail (`ontum-node:<id>`, §7 prompt, trust rung).
- ✅ **The mesh** — herald (open-set registration + reputation), trust ladder, inference-queue (concurrency backpressure).
- ✅ **The gateway primitives** — fence/policy, command/write/freeze guards, the pens.
- ✅ **The sensors** — digest, census, heal, gaps, activity, watcher, retro.
- ✅ **The record substrate** — the append-only log, atoms, receipts, admissions, epics, the declarative-fleet records.
- ✅ **A witness surface** — the canvas (schema-driven, "Interface as AI" authoring front door prototyped).

What is **missing** — the gap between "vision stated" and "bdo can author agents over the work today":

- ◐ **The Administrator — its two halves, only one missing (bdo, 2026-06-21).**
  - **The fleet-state join** — read the sensor folds into one situation. *Largely already owned by `epic.virtual-fleet`'s `atom.fleet-plan.v0`* (declared-vs-running, read-only, each diff carrying its one converging step). **Compose it, do not re-derive it (§10).**
  - ❌ **The present-face — the load-bearing half, and the one that's actually blocking.** The fleet-state rendered *to bdo in the easiest shape to engage* — the **inference-construct** (cited context → one recommendation + reasoning → the single divergence that is genuinely his), never a queue. bdo named this directly: *"you probably also suck at presenting my work to me in the easiest way for me to engage… you might be blocked on your inability to remind an owner in an appropriate way."* The bad present-face is **upstream of the stamp-latency bottleneck** (report's Consequence II): if engaging is hard, the stamp is slow. This composes, and may complete, the `epic.owner-harness` brief/digest organs rather than starting fresh.
- ❌ **The Conductor** — the per-unit (per-arc) steerer the Administrator dispatches.
- ◐ **The authority dial — risk-tiered, ask-forgiveness (bdo, 2026-06-21).** Not one unattended/escalate bound but a **tiered** one: *reversible + low-blast-radius → act, log, surface as FYI* (ask forgiveness); *irreversible / high-blast-radius → ask first* (ask permission). This is what keeps the present-face **short** — most reversible motion never reaches bdo, so what does is rare and shaped. The same dial gates the unattended review-drain (report 0122). bdo's to set; the tiers are the gesture.
- ◐ **The conversational authoring loop wired end-to-end** — describe → compose schema-valid agent-spec → launch through the rail → witness on the canvas.

## The first buildable slice (when bdo says build)

> **Grounding correction (2026-06-21).** A read of the repo (not inference)
> changes the slice. (a) The **present-face already exists and is engageable** —
> `loop/brief.py` renders the two-zoom inference-construct (digest + drill-in)
> from the log's own records. Its gap is **adoption + reminder**: sessions
> bypass it (free-handing dense reports), and the push channels (owner-ask
> issues, daily digest) are queue-shaped, not "reminding in an appropriate way."
> (b) The **fleet-state join is declared-only under `epic.virtual-fleet`**
> (`atom.fleet-plan.v0`, unbuilt) — building it is *that* arc's, not a new one
> (§10). So the genuinely-missing, non-double-building first slice is the
> **risk-tiered ask-forgiveness dial** (the keystone to the button — it shrinks
> what must reach bdo at all, making the present-face short and rare), composed
> with `loop/brief.py` for what does reach him. The dial likely composes the
> consequence-gate / `gateway-policy-spine.proposal.md`, not a fresh mechanism —
> check before building.

Per *blueprint before build* and *one real node at a time*: the original-slice
candidate was the **Administrator as a read-only join** —

> a pure fold that reads the existing sensor folds (digest/census/heal/gaps/
> activity/watcher), composes one **fleet-state**, and **proposes** the next
> governed launch per unit (which seat to fill, on which arc, at what rung) —
> *propose-only, never dispatching unattended* until bdo sets the authority dial.

This is the same grain as `gaps`/`census`/`heal` (read-only, propose, the cut
stays bdo's — D-4). It is witness-before-actuator: the Administrator *sees the
fleet whole* before it is ever allowed to *move* the fleet. The dispatch crease
(actually launching) and the Conductor ride later increments, gated on the
authority dial.

## Calls to action — what is bdo's to stamp

1. **The bridge model** (the spine above): is the *crease + sensors-as-staff*
   answer right, or do you want a different shape (a real Controller tier, named
   departments, something else)? This is the one decision the rest hangs on.
2. **The name**: Administrator vs Controller vs Overseer (carried over from
   report 0122 / PR #416).
3. **The authority dial**: what may a governed launch do unattended; what
   escalates to you. (Same dial that would let the review-drain run unattended.)
4. **Graduate or hold**: does this blueprint graduate into an `epic.authoring-
   platform` (with pieces), or stay a PROPOSED map a while longer?

## Composition note (no second truth, no double-build — §10)

This document **cites** the proposals and epics above; it does not copy or
supersede them. It adds exactly one thing none of them held: the **single home**
for the vision and the **answer to the tier-bridge question**. When bdo names
it, it graduates to `epic.authoring-platform` and this proposal stays as the
record of where that arc was born (the proposals-dir contract).

# Proposal — the session gateway, governed folding, and the insulated workspace

**Status:** PROPOSED — offered, not claimed. bdo names arcs; this takes no
stamp it was not given. Provisional until confirmed.
**Provenance:** co-designed in conversation, 2026-06-18 (bdo + Claude),
triggered by a real branch collision in the shared worktree. Coinages
attributed inline; the completeness sweep in §8 is Claude's, flagged as such.
**Frame:** this is one composition. Each part stands alone as an increment
(§11), but they share a spine: **a fold is a governed, attributed act over a
capacity-bounded surface**, and the *session gateway* is that law applied to
the seam where a session is born and where it writes.

---

## 1. The trigger

A session (Claude) committed eval work onto a *parallel* session's branch in
the shared primary worktree (`C:\Users\bdf19\ontum`). The branch had switched
out from under it between reading HEAD and committing. The work had to be
extracted into an isolated worktree and re-homed; the stray commit still sits,
local-only, on the other branch. Recovery was clean but the failure was
structural, not careless — which means it will recur until the structure
changes.

## 2. Root cause

A git working tree has exactly **one HEAD**. Multiple sessions sharing one
tree makes "the current branch" a **shared mutable global**, while each session
treats it as **private, stable session state**. Read-modify-write race on a
shared pointer.

The deeper read: ontum's entire design eliminates shared-mutable-state — the
log is append-only, identity is content-hash, state is re-derived by a fold,
"queue membership is never authoritative." **The git working tree is the one
layer that never had that discipline applied to it.** This proposal applies it.

Corollary (the repo's own law): the fix must be **structural**, not "sessions
should verify HEAD." A session's self-discipline is the unreliable component —
it is why `gaps`, `mock-shame`, and the fences exist. A fix that relies on
care is, by ontum's standard, not a fix.

## 3. Principle — insulated, not isolated (bdo)

Isolation = severance = orphaning — the *other* failure mode this repo already
fights (stranded branches, the gardener, the viewport-sync rescue). The stray
commit *was* an orphan. Pure per-session isolation would manufacture more.

**Insulated:** separated so two conductors don't short, still on one circuit.
Kill **coordination-through-shared-mutable-state** (the HEAD short); keep and
strengthen **coordination-through-routes**:

- a **route in** — provision a workspace off `origin/main`, attributed;
- a **route to land** — PR pen → merge-node → main;
- a **route home** — the workspace is landed *or* reclaimed, never left to strand;
- the **shared conductor** everyone wires to is `origin` + the append-only log.

The insulator between sessions is the per-session HEAD; the circuit they share
is the log. This is the same shape as the log itself: *shared truth everyone
routes to, not a mutable global they fight over.*

## 4. Scale — the branch belongs to the work, not the session

Per-session branches don't scale and *create* orphans: a session is **mortal**,
so a branch tied to it is **born to be orphaned** (session dies → branch
strands). The atom is **durable** (files survive; sessions don't). Tie the
branch to the **claimed atom** and it survives session death — a new session
re-claims and continues.

- **Capacity universal; act on demand.** Every session *can* provision a
  workspace; almost none need to. Most sessions write only to the **log**
  (judging, receipts) — collision-free, no branch. A branch is for a **code
  diff** that becomes a PR.
- **Branch = claimed code-atom's workspace.** Born on the claim (occupancy,
  done-line 0067), reclaimed on land/abandon. Therefore:
  **branch count = in-flight code-atoms = already bounded by `max_inflight_atoms`** —
  the scale governor already exists, and the slow loop already tunes it.
- **Sub-branches only for dependency, lazily** (bdo's "maybe sub-branches,
  idk"): a piece that must build on a *sibling's unlanded code* branches off it
  and merges up when the sibling lands. Default is flat-off-main; arc-confirm
  coordinates the arc's pieces; no structural hierarchy.

## 5. The session gateway

The unifying piece. **`loop/inference.py` is the proven template** — a real
policy enforcement point: `authorize(caller, surface, mind) → permit/refuse`,
default-deny, RBAC over admitted records. The session gateway is its sibling at
a different seam:

| | inference gateway (exists) | session gateway (proposed) |
|---|---|---|
| seam | a thought (inference call) | a session's birth / its first write |
| input | (caller, surface, mind) | (session identity, role, claimed work) |
| issues | permit / refuse | a **binding**: workspace, rung, claim, routes, capacity |

A session is **born through the gateway**: authenticated (who/what summoned me),
authorized (trust ladder + policy, *composed*), provisioned (a worktree —
*lazily*, only on a code claim; read/judge sessions get a read-only binding and
no tree), and **handed its binding** instead of inferring it from a shared HEAD.

**Shape: fold + pen + enforcement (the loop's own pattern).**
- As a **fold** (sense), the gateway answers "what is this session bound to /
  allowed / sufficiently provisioned for?" — read on **every pulse** by the
  summon hook (which already runs at SessionStart + UserPromptSubmit).
- **Level-triggered (bdo):** silent when the binding is sufficient; **returns
  only on a deficit.** Next pulse re-folds → self-healing, no stored state to
  race on.
- The **read-only hook is a sensor, not a limit** (bdo's correction; I-3 — the
  surfacer sees and never acts). On a deficit it *sets the session into a state
  that demands discharge*; the actuator is downstream:
  - **deterministic route** — a PreToolUse guard on the git pen refuses a
    commit until a binding exists, and/or the injected briefing routes the
    agent to run the provisioning pen;
  - **inference route** — summon a node when the deficit needs judgment.
- As a **pen** (act), the gateway *issues* the binding and provisions the
  worktree at the write seam. The **git pen enforces**: no commit unless the
  gateway shows a valid workspace binding for this HEAD.

The branch collision cannot occur under this: you never read HEAD — the gateway
*hands* you your bound branch, and a commit on an unbound HEAD is refused.

## 5b. Homing — the Anthology (the arc-tier Fold) (bdo)

This work should **not** be an 11th named arc. There are already ~10 confirmed
arcs, 5 with zero landings (the WIP sprawl the session's opening /insights crawl
flagged), and they **overlap**. bdo's instrument for that: the **Anthology** — a
*derived envelope over arcs*, a collection of like arcs re-derived into one body
of work.

It is the same Fold, **one tier up**: `atom → arc → anthology`. The anthology
folds *arcs*; its **derived type is the throughline** — the shared intent no
single arc states, re-derived from the members. Overlaps don't survive the fold:
where two arcs duplicate intent or share atoms (`incidence.serves`), the
re-derivation states it once. Hash-named over its member arcs; re-derives when
membership shifts. **Derived, not authored** — a fold proposes the groupings and
the throughline; bdo names and blesses the anthology (propose/dispose, D-4).

Why it belongs here, not as a footnote: it is the **aggregate-backpressure move
at the arc tier** (§7's capacity rule, one level up — many overlapping arcs → a
few anthologies), and the **same lift as done-line 0028** (which moved the
owner's stamp piece → arc; this moves steering arc → anthology — fewer, larger,
re-derived bodies; the loop carries the arcs/atoms within). "Your stamp stays
leverage as the system grows," literally.

**So the session gateway is a *chapter*, not an arc.** It re-homes into an
anthology that re-derives the arcs it already composes — `owner-harness`,
`substrate`, `inference-gateway`, `virtual-fleet`, `the-field` — whose shared
throughline is roughly *the loop governs, provisions, and staffs itself safely*.
bdo names that anthology; the gateway lands as one of its chapters.

**As an organ (when built):** `loop/anthology.py`, sibling of
`digest`/`retro`/`heal` — read-only, propose-only. Folds the arcs, detects
overlap (shared atoms; near-duplicate horizons), re-derives each cluster's
throughline, proposes anthology groupings; bdo blesses and names. The digest
then surfaces anthologies instead of a wall of arcs. (Itself a chapter of the
same anthology — the consolidation organ for the self-governing substrate.)

## 6. Folding, made precise (bdo)

"Fold" is a **verb** that produces a **Fold** (noun) which can be folded again —
self-similar. Today's `reconcile.Fold` is the degenerate ancestor: one
un-named, un-typed god-object computing "the state." The real model:

- **A Fold (operator) is a record, config-as-code:** `{name, fold_type,
  input_spec, fn}`, versioned like a node prompt — governed, auditable.
- **Folding = composing named, typed folds over a slice of the mesh** — and
  folds take folds as inputs (the recursion).
- **The product is a hash-named fold**, content-addressed exactly like an atom:
  `id = sha256(canonical(typed-composition + result))`. Consequences:
  idempotent / level-triggered (same inputs → same hash → already exists →
  silent); cacheable (the `queues/offsets` pattern, generalized);
  **holographic** (bdo) — the hash carries its route back to source.
- **Derived type = a pure typing function over the inputs' types-and-salient-
  values → a canonical signature** (plus a human label). Type **by composition**
  (bdo's cat-glyph: `cat = actor+objective`). Same signature → same type
  (equivalence); a new dimension is a new typed fold the derivation composes —
  no rewrite ("a new node type ships as a schema entry, not new code").

**The derived type is the routing decision.** For the gateway: cheap folds
(`identity`, `rung`, `claim`) compose; if they settle the type as `sufficient`
→ silent; `deficit:unprovisioned` → provisioning pen; `deficit:no-rung` →
inference/escalate. Every gate (value, placement, merge, gateway) is *the same
operation*, differing only in inputs and typing rule. The mesh is
folds-of-folds, each content-addressed, each a holon typed by what composed it.

## 7. Capacity — surfaces have fold limits (bdo)

The bound that makes the recursion **practical** instead of explosive.

- **Capacity is an admitted, typed, re-dialable property of the surface** —
  `{accepts: [fold_types], cap, budget}`, `budget = f(money, environment)`
  (inference $, context tokens, disk/worktree-count, *attention*). The existing
  setpoints (`human_queue_cap`, `max_inflight_atoms`, `step_budget_per_tick`)
  **are** per-surface fold-capacities; the generalization gives every surface
  one, **issued by the gateway as part of the binding** and **re-dialed by the
  slow loop**.
- **Folding is lazy and metered** (`gaps.py`'s pattern): cheapest deterministic
  folds first; expensive (inference) folds fire *only* on residual deficit
  *and* within budget. Most pulses cost ~nothing.
- **Surfaces receive folds compressed** — `hash + derived-type + one-line
  glance` — and **unfold on demand within remaining budget**. The summon hook
  already does this (clip to 200 chars + `python -m loop.X` to unfold).
  Content-addressing is what makes capacity-bounded delivery work.
- **At capacity → backpressure = I-7 cooling, generalized off the human queue
  onto every surface:** **shed/defer** (carry to next pulse), **aggregate**
  (N folds → 1 — the merge-divergences kind; the digest's "lead with the one
  answer"), or **refuse** (the queue refusing to flood). "Impractical" is the
  precise name for a surface folded past its cap — the "hard-to-read digest"
  was exactly that.
- **Budgets are hierarchical/shared:** a fold debits *up* the enclosing
  budget-mesh (the Workflow `budget.spent()` shared-pool shape); a surface's
  **effective capacity = `min` over the enclosing budgets** (proposed rule, §10
  fork). Routing a deficit reads **live load-vs-cap** (a "load fold").

## 8. The folding decomposition — what characterizes a fold

bdo's stat-bearing decomposition (the *physics and telemetry* of folding):

1. **what** you're folding (subject)
2. **how many times** (repetition — churn)
3. **in what way** (named technique / fold-type)
4. **layered with what else** (composition / co-folds)
5. **where you used glue instead of folding** — *glue* = a fixed/asserted/manual
   join that is **not re-derived** (vs a fold, which is). Glue is where you
   stuck it rather than computed it.
6. **total tension stats** across folds, glue, surface, environment, operator,
   and orchestration (parallel/iterative) — the strain/yield/freedom budget
7. **comparisons to past folds and exemplars** (the oracle / val_bpb)
8. **named gaps** in glue and/or fold (grip discipline — absence is information)
9. **spans/mocks clearly marked and vocalized** (mock-shame; nothing fake hidden)

**The load-bearing additions (Claude's completeness sweep) — these turn a
*gauge* into a *gateway*.** bdo's nine are the **surfacer** (they *see* the
fold). A gateway must also **decide** and **record**:

- **A. Authority to fold (the decider — the missing spine).** May *this*
  operator apply *this* technique to *this* surface with *this* intent —
  checked **before** effort? RBAC, the rung (`trust.py`), the policy
  (`inference.authorize`), D-4 (owner is the last stop), no-self-sign (D-2).
  In the nine the operator is only a *tension contributor*, never a
  *permission holder*. A fold the operator isn't entitled to is refused at the
  door — that refusal is what makes it a gate.
- **B. Attribution — the signed receipt (the recorder; precondition for all
  nine).** Every fold *and every glue* is an attributed act on the record:
  `--by`, technique/prompt hash, a receipt. Without it, the stats (effort,
  tension, exemplar comparison) have **no subject to accrue to** — "this
  operator's folds tend to tear" is uncomputable. No-self-sign keeps it
  non-circular (the gateway cannot self-issue past its fence).
- **C. Reversibility / blast-radius.** Is the fold *unfoldable*? Is the glue
  *permanent*? This sets **gesture-vs-autonomy** (the reversibility line) and is
  half of teeth-placement (reversibility × uncertainty). Glue you can't un-glue
  is a one-way door — gate it harder.
- **D. Consumption / use-trace.** The nine are **producer-side**. A fold
  *produced but never consumed* is a **dead valve** (capability-vs-realization).
  "Was it acted on?" is where waste hides.
- **E. Atomicity under interruption.** A fold killed *mid-apply* (a torn fold)
  must leave no corruption — the line-atomic / torn-tail / hard-kill-safe
  property the log already lives by. The half-applied fold is the dangerous case.
- **F. Grounding (the recursion's base case).** Folds-of-folds must bottom out
  in **committed truth** (the log bytes), or it's glue/mock all the way down.
  Point 9 *marks* the ungrounded; this is the positive law that every fold chain
  must *terminate in truth*.
- **G. Freshness / re-fold trigger.** When does a derived fold go **stale** and
  demand re-derivation ("settling drift")? Temporal validity — the difference
  between truth-now and a cached lie.

**The one-sentence law:** *a fold is not just a measured composition — it is a
**permitted, attributed**, reversible-or-not, consumed-or-not, interruption-safe
act that **bottoms out in truth** and **goes stale**.* The nine cover the
measured composition; authority + attribution are what make it a gateway.

## 9. What it composes / reuses (no double-build, §10)

Nothing here is new architecture; it wires organs that exist:

- `loop/inference.py` — the RBAC/PEP **template** (authority half).
- `loop/trust.py` — the rungs (capability authority).
- the claim / occupancy signal (done-line 0067) — what a session owns.
- the merge-node — the route to land; the **gardener** — the route home/reclaim.
- the setpoint dials + slow loop — capacity, admitted and re-dialed.
- the summon hook — the **pulse** the gateway folds on.
- the git pen — the **enforcement** seam (no commit without a binding).
- `reconcile.Fold` — the untyped ancestor of the typed-fold algebra.
- `heal` / `retro` / `digest` / `gaps` — existing folds; siblings of the model.

## 10. Open forks (bdo's calls)

1. **Typing-function governance.** `derive_type` must be **pure, named, and
   versioned**, with the hash covering it (a typing-rule change is new lineage,
   not silent reinterpretation — I-2). Else the derived type is an unfalsifiable
   vibe (§10 failure).
2. **Replace vs layer `reconcile.Fold`.** Decompose the god-object into the
   typed-fold algebra (foundational, large) — or layer the typed folds *above*
   it first and migrate (the increment). *Lean: layer first.*
3. **Capacity ownership.** When a surface's local cap and an enclosing budget
   disagree, which binds? *Lean: `min` over the enclosing budget-mesh.*
4. **The claim↔workspace binding record shape.** A new admission kind
   (`workspace_claimed`, naming its worktree) — or a field grown on the existing
   occupancy signal?
5. **Worktree-per-writer aggressiveness.** Default for every writer
   (clean cure, more setup/disk) — or guard-only (§11.1–2: keep the shared tree
   but make committing on the wrong/unbound HEAD *impossible*). *Lean: guard
   first, default later as its own arc.*

## 11. Suggested increments (smallest-first; consolidation-aligned)

1. **HEAD-intent guard in the git pen** — pins the session's intended branch at
   first write, refuses a commit when HEAD has moved. Catches *this thread's
   exact bug*, pure git-pen change, ships now. (The "sheath.")
2. **Claim↔workspace binding + git-pen enforcement** — no commit without a
   binding for this HEAD; the binding is an attributed record.
3. **The gateway fold** — compose `trust` + `policy` + provisioning-sufficiency;
   the summon hook routes the pulse through it and emits the deficit line.
4. **The provisioning pen + gardener reclaim** — issue a worktree on a code
   claim; guarantee the route home (no orphans).
5. **The typed-fold algebra** — generalize `reconcile.Fold` into named typed
   folds with derived types (the big one; layer-above first, fork §10.2).

## 12b. Convergence (2026-06-18, this session)

**Disposition:** no build yet — design first. **Not an 11th arc** — a *chapter*
of an **Anthology** (§5b) that re-derives the overlapping arcs it composes
(`owner-harness`, `substrate`, `inference-gateway`, `virtual-fleet`, `the-field`)
into one body of work; bdo names the anthology. The §10 detail forks are closed (1 typing-fn:
pure/named/versioned/hash-covered; 2 reconcile.Fold: layer-above-first; 3
capacity: min-over-enclosing-budget; 4 binding: a new `workspace_claimed`
admission). Worktree aggressiveness: guard-first, default-per-writer as a
later stretch of the arc.

**"Glue" pinned:** an *asserted/manual join that is not re-derived* (vs a fold,
which is). Legitimate **at boundaries** where derivation grounds out — a human
decision (bdo's stamp *is* glue), an external system, an axiom — and a **smell
in the interior**, where it stands in for a join that *could* be folded (a
settled literal, a mock). Glue must be **named + attributed + reasoned** (why it
isn't a fold), and **challenged over time**: the inference-as-composition move
(re-derive bounded behavior just-in-time) is precisely *converting interior glue
into a fold* to kill settling-drift. Glue→fold is the arc's quality gradient.

**Four deeper threads closed (each reuses an existing organ — no double-build):**

- **Tension (§8.6) — measured, with a yield point and a response.** Tension is a
  fold over: energy-strain (`energy.py`: burned/fallback acts), the **glue:fold
  ratio** (more glue = more brittle), churn/re-derivation, surface load-vs-cap,
  and parallel contention (competing claims). The **yield point** is a
  per-surface admitted threshold (a dial, like capacity); crossing it triggers
  the **same I-7 ladder** — relax (defer/cool), escalate (to a node/owner), or
  refuse. Tension *is* generalized load; yield *is* generalized cap.
- **Freshness (§8.G) — structural, not a TTL.** A fold is content-addressed over
  its input folds' hashes; if any input's hash moves, the fold's hash moves →
  it is stale → re-fold. So freshness is just **level-triggered re-derivation**:
  a cached fold is valid exactly while its input-hashes hold; re-derive and
  compare. "Settling drift" is the failure of *not* re-deriving — the gateway
  folds fresh every pulse, so it can't settle.
- **Operator trust-accrual.** An operator's competence is a fold over their
  **attributed fold-stats** (§8.B is the precondition) vs exemplars (§8.7) — do
  their folds hold or tear? That fold **proposes** rung changes (`trust.py`:
  "trust accrues as receipts against rungs"); the grant stays bdo's (D-4), now
  evidence-backed. This closes the loop: authority (§8.A) is gated by rungs;
  rungs accrue from fold track-record; the gateway gets better as it runs.
- **Glue lifecycle** — see "Glue pinned" above (boundary-legitimate,
  interior-smell, named+challenged, glue→fold via inference).

**Still open / yours:** the **arc name**; confirm/correct the glue definition;
veto any closure above. When the design is blessed, increment #1 (the guard)
is the obvious first cut.

## 12. §10 teeth — what would make this rot (non-examples)

- a `derive_type` that is a closure/vibe (unfalsifiable type);
- a gateway fold that can never refuse (a gauge, not a gate);
- capacity as a code constant instead of an admitted, re-dialable record;
- isolation without routes (multiplies orphans — the thing §3 forbids);
- authority without attribution (stats with no subject) or attribution without
  authority (a recorder that can't refuse);
- a fold chain that bottoms out in glue/mock instead of committed truth, or an
  unmarked span (§8.9 / §8.F);
- worktree-per-writer done as bare isolation (back to §3's orphan failure).

---

## 13. The particle mesh — the physics beneath the gateway (continued session, 2026-06-18)

**Provenance:** continued co-design (bdo + Claude), same day, extending §§5–7.
Where §5 named the *session* gateway as one seam, this section gives the
**general physics** every gateway is an instance of: what moves, how it moves,
and how it condenses into the nodes §6's folds run on. Coinages are bdo's unless
marked; the trichotomy (13.4), the self-summon floor (13.3), and the landing
diagnosis (13.6) are Claude's completeness sweep, flagged as such. PROPOSED — no
stamp it was not given. (This is the layer the **envoy package** carries out for
outside review — see 13.7.)

**13.1 The keystone (bdo).**
> A message is a typed particle with the capacity to become a node, based on its
> privileges and path. When a particle needs to become a node, it can summon or
> travel.

Wave/particle duality as architecture, and it snaps onto physics the repo
already speaks: condensation = *precipitate* (the emergent-determinism frame — a
node is a particle that has settled); dissolution = D-10 (a summoned node blinks
in, acts, dissolves, emits new typed particles). The cycle:
`particle → (summon|travel) → node → acts → dissolves → particles`. **Nodes are
temporary condensations; the mesh is what persists.** Identity is *earned by the
journey* — what a particle may condense into is set by its **privileges**
(cumulative monotonic policy) and its **path** (the gateways it crossed, the
policy it accreted).

**13.2 Typed movement; summon ⊆ travel (bdo).**
Gateways, routes, edges, travel are one thing: **typed movement through the
mesh/graph/fibers**. **Travel is the genus; summon is a species** —
condense-at-a-distance is still a traversal (a different edge type), as against
*travel-then-condense* (the particle moves to the destination and settles
there). Summon is **bidirectional and metered**: a node may summon a particle, a
particle may cause a summon — gated by **budget + threshold** (§7's contested
resource; nothing condenses for free). (Log-replay is movement along the
temporal axis — the same operator; parked.)

**13.3 The message is the one traveler; the gateway is a router (bdo).**
There are not two traveler classes (capability vs payload) — there is one
**message**, and *summon* is what a message **becomes** when routing decides it
needs a node. The gateway is therefore a **typed router**, not only a guard: a
message enters → routes → *might* be enqueued as a **summon queue item** → which
is itself a message that may route again (recursive).

**Self-summon (bdo), with its floor (Claude).** A message that arrives
under-specified can **summon itself** — spawn an agent with *discovery* options
to onboard its own context, then re-enter as a proper queue item. The floor that
keeps this from being a hole: by the monotonic rule, a self-summon **begins at
minimum capability — discovery-only (read/explore/ask, never mutate)**, and
"onboarding its context" *is* producing a **proposed** identity an authoritative
gate must admit before any acting power. Self-summon never self-grants; it
bootstraps a proposal. Loop-safety = **budget + monotonic shrink** (each
recursion strictly more fenced than its parent unless escalated, so depth bounds
itself).

**13.4 Typed messages — the contract at the door (bdo; trichotomy Claude).**
Every message is **typed at gateway entry**, and the type is a contract
declaring the **schema of data the message must carry** to route and act
(`chat-message` → {target session, content} → route+activate; `tool-request` →
that tool's request config). This reuses the door-validation discipline already
in the repo (the canvas validates a graph-spec against `SCHEMA` before render;
placements load only through a kind-mismatch-refusing gate). The type registry is
**governed vocabulary** (closed core + admitted extensions, like `loop/tags.py`;
an unknown type = `proposed` drift, promotable). A type binds
**{schema, route, ingress/egress policy}** as one registration.

A **typed-but-incomplete** message is handled by *which kind* of data is missing
(Claude's trichotomy): **discoverable** → self-summon to fill it; **must come
from the sender** → refuse with the missing fields named (carry-the-prompt error
UX); **needs the owner / escalation** → park and escalate.

**13.5 The mesh topology — graded trust by distance (bdo).**
How hard a crossing is scales with distance from origin: local neighborhood =
neighborhood policy + fiber logging (cheap); out into the mesh = a **gateway or
fiber-audit**; **re-entry, or reaching an authored (foreign) system = a mandatory
gateway** — standing, or a **summoned virtual gateway** stood up at the boundary
(the summon move applied to gateways). Gateways are **nested and directional**:
**ingress and egress carry different policy** at the same gateway; the **origin
is root**; policy is **cumulative and monotonic — never looser than already held,
unless an authoritative system grants escalation** (the mesh's `sudo`, the one
exception to one-way narrowing).

**13.6 The observation fiber — the afferent floor (bdo; landing diagnosis Claude).**
*Status: PROPOSED — and here the seed is real but the fiber is not, so the line
is drawn explicitly.* What **exists today**: `orchestrate.py` senses pressure and
holds **one** admitted setpoint (`max_inflight_atoms` / `human_queue_cap` /
`step_budget_per_tick`); the summon hook and `digest` already surface that
pressure **read-only**; `disposer.py` and `heal.py` are real downstream
actuators. What is **proposed**: the *fiber* generalizes that single seed — a
read-only sensor that **would** run through every surface, stamping each crossing,
deriving the queues and pressure, surfacing them compressed to a threshold, and
**never acting** (I-3; the surfacer sees, the actuator stays downstream). Where
today's control is **one** channel, the fiber proposes **multi-channel
competing-setpoint homeostasis** — "hold 5 tickets / 5 issues / 10 arcs",
thresholds derived from system files then tuned with the user, the channels
**contending for one bounded resource** (step-budget / inflight / attention) so
prioritization is forced instead of unbounded WIP. `orchestrate`'s single
setpoint is the proof the shape works at n=1; the n-channel fiber is still to
build.

**The landing diagnosis (Claude).** This names why *work grows but doesn't land*:
the loop today has **drain pressure (gates that refuse) without pull**.
Generation pressure ("always 5 tickets") + gates, with no through-line that
*pulls a batch to done*, manufactures WIP. The missing organs are the **pull** —
the cross-arc through-line (the **Anthology**, §5b, is its arc-tier form) and a
**bounded free-form lane** (an escalated-and-fenced summon scoped to a
neighborhood + through-line).

**13.7 What the package is for.**
All of the above is one claim: ontum is a **meta-agentic, closed,
user-configurable platform for authoring AI-worker systems** against a target
environment and use case — ambient/scheduled/habitual workflows composed from
primitives (agents, skills, tools, data sources), every act routed through the
gateway, observed by the fiber, self-healing, surfacing operational data at
**typed planes** (the platform *itself* / the target it's *pointed at* / the work
it *does*). ontum is **instance #1, pointed at itself** (dogfood); the platform
is meant to generalize. **The envoy package presents this vision as the subject**
and asks one sharp question: *why doesn't a through-line pull work to done, and
what three organs stand between here and the platform these pieces already
imply?*

**13.8 Still open (bdo's calls).**
- the **exact afferent/efferent seam** for self-heal (which deficits a
  deterministic actuator discharges vs. which summon a node);
- whether a particle may **choose to summon when it could travel** (to stay
  cheap / avoid disclosure) or is *forced* by privilege/path;
- whether "typed planes" is the three subjects above, the stack layers
  (config/infra/prompt/inference), or both crossed;
- the **anthology name** (still §12b's open) under which the session gateway and
  this physics land as chapters.

**13.9 §10 teeth (additions).**
- a router whose outcome set is open (inference inventing actions beyond
  `{deliver, enqueue-summon, self-summon, escalate, deny, dead-letter}`) —
  unauditable routing;
- a self-summon that self-grants acting capability (bypasses the monotonic floor);
- an observation fiber that *acts* (collapses sense into actuation — the I-3
  violation);
- a message type whose schema is not validated at the door (a contract that can
  never refuse);
- competing setpoints that don't share a bounded resource (independent
  thermostats = unbounded WIP, the failure this whole layer exists to end).

## 13.10 The gateway economy (envoy review + bdo co-design, 2026-06-18)

**Provenance:** the foreign-reviewer pass on the `landing-throughput` envoy
package (logged as `epic.landing-throughput-response`) proposed promoting each
gate into a **gateway** (guard policy + judgment + patrol + discharge route);
bdo's co-design then gave the gateway its **actuator** and its **economy**. Both
strands are queued as value-gated atoms under that arc; this subsection is their
design home. PROPOSED.

**Gate → gateway → patrol → actuator.** A *gate* answers "does this work pass?" A
*gateway* answers "may this actor move this work across this seam, under this
policy, at this capacity, with this audit trail — and what route happens next?"
The **actuator is the gateway enforcing an ambient threshold** (a homeostatic
setpoint), and it enforces *both ways*: **shed/quarantine** the excess, and
**fill the void** — a sub-setpoint absence (a vacuum) is a generation trigger,
not just an idle state. This is the §13.6 fiber's competing setpoints given a
hand: the gateway is where a threshold *acts*.

**The patrol** is a **scheduled surfacer over a bounded location, composed of
surfacers** (a surfacer-of-surfacers, §6's fold recursion scoped to a seam). It
finds work near its gateway and **routes it by state**, reports activity, **logs
threshold use**, and **detains bad actors** — where "detain" is *reversible
quarantine* (a hold that removes from flow but issues **no verdict**) and "route"
is *present-to-gateway* (the gateway decides). So the I-3 sense/act line holds:
**the patrol may quarantine and present, never judge.** Temporally distinct from
the gateway: the gateway is level-triggered (every pulse, silent unless deficit);
the patrol is the **scheduled/ambient/habitual workflow** of §13.7, pointed at a
seam. The patrol's load-bearing signal is **passed-but-unpulled** work — the
current failure mode the existing surfaces (which watch refusals) miss.

**Pull is workflow-as-code.** What a gateway pulls *on* (arc vs slice) is the
wrong axis; **where/how/when it pulls are inferred per case from exemplars**,
bounded by the gateway's enumerated routes + environmental policy (the §13.9
closed outcome set; BOUNDED is load-bearing). The behavior is **workflow-as-code:
composed from configuration, compiled by composition (the `@`-import scope-stack
generalized), routed through a gateway** — the inference-as-composition layer
made the engine of pull (re-derive *behavior* just-in-time within bounds, the
inference-sibling of the fold's re-derive *state*).

**The contribution economy.** Contribution accrues **wealth**; wealth is policed
into **policy/privilege** ("policy policed by wealth of contribution"); anything
**spending or gaining disproportionate value is inspected** (the loop's
anti-money-laundering). It **wires on folds that exist — no new currency**:
`impact.py` is the value/wealth meter (field weight by *settling*; it already
*refuses mercury* = fake value) and `energy.py` is the cost/spend meter (strain).
"Disproportionate" is an anomaly over impact (gain) and energy (spend); the
inspection it triggers is a patrol on the value seam.

**Exemplars and notorieties — two derived poles.** The bank starts at zero but is
**not** a cold-start, because an exemplar is *defined and derived*, not
waited-for:

- **Exemplars** (good, to share/emulate) are **derived by folding over agents'
  impacts and efforts at gateways** — so *exemplar ≠ landing*, and the stalled
  arcs (effort on the record, zero landings) are **not exemplar-dark**.
- **Notorieties** (bad) are **derived from witnessed violation of policy and of
  priors**, plus **untidiness** (disorder — stranding, churn, *and* the
  assumed-monster named before proof).
- **The negative pole *generates* the exemplar definitions by inversion** — the
  grip discipline made generative: the witnessed non-example *is* the frame of
  the example. The **positive fold populates** the bank; the two poles compose
  (negation alone gives only "not-bad"). The **violation stream re-derives** the
  definition (the §12b freshness rule applied to definitions — never frozen, so
  it can't settle into a lie). The definitions of exemplar *and* boogeyman are
  themselves **versioned, refusable, gated atoms** (like `derive_type`, §10.1) —
  never self-asserted.

**The boogeyman lifecycle — star-chamber-proof by category.** A *boogeyman*
(assumed-bad, **named before proof**) is filed as **untidiness** — the same shape
as a **ghost** in the term economy (a claim whose backing doesn't resolve). Three
states, all worked by the patrol: **named-before-proof** → untidiness → *surface
+ inspect, never detain*; **witnessed violation** → hard notoriety → licenses
*reversible quarantine*; **rehabilitated/dissolved** → the notoriety superseded
(history intact, §-invariant), or the stale accusation *cleaned* as the disorder
it was. Naming a monster is permitted; a name alone is *mess*, never grounds to
detain — it must graduate by proof or be swept up. No one is detained on a vibe.

**§10 teeth (this subsection).** A patrol that judges (collapses sense/act); an
exemplar/boogeyman definition that is self-asserted instead of gated; an economy
minted as a new currency instead of folded from `impact`/`energy`; a void-fill
that manufactures work to hit a vanity number (fake tickets = mercury); a
notoriety that detains on assumption rather than witnessed, reversible evidence
(the star chamber).

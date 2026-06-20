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

**The three A's (bdo, 2026-06-19).** Stated as a property rather than a
mechanism, a session is born **authenticated, authorized, and attributed** —
and *attributed* carries both senses on purpose. The session is **given its
attributes** (the binding *is* the attribute set — workspace, branch, rung,
claim, routes, capacity) **and** each attribute is a **signed record**
(`--by`, `ts`, `supersedes`) that the session's every future act attributes
back to. These are not two steps but one act: an attribute that is not
attributed — asserted, on the record, by someone — is exactly the failure this
arc fights, the inferred or self-asserted state (the current branch read from a
shared HEAD; the merge-node's unadmitted landings). The load-bearing word is
**given/asserted = not inferred**: you cannot attribute what you inferred, so
the no-inference rule of §2 falls out as a *consequence* of attribution rather
than a separate axiom. The three A's are the governance spine of §8 (authority
+ attribution) in session-birth form — authn + authz = **authority** ("may
you"), and attributed = **attribution** plus the very attributes that authority
granted.

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

**The standard is generative, capability-indexed, and self-updating — which puts
it in a feedback loop with the thing it judges.** Ambient operations need
something to *imagine against and compare against*: not a frozen catalog of
golden runs (a stored instance rots the moment it is frozen — the §12b freshness
failure, mercury at the example level), but a **generative quality standard** — a
*quality-control manual* an op can generate the expectation from ("what would
smooth action of the teeth look like *here*, in a case never seen?") and then
score the actual against (the oracle / val_bpb move, the latent structure being
*smooth operation* instead of a sentence's mesh). This **hoists** the
exemplar/notoriety poles: the manual is the generative *type* (a versioned,
refusable, gated atom, the `derive_type` shape); an exemplar is one *instance*
drawn from it, the meters score conformance, and the patrol *infers over the
gap* with freeform creativity. Three layers: the manual (generative definition),
the meters (`impact`/`energy`/`heal` — measure deviation), the inference (the
patrol, creative within bounds).

Because the system keeps *offering new capabilities*, the standard cannot be
static — expectation must rise to meet capability, so the standard is **regulated,
re-derived from current events, and inferred over** to keep meeting expectation.
But a standard that is derived from the operations it governs *and* judges them
has one dominant failure: **the bar becomes a mirror** — it rises to whatever the
system already does, so the teeth never bite (the §10 failure lifted from one
verdict to the whole standard). The fix is to break the loop deliberately, with
**insulation** (controlled, lagged coupling — they talk through a buffer) where
the standard must track capability, and **airgaps** (a hard break — no direct
channel may exist) where a path would let the judged corrupt the judge.

*The issues (hazards in the self-updating standard):* **mirror drift / grade
inflation** (derived-from + judges → self-justifies); **capability-laundering**
(a capability that can't meet the bar triggers a bar *edit* so it passes, instead
of being refused — the AML problem at the standard seam); **who-judges-the-judge**
(the inference that updates the standard is itself an operation; scored by the
standard it produces, it signs its own line); **lag in the wrong direction**
(standard outruns proven capability → aspiration-as-bar → autoimmunity; or lags
it → ungoverned frontier borrowing unearned trust — the rated-zone-vs-frontier
hazard); **retro-invalidation** (an update silently re-judges settled work);
**frozen-vs-fresh tension** (the manual must stay fresh, but the bar a piece was
*already judged against* must stay stable).

*The airgaps (hard breaks — no direct channel):*
- **AG-1 · operation ⟂ standard-setter.** The node whose operations a standard
  governs cannot set or update that standard — *no-one-signs-their-own-line* /
  D-2 / merge-node applied to the rubric. The standard-update is itself a gated,
  refusable, versioned atom.
- **AG-2 · capability-admission ⟂ standard-update** (the load-bearing one).
  "We can now do X" lands on one seam; "X is the new normal of good" moves on a
  *separate, separately-authorized* seam. No path may exist from *wanting a
  capability to pass* to *the bar moving in the same breath*. This is the
  anti-laundering gap.
- **AG-3 · inference-fill ⟂ the bound.** The standard splits into a **bounded**
  part (settled, owner-stamped) and a **fresh** inferred part; the inference
  ranges freely *inside* the bound but has *no channel to move the bound* —
  moving the bound is a separate gated act. This is the airgap that keeps
  freeform creativity from drifting into self-justification.

*The insulations (buffered coupling — coupled, but damped/lagged):*
- **IN-1 · capability → standard, with a deliberate lag.** Coupled (the standard
  *tracks* capability), but through a damper: it moves toward *proven* capability
  (evidence on the log), never toward announced/aspirational capability. The lag
  is the buffer against autoimmunity-vs-frontier.
- **IN-2 · events → standard, through the settled fold.** The standard re-derives
  from the *append-only log fold* (truth, immutable), never from the live
  in-flight operation — so operations cannot steer their own standard by writing.
  (The loop's deepest pattern: the log is truth, everything else is a fold.)
- **IN-3 · meter ⟂ interpretation.** The meters stay dumb (measure raw reality);
  the standard interprets. One organ that both measures and sets the bar can move
  both to pass — keep them separate.

*The governance spine (who owns what — authority + attribution, mapped onto the
disposer fence):* the **bound** is bdo's stamp (he draws the envelope — how far
the standard may move, what "expectation" may legitimately include — as
`disposer admit-fence` draws per-dial bounds); the **fill** is inference
self-admitting *within* the bound, citing the fence as `authorized_by` (the loop
executes the stamp, never signs its own line); an **out-of-bound** move cannot
self-admit and surfaces to bdo. Versioning resolves the retro-invalidation and
frozen-vs-fresh hazards: the standard versions forward like a node prompt (§7) —
the hash rides the receipt, a new version lands as history, old verdicts stand.

*§10 teeth (this subsection).* A standard derived from the live operation instead
of the settled fold (IN-2 breached → steerable bar); a standard-update admitted
by the node it governs (AG-1 breached → self-sign); a capability that passes by
editing the rubric in the same act (AG-2 breached → laundering); an inference
that moves its own bound (AG-3 breached → self-justification); a frozen catalog
of golden runs sold as the standard (the example-not-manual failure this
subsection exists to refuse); a standard that has never refused an operation
(mirror drift — the §10 self-test, the bar that could not have been a reject).

*The one open dial:* **IN-1's lag** — how tightly the standard should trail
proven capability. Too tight is autoimmunity; too loose is the ungoverned
frontier. That envelope is bdo's to set (it is itself an AG-3 bound). Everything
else above reuses patterns already on disk.

*Pressure-test (diverge-judge panel, three independent skeptics, 2026-06-18).*
AG-2 **as first written leaks**, and the panel converged on why and the fix:

- **It only blocks same-*breath* laundering.** The patient path survives: admit a
  sub-bar capability X on the capability seam (AG-1 clean); let ambient ops *run*
  X over the lag window so it accrues log-evidence; then re-derive the standard
  from the settled fold (IN-2 clean) where IN-1 reads X as "proven capability" and
  legitimately raises the bar to bless it. The insulations *are* the laundromat;
  the lag is a low-pass filter, not an airgap. This is the temporal form of the
  same "mirror drift" the subsection lists separately — they are one failure.
- **The fix (two skeptics, one mechanism): IN-1 must track *blessed* capability,
  not *exercised* capability.** The deriving fold may count X as "proven" only via
  a receipt showing X **passed the standard-version in force at its admission** (a
  pass-receipt), never merely that it *ran*. A sub-bar X then produces no
  pass-receipt, so no later fold can launder it in. This converts AG-2 from a ban
  on a "same act" (unenforceable — motive isn't on the log) into an **eligibility
  gate on what the standard-deriving fold may see** (enforceable — pass-receipts
  are on the log).
- **The breach is *not* silent** — the earlier note was wrong. Because the rubric
  is §7-versioned and `prompt_hash` rides every receipt (`loop/node.py`), a
  laundering bar-move shows as a **verdict-flip-without-work**: same `artifact_id`
  (work unchanged), same judging node, `prompt_hash` moved H1→H2, verdict flipped
  refuse→accept, and *no offsetting new refusals* elsewhere — a legitimate rise
  bites *harder* (leaves new refusals), laundering only *admits*. This is a pure
  fold, the sibling of `retro`'s churn and `digest`'s divergence, and I-2 helps:
  the pen refuses to re-judge the same `(node, artifact_hash)`, so a launderer
  must mint a new version, which surfaces in the version-split. Give AG-2 teeth by
  the **disposer shape**: a standard-update self-admits within bdo's fence *only
  if* it flips no settled refusal for unchanged work; a flip is an out-of-bound
  key and escalates the whole move to bdo.
- **Honest residue: greenfield laundering.** A brand-new capability never
  previously refused has no settled refusal to flip, so the verdict-flip fold
  finds nothing (`impact.py`'s own limit: absence is not lightness). Against
  *prospective* laundering — authoring the bar around an untested capability —
  AG-2 is only insulation-strength, governed by IN-1's lag, which is bdo's open
  dial. AG-2 is **airgap-strength against retroactive laundering, lag-strength
  against greenfield** — and should claim only that.
- **Right-size the frame (third skeptic).** AG-2 is the *one* genuinely new
  invariant here — anti-structuring: two correctly-signed acts may not be fused
  into one authorization (distinct from AG-1's no-self-sign and IN-1's
  content-coupling; it decouples the two *acts*). The other five hazards and
  AG-1/AG-3/IN-1–3 are existing invariants at standard scale (D-2, log-as-truth,
  the disposer split, §7 versioning, the §10 self-test). And the self-updating
  *engine* is **premature**: no ambient ops at scale exist yet (the economy,
  patrol, and poles are all still PROPOSED). The minimal build the evidence
  supports today: a **§7-versioned rubric atom a gated node bumps**, carrying the
  AG-2 eligibility gate and the verdict-flip check; add the disposer auto-admit
  *fill* only when the owner-stamp volume is witnessed on the log as a bottleneck
  (the system's own evidence-before-build rule).

*Self-healing — the litmus that keeps it the right side of every airgap.* Teeth
without a healing reflex is autoimmunity (`heal.py`'s founding line), so this
standard must heal itself — but only one *kind* of healing is admissible. The
litmus is a single question: **does the heal act *inside* the bound, or move the
bound?** Healing that takes a *reversible* corrective act within bdo's fence
(quarantine a suspect bar-version, re-derive within the envelope) and escalates
anything that would exceed it is the disposer shape — admissible, the boogeyman
lifecycle's "witnessed violation → reversible quarantine" applied to the standard
judging *itself*. Healing that resolves the deficit by *lowering the bar to stop
the pain of refusals* is anesthesia — it **is** mirror drift / capability-
laundering (AG-3 breach), the failure this subsection refuses. So the standard
self-heals *toward more honest biting, never toward less*. The organ is three
pieces, two already real: `heal.py` (the bite-axis sensor), a new
**verdict-flip-without-work** detector (a fourth `heal.py` detector — same `Fold`,
version-split, and propose-only contract as its siblings; greenfield today, a
sensor-before-the-load like `heal`'s own flapping/override), and the disposer
fence (the bounded actuator, when the bottleneck is witnessed). The sensor ships
read-only and propose-only; it never clears a park or moves a bar — the heal stays
a session's or bdo's (D-4).

## 14. The registration-and-repair gateway activity (bdo, 2026-06-19)

**Provenance:** co-designed in conversation (bdo + Claude), 2026-06-19, triggered
by a *live* recurrence of §1 — a session (this one) built a whole confirmed-arc
slice (`epic.diagram` wave 1) directly in the **stranded primary viewport**
because nothing forced the work into its own container first. The diagnosis bdo
asked for named the root cause precisely; this section is his fix for it. The
organ-mapping and the §10 teeth are Claude's completeness sweep, flagged as such.
PROPOSED.

**The sharpening over §5/§11.** §5's gateway is a level-triggered *sense* + a
deterministic-or-inference *route*; §11.1–2 give the *guard* (refuse a commit on
an unbound HEAD). All of that would have **bounced** this session's first write —
but bouncing leaves the *actual* root (a viewport a prior mortal session left
stranded off `main`) sitting there for the next session to inherit and re-trip. A
static tooth fixes the symptom. bdo's reframe: the gateway is an **activity**, not
only a guard — it **registers a worksurface to a user, alerts when a session ends
up in the wrong environment, and investigates and repairs the root cause.** A
MAPE-K loop at the session seam, three phases, each composing an organ that
already exists (no double-build, §10):

- **Register** (worksurface → user) — the claim↔workspace binding (§11.2,
  `loop/workspace.py` + the git-pen `--claim`, done-line 0121), elevated from an
  optional flag to a **gateway registration act at session entry**. The binding
  *is* the attribute set of the three A's (§5, "attributed").
- **Detect + alert** (wrong environment) — a fold of *registered claim* vs
  *actual* (HEAD, cwd, git toplevel, **owner**). Divergence ⇒ wrong env. The
  HEAD-intent guard (done-line 0118) is the *point-check* of this; the activity
  makes it the **ambient, every-pulse** check the summon hook already runs.
- **Investigate + repair** (root cause) — `heal.py`'s bite-axis fold (*proposes*
  the repair, propose-only by D-4) + the git-pen `sync`'s stranded-viewport
  restore (*executes* the safe case) + branch dissolution (the gardener's route
  home). The activity is the loop that binds sense → propose → execute into one
  beat, and aims at the **cause** (the stranding) not the symptom (this write).

**The insight in "to a *user*."** The worksurface belongs to the **user**, not the
session. The viewport is bdo's — a *reading* surface, parked on `main`; a
**session** gets a *workbench*. So "wrong environment" has a precise definition: a
session operating in the user's viewport (exactly what recurred here), or two
sessions colliding on one bench. This is the membrane architecture's
external/internal line drawn at the session seam — the user's surface vs the
session's container — and it is *why* registration must bind to `(user|session)`,
not to a bare HEAD.

**The open owner decision — the bounded-repair fence.** Repair that restores a
*clean* stranded viewport or dissolves a *merged dead* branch is reversible and
safe — auto-do it (the `sync` hook already does this much). Repair that **moves
uncommitted work** is high reversibility-cost — auto-doing it can destroy work. So
the activity must split: **auto-repair the reversible, escalate the work-bearing.**
That split is the disposer-fence shape (a bounded standing auto-admit bdo stamps
once, per-case bounds) applied to repair — and it is the concrete form of bdo's
standing open question across this arc (bounded-autonomy regulation vs.
escalate-every-policy). *Lean (Claude): bounded-auto within a fence bdo draws —
the third application of a shape already proven by the disposer and by `sync`'s
safe-restore — escalating only the cases a repair would lose work.* The lag/extent
of auto-repair is bdo's dial, the §13.10 IN-1 shape at the session seam.

**Where it sits in §11.** It is not a new increment so much as the *binding* of
#2 (claim↔workspace), #3 (the gateway fold), and #4 (provisioning + gardener
reclaim) into one level-triggered activity — buildable only after #2's record
shape (§10.4) is chosen. The first cut is the alert (sense), which ships the day
#2 lands; repair (execute) waits on the fence stamp.

**§10 teeth (this section).** A registration that stays advisory instead of
enforced (the exact failure that recurred here — a ritual a session must
remember); an activity that only *alerts* and never repairs the root (back to
symptom-bouncing — the next session re-inherits the stranding); an auto-repair
that moves uncommitted work without escalation (destroys work — the orphan failure
of §3, inverted); auto-repair outside a fence (unbounded autonomy — the
escalate-everything question answered by *not* answering it); a "repair" that
heals toward *less* friction by abandoning the binding rather than restoring the
environment (anesthesia, the §13.10 litmus — heal toward more honest insulation,
never less).

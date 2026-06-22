# Partition · ranking · deferral plan

The harsh requirement, partitioned and ranked. Per bdo (this session):
nothing is dropped without a deferral plan, and every deferred partition
has an opened session.

## Decisions locked

- **Documents are a new parallel `spec` particle** (Q1). Not code atoms,
  not loose prose. A `spec` (arch diagram · requirement · user story ·
  expectation · suggestion) carries its own identity, versioning, gates,
  and lifecycle — a *sibling* of the atom pipeline, sharing the log and
  the pen/gate machinery but with its own stage table and its own
  "soundness" gate.
- **The mesh is a projection anchored by a log pointer** (Q2, bdo's
  words). The log stays truth (D-8). A record holds a *pointer* to a
  graph; the graph is a *projection* of a logged file; the system that
  made/requested the graph is itself logged. Recursive projections,
  every one anchored to a log pointer. This is "Records is pointers"
  operationalised — a pointer may point to a graph-projection — and it
  needs **no second store**.

## Partitions

| id | partition | grounded state today |
|---|---|---|
| **P1** | **Spec particle** — documents as versioned, gated, refactorable particles; the spec→atom link so an edited requirement flags the atoms that serve it | prose only; `.ai-native/proposals/` editable, no identity/gate (issue: a landed atom can't know if its requirement is current) |
| **P2** | folded into P1 — refactor/version + cross-link invalidation engine | — |
| **P3** | **Projection mesh** — log-pointer → graph projection; spec↔atom edges traversable as a live fold | graphs exist as read-only after-the-fact folds (`consequence_graph`, `term_economy`) + isolated canvas; not loop-walkable |
| **P4** | **Spec SDLC** — lifecycle stages for specs (draft → review → version → supersede), reusing the pipeline | atom pipeline real (`reconcile.PIPELINE`); no spec lifecycle |
| **P5** | **CI/CD + environment controls** — extend Actions beyond the lone atom-invariant gate; session-gateway bind-at-birth | one Action (`atom-invariant.yml`); fence/guards real; session-gateway only proposed (#534) |
| **P6** | **Virtual fleet + Administrator agents** — `fleet.py` eyes, Administrator→Conductor→Agents, control settings, authority dial | `epic.virtual-fleet` defined; blueprint on a branch; `fleet.py` is a ghost on main (#548); needs bdo confirm |

## Ranking & tiers

- **NOW — P1.** The harsh requirement's core, and we are *about to author
  many documents* (the `grammar/` files, requirements, stories). P1 puts
  them under version + refactor control from day one — `grammar/*` become
  the first specs. Dogfood before scale.
- **NEXT — P3 (minimal) + P4.** They close P1's loop: the spec→atom
  invalidation link needs the projection mesh (P3); refactor needs the
  lifecycle stages (P4). Minimal P3 = a log pointer to a spec-graph
  projection + the spec↔atom edges; the full traversable mesh rides later.
- **DEFERRED — P5, P6.** Real, but they *serve/manage* what P1–P4 produce,
  so they sit behind them; P6 also gates on your Administrator confirm
  (frame · name · authority dial). Deferral plans below; sessions opened.

Rationale = blueprint-first + dogfood + unblock-order. Nothing here is a
drop.

## Deferral plans (nothing dropped)

### P5 — CI/CD + environment controls  · DEFERRED
- **Why deferred:** the spec-gate and spec lifecycle (P1/P4) must exist
  before CI has a spec check to run; multi-env promotion has nothing to
  promote until specs+atoms compose an SDLC. Independent value (test
  automation) is real but lower-leverage than closing the doc gap.
- **Unblocked when:** P1's spec-gate exists (so CI can run it) and P4's
  lifecycle defines the stages CI enforces.
- **Dependencies:** P1 (spec-gate), P4 (lifecycle), `.github/workflows/`
  pattern from `atom-invariant.yml`, `fence/policy.py`,
  `session-gateway.proposal.md` (#534).
- **Session opened:** [deferral-p5.md](deferral-p5.md) — full build
  blueprint + pickup, authored by an opened background session.

### P6 — Virtual fleet + Administrator agents  · DEFERRED (also needs bdo confirm)
- **Why deferred:** the fleet *manages* work-particles; until P1–P4 give
  it specs+atoms to conduct, the management layer has thin material. The
  Administrator blueprint also awaits your confirm (frame · name ·
  authority dial) — a D-4 gesture, not a build.
- **Unblocked when:** you confirm the Administrator frame, AND P1–P4 give
  the fleet first-class particles to conduct.
- **Dependencies:** bdo confirm; `epic.virtual-fleet`; the ghost
  `fleet.py` (#548); herald/trust/spawn-rail (real); the existing control
  dials (setpoints · disposer fence · act-fence).
- **Session opened:** [deferral-p6.md](deferral-p6.md) — full build
  blueprint + pickup + the exact confirm gestures, authored by an opened
  background session.

## Immediate next (the priority)

P1's **bundle first** (blueprint-before-build, the hard rule): full shape
→ categorised concept-list → CTAs against the purpose, *before* any spec
code. This `plan.md` is itself the first thing that wants to *become* a
spec once P1 lands (the dogfood test). That bundle is my next deliverable.

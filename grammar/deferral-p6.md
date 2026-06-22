# P6 — Virtual fleet + Administrator agents · DEFERRED build blueprint

**Status:** PROPOSED blueprint only. No code, no build. Deferred behind
P1–P4 *and* gated on bdo's confirm (frame · name · authority dial — a D-4
gesture, not a build). This file exists so the deferred work is not dropped
([plan.md](plan.md) §"Deferral plans"). It composes existing machinery; it
invents none.

Grounding read this session (read-only): `epic.virtual-fleet`
([.ai-native/epics/epic.virtual-fleet.json](../.ai-native/epics/epic.virtual-fleet.json));
the Administrator blueprint on branch `claude/conductor-blueprint`
(`administrator.proposal.md`, `.ai-native/atoms/atom.administrator-blueprint.v0.json`,
concept list C1–C7); `loop/herald.py`, `loop/trust.py`,
`.claude/hooks/spawn_guard.py`, `loop/act_fence.py`, `loop/orchestrate.py`,
`loop/slowloop.py`, `loop/disposer.py`, `loop/field.py`, `loop/merge.py`.

---

## 1. Purpose

P6 makes the loop **staff and steer itself**: a declarative virtual fleet —
the mortal sessions, branded judges, landers, and model backings that move
atoms (and, post-P1, *specs*) through seams — managed by **Administrator**
agents over the existing **fast/slow loop**, reading a **meshed graph
substrate** that is a *projection* anchored by a log pointer (Q2,
[plan.md](plan.md):16–21; the log stays truth, D-8). bdo declares the shape
of the workforce once; the system keeps reality converged to it — open
summonses get judges, landable PRs get a lander, down minds get restarted,
over-capacity is refused by the same record that declared it
(`epic.virtual-fleet` value, line 7). The Administrator reads the fleet whole
and dispatches one governed launch per unit; owner-gated items escalate, never
auto-launch (`administrator.proposal.md` §2). Managing sessions stop being the
workers — the conductor steers, the fleet plays.

## 2. Scope — the concrete pieces (mapped to C1–C7 and `epic.virtual-fleet`)

The Administrator concept list (`administrator.proposal.md` §8) and the epic's
four pieces are the **same arc at two altitudes**. The mapping:

| C-piece (role) | epic piece | composes (real today) | new? |
|---|---|---|---|
| **C1 fleet-fold** — the *eyes*, read-only | `atom.fleet-plan.v0` | `loop/field.py` occupancy rungs (`field.py`:42 `RUNGS`), `digest`/`census`/`heal`/`gaps`/`activity`/`watcher`, `loop/merge.py` landables (`merge.py`:79 `readiness`), `herald` roster | the join fold — **foundation** |
| **C2 per-item launch recommendation** — pure, no action | `atom.fleet-plan.v0` | rides C1; the "one apply step that converges it" per diff (epic piece glue, line 11) | derived field on C1 |
| **C3 the launch loop** — the *hand*, governed + receipted + idempotent | `atom.fleet-apply.v0` | the spawn rail (`spawn_guard.py`:47 `ontum-node:<id>`), `trust.permits` (`trust.py`:90), `inference_queue` concurrency dial, the runs ledger | the provisioner pen |
| **C4 the Conductor role** — per-unit driver, branded | `atom.conductor.v0` | a session/spawn the rail fills; generalizes tonight's hand-conducting (`administrator.proposal.md` §11) | a branded node prompt (`.ai-native/nodes/`) |
| **C5 the authority dial** — standing-authorized vs escalate | (governance for `fleet-apply`) | `loop/act_fence.py` tiers (`act_fence.py`:67 FORGIVENESS/PERMISSION/FORBIDDEN), `disposer` fence shape | bdo-signed admission |
| **C6 owner oversight surface** — fleet glance, arc-first | (the conductor's read, epic horizon) | `digest`/`web` render, `field.py` topology | a render over C1 |
| **C7 reputation feedback** — launched-agent outcomes → reputation | (closes the mesh) | `herald` reputation fold (`herald.py`:11 — standing is a fold, earned forward) | edges only, no new engine |

Most cells **compose existing real machinery**; only C1 (the join), C3 (the
provisioner pen), C4 (a node prompt), and C5 (one admission) are genuinely new,
and each is a fold or a pen in the established grain — no second source of truth
(§10; `administrator.proposal.md` §2, the rule Causality lives by).

The **fast/slow loop** is the fleet's clock: C3 rides the Stop hook the way
`reflect_auto` does (`atom.conductor.v0` glue, line 13) — `orchestrate`'s
admitted setpoints (`orchestrate.py`:36 `SETPOINT_KEYS`) are the capacity caps,
`slowloop` proposes dial moves from outcomes, `disposer` disposes the in-fence
ones. The fleet is one more occupant-set those same dials budget.

## 3. The bdo confirm gates (decide first — D-4 gestures, not builds)

P6 cannot start until **all three** land. None is a build; each is one
authorizing gesture (`administrator.proposal.md` §9, CTA-1/2/3).

1. **Frame** — confirm the projection-plus-governed-loop frame and the
   three-tier model (Administrator → Conductor → Agents), never a second
   authority. Gesture:
   `python -m loop.node confirm-arc --epic epic.virtual-fleet --by bdo`
   (the arc's standing stamp for every piece under it — the loop then satisfies
   the owner-stamp on his confirmation; `loop/CLAUDE.md` invariant).
2. **Name** — pick **Administrator** (recommended; "Controller" collides with
   `orchestrate` already being the *control* loop — `administrator.proposal.md`
   §0) or Controller. This is a wording decision; it rides the same confirm
   comment / arc-intake skill, no separate pen.
3. **Authority dial** — draw the fence that bounds what C3 may launch unattended
   vs what escalates. Gesture (the act-fence draw verb,
   `act_fence.py`:352):
   `python -m loop.act_fence draw-fence --forgivable <scope-tags...> --by bdo`
   — e.g. summon-a-named-judge and run-a-down-mind-converge as FORGIVENESS;
   anything owner-gated (`confirm-arc`, `admit-real`, drawing a fence) is
   FORBIDDEN to self-admit by construction (`act_fence.py`:81). Drawing the
   fence is itself an owner gesture, FORBIDDEN to self-admit (`act_fence.py`:185).

Until all three exist on the log, C3/C4 stay inert; C1/C2 (read-only) may be
built but provision nothing.

## 4. Dependencies / unblock condition

Unblocked **only when**: bdo confirms (§3, all three) **AND** P1–P4 have given
the fleet first-class particles to conduct ([plan.md](plan.md):66–75). Concretely:

- **P1 spec particle** + **P4 spec SDLC** — so the fleet has *specs* as well as
  atoms to staff seats for; the management layer has thin material until then
  (the deferral rationale, `epic.virtual-fleet` context).
- **P3 projection mesh** — the "meshed graph substrate" C1 reads is the
  log-pointer→graph projection; without it C1 falls back to flat folds. Minimal
  P3 (the spec↔atom edges) is enough to start; the full traversable mesh rides
  C6.
- **Real today (no wait):** `herald`/`trust`/spawn-rail; the control dials
  (`orchestrate` setpoints · `disposer` fence · `act_fence`); `field.py`;
  `merge.py`. The **ghost** to resolve: `loop/fleet.py` is named but **not
  landed** (issue #548) — confirmed this session *not* present on
  `claude/conductor-blueprint` or `claude/agent-training-run`. C1 is its first
  real landing, not an edit.

## 5. Build CTAs (ordered, categorized — foundation first)

> **Foundation** before **hand** before **steering**. Each cites the machinery
> it reuses; each is atom-backed and §10-tested (a fabricated row / ghost launch
> refused), in the `loop/gaps.py`/`census.py` grain.

- **CTA-1 · foundation · C1 fleet-fold** — build `loop/fleet.py` (resolve the
  #548 ghost): a pure read-only fold joining `field.py` occupancy + `merge.py`
  landables + `census`/`gaps`/`heal`/`watcher` + `herald` roster into one map of
  every unit/agent/block. Writes nothing. **Build first** (`administrator.proposal.md`
  CTA-4; epic `atom.fleet-plan.v0`).
- **CTA-2 · projection · C2 per-item recommendation** — derive, per diff, the
  single governed launch that converges it (the spawn the summons names, the
  mind-converge a down backing needs, the merge-node when landables exist).
  Pure; rides C1 (epic `atom.fleet-apply.v0` glue, read half).
- **CTA-3 · pen · C3 the launch loop** — the provisioner pen: one converging
  step per invocation through existing rails only, each provision a receipt on
  the runs ledger citing the declaration that wanted it; bounded by
  `trust.permits` + the `act_fence` dial + `inference_queue`; level-triggered and
  idempotent (re-fire = I-2 no-op, like the drain). A seat the ladder refuses is
  reported drift, never an escalation of privilege (`atom.fleet-apply.v0` glue, line 12).
- **CTA-4 · declaration · `atom.fleet-declaration.v0`** — desired occupancy as
  bdo-signed admitted records (which seat under which condition; caps from
  setpoints; the trust ladder as the ceiling). The vocabulary is `field.py`'s
  occupant rung (epic piece, line 10).
- **CTA-5 · role · C4 Conductor** — a branded node prompt in `.ai-native/nodes/`
  for the per-unit driver; the ambient beat candidate wired like `reflect_auto`
  on Stop (`atom.conductor.v0`).
- **CTA-6 · surface · C6 oversight + C7 reputation** — the arc-first fleet
  glance (render over C1, sibling of `digest`) and the launched-agent-outcome →
  `herald` reputation edges (no new engine). Last, after the loop converges.

Increment law (`loop/CLAUDE.md` §9): one real node at a time — no second until
the first carries a passing receipt. C1 before everything.

## 6. Pickup (the exact first move for a future session)

1. **Check the gates are open** — confirm on the log that bdo has (a)
   `confirm-arc`'d `epic.virtual-fleet`, (b) named it, and (c) drawn an
   `act_fence` (`python -m loop.node arcs`; `python -m loop.act_fence`). If any
   is missing, **stop** — surface it as `needs-you`, do not build (D-4).
2. **Confirm P1–P4 landed** — specs + the projection mesh are real on main; if
   not, P6 stays deferred (re-read [plan.md](plan.md) ranking).
3. **Then, and only then, CTA-1** — open a `done/` line for the C1 fleet-fold,
   branch `claude/fleet-fold`, build `loop/fleet.py` as the read-only join
   (resolving ghost #548), with a §10 test proving the fold refuses a ghost
   occupant / fabricated diff. Requisition the independent review, ready the PR
   for the merge-node. Eyes before hand.

---

*Propose-only. This blueprint builds nothing and authorizes nothing; every
downstream organ is gated by bdo's confirm of the frame and the dial (D-4). The
blast radius of a wrong blueprint is a revised blueprint
(`atom.administrator-blueprint.v0` `cost_of_wrong_call`).*

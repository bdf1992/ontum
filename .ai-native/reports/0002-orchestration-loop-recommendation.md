# Session report 0002 — recommendation: the orchestration loop

- **Date:** 2026-06-10
- **Session:** Phase 1 worker, recommendation pass (continues 0001's `done`)
- **Branch:** `claude/friendly-allen-occrt3` (bdo merges — D-4 applied to git)
- **End-state:** `report` — a recommendation, not a build. Nothing in `loop/`
  changed; phase-1 stays at its passing receipt (§9.3).
- **Doctrine:** `ai-native-loop-substrate.md` v0.4.0, authoritative, unedited
  (§12: a recommendation is not a doctrine edit).

This report answers one question: **over the primitives we now have, what is
the orchestration loop the spec calls for?** It recommends a shape, names what
must change to reach it, names what must not change, and proposes the single
smallest next version. It builds nothing — per §11 the orchestration concerns
are explicitly "not in scope yet," and per §9.3 no second real node lands
before the first has a passing receipt.

---

## 1. What we are standing on (the primitives that exist)

Phase-1 (`loop/reconcile.py`, report 0001) gave us four primitives, all green
under `tests/test_loop.py` (6/6):

- **The fold** — `Fold(root)` (`reconcile.py:115`). The read down `log/` is the
  only thing that remembers (D-5). Dedup by id, replay-safe.
- **The reconcile step** — `pass_once` (`reconcile.py:219`). One level-triggered
  move (D-8): re-read the fold, advance the atom *at most one step* toward
  `desired_state`, idempotent by `(node, artifact_hash)` (I-2), ending
  `done | report | needs-you` (D-6). It asks §14.4's five questions every time.
- **The seam surface** — `events.jsonl` + `receipts.jsonl` as truth, `queues/` +
  `offsets/` as a pure fold cache (`rebuild_cache`, `reconcile.py:200`; the
  §14.1 cache rule, tested by `test_queue_membership_is_never_authoritative`).
- **A naive driver** — `until_done` (`reconcile.py:296`). Loops passes until the
  one atom is `done` or stuck.

**The load-bearing observation: `until_done` is not the orchestration loop.**
It is a single-atom drainer with no control — it admits every step it can, as
fast as it can, for exactly one atom, and stops. It can only heat. The spec
(§15, I-7) says the capability that matters is the *other* direction.

---

## 2. What the spec calls for above the step (the gap)

The doctrine names the layer between "one reconcile step" and "a running
system," and it is not in `loop/` yet:

- **§2 — a control session.** Routes, launches, swaps config; sees a system-wide
  index; **makes no value calls** (D-3). This is the agent the loop runs inside.
- **§15 — ambient control.** The loop is a *bidirectional homeostat*, not a
  drainer. Sense pressure (field-state read from the log), compare to an
  **admitted setpoint** (I-8), and act *both ways*: too cold → **heat** (fan-out,
  summon nodes, ring signals); too hot → **cool** (throttle, shed, defer, bleed).
  **Cooling is the load-bearing direction (I-7)** — every "add more agents"
  design can heat; almost none can tell themselves to back off.
- **D-10 — summoned, not staffed.** A node is a standing offer answered by a
  signal — blink in, read the place, do one bounded thing, write a line,
  dissolve. The loop *summons*; it does not babysit processes.
- **I-3 — the surfacer sees wider** than any worker, and writes nothing.
- **§3 — the gear model** is the acceptance picture: result = torque, mesh =
  reconcile, ratio = fan-out, pulley = the human stamp, herringbone =
  worker/reviewer opposition that cancels drift.
- **Two time-scales (§15).** A **fast loop** holds the setpoint each tick; a
  **slow loop** moves the setpoint itself from accumulated outcomes (run hot to
  explore, cool to consolidate). The slow loop *is* the environment adapting
  (D-12).

---

## 3. Recommendation — the orchestration loop

**Recommendation: the orchestration loop is a control session that, each tick,
folds the log, senses pressure against an admitted setpoint, derives a step
budget in either direction, and spends that budget by invoking the existing
reconcile step across the atoms that are short of goal — adding no new source of
truth.** In one shape:

```text
orchestrate(root):                         # the control session (§2), D-3: routes, no value calls
  until every atom is settled:             # terminal: each atom done | parked at needs-you
    fold     = Fold(root)                  # D-5: re-read truth every tick — never carry it
    atoms    = load_atoms(root)            # the field: many atoms, not one
    pressure = sense(fold, atoms)          # §15 field-state, a pure fold over the log
    setpoint = read_setpoint(fold)         # I-8: an admitted dial, read at runtime
    budget   = control(pressure, setpoint) # §15 BIDIRECTIONAL — the whole point:
                                           #   too cold -> heat: raise budget, seed/summon
                                           #   too hot  -> cool: lower budget, shed, defer, bleed
    for atom in schedule(short_of_goal(atoms), budget):
        pass_once(root, atom)              # THE EXISTING PRIMITIVE, per-atom — unchanged contract
    admit(root, tick_record(pressure, setpoint, budget))   # the tick is itself an admitted line
```

Why this is the right shape, against the doctrine:

- **It rides reconcile; it does not replace it (D-8, §13.2).** Every actual move
  is still `pass_once` — one level-triggered step, idempotent, ending in a
  result. The loop only decides *how many* steps to admit this tick and *which
  atoms* get them. Truth stays the fold.
- **It is the homeostat, both ways (§15, I-7).** `control()` is the herringbone-
  solenoid: it pushes (more budget, seed atoms, summon gates) *and pulls* (less
  budget, stop seeding, defer backed-up atoms). The cool path is a first-class
  branch, not an afterthought — that is the requirement I-7 makes load-bearing.
- **It summons, it does not staff (D-10).** Each admitted step is a node blinking
  in for one bounded judgement and dissolving back into the log. The loop holds
  no worker processes; it holds a budget and a fold.
- **It adds no new truth (D-5).** Pressure is a pure fold over the log. The
  setpoint is an admitted record (I-8). The per-tick budget and the tick itself
  are admitted lines. Delete every derived thing and a replay rebuilds it — the
  §14.1 cache rule, lifted to the whole controller. The moment the loop trusts a
  number it kept in memory instead of re-reading, D-8 is broken.
- **It keeps the human at the top (D-4, §3 pulley).** Atoms that reach
  `needs-you` are *parked*, not retried into the void; they raise sensed
  pressure (the human queue is backing up) and the loop *cools* in response
  rather than flooding the one slow stage. Backpressure falls out of the control
  law instead of being bolted on.

### 3.1 Sensing pressure — concretely, from the log we already write

Each sensor is a pure fold; none needs new infrastructure:

| signal | read from | direction it pushes |
|---|---|---|
| **queue depth** | unreceipted announced events (the `queues/` fold) | hot → cool |
| **staleness** | newest event `ts` per atom vs. now | cold → heat |
| **human backlog** | atoms at `needs-you` / pending owner stamps | hot → cool (protect the slow stage) |
| **contradiction** | conflicting receipts on one seam (the I-4 / §13.3 clash) | hot → cool + surface |
| **inflow** | rate of new `atom.created` events | hot → shed (stop seeding) |

`sense()` is these folds rolled into one field-state number (or vector) read
against the setpoint. "Pressure" is never a hidden metric — it is visible in the
log (§15).

### 3.2 The setpoint is an admitted record (I-8), and the slow loop moves it

The setpoint — what temperature to hold — is a typed line in the log, read at
runtime, *not* a literal in the loop:

```yaml
admission:
  id: adm.2026-...
  type: setpoint
  dial: orchestration.temperature
  value: { step_budget_per_tick: 3, max_inflight_atoms: 8, human_queue_cap: 2 }
  by: bdo            # admitted, not self-set (D-4)
  supersedes: adm.<prev>
```

The **fast loop** reads this dial each tick and holds it. The **slow loop** is a
separate, much rarer pass that reads accumulated outcomes (how many halts, how
much rework, how much drift) and *re-admits* the dial — hot early to explore,
cooler as halts accumulate to consolidate. That re-admission is the environment
adapting (D-12); it writes a new `admission`, it never mutates the old one.

---

## 4. What must change in the primitives to support this

Small, named, and mechanical — the phase-1 skeleton was built single-atom on
purpose, and these are the seams where it generalizes:

1. **`load_atom` (exactly one) → `load_atoms` (many).** `reconcile.py:147`
   hard-fails on anything but one atom. The loop needs the *set*.
2. **`pass_once(root)` → `pass_once(root, atom)`.** Today the step re-derives
   "the atom" each call (`reconcile.py:229`); the orchestrator must hand it which
   atom to advance, so per-atom hashing and the fold stay correct across many.
3. **Sensors as pure folds** — new read-only functions over `Fold`, one per row
   in §3.1. No writes, no new files.
4. **The setpoint reader + the `admission` record type** — one new event type,
   read at runtime (I-8). The atom schema already has the shape vocabulary;
   this is an admission, not an atom.
5. **`control()` — the bidirectional law** — maps `(pressure − setpoint)` to a
   step budget and a heat/cool action set. This is the only genuinely new logic;
   everything else is generalization.

Note what is **not** on this list: the reconcile contract, the fold, the cache
rule, idempotence, line-atomic appends, the result vocabulary. The orchestration
loop is built *over* the primitives, not *into* them.

---

## 5. The test that would matter (the §10 discipline, lifted)

Phase-1's real test was "can two locally-fine atoms refuse to fit" — the seam,
not the cell. The orchestration loop's equivalent real test is **the cool path,
because that is the direction I-7 says everything else gets wrong**:

> Seed atoms faster than the (mocked, rate-limited) human stamp can clear them.
> A drainer floods the human queue without bound. The recommended loop must
> *sense the backlog and throttle its own inflow* — measured by: the human
> queue never exceeds its admitted cap, and the loop still makes progress on
> already-admitted atoms. If the loop only ever speeds up, the control law isn't
> doing its job yet (the §10 mirror: if nothing ever throttles, the cool path is
> untested).

A loop that passes "many atoms reach goal" but cannot be made to *back off* has
built the easy half. The kill-test proved durability; this test proves control.

---

## 6. The single next version (if we build, build only this)

Per §9.3 and §11, one useful thing at a time. The smallest version that makes
the recommendation real and leaves a working artifact:

> **v-next: a control session that runs the fast loop over ≥2 atoms with a
> fixed admitted setpoint and a working cool path — no slow loop yet, no real
> nodes yet.** Done when: two atoms reach goal under a per-tick step budget read
> from an `admission` record; and the §5 flood test throttles inflow to keep the
> mocked human queue under its admitted cap without stalling. Mocks stay mocks
> (the owner-stamp mock is still the first to be replaced when a node goes real).

This is one capability (the fast ambient loop), it leaves something useful alone
(phase-1 untouched), and it defers the slow loop, real nodes, the surfacer
ensemble, and the control/surfacer split — each its own later version (§11).

---

## 7. End-state and what was not done

- **End-state: `report`.** This is a recommendation; it changes no code and edits
  no doctrine. The next move needs bdo's read and a fresh stamp (D-4) before any
  of §4/§6 is built.
- **Not done, on purpose:** no `loop/` changes, no doctrine edit (§12 tripwire
  respected), no invented `docs/culture/` files (still absent — noted, not
  authored), no phase-2 integration (read-only, §11).
- **Open for bdo:** whether v-next (§6) is the next version, or whether the
  control/surfacer split (§2) or a real L0 node (§11 "Next") should come first.
  The recommendation orders them ambient-loop-first because I-7 says the cool
  path is the capability the whole design exists to prove, and we have not proven
  it yet.

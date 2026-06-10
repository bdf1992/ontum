# Report 0021 — the trust ladder: rungs admitted, ontum-touch locked

## What landed

**[done-line 0024](../done/0024-trust-ladder-rungs-locked.md) — met.** The
second wave-1 piece of [epic.experience-layer](../epics/epic.experience-layer.json)
(`atom.trust-ladder.v0`): what each class of agent may do is now an admitted
record, not an assertion in prose — and the top rung is locked shut.

- **[loop/trust.py](../../loop/trust.py)** — a pure fold over `trust_rung`
  admissions. Five agent classes (summoned-session, branded-subagent,
  local-model, external-mind, deterministic-rule) × a cumulative ladder of
  capabilities (`read < judge < author < ontum-touch`). `permits(class,
  capability)` answers from the log; reads nothing it isn't handed, writes
  nothing.
- **[loop/node.py](../../loop/node.py)** — gains `admit-rung`, the one write
  path for a rung. bdo-only (`--by` must be bdo — nothing grants itself a rung,
  D-4), superseding (a later rung lowers an earlier one, never erases it).
- **`ontum-touch` is LOCKED** — denied for every class, the pen refuses to
  grant it, and bdo's trust boundary is the standing reason, quoted verbatim
  in the refusal. Unlocking it is a deliberate change to the pen, his alone —
  not a flag a session can pass.
- **[tests/test_trust.py](../../tests/test_trust.py)** — the §10 proof as
  tests: the ladder refuses. A class with no rung is denied; a grant permits
  up to its level and no higher; ontum-touch cannot be granted; a non-bdo
  grant is rejected. Suite: 190 OK.

## needs-you

- **Stamp this PR** (trust-ladder, done-line 0024).
- The ladder starts **empty** — every class is denied everything until you
  grant a rung:
  `python -m loop.node admit-rung --class <c> --capability read|judge|author --by bdo`.
  `ontum-touch` stays locked by construction; it is yours to unlock, deliberately,
  if ever.

## End-state

`report` — capability rungs are admitted records with a pure read-fold and a
bdo-only write pen; the locked top rung refuses by construction. Enforcement at
act time (pens calling `permits`) and the wave-2 backings are named out of
scope. Ready for the branch ritual and your stamp.

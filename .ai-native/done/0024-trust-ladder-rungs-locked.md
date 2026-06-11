# Done-line 0024 — the trust ladder: capability rungs, ontum-touch LOCKED

Written before code, per §9.4. When this line is met, stop.

> **Done when:** capability rungs are admitted records read by a pure fold —
> `loop/trust.py` answers `permits(agent_class, capability)` over `trust_rung`
> admissions; rungs are granted only through the one pen (`loop.node
> admit-rung`), bdo-only and superseding, never self-granted (D-4); and the
> top rung `ontum-touch` is LOCKED — denied for every class, the pen refuses
> to grant it, and bdo's trust boundary is quoted verbatim as the standing
> reason. §10 proof: the ladder *refuses* — a class with no rung is denied
> everything, ontum-touch cannot be granted, and a non-bdo grant is rejected.

## Out of scope, named (later increments)

- **Enforcement at act time** — pens and the branded-spawn-rail calling
  `permits()` before an act, raw acts denied. The seam exists here
  (`permits`); wiring it into the pens is its own increment.
- **The spawn rail and model registry** (wave 2) — the classes
  `branded-subagent`, `local-model`, `external-mind` get real backings there;
  this increment defines the rungs they will hang on.

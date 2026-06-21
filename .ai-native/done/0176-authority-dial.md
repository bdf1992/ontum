# Done-line 0176 — The autonomy dial — ask-forgiveness, default set, with an owner's manual

Written before code, per §9.4. When this line is met, stop.

> **Done when:** the authority dial (`loop/authority.py`) routes any declared act to ACT-AND-FYI vs ASK-FIRST by CONSEQUENCE — it proceeds unattended only when the act is observable AND reversible AND low-blast AND advancing a confirmed arc, and ASKS FIRST on any doubt (new, partial, undeclared, irreversible, high-blast, or off-arc) — composing the consequence-gate (`loop/observe.py`), never re-deriving it; the tiers are an admitted `authority.tiers` setpoint with a default-safe fallback I set (never a code constant), tunable by bdo's one gesture; a §10 test proves an irreversible / high-blast / undeclared / off-arc act ALWAYS asks first (non-vacuous — a freely-permissive dial fails it); and the owner gets a real **owner's manual** (`docs/culture/the-administrator.md` plus the live `python -m loop.authority` surface) stating the defaults I chose and the exact gesture for each knob — Apple, not IKEA.

## Why

bdo, 2026-06-21: *"ask-forgiveness = risk-tiered authority dial (reversible -> act + FYI, irreversible -> ask)"* and *"set the default and give me an owner's manual — I don't want to put all the nuts and bolts together. This isn't ikea, it's apple."* The dial is the keystone to the autonomous-authorship button (the `authoring-platform.proposal.md` first slice): it bounds what the world may BECOME without bdo in the loop, so most reversible motion never reaches him and what does is rare and shaped. CTA-1 stamped (crease + sensors-as-staff); the build follows.

## Shape

- Defaults are MINE to set, conservative and default-safe (the setpoints law: default-safe when unset, owner tunes the named gesture). Apply it to a DECISION (the tiers), not just a number.
- Composes `observe.gate` (Observable first) + the consequence-policy model (govern consequence, not action). Native — no external policy engine.
- The owner's manual is the deliverable bdo named: what it does, the defaults, the knobs, the gesture per knob — no assembly.

## Not in scope

- The Administrator itself (the join that runs the fleet's acts past this dial and shapes the ask-first ones into a briefing) — named, this is its keystone, it rides later.
- The gateway-policy-spine adopt-vs-native question — the dial is built native; that broader call stays bdo's.

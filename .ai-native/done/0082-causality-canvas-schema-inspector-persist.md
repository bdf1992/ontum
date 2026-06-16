# Done-line 0082 — Causality canvas: one solution, schema-driven, editable and persistent

Written before code, per §9.4. When this line is met, stop.

> **Arc:** causality-canvas

The first landed Causality canvas feature, and the move that wraps the prior iteration into one solution: the demo canvas (the experience-foundry prototype), the term-economy fold, and the holonic/strata/anima learnings converge into one governed surface homed in `causality/`. The spec is `causality/display-system.md`. This composes `epic.causality-surface`'s `atom.causality-schema.v0` (persistence) and `atom.register-ux-discipline.v0` (the per-element config panel) — it does not double-build them (§10), it lands their first cut on the real engine. It is the toy→tool flip the feature audit named (P0): the canvas becomes editable beyond a label, and what you make survives a reload.

> **Done when:** the Causality canvas, homed in `causality/`, (1) derives node defaults, its inspector, and its serialization from one per-type config SCHEMA; (2) lets you click a node to open an inspector that shows and edits its type's config, and click an edge to edit its config, with every edit persisted to the model; (3) round-trips the whole graph through `toJSON`/`fromJSON` to localStorage and a file export/import so a reload restores it; and (4) carries on the node model the declared, schema-described fields the full vision lands on next — `sites[]`, `space`, `strata{fundamental,derived,learned}`, and `anima{strength,tempo}` — even though their population and comparison are a later piece. Proven by a headless or browser check that a config edit and a newly added node both survive a reload.

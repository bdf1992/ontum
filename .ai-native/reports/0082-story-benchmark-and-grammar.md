# Report 0082 — The story benchmark: deterministic recovery-scorer + well-formedness gate, and the fleet-id cleanup

## What landed

bdo struck a frame and we built its deterministic spine: the Causality story-demo
is a *generator with known latent structure*, so `causality/phrases.json`
round-trips (text → recovered mesh, scored against the JSON) — the same files that
demo Causality are its own benchmark oracle.

**Homed the outcome** — `outcomes/causality-story-benchmark.md`: maximal statement,
probe-set (spine G0–G2; seam G3–G4/B1–B2; realization OUT1–OUT3), the five-node
roster, and the trap taxonomy. Defaults on bdo's confirmation: band authority
(he stamps the calibration band once) and local-subjects-first.

**Two deterministic scorers, both with teeth (committed, green):**
- `recovery_scorer.js` (done-line story-benchmark-scorer, id 0108) — facet-F1 +
  relation recovery + a trap flag. §10 test separates cat-sunbeam's mechanism-
  reading (warmth mediates: composite **1.000**) from its grammar-reading
  (shadow→cat: **0.143**). `surface_trap` annotated on 5 of 8 phrases (the 3 with
  no genuine commission trap left untrapped — forcing one is the fake-trap failure).
- `grammar_scorer.js` (done-line story-grammar-wellformedness, id 0109) — bdo's
  ask. Catches the two kinds of nonsense his example exposes: **structural** (a
  `source` cannot drive an `actor` directly — "sunlight napped on the cat") and
  **lexical** (the verb "ate" needs an `actor`; shadow has none). Unknown verb →
  `unknown`, never a false verdict. Every real phrase well-formed; constant scorer
  fails. The deterministic floor under the (now-narrow) coherence-judge.

**Tests:** all 8 causality node test files green; full Python suite 839 OK.

**Fleet-id cleanup (this session's mess, cleaned):** a parallel session shared
this branch. My done-lines/reports collided on ids with another branch
(`decomposition-change-axes`). The concurrent re-home commit (`bb965ad`) swept my
grammar code + outcome into a commit (the shared-tree sweep hazard) and re-homed
the benchmark done-line to 0108. I re-homed the grammar done-line to 0109,
consolidated my two stranded reports into this one, removed the stranded
colliding-id files and digest strays. Records now reference done-lines by **slug,
not numeric id** — the fix that makes them fleet-collision-proof.

## needs-you

- **The deterministic spine is complete** (G0+G1+G2, all met). The open frontier
  is **M2** — the inference seed-author, the live `mesh-recovery` subject through
  the local minds, and the floor/ceiling calibration band (B1/B2/OUT1). The next
  build whenever you want it; nothing of yours blocks it (epic.causality-surface
  is confirmed; the merge-node lands this branch).
- The branch is shared with a parallel (overnight) session — coordination, not a
  chore: both streams are green and committed, but watch the shared branch at land.

## End-state

`report` — the benchmark grades on two deterministic axes (well-formedness +
trap-aware recovery), both with teeth; records re-homed to fleet-safe ids and
slug-referenced. M2 (the inference nodes) is the next build.

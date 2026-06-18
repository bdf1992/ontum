# Report 0081 — The story benchmark's deterministic spine: scorer + calibrated traps

# Report 0080 — The story benchmark's deterministic spine: scorer + calibrated traps

_Provenance: re-homes the prior session's stranded report (minted 0076, fleet-
colliding with `0076-change-axis-gate` on `origin/claude/decomposition-change-axes`).
Content carried verbatim; its done-line reference is updated 0105 → **0108** (the
done-line was re-homed for the same fleet collision)._

## What landed

**bdo struck a frame** — the Causality story-demo is a *generator with known
latent structure*, so `causality/phrases.json` round-trips: text → recovered
mesh, scored against the JSON. The same files that demo Causality are its own
benchmark oracle ("workbuilding"). The shape was co-designed across the session
and confirmed ("yeahhh").

**Homed the outcome** — `outcomes/causality-story-benchmark.md`: the maximal
statement, the probe-set (deterministic spine G1–G2; the generative+grading seam
G3–G4/B1–B2; realization OUT1–OUT3), the five-node roster (seed-author,
skin-author, mesh-recovery=device-under-test, recovery-scorer, coherence-judge),
and the trap taxonomy. Two owner defaults recorded on his confirmation: **band
authority** (bdo stamps the calibration band once, confirm-arc shape) and
**local-subjects-first**.

**Built the deterministic spine (done-line 0108, M1):**
- `causality/recovery_scorer.js` — a pure, stdlib-node scorer: facet recovery
  (F1 over glyph·facet pairs) + relation recovery (over from→to edges) + a flag
  for whether the recovery drew the phrase's `surface_trap` edge. Trap taxonomy
  (`TRAP_TYPES`) lives here, deliberately not in the render vocabulary.
- `causality/phrases.json` — annotated `surface_trap` (type + tempting-wrong
  edge + why) on the **5 of 8** phrases with a genuine commission trap
  (cat-sunbeam, robot-plant, mouse-crumbs, bee-flower, fox-berry); the other 3
  left untrapped (forcing a trap where surface≈mesh is the fake-trap failure).
- `causality/recovery_scorer.test.js` — §10 teeth: on cat-sunbeam the scorer
  **separates** the mechanism-reading (warmth as mediator, no shadow→cat:
  composite **1.000**) from the grammar-reading (shadow→cat, mediator missing:
  composite **0.143**); a constant scorer cannot separate, proven by negative
  control.
- `causality/phrases.test.js` — extended: a declared trap must use a real
  `trap_type`, resolve to real glyph endpoints, carry a real 'why', and **not be
  a true edge of the mesh** (a non-trap is refused).

**Tests:** all causality node tests green (recovery_scorer 11/11, phrases 11/11,
canvas-system, persist/authoring/inspector/space all pass).

## End-state

`report` — the benchmark's deterministic spine is built and green (done-line
0108, outcome homed); M2 (the generative + grading nodes) is the open frontier.
The M2 seam (inference seed-author + live `mesh-recovery` subject + floor/ceiling
calibration band) plugs into teeth that already bite.

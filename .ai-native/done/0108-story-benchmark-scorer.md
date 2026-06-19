# Done-line 0108 — The story benchmark's deterministic spine: recovery-scorer + calibrated traps

# Done-line 0108 — The story benchmark's deterministic spine: recovery-scorer + calibrated traps

Written before code, per §9.4. When this line is met, stop. One increment toward
the outcome `outcomes/causality-story-benchmark.md` (the story surface as a
self-calibrating NL→structure benchmark) — NOT a replacement for it; the
outcome's remaining probes stay live pressure.

_Provenance: re-homes the prior session's stranded done-line (minted 0105, which
fleet-collided with `0105-undercut-axis-one-module-two-reasons.md` on
`origin/claude/decomposition-change-axes-a57frr`). The bar below is carried
**verbatim**; only the id moves, so the already-green benchmark code can land._

This line builds the **deterministic spine** of the benchmark (outcome probes
G1 + G2): the part that needs no inference and proves the grader has teeth
before any agent / inference node is written.

> **Done when:** `causality/` carries (1) a **deterministic recovery-scorer**
> (`recovery_scorer.js`, stdlib node, a pure function) that scores a *recovered*
> mesh against a phrase's *true* mesh — facet recovery (F1 over glyph·facet
> pairs) and relation recovery (over from→to edges) — and flags whether the
> recovered mesh drew the phrase's `surface_trap` edge; pinned by a §10 test
> (`recovery_scorer.test.js`) that, on the `cat-sunbeam` case, **separates a
> mechanism-reading (warmth as mediator, no `shadow→cat`) from a grammar-reading
> (`shadow→cat`, mediator missing)** — a constant / fabricated scorer fails the
> separation. (2) The phrase portfolio carries a typed **`surface_trap`** (type +
> the tempting-but-wrong edge + why) on every phrase that genuinely has one (no
> forced traps), with `phrases.test.js` extended to **refuse a trap that is a
> subset of the true mesh** (a non-trap) and an **undeclared `trap_type`**, while
> requiring the trap's endpoints to still resolve to real glyphs (a plausible
> misreading, not nonsense). The full causality test set green; a numbered report
> names end-state and every `needs-you`.

> **Non-example:** a scorer whose number does not move between the mechanism- and
> grammar-readings of cat-sunbeam (no teeth); a `surface_trap` invented where the
> surface genuinely matches the mesh (a fake trap — open beats invented); a trap
> edge that is actually a true edge of the mesh, or whose endpoints don't resolve;
> putting trap vocabulary into `canvas-system.js` (that is render vocabulary — the
> benchmark's trap-types live with the benchmark); reaching for live inference to
> meet this line (this is the deterministic spine; the recovery *subject* and the
> calibration band are later probes, B1 / B2).

> **Arc:** serves the confirmed `epic.causality-surface` (adm.a675cb9d36fb).
> The outcome it increments is `outcomes/causality-story-benchmark.md`; design
> lineage `causality/iterations.md` 0003-0005 + the story-corpus-is-benchmark
> memory note.

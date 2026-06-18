# Done-line 0109 — The benchmark's well-formedness gate: a deterministic grammar scorer refuses nonsense

Written before code, per §9.4. When this line is met, stop. Re-homed to a free
fleet id (the original collided with another branch's id; the work and its code
are committed, slug-referenced, not numeric). One increment toward the outcome
`outcomes/causality-story-benchmark.md`; not a replacement for it.

bdo, 2026-06-17: "we should have a grammar score too — in case of nonsense
stories like 'sunlight napped on the cat until the shadow ate the plant'." A
nonsense story must be refused at generation, never graded; type-by-composition
gives the grammar deterministically.

> **Done when:** `causality/` carries a deterministic **grammar / well-formedness
> scorer** (`grammar_scorer.js`, stdlib node, pure, reusing the recovery-scorer's
> mesh helpers) that reports (1) **structural** well-formedness — every relation's
> facet pair is in one declared `LICENSED` table, where a `source` may emit into a
> `state` but may NOT drive an `actor` directly (the mediator must intervene); and
> (2) **lexical** well-formedness — a relation whose label verb is known
> (`SUBJECT_FACET`) must have a subject glyph carrying the required facet, while an
> unknown verb returns `unknown` (an honest gap, never a false pass) — yielding a
> `wellFormed` boolean, a grammar score, and named violations. Pinned by a §10 test
> (`grammar_scorer.test.js`) that flags bdo's nonsense — "sunlight napped on the
> cat" (a `source` cannot drive an `actor` — structural) and "the shadow ate the
> plant" (eat needs an `actor`; shadow has none — lexical) — as malformed, while
> every real portfolio phrase is well-formed, and a constant scorer fails. The full
> causality test set green; a numbered report names end-state and every needs-you.

> **Non-example:** a grammar scorer that passes the nonsense story; guessing a
> verdict for an unknown verb instead of returning `unknown`; a `LICENSED` table so
> loose it licenses `source→actor` or so tight it false-flags a real phrase;
> grammar vocabulary in `canvas-system.js` (render vocabulary); re-implementing the
> mesh helpers instead of importing them from `recovery_scorer.js`.

> **Arc:** serves the confirmed `epic.causality-surface` (adm.a675cb9d36fb). The
> outcome it increments is `outcomes/causality-story-benchmark.md`; design lineage
> bdo's nonsense example, 2026-06-17.

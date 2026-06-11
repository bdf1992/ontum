# Done-line 0031 — Pivot: meaning recovers the cube, or the grader refuses it

Written before code, per §9.4. When this line is met, stop.

> **Done when:** the Pivot harness produces **one calibrated number**
> for "does meaning carry the cube" — a *cold* recoverer (an agent that
> has never read the placements; this surface is contaminated and the
> harness says so) is handed N occupants and the bare cube container
> (the 27 cells of {−,0,+}³ with their kinds named) but **not the
> mapping**, and assigns each occupant a coord; the harness grades that
> assignment **deterministically** — cell-kind match rate against the
> known frame *and* the incidence laws (the lawful census 8/12/6/1 = 27,
> closure = 3^dim, star = 2^codim, Σ = 125), reusing `glyphs/knoll.py`'s
> cube functions, never re-deriving them; and it runs across three
> populations to anchor a scale — **random words** (floor: recovery ≈
> chance), the **S-frame** (the test object), and a **surface-encoded
> set** (ceiling: coord forced by an obvious feature, the cube's Pilish
> analog) — so the output is not a bare accuracy but *where the S-frame
> sits between noise and obvious*. A test exercises the refusal: a
> recovery that is locally plausible (every word in a believable cell)
> but violates the census or an incidence law is **refused by the
> grader**, not scored as fine.

## Direction (bdo, chat, 2026-06-10)

bdo's "onton benchmark" — the cube + address + occupants, a multi-stage
suite (generate → place → measure → recurse → recreate) measuring
whether natural LLM inference recovers deliberately-hidden structure,
and how deep it recurs. Lineage: his informal π/XYZ result — two
encoders hide a concept in a word-set, a third *naive* model recovers
it cold and detects it's a test, never told to look. Pivot is that at
high dimension. Named by bdo ("Pivot" — the vault's own word for the
hidden center, Seam at (0,0,0)). The suite is the epic
[epic.pivot](../epics/epic.pivot.json); this done-line is its first
rung.

## The contamination pin (the spine)

The harness **never calls a model**; it is deterministic stdlib (cube,
prompt, grader, scale). The *inference* — generation and recovery — is
done by **cold agents/sessions**, and results land as records. This
keeps the substrate's no-network rule intact and makes the benchmark
self-checking like `knoll.py`. epic.ontabet-speaks (wave-3.measures)
already records why: a session that has read the placements is
"contaminated as a scorer." Pivot's rung 1 *is* that epic's
"measured verdict on cube-vs-random" — linked, not duplicated.

## Out of scope, named

- **Blind detection** ("here are N words, notice anything?" — free-text,
  needs a judge): rung 1 reveals the *container* and hides the
  *mapping*; fully-blind is a later rung with its own grader.
- **Recursion / unscramble / centroid-fill**: later rungs bolt onto this
  frame once it stands. One real node at a time.
- **The cold run as a standing service**: rung 1 proves the loop with at
  least one real cold-agent datapoint; wiring it to the summons/orchestrate
  beat is its own increment.

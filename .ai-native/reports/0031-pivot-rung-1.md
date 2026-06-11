# Report 0031 — Pivot rung 1: the recoverability instrument stands

**Branch:** `claude/pivot` · **Done-line:** 0031 · **Epic:** epic.pivot (new)

## What this session built

bdo pitched an "onton benchmark" in chat (2026-06-10/11): the cube +
address + occupants, a multi-stage suite (generate → place → measure →
recurse → recreate) measuring whether natural model inference recovers
deliberately-hidden structure encoded on the glyph cube, and how deep it
recurs. Lineage is his informal π/XYZ result — a naive third model
recovers a hidden concept cold, never told to look. We mapped it in
discussion, he named it **Pivot** (the vault's word for the hidden
center, Seam at (0,0,0)), and asked for a benchmark *suite*.

Landed (done-line 0031, the first rung):

- **`epic.pivot.json`** — the suite as an arc: six rungs (recover,
  centroid, partial-reveal, unscramble, blind-contrast, recursion), owner
  bdo, PROPOSED.
- **`pivot/`** — the deterministic home-half. `instrument.py` reuses
  `glyphs/knoll.py`'s cube (never re-derives the lattice): the reference
  frame, three calibration populations (random floor / s-frame test /
  surface ceiling), a grader that **refuses an unlawful tiling before it
  scores** (§10), and the cold-recoverer prompt. `run.py` is the CLI:
  emit the question (truth withheld), grade the returned recovery.
- **`tests/test_pivot.py`** — 11 tests, green. The §10 case: a recovery
  where every word sits in a believable cell but two claim one address —
  the grader refuses, the gate notices.

## The spine, confirmed by bdo

The harness **never calls a model** (no-network, stdlib). Inference is
played by a **cold** agent that has never read the placements — this
session is contaminated and says so. bdo added the production path: the
benchmark **cannot be run in-repo**; the recoverer is reached by an
**envoy package** (the purest uncontaminated instrument). So the in-repo
half is exactly: *build the question to ship, grade the answer that comes
home.* You ship the question, never the answer key.

## The proxy run (a smoke-test, NOT the verdict)

Three same-family cold sub-agents (one per population, each blind), no
tools, graded by the instrument:

| population | kind-match | vs chance 0.336 | scale |
|---|---|---|---|
| surface (ceiling) | 1.000 | — | 100% |
| random (floor) | 0.407 | ≈ chance | 11% |
| s-frame (test) | **0.185** | **below chance** | 0% |

Ceiling and floor behaved exactly as designed — the instrument is sound.
The S-frame scoring *below random* is a real finding, and the smoke-test
earned its keep by surfacing **the confound behind it**:

> **The question's placement-law must match the truth's generating law,
> or you measure framing-divergence, not recoverability.** The S-frame
> was generated under "I/S/O = sit/act/read" (its own JSON `law`); the
> rung-1 prompt used a generic "−1 interior / +1 exterior" reading. The
> cold recoverer answered a subtly different question than the one the
> S-frame answers, so 0.185 conflates disagreement-on-meaning with
> disagreement-on-law. A fair read carries the truth's own axis
> semantics into the question.

This is exactly why we ran the proxy before spending an envoy seal.

## End-state

Instrument real and tested; loop proven end-to-end; one provisional
(proxy) calibration in hand. Done-line 0031 met at the instrument level.

## needs-you / next pieces (named, not coded around)

1. **The real number is cross-family, via envoy** — can't run foreign
   models in-session. The envoy *seal* for a Pivot "play" package
   (question files + rubric, truth withheld) is unbuilt; it reuses
   `exports/` + the disclosure ledger but with a "play this benchmark"
   framing rather than "review our work." bdo: is this its own rung
   (rung-1.ship) or folded here?
2. **Law-alignment fix** — rung 1's question should carry each truth's
   own generating law (the s-frame's `law` field) so the verdict is
   recoverability, not framing drift. Small, and it changes the headline
   number.
3. **bdo stamps the arc** — epic.pivot is PROPOSED; the rung order and
   the name are his to confirm (`loop.node confirm-arc --epic epic.pivot
   --by bdo`).

## Addendum — the inversion (same session)

bdo killed the "grade against a borrowed truth" framing. The S-frame is
`PROPOSED, MODEL-GUESSED` — never a canon, never agreed. So we **inverted
it** (his word): no external truth; the measurement is **convergence
across independent generations**, and the convergent core *becomes* the
candidate canon (corpus-to-system). His second cut: don't collapse to one
number — the cube is **graded**, so measure per piece, per grade, with
**metrics held in tension**; the gap between two metrics localizes the
*why*. A run yields a **dataset**, not a data point.

Built: **`pivot/measure.py`** — the battery over N generations (each
validated as a lawful tiling first). WHY-detectors: `orientation_slack`
(kind ⊖ exact), `convention_slack` (best-of-48-symmetries-aligned ⊖ raw),
`vocab ⊖ placement`. WHERE-detectors: per-grade consensus,
consensus-by-distance-from-pivot. `run.py --measure <dir> --dataset
<jsonl>` flattens each run to `(seed, scope, grade, metric, value)` rows
that accumulate. 7 tests plant known tensions (identical, same-cube-
rotated, kind-preserving swap, disjoint vocab) and read them back.

First real reading — **4 independent cold placements of the S-words**,
vocabulary held fixed so placement convergence is isolated:

| reading | value | what it says |
|---|---|---|
| placement kind | **0.769** | the *grade* of a word's cell replicates well |
| placement exact | **0.380** | the *exact corner* does not |
| orientation_slack | **0.389** | most disagreement is axis convention, not meaning |
| pairwise raw → aligned | 0.123 → 0.247 | a cube symmetry doubles agreement — a third of the scatter is pure rotation |
| per-grade: center | **0.750** | the **pivot is the most-agreed position** |
| per-grade: corners | 0.312 | the 8 corners scatter most |

The finding: independent cold reads converge on **kind and on the pivot**,
not on exact position — and a measurable slice of the positional scatter
is just rotation. The encoding carries *semantic grade* robustly and
*absolute orientation* weakly — which quantifies the earlier "reveal the
axis to make it well-posed" intuition, and vindicates the name: the
**center is the convergence anchor**. (Caveat: N=4, same model family,
center is one cell. Cross-family via envoy is still the real verdict.)

This replaces needs-you #1's framing: the path forward is convergence
over independent generations (vocabulary varying too, the harder test),
not grading against any one guess.

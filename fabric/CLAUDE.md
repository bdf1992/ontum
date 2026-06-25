# fabric/ — the thing the harness builds

**This is not the harness.** `loop/`, `.ai-native/`, the gates, the pens —
that is the *harness*, the handle by which we derive what ontum is and
means. `fabric/` is the **fabric of the field**: the thing the harness is
building. Keeping the two apart is load-bearing (report 0004's category
error); a session that starts describing fabric in terms of harness organs
has lost the frame.

Status: **bootstrap.** We are authoring the priors, by hand, to make the
engine that will later progress generations on its own. The line where the
hand-crank stops and a generation produces the next one itself is **OPEN**
(named, not built) — the honest edge of the whole project.

## Hard rules of this directory

- **Re-ground, never import.** The precursors in `docs/sources/` (the
  `priors/` synthesis, `colorchain.py`, `hadron.py`, the wave1 cards) are
  **read-only context**. fabric *cites* them and re-derives fresh — it never
  vendors or imports them. That re-grounding *is* the point: this time, with
  provenance.
- **Every part carries a Pointer or it is OPEN.** No claim stands as prose.
  A part carries a **representative pointer** (a `file:line` or log record it
  resolves to) and a **typed pin** (its grade), or it is marked OPEN.
  Absence is information; an ungrounded part is named OPEN, never invented.
  Grades: `[P]` PINNED · `[D]` DERIVED · `[M]` MINTED/convention · `[O]` OPEN.

## The universal contract (the P-words)

One set, carried across every generation:

> Provenance · Pointers · Precursors · Primitives · Primaries · Primes ·
> Principles · Parts · Properties · Pigment · Poset · Prose · Parity

## Generations (the build-ladder)

**−1 · −1/2 · −1/3 · 0 · 1/3 · 1/2 · 1**

- **Integers (−1, 0, 1)** = whole generations (shells).
- **Fractionals (±1/3, ±1/2)** = *iteration states* — particles, parts, pieces, and the
  computation of the next whole gen. **1/3 = triality** (color/charge thirds, the C₃
  axis); **1/2 = duality** (spin/parity halves, the bicone/C₂).
- **0** = the configuration event (C set, fields couple — the "big bang").
- **gen < 0** = pre-config / anti = read-only **mythos** (no C yet → uncomputable);
  **gen > 0** = the computable fabric.

Each generation has the same universal shape; the recursion lives at the **necks** and
is **toroidally bounded** (it wraps; the bedrock is reached only as mythos), not a base
case. Note: this build-ladder's "generation" is distinct from the **physics
flavor-generations** (1/2/3 in `library.py`), which live inside gen > 0.

## Structure (declared; filled as we go — absence is information)

- `precursors/` — provenance-carrying pointers to the audited sources.
- `domains/` — the 8 domains (one folder each), generated from 3 binary axes.
- `fields/` — the actual fields.
- `gen0/` — the first generation.
- `codebase-cards.v0.md` — the first artifact: learning cards that document
  the existing code and prototype the card form the fabric will use.

The cube, the 3 binary axes, the bicones, and **self-as-emergent-field** are
the working design — **PROPOSED**, still forming in conversation, not yet
codified here as governance. They graduate into this surface only when stable
and bdo-stamped (D-4).

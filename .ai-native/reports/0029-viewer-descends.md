# Report 0029 — the viewer descends

## What landed

**[done-line 0029](../done/0029-viewer-descends.md) — met.** BUILD-3 of
epic.ontabet-speaks, extended by bdo's ask: surface the wave-1 harness
data and *mutate it through operations* — Rubik's turns, descent/ascent
between global and local frames.

The architectural move: **descent re-labels the one cube** instead of
opening a side widget. A frame stack with breadcrumbs (global ⊘ ▸ S…)
swaps which vocabulary the 27 pieces carry; words ride PIECES while
addresses stay cells, so every existing operation — drag turns,
keyboard moves, scramble, unwind, explode, x-ray, knoll, sound — works
identically at every level, and turning a descended frame visibly
displaces words from their addresses. The state line reads the pairing
("canonical pairing" / "N of 27 displaced"). Descent into S shows its
27 placed words [PROPOSED, MODEL-GUESSED — read live from
`REGISTRY.placements`, never hardcoded]; a letter shows its term-frame
slots with the basin pivot candidate riding the center as a named hole
[OPEN]; ⊘ descends to the interstitial frame (kind pools in the panel,
cell assignment honestly OPEN). Depth stops at one level with an
honest caption: child frames are not drafted (MEAS-5 territory).

Also landed, per the zip spec but data-driven from the grown registry:
- **the index** — one panel, four tabs: ontabet (27 glyphs graded:
  address/kind/bit-code/bits/chips/frame capacity, plus the
  48-spelling syllabary), **basin** (per-frame pivot/filled/density,
  census claimed-vs-measured with the divergence finding, all 27
  cross-frame collisions, the interstitial pools), terms (with the
  demotion line), findings. The donors column renders the **measured**
  lexifier density; sc renders OPEN until MEAS-3.
- **composition section** in the cell inspector — closure/star fans
  read from the registry (clickable), the bit cost, the falsifier text.
- removed: trio spotlight, cascade, trio panel (conversation-
  invalidated); mobile bar fix added.

Testing: the frame vocabulary is a pure `FRAME_MATH` block beside
`CUBE_MATH`, extracted and run under node — placed frames keep
PROPOSED, pivot candidates stay OPEN, interstitial cells stay
unassigned, displacement counts honestly. Shell tests prove the
hardcoded-placements path is impossible and the invalidated features
are gone. Suite: 254 OK; generator byte-idempotent.

## needs-you

- **Stamp this PR** (done-line 0029).
- Open `glyphs/viewer.html`, click a cell, hit **descend** — then
  scramble. Whether the displaced-pairing experience reads as PIN-1
  evidence or noise is exactly the kind of call that's yours.

## Out of scope, named

Deeper descent (children of letter frames — blocked on drafting them,
MEAS-5), I/O placement (PIN-2), all measurement runs, and any viewer
write path (there is none, deliberately — verdicts only through pens).

## End-state

`report` — the viewer surfaces everything wave 1 landed and mutates it
through the cube's own operations at every frame level; nothing
decided, everything labeled with the status it carries. Ready for your
stamp.

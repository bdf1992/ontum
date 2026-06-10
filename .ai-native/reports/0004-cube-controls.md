# Session report 0004 — cube controls + polish (and Pilish)

- **Date:** 2026-06-10
- **Session:** continuation of 0003, bdo request: "add rubick cube control
  too … we can add some serious pilish to this"
- **Branch:** `claude/busy-feynman-4hd46k`
- **End-state:** `done`
- **Reading note:** "pilish" taken both ways — serious *polish*, plus actual
  *Pilish* (word lengths follow the digits of π), which the cube-alphabet
  doc practically begs for.

## What landed

- **Working cube in the viewer.** The six generators {U,D,L,R,F,B} — the
  doc's generative minimum — as buttons, keys (u d l r f b, shift/′ for
  counterclockwise), with animated quarter-turns. Full permutation and
  orientation tracking: each piece carries its home cell, current cell,
  and accumulated integer rotation; edge orientation and corner twist are
  derived from the rotation, not bookkept separately.
- **The live state string**, in cube-alphabet.md §7's exact format:
  `edge word (G–R) | 12 EO bits | corner word (S–Z) | 8 CO trits`.
  Solved state glows green at `GHIJKLMNOPQR | 000000000000 | STUVWXYZ |
  00000000`. Centers drop out — the spindle's retinue carries no state,
  exactly as the doc says.
- **The word display** — the move history as a literal word over the
  6-letter alphabet, with **scramble** (a 20-letter word; God's number
  says no state is farther), **unwind** (the word read backwards, every
  letter inverted, replayed fast like the solver videos), **reset**.
- **The two-alphabet split, demonstrated live:** address letters (⊘ frame)
  stay glued to cells while pieces rotate through them; occupant letters
  (∅ frame) travel with the pieces. Orientation ticks (a dot on each
  piece's primary sticker) make F/B edge-flips visible.
- **Pilish.** Returning the cube to solved (not by reset — no Pilish for
  shortcuts) earns:
  > *Now I turn a facet carefully, to settle every odd cubie homeward —
  > spiraling through emptiness.*
  Word lengths: 3·1·4·1·5·9·2·6·5·3·5·8·9·7·9 = π to fifteen digits.
- **Tests:** `tests/test_viewer_cube.py`. The cube math lives in a pure
  `CUBE_MATH` block (no DOM, no registry — purity is itself tested) that
  the test extracts and runs under node: every generator has order 4,
  (R U R′ U′)⁶ = identity, F/B flip exactly four edges while U/D/L/R flip
  none, EO parity stays even and CO sum stays ≡ 0 (mod 3) along 300
  random moves, and any word followed by its inverse returns to the
  solved string. Auto-skipped when node is absent. Suite: 26/26, loop
  tests untouched.

## Discipline notes

- `glyphs/knoll.py` re-run after the viewer edits: byte-identical registry
  and data block (the authored app changed, the generated data did not).
- Orientation conventions chosen, recorded in the block's comments:
  primary sticker = U/D else F/B; corner twist = clockwise index from the
  ±y normal (clockwise-from-outside has det = −1). Under these, solved is
  all-zeros and F/B are the flipping generators — the standard convention.

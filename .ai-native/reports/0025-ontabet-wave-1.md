# Report 0025 — ontabet wave 1 — the harness learns the laws

## What landed

**[done-line 0027](../done/0027-ontabet-harness.md) — met.** The ontabet
session came home in `docs/sources/files.zip` (the foreign review of the
creole-glyph-language envoy: 15 proposals, the recursive-pilish basin,
a fully-placed S-frame, a landing map of 7 pins · 7 builds · 5
measures, and a viewer spec). This session landed its Wave 1 — the
no-pin harness work — so measurement data has somewhere to land:

- **[language/basin.md](../../language/basin.md)** — the surveyed
  lexicon (24 frames on disk; S/I/O are bdo's, not restated), landed
  with a provenance header and parsed live by the generator, like the
  grip ledger. Editing a word is re-surveying.
- **[language/s-frame-placements.json](../../language/s-frame-placements.json)**
  — byte-exact from the zip; 27 S-words, every score MODEL-GUESSED.
- **[glyphs/knoll.py](../../glyphs/knoll.py)** — derives and re-verifies
  the incidence laws every run (closure = 3^dim, star = 2^codim,
  duality pairwise, graded census Σ = 125 both ways); emits the fans
  and the axis-code bits per cell (Kraft sum exactly 1); parses the
  basin (measured census, per-letter density as the first measured
  weight donor, cross-frame collisions knolled never deduped, the
  interstitial 27); loads the S placements through a structural gate
  (address collision / kind mismatch / short frame → refusal with a
  receipt); demotes MINTED terms without a non-example to OPEN,
  visibly. Schema grown ahead of data: placements, attestations,
  chips + escape, typed empties, sc — columns exist, values honestly
  OPEN.
- **[tests/test_knoll.py](../../tests/test_knoll.py)** — the laws
  recomputed independently; the §10 proof: Span and Semantics each sit
  fine alone, both claiming one cell refuses loudly. Suite: 217 OK,
  generator idempotent.
- **[epic.ontabet-speaks](../epics/epic.ontabet-speaks.json)** — the
  landing map transcribed as a PROPOSED epic (four waves); steering is
  bdo's.

**The gate noticed on first contact (§10):** the basin's own census row
claims 588 filled / 60 OPEN; parsing the same document measures
583 / 65. Recorded as finding `basin.census-arithmetic` in the
registry — reported, never edited. Also recorded: `basin.sio-not-restated`
(S recoverable from the placements artifact; I and O lists are nowhere
on disk — absence is information).

## needs-you

- **Stamp this PR** (done-line 0027) — the wave-1 harness.
- **The seven pins** (PIN-1…PIN-7, laid out in the zip's
  `landing-map.md` and `handoff-ontabet-session.md`). PIN-1
  (complementarity) and PIN-2 (placement law) are load-bearing;
  everything in waves 2+ assumes them. The Span↔Semantics refusal is
  also yours to resolve.
- **The unsealed export:** the `creole-glyph-language` package these
  files review has no receipt on `exports/log.jsonl` on any branch —
  it left the machine without a committed disclosure. Naming it, per
  the ledger's own rule.
- **No envoy return route exists:** the landing map leans on "the
  done-line 0016 flow" to admit the memo's 15 proposals per item, but
  0016 was a one-off import, not machinery. If returns keep coming
  home, that pen is worth minting (its own done-line).

## Conflicts named, not silently resolved

- The basin census arithmetic (above) — the artifact's self-claim vs
  its own content; held as a finding.
- The records pen minted ids 0026/0023 locally while the fleet-safe
  ids were 0027/0025 (sibling branches hold the lower ones); renamed by
  hand per `placement.py`. The pen itself folding across refs is the
  known out-of-scope item from report 0020, still open.

## Out of scope, named

BUILD-3 (viewer template port — the zip's `viewer.html` is the spec,
never the landing), all measurement runs (MEAS-1/2/3 need an
*uncontaminated* instrument — this session has read the placements and
is contaminated as a scorer; MEAS-2 needs an embedding endpoint), I/O
placement (gated on PIN-2), and the interstitial edge pole-pairs. Each
is its own done-line.

## End-state

`report` — wave 1 of epic.ontabet-speaks is landed and green: the laws
are machinery, the basin is parsed and measured, the placements are
gated in as PROPOSED, and the first falsifier the harness ran caught
the artifact's own census error. Ready for your stamp; nothing built
past any pin.

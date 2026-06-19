# causality/patterns/ — the Pattern Commons (v1), homed

The AI-native UX pattern vocabulary, evolved this session and brought out
of ungoverned foundry scratch into a governed home next to the Causality
surface. This is the **library** — the named vocabulary of how an
AI-native surface is built — together with the **playable portfolio** that
witnesses it and the **record of how it was evolved** (the experience SDLC
loop: a rubric gate, an issues channel, ten per-family agents, an
independent review, a reconciliation against the live spec).

It is the homed sibling of [`../display-system.md`](../display-system.md):
that file is the component/type **board** (what the engine must render);
this directory is the **pattern vocabulary** the generative typing process
and the experience skill compose surfaces *from*. `causality/` is the
surface that renders patterns; this Commons is the vocabulary it renders
them with — consulted **Commons-first**, so generation stays consistent
rather than random (the load-bearing third of *Interface as AI*).

## What evolved (the v1 shape)

v0 (26 patterns across 7 families) → **v1: 10 families, 53 patterns**
(15 decoration · 12 truth-capable · 26 ai-native), folded deterministically
by `merge.py`. The evolution honestly **re-tagged** the v0 craft patterns
against an AI-native acceptance gate (decoration is a valid, kept verdict —
the refused lie is calling a pretty-graph pattern "AI-native") and
**authored** three new ai-native families (Register & Provenance, Interface
as AI, Honest Async). The final merge gate found **0 verdict/axis
mismatches** — no inflation survived.

## The register triad (the spine of v1)

Every pattern is scored on three **orthogonal** facets, each on its own
display channel — reconciled against `../display-system.md` (the live spec
is the authority), recorded in `RECONCILIATION.md`:

- **register = commitment** → **line treatment + badge** (solid = ink /
  admitted record; dashed = pencil / proposed·simulated; broken = ghost).
  Bound to the generative-typing lifecycle (propose → admit) and the C4
  verdict classes, **not** a free enum.
- **strata = epistemic** → **colour / layer** (fundamental / derived /
  learned — display-system C1–C3, H4).
- **anima = felt** → **size / motion** (strength × tempo — display-system
  C18).

A node carries all three; no two facets compete for a channel. The
proposed `C19 · RegisterFacet` amendment to `display-system.md` is **held
for bdo's stamp** — it is bdo's spec (D-4), not written here.

## Contents

- `pattern-commons.v1.json` — **the evolved library** (the canonical
  output). **Do not hand-edit it** — it is the deterministic fold's
  output. To change a pattern, edit its family source and re-merge.
- `families/` — the ten per-family sources (`*.evolved.json`), one owned
  artifact per family; the editable truth the fold reads.
- `current-commons.json` — the frozen **v0 reference** (the source every
  family agent read; kept for provenance and diffing).
- `merge.py` — the **deterministic fold**: reads `families/*.evolved.json`
  (relative to its own dir) and regenerates `pattern-commons.v1.json`,
  re-checking every verdict against its axis scores (the final inflation
  gate). Run `python causality/patterns/merge.py`; it reproduces v1
  byte-identical from the families. **v1 is regenerated, never authored.**
- `portfolio.html` — the **playable portfolio** (the witness): each card a
  small live demo of its pattern, the register-grammar flagship on a real
  graph. Fetches `./pattern-commons.v1.json` relative; open under a static
  server. It is a witness, not a second source of truth.
- `RUBRIC.md` — the **AI-native acceptance gate** (the "tests"): the three
  axes and the derived verdict; what makes "AI-native" an earned label.
- `RECONCILIATION.md` — the **register-triad decision**: commitment = line,
  strata = colour, anima = motion, reconciled against `display-system.md`.
- `DEPOSITS.md` — bdo's refusals on the v1 render, lifted to intent (taste
  as a deposit — the editorial bars the next render must clear).
- `ISSUES.md`, `LOOP.md`, `PORTFOLIO-DONE.md`, `LAB-PARKED.md` — the **loop
  record**: the feedback channel, the SDLC process + agent roster, the
  portfolio done-line, and the parked theme/variation lab.

## Commands

```sh
# regenerate v1 from the family sources (deterministic — reproduces byte-identical)
python causality/patterns/merge.py

# the playable portfolio (served, fetches ./pattern-commons.v1.json)
python -m http.server 8080   # then open http://localhost:8080/causality/patterns/portfolio.html
```

## The hard rule of this directory

**`pattern-commons.v1.json` is PROPOSED.** Promotion past `proposed` is
bdo's alone (D-4) — a pattern is never minted by appearing here; bdo's
praise is the only promotion past the rubric gate. The **register triad is
reconciled to `../display-system.md`** — that live spec is the authority;
where this Commons proposes an amendment (C19), it stays proposed until
bdo stamps it. The **portfolio is a witness, not a second source of
truth** — and `pattern-commons.v1.json` is a fold output: edit a family
and re-merge, never hand-edit the canonical file (the same discipline as
`causality/examples/*.projection.json`).

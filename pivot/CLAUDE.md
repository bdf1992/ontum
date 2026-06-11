# pivot/ — the recoverability instrument

Pivot is a benchmark suite (epic.pivot): does deliberately-hidden
structure, encoded as a placement of meaning on the glyph cube, survive
recovery by natural model inference — and how deep does it recur? The
arc, the rung order, and the name are bdo's (done-line 0031).

## The two halves, and the wall between them

- **The harness is deterministic and never calls a model.** Stdlib
  only. It reuses `glyphs/knoll.py`'s cube (`ternary_cells`,
  `cell_kind`, `closure_of`, `star_of`, `verify_incidence_laws`) —
  never re-derives the lattice. It builds the recoverer's prompt, grades
  the returned placement against the laws, and scores it on a calibrated
  scale. Grading is pure: a contaminated builder cannot taint a verdict
  that only checks census and cell-kind.
- **The inference is done by cold agents.** Generation and recovery are
  played by a session/agent that has **never read the placements**. A
  session that has read `language/s-frame-placements.json` or the
  viewer is *contaminated as a scorer* (epic.ontabet-speaks,
  wave-3.measures) — the harness records recoverer provenance and
  refuses a contaminated grade.

## The calibrated scale (rung 1)

One number is meaningless alone; Pivot anchors it. Every recovery is
read between two controls:

- **random words** — the floor: no relation between word and cell,
  recovery ≈ chance.
- **surface-encoded** — the ceiling: the coord is forced by an obvious
  feature of the token (the cube's Pilish analog), recovery ≈ perfect.
- the **S-frame** (and any real onton encoding) sits between them — and
  *where* it sits is the measurement: how much structure the meaning
  actually carries.

## The law that bites (§10)

A recovery is a placement of 27 occupants onto the 27 addresses. It
**refuses to fit** when it is not a lawful tiling — a cell claimed
twice, a cell left empty, the census 8 corners / 12 edges / 6 faces / 1
center broken. The grader refuses such a placement rather than scoring
it as fine; that refusal is the gate doing its job. The container's own
incidence laws (Σ=125) are verified via knoll before any occupant is
placed.

## Run

```sh
python -m pivot.run --status              # the instrument, read-only
python -m unittest tests.test_pivot -v    # the laws and the refusal
```

Marks here are PROPOSED until bdo stamps. The S-frame placements stay
MODEL-GUESSED; Pivot measures against them, it does not mint them.

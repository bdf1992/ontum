# Report 0030 — the experience unit: an obligation, or it is weather

*First piece integrated through the new topology (done-line 0029): this PR
targets `claude/epic-experience-layer`, not main, and the loop integrates it
there. bdo sees the arc, not this piece.*

## What landed

**[done-line 0030](../done/0030-experience-unit.md) — met.** Wave 3 of
[epic.experience-layer](../epics/epic.experience-layer.json) opens with
`atom.experience.v0` — the typed experience and its birth-gate.

- **[loop/experience.py](../../loop/experience.py)** — an experience is a
  source beat composed with a registered surface, a context (the place), a
  granted expectation (a return shape with a non-empty terminal set), and a
  rung-checked backing. `experience_refusal()` is the birth-gate: an experience
  that obligates nothing is **weather**, and weather is refused — as are an
  unregistered surface, an unknown beat, a missing context, and a backing whose
  class holds no rung for the shape it must return. It composes the surface
  registry, the trust ladder, and the shape→capability obligation.
- The term `experience` stays **PROVISIONAL** (owed to the glyph-knolling
  ritual), as the epic directs; `loop/` stays pure.
- **[tests/test_experience.py](../../tests/test_experience.py)** — the §10
  proof: a well-formed experience is born; strip the obligation, surface,
  context, or rung and it is refused. Suite: 258 OK.

## needs-you

- **Nothing.** This piece integrated into the epic branch on its own; your
  stamp waits for the whole arc.

## End-state

`report` — the experience unit and its weather-refusing birth-gate stand,
composing the surfaces, the ladder, and the obligation a return shape carries.
Next piece into this epic branch: the launcher (live beats become launched
experiences). The arc reaches your stamp when it is whole.

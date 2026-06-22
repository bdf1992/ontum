# The generative basis — the membrane that cuts slots into a reality

**Status:** PROPOSED · owner **bdo** · companion to the panel report
([corpus-derivation-organ.proposal.md](corpus-derivation-organ.proposal.md)). Nothing minted.
**One line:** the five primaries are not the floor — they are one quantization of a transition space
under one pressure. The layer beneath them is a *membrane* that cuts slots into a reality; "five" is what
it emits under accountability pressure, the way RGB is what the eye's membrane emits under screen-emission
pressure. The instrument `loop/basis.py` makes this mechanical, not metaphor.
**Re-verified this session:** `loop/basis.py`'s §10 self-test runs and passes — it admits the four real
moves (POSTURE `DROP` under accountability, POSTURE `ADD` under governance, a legal `MERGE`, the two real
membrane cuts) and refuses the four fakes (a poetry `SPLIT`, a gamut-hole `MERGE`, a poetry cut, a
gratuitous cut). All five new citations resolve: `strata.md:42,69`, `node.py:108`, `act_fence.py:21`, and
`glyphs/viewer.html:192` — the last corroborated by `glyphs/knoll.py:51`, which names ⊘ literally **"the
null slot."** The corpus already held the cut/slot reading.

---

## 1. The reframe

Colour has no correct number of primaries: B&W (1), grayscale (2), RGB (3), CMYK (4), PANTONE (n) are
different spanning sets over the same perceptual spectrum, each fitted to a different pressure
(storage, screen-emission, ink-subtraction, exact-match). Cardinality flexes with pressure; the spectrum
underneath does not.

`APPEND · FOLD · HASH-IDENTITY · CITE · VERDICT` is ontum's "RGB under accountability pressure" — *a*
basis, not *the* basis. The spectrum underneath is the **transition space**: the moves a fact can undergo
on the log. A basis is a spanning set of transition-*roles* over it — moves, not nouns.

So the right object is not a fixed basis but a **basis-generator**: declare the pressure, and the basis is
fitted to it, expanding under discrimination and collapsing under economy. *Govern the pressure, not the
basis* — the setpoint discipline, one level up. This is "derive, don't pick" made structural.

## 2. The shaper (the one load-bearing definition)

- a **refusal** is a **discrimination** — a distinction a slot can reject on;
- a **pressure** is the **set of discriminations the medium must preserve.**

Everything else is computable from that. If this definition is wrong, the whole layer is wrong.

## 3. The slot lifecycle

A primary is a **slot** with a two-phase life, reusing the corpus's own mock→real lifecycle:

- **shape** — declare a role + its refusal-tooth. A slot that can refuse nothing is poetry, refused at
  shaping (this is `CITE`, turned on the basis itself).
- **fit** — an actual corpus operation occupies the slot and must satisfy its refusal. An unfitted slot is
  a **gap** — a named role with no machinery, surfaced, never faked (`loop/gaps.py`).

## 4. The gamut law

A basis move is legal only if it preserves:

- **coverage** — every operational term still decomposes into the basis;
- **grip** — every slot keeps a live refusal (no poetry slot, no wholly-redundant slot).

This is what stops "flexible" from meaning "arbitrary" — it is the colour-gamut constraint.

## 5. The four operators (under a pressure P)

- **SPLIT** a role when P needs a distinction it conflates — each child must keep its own refusal.
- **MERGE** two roles P cannot distinguish — *illegal* across distinct live refusals (a gamut hole).
- **ADD** a role when the medium has a discrimination no slot expresses — irreducible, carrying a refusal.
- **DROP** a role whose refusal can never fire under P.

## 6. The colour ladder

| basis | n | pressure (the dial) | slots |
|---|---|---|---|
| B&W | 1 | "did it happen?" | APPEND |
| grayscale | 2 | "what is the state?" | APPEND · FOLD |
| **work (RGB)** | 5 | accountability | APPEND · FOLD · HASH · CITE · VERDICT |
| governance (CMYK) | 6 | who-may | + POSTURE |
| meaning / fabric (PANTONE) | 5+n | consequence | + RELATE · PREDICT · SCORE … (CTA-1 discovers) |

`POSTURE` is ontum's "CMYK black": separated or folded depending on the press — a legal `DROP` under
accountability (its "who-may" is covered by `FOLD∘APPEND∘VERDICT`), a legal `ADD` back under governance,
where it re-earns an irreducible refusal: owner self-admit is FORBIDDEN (`act_fence.py:21`, D-4).

---

## 7. The membrane — the seam, generalized

The basis-generator is not a layer in the stack; it is the layer *between* layers. Its job is to cut
slots into a reality. A reality on its own is undifferentiated — the all-axes-open prior, ⊘. It has no
slots until something decides axes in it. That decider is the membrane.

This is not a new word. It is one of the corpus's most-minted ideas, verified:

- the **seam** is minted and enforced — a `VERDICT` lands at a seam, refusing any verdict outside its
  terminal set (`node.py:108`);
- the **membrane** is the seam at full generality — `strata.md:69` defines it as "the seam where 1.0 and
  3.0 negotiate; mismatch measured, not crashed"; and `strata.md:42` already lifts the seam past pipeline
  stages: "meaning is a relation across a gap, the seam between two."

So the seam was never "between two pipeline stages" — it is **between a reality and its basis.** Pipeline
seams are one instance (the harness pressure). The membrane is the seam at full generality.

**One correction, by the gamut law's own rule.** The temptation is to merge `seam = membrane = ⊘`. The
first identity is legal (same role, the membrane is the seam under negotiation pressure). The second is
*illegal*: ⊘ is the all-zeros wildcard **cell** (`glyphs/viewer.html:192`; named "the null slot" at
`glyphs/knoll.py:51`) — a position, the prior — while the seam is the **edge**, the act that cuts. They
carry distinct live refusals (positional vs. verdict-in-terminal-set); merging them punches a gamut hole,
losing the distinction between the uncut prior and the act that cuts it. The corrected stack:

```
⊘  (the prior — all axes open, the input the membrane cuts into)
  → SEAM / MEMBRANE  (the cut: VERDICT decides an axis, APPEND collapses 0→±, under a pressure)
  → BASIS  (the slots = the decided axes)
  → OCCUPANTS  (ontums in the slots)
```

The cube makes "create a slot" literal: a slot is a decided axis (`0 → ±`). The membrane's atomic act —
the **cut** — is `VERDICT (decide the axis) ∘ APPEND (collapse it durably)`, at a seam, under a pressure,
gated by the gamut law: a cut that discriminates nothing is poetry, refused. The basis operators of §5 are
compositions of cuts.

**Why the meaning center is hollow.** The meaning reality is currently all-⊘: no meaning-pressure has been
driven through the membrane, so no meaning-axes have been cut, so there are no meaning-slots to occupy.
CTA-1 is not "mint a record" — it is the **membrane's first stroke under meaning pressure**, the first
decided axis in a reality that is currently all-prior. That is why one crossing matters so much.

---

## 8. The proof — `loop/basis.py`

The layer is real because the instrument refuses bad moves, not because the prose is pretty. `loop/basis.py`
runs a §10 self-test and a membrane demo. **Run this session, output verbatim:**

```
basis algebra:
  [ADMIT ] DROP   POSTURE under accountability   (the report's demotion, computed)
  [ADMIT ] ADD    POSTURE under governance        (re-earns the D-4 refusal)
  [REFUSE] SPLIT  child that discriminates nothing (poetry — CITE on the basis)
  [REFUSE] MERGE  CITE + VERDICT                   (distinct live refusals — gamut hole)

the membrane (one organ, two pressures):
  [ADMIT ] CUT    work seam, accountability pressure
  [ADMIT ] CUT    meaning seam, meaning pressure   (CTA-1: all-⊘ → one decided axis)
  [REFUSE] CUT    poetry cut (discriminates nothing)
  [REFUSE] CUT    gratuitous cut (right axis, wrong pressure)
```

The POSTURE demotion in the report is no longer asserted — it is *computed* as a legal basis move, and so
is its re-emergence. The same machinery is the kernel of CTA-2's skill: deriving a corpus's primaries is a
`basis(pressure) → slots` call, and the self-demote-POSTURE test is one `DROP`.

---

## 9. The honest edge

This is a **model** of the membrane, not the membrane. The `cut` emits slots and reality-transitions in
the abstract; nothing yet binds a slot to a live corpus operation and confirms its refusal fires against
real code. A model of the membrane is not the membrane — and enriching the algebra further is where
elegance starts to outrun teeth.

The next move that produces something new touches live code, not the model:

- **`fit` one slot** — bind `CITE` to `consequence_graph.resolves` and confirm it rejects an unresolved
  citation. Turns the checker into the kernel CTA-2 ships.
- **Run CTA-1 for real** — drive RELATE · PREDICT · SCORE through `relation_ledger` with one actual
  meaning record, and get a real `PREDICTIVE`/`TRIVIAL` fold. The membrane's first *real* stroke.

Either is the honest continuation. More basis algebra is not.

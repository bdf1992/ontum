# The strata — four layers, one traversal

*Status of the correspondence: MINTED 2026-06-10 — bdo's direction
("organize our syntax, semantics, semiotics, all leading to what is
our Pragmatics"), shaped in-session. Provisional until knolled and
admitted. The cells and the traversal rule it stands on are PINNED.*

---

## The stack

| Stratum | Cell | Address | Decided axes | Status today |
|---|---|---|---|---|
| [syntax](syntax.md) | corner | **A** `(−,−,−)` | 3 | DERIVED — the grammar is real in `glyphs/` |
| [semantics](semantics.md) | edge | **I** `(0,−,−)` | 2 | OPEN — the metric is unbuilt |
| [semiotics](semiotics.md) | face | **Y** `(0,0,−)` | 1 | REAL — `glyphs/` is this stratum, running |
| [pragmatics](pragmatics.md) | center | **⊘** `(0,0,0)` | 0 | OPEN — the question this stack leads to |

## The traversal

`A → I → Y → ⊘` is a legal spelling in the coordinate grammar: open
x, then y, then z — corner → edge → face → center, one axis per step
(`docs/phase-2/autojective-polysheaf.md:119`, the only move the
coordinate allows). Each step is on the previous cell's seam-star: I
is requested by A, Y's seams include I, the center's seams include Y
(the knolling's address table). The cascade "terminates at the
obscured wildcard — the one cell … that requests nothing"
(`docs/phase-2/autojective-polysheaf.md:146`).

So the strata stack is itself one boundary traversal, and it
terminates at the open center. **"What is our Pragmatics" is the
spindle, not a missing chapter** — the stack does not end at an
answer; it closes around the question the way the 26 letters close
around `⊘`.

## The rule the mapping stands on (DERIVED)

Each stratum opens one more axis to context. A sign (− or +) means
*decided*; a 0 means *opened*
(`docs/phase-2/autojective-polysheaf.md:111`). Syntax is the fully
decided stratum — form is settled by rule alone. Semantics opens one
axis: meaning is a relation across a gap, the seam between two
decided forms. Semiotics opens another: a sign is one decision made
visible, organizing many relations. Pragmatics opens the last: use is
decided entirely by context, and the cell that represents it carries
no decided axis at all.

This is the classical formality gradient of linguistics (syntax most
formal, pragmatics most contextual), read off the geometry instead of
asserted.

**Non-example (the grip):** this is not Morris's triad plus a guest.
In the classical frame semiotics is the umbrella discipline and
syntax/semantics/pragmatics are its three divisions. Ontum runs
semiotics as a *stratum* because here the signs are authored
artifacts with a registry and a generator — the sign layer is a place
on disk, not the umbrella. bdo's framing (2026-06-10), recorded
rather than silently adopted.

## The creole map

The rosetta-creole reading (`docs/sources/rosetta-creole.md`, cited
as inspiration) distributes across the strata:

- **Grammar** — the geometry: the coordinate alphabet, traversal as
  spelling → *syntax*.
- **Lexifiers** — Python, JSON, English contribute vocabulary, never
  rules; the borrowed letterforms get ontum addresses → *semiotics*.
- **Membrane** — the seam where 1.0 and 3.0 negotiate; mismatch
  measured, not crashed or papered over → *semantics* (the comparison
  struct) and *pragmatics* (the negotiation).
- **Aliveness** — the language grows exactly where it fails to speak
  (the third verdict) → *pragmatics*.

## Recorded finding (vault, read-only)

`docs/phase-2/autojective-polysheaf.md:111` says "the count of zeros
in a cell's coordinate is its codimension," but line 115 calls corner
`A = (−,−,−)` — zero zeros — "codim 3." The zero-count is the cell's
*dimension*; codimension is the count of *decided* axes. The two
lines disagree by exactly this swap. Recorded here per the house rule
(finding, not fix); this file uses "decided axes" and avoids the
contested word.

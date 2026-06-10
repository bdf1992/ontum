# Syntax — the rules of legal form

*Mark (proposed): **A**, the corner `(−,−,−)` — fully decided on
every axis; the worked example's Self. Provenance of the mark:
MINTED, provisional until knolled.*

## Pin

Syntax is what makes a form legal before it means anything. In ontum
that is the coordinate grammar of `{−, 0, +}³`: what counts as a cell
(27, letters on the 26 decided-enough, the all-zeros center as
wildcard — `docs/phase-2/autojective-polysheaf.md:111`), and what
counts as a move — *open one decided axis*, "the only move the
coordinate allows" (`autojective-polysheaf.md:119`). Spelling is
boundary traversal: corner → edge → face → center, terminating at
`⊘`. The transformation rules are the cube's group action; the
cube-alphabet's piece types (corner / edge / center) are the typed
slots (`docs/phase-2/cube-alphabet.md:58`).

The deep syntactic claim: well-formed structure *requests its own
continuation*. A's seam-logic asked for exactly I, M, Q and stopped
(`autojective-polysheaf.md:127`). The grammar is generative the way a
creole's is — a small rule set producing the lattice, not a lookup
table of allowed strings.

## Creole reading

A creole's syntax is its own, never its lexifiers'. Ontum's
combination rules come from the geometry — not from Python, JSON, or
English, which contribute vocabulary only. A schema language borrows
its grammar from its parents; that is what makes it a cipher rather
than a language (`docs/sources/rosetta-creole.md`, cited as
inspiration).

## Holdings (real on disk today)

- `glyphs/registry.json` + `glyphs/knolling.md` — the address
  alphabet with its `seam of` and `requests` columns: the
  request-logic, operationalized and re-validated against the vault
  on every knoll.
- `glyphs/viewer.html` — the six generators, live state string,
  traversal made manipulable.

## Non-example

A JSON Schema for atom files is not ontum syntax. It is lexifier
grammar — a parent language's rules applied to ontum's carrier files.
Conforming to it makes a file well-formed *JSON*; it spells nothing
in the coordinate grammar.

## Open

- Nothing today *refuses* an illegal spelling. The grammar is
  described and rendered, but no check exists that two locally-fine
  moves cannot compose (the §10 test, applied to language). Until
  something can refuse, syntax is a description, not yet a gate.

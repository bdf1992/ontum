# Report 0017 — the language directory - strata as one traversal

## What landed

Done-line 0019: `language/` exists under its own governing
`CLAUDE.md` (composed into the root via `@language/CLAUDE.md`), with
[strata.md](../../language/strata.md) as the spine and one file per
stratum — syntax, semantics, semiotics, pragmatics. Each stratum
carries the grip discipline at stratum scale: pin (vault-cited, with
line numbers), creole reading (citing `docs/sources/rosetta-creole.md`
as inspiration, never as material), holdings (what is real on disk
today), a proposed mark, a non-example, and named holes.

The organizing move: the four strata are mapped to the four cell
types by a stated rule — each stratum opens one more axis to context
(syntax 3 decided axes, semantics 2, semiotics 1, pragmatics 0) — and
their marks `A → I → Y → ⊘` form one legal spelling in the coordinate
grammar (open x, then y, then z, each step on the previous cell's
seam-star). The stack terminates at the open center: **"what is our
Pragmatics" is the spindle, not a missing chapter.** The
correspondence is MINTED (provisional, 2026-06-10); the cells and the
traversal rule it stands on are PINNED.

Statuses, honestly: semiotics is the one stratum already real and
running (`glyphs/`); syntax is described and rendered but nothing yet
*refuses* an illegal spelling; semantics is a frame with no metric;
pragmatics holds bdo's question with status OPEN, plus the falsifiable
test (the agent-context emitter) named, not built.

Tests: 140 pass (`python -m unittest discover -s tests`, exit 0) —
including the in-flight reflect tests, see shared-tree note below.

## Recorded finding (vault, read-only)

`docs/phase-2/autojective-polysheaf.md:111` ("count of zeros … is its
codimension") and `:115` ("corner A = (−,−,−) — codim 3") disagree by
a dimension/codimension swap: the zero-count is the cell's
*dimension*; codimension counts the *decided* axes. Recorded in
`language/strata.md`; the vault is untouched. The strata files use
"decided axes" and avoid the contested word.

## Shared-tree note (named, not resolved)

This session worked on `claude/surface-reflector-ui`, which carries
another session's in-flight, uncommitted reflect work
(`loop/reflect.py`, `tests/test_reflect.py`, modified
`loop/summon.py`, `.claude/skills/reflect/`). Per the fleet
discipline those files were left untouched and excluded from this
session's explicit-path commit. `docs/sources/rosetta-creole.md` and
the `docs/sources/README.md` entry (bdo's source, filed but
uncommitted) **were** included, because the language directory cites
the source and a dangling citation at merge time is worse than a
trivial double-commit if the filing session also lands it.

## needs-you

- **The stratum marks (A, I, Y, ⊘ read as cells) are proposed, not
  minted.** They graduate only through the glyph-knolling ritual and
  your admission; until then they live in `language/` and
  `glyphs/registry.json` is untouched. Say the word and a knolling
  session reviews them under the grip discipline.
- **Pragmatics is yours to pin.** `language/pragmatics.md` holds the
  question with the frame and the candidate test (the agent-context
  emitter). The named collision in semantics — mark I vs the OPEN
  S·I·O trio — also waits on your pin of the trio.
- **The semiotics-as-stratum decision is recorded** (vs Morris's
  umbrella reading) in `strata.md` as your framing; flag if that
  misreads the directive.

## End-state

`report` — `language/` is set up and composed into the environment;
done-line 0019 met; one vault finding recorded; marks and pragmatics
queued on the owner.

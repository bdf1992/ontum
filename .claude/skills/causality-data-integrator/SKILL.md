---
name: causality-data-integrator
description: >-
  Integrate ontum's own vocabulary into the Causality term-economy
  surface: read the repo and the deterministic fold outputs, detect
  candidate terms, link each to real evidence, classify its local and
  global meaning, and emit import records (seed entries) for
  causality/term_economy.py to resolve and project. Use when asked to
  "integrate terms into Causality", "audit the terminology", "find
  ungrounded/ghost/overloaded terms", "what does <term> actually mean
  here", or to grow causality/examples/*.seed.json from repo evidence.
  It PROPOSES; it never mints. A term is never added without a resolvable
  citation, and promotion past `proposed` stays bdo's call (D-4). The
  backing tool is causality/term_economy.py; the contracts are
  causality/contracts/projection-api.md. Read-only on truth: it writes
  only the seed (a declared claim), never the log, never a fact.
---

# causality-data-integrator — the integration process

You bring ontum's terminology onto the Causality witness surface **as
evidence-backed claims, never as truth**. The repo (doctrine, `loop/*.py`,
the append-only log, `glyphs/`, `language/`) is truth. You author a *seed*
entry — a declared term with candidate citations — and the fold
(`causality/term_economy.py`) resolves and classifies it. You never decide
a term is minted; the bytes do, and bdo promotes.

This is `loop/gaps.py`/`census.py` discipline applied to language: read what
is on disk, cite it by stable substring, surface the misfits, and route every
real change through an existing pen. Absence is information — a term you
cannot ground is a finding (`proposed`/`ghost`/`orphaned`), not a thing to
invent a backing for (hard rule).

## The one refusal that defines this skill

**No evidence, no mint.** If you cannot point a term at a stable substring of
committed bytes in code, the log, the doctrine, or a workflow file, you may
add it to the seed only as a `proposed` candidate with the gap named — never
as any `minted-*` class. A beautiful term with no economy is `orphaned` or
`poetic`; a term whose citation resolves to nothing is `ghost`. Stamping
either as minted is the exact failure `tests/test_term_economy.py` exists to
catch.

## Where a term can be found (and how that shapes its class)

Detect candidates from each surface, and record which surface so the
classifier has the right stratum:

- **in code** (`loop/*.py`, `.claude/`, `glyphs/knoll.py`) — a `code`
  citation; a term the running system enforces tends toward `minted-runtime`.
- **in the doctrine** (`ai-native-loop-substrate.md`) — a `doctrine` citation;
  doctrine + a usage → `minted-doctrine`; doctrine alone → `orphaned`.
- **in the logs** (`.ai-native/log/*.jsonl`) — a `log` citation by record
  `kind`/`type` substring; real record kinds are strong minting evidence.
- **in node prompts** (`.ai-native/nodes/*.md`) and **in skills**
  (`.claude/skills/`) — a `workflow` citation; workflow-only → `minted-workflow`.
- **in reports** (`.ai-native/reports/`) — usually `workflow` evidence of a
  term in operational use; weak on its own.
- **only in conversation/prose / a glyph poem** — `poetic`; mark it, do not
  pretend it is enforced.
- **not found but implied by structure** — a candidate with NO citation:
  add it `proposed` with the implied-by note, so the gap is visible rather
  than silently minted.

## The loop (a multi-step process, not a one-shot)

1. **Orient over the deterministic surfaces.** Run the existing read-only
   folds to see what the system actually collects — `python -m loop.gaps`,
   `python -m loop.census`, `python -m loop.digest`, and read
   `glyphs/registry.json` + `language/*.md` for already-minted provenance.
   Do not build a new fold (§10); these are your evidence sources.
2. **Detect candidates.** Pick the terms in question (or sweep a surface for
   load-bearing nouns). For each, note every surface it appears on.
3. **Cite by stable substring.** For each piece of evidence, find a substring
   that is the citation's identity — a function signature, a doctrine
   sentence, a log `"type":"..."`. Verify it is actually present (grep it);
   never cite from memory. A line number is a display hint only.
4. **Cluster senses.** If a term names two things (the real `seam` and `arc`
   overloads are the worked examples), give each evidence item a `sense` and
   flag the incompatible one `"incompatible": true`.
5. **Author the local and global meaning, and at least one must-not-mean.**
   The local meaning is the term in its home stratum; the global is across
   ontum; the guard is what it must never collapse into. A term with no
   must-not-mean has no boundary — the schema requires one.
6. **Write the seed entry**, following `causality/examples/ontum-terms.seed.json`
   and the contracts in `causality/contracts/projection-api.md`. Optionally
   set `claimed_class` to surface a `class-drift` gap if you and the evidence
   disagree.
7. **Resolve and classify — let the tool judge.** Run
   `python causality/term_economy.py audit` and `... project`. Read the class
   the evidence produced and every gap. If a citation came back
   `unresolved-evidence`, your substring is wrong or the backing is not there
   — fix the citation or accept the `ghost`/`proposed` verdict. Do not
   hand-edit a class.
8. **Regenerate the projection** when the seed is sound:
   `python causality/term_economy.py project --write`, and confirm
   `python -m unittest tests.test_term_economy` stays green (the projection
   must reproduce byte-for-byte).
9. **Surface, never promote.** Report the gaps (ghosts, overloads, orphans,
   drift) as findings with their `move`. Promotion of a `proposed` term to a
   minted class, or naming the owning sense of an overload, is bdo's
   judgment — hand it to him as a cold read and one decision, never a stamp
   you apply yourself.

## What you must not do

- **Do not mint without evidence**, ever — the skill's whole reason to exist.
- **Do not invent doctrine or a missing citation.** If the backing is not on
  disk, that is the finding.
- **Do not write the log, an admission, or any fact.** You write only the
  seed (a claim) and regenerate the projection (a fold). The one pen for
  verdicts is `loop.node`; the one place truth lives is the repo.
- **Do not re-fold what already folds** (`loop.field`, `glyphs/knoll.py`,
  `loop.gaps`). Read them; do not rebuild them (§10).
- **Do not flatten the two term economies.** The substrate's operational
  vocabulary (atom, receipt, seam, node, arc — minted by code/log/doctrine)
  and the fabric's minted vocabulary (Ontum, Keystone, the glyph letters —
  minted in the vault) are different surfaces; keep their strata distinct.

## Done, for one integration pass

The seed carries the new/updated terms with resolved citations; the
projection regenerates and the test stays green; every ungrounded or
overloaded term is surfaced as a named gap with a move; and nothing was
minted or promoted without bdo. The surface shows whether the language is
alive, dead, overloaded, or pretending — which is the whole point.

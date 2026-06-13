# Term/fold audit — the method

*Deliverable #4, done-line 0060. How to compare what the deterministic
surfaces actually collect against what the terminology claims to be — and
how a term earns (or fails to earn) its economy class. The method is run by
`causality/term_economy.py`; this document is its written form and a worked
sample.*

## The question

ontum's vocabulary spreads faster than it is checked. A term can be:

- **minted** — enforced or produced by code/log/fold, defined in doctrine, or
  load-bearing in the workflow;
- **projected** — visible on the Causality surface, derived from evidence;
- **proposed** — useful but not yet grounded;
- **poetic** — a metaphor with no authority;
- **overloaded** — one word, two incompatible meanings;
- **orphaned** — a term with no live economy;
- **ghost** — visible in docs or UI but backed by nothing on disk.

The audit answers, for any term: *which is it, and what is the evidence?* It
never asks a human to remember; it reads the bytes.

## The three sources of truth (the fold never invents a fourth)

1. **The deterministic surfaces** — the doctrine (`ai-native-loop-substrate.md`),
   `loop/*.py`, and the append-only log (`.ai-native/log/*.jsonl`). What the
   running system actually produces and enforces.
2. **The minted-vocabulary surfaces** — `glyphs/registry.json` +
   `glyphs/knolling.md` (the building's structure, with provenance status
   PINNED/DERIVED/MINTED/OPEN) and `language/*.md` (the strata, with PROPOSED
   marks). ontum already carries provenance markers; the audit reads them, it
   does not replace them.
3. **The workflow surfaces** — `.claude/skills/`, `.ai-native/reports/`,
   `.ai-native/nodes/`. Where a term is used to do work.

Causality is **not** a fourth source. The seed (`examples/*.seed.json`) is a
*declared claim*; the audit's only power is to resolve that claim against 1–3
and classify. (causality/CLAUDE.md, the one hard rule.)

## The method, step by step

1. **Declare** a term and its candidate evidence as citations — each a
   `{stratum, file, contains}` pointing at a stable substring of committed
   bytes (a `line` is a display hint; the substring is the identity, because
   line numbers drift and a substring does not).
2. **Resolve** each citation: open the file, check the substring is present.
   Absent file or absent substring ⇒ the citation does **not** resolve. This
   is the ghost detector — a claim of a backing that is not there.
3. **Cluster** evidence by `sense`. Two evidence items with different `sense`
   labels, at least one flagged `incompatible`, mean the word names two
   objects.
4. **Classify** by precedence (the one rule in `classify()`):
   - declared poetic ⇒ `poetic`;
   - claims a backing, none resolves ⇒ `ghost`;
   - ≥2 incompatible senses, resolving ⇒ `overloaded`;
   - code resolves ⇒ `minted-runtime`;
   - doctrine + a usage (log/workflow) ⇒ `minted-doctrine`;
   - workflow only ⇒ `minted-workflow`;
   - causality-surface only ⇒ `projected`;
   - prose/poetic only ⇒ `poetic`;
   - lone doctrine, no usage ⇒ `orphaned`;
   - nothing solid ⇒ `proposed`.
5. **Surface gaps**, never patch them: unresolved citations
   (`unresolved-evidence`), ghosts, overloads, orphans, and any drift between
   a term's self-declared `claimed_class` and the evidence-derived class
   (`class-drift`). The move on each is an existing-pen verb or a human call —
   the fold writes nothing and decides nothing (D-4).

## What the fold does NOT do (§10 boundaries)

- It does not re-fold `epic.the-field`'s decomposition ladder (`loop/field.py`)
  or re-derive `glyphs/registry.json`. It *reads* both as evidence sources.
- It does not promote a term. Past `proposed`, promotion is a human/owner
  judgment; the integrator skill proposes, it never stamps.
- It does not mutate the log. It is a pure read, like `loop/gaps.py` and
  `loop/census.py`.

## Worked sample — the committed five

Run: `python causality/term_economy.py audit`

```
term-economy audit — what the evidence resolves to
  terms folded: 5
    minted-runtime   3
    overloaded       2
  gaps: 2
    [overloaded-term] arc: arc carries incompatible senses
        ['arc-as-confirmed-admission', 'arc-as-prose-narrative']
        that each resolve but cannot both be 'the' meaning
        move: split the term, or name one sense the owner
    [overloaded-term] seam: seam carries incompatible senses
        ['loop-event-surface', 'phase2-site-primitive']
        that each resolve but cannot both be 'the' meaning
        move: split the term, or name one sense the owner
```

- `atom`, `receipt`, `node` ⇒ `minted-runtime`: each has doctrine + code + log
  evidence that all resolve (e.g. `node` → D-10 at
  `ai-native-loop-substrate.md:101`, the pen `loop/node.py:68`, and
  `"type":"node_real"` on the admissions log).
- `seam` ⇒ `overloaded`: the loop's event surface
  (`ai-native-loop-substrate.md:458`, `loop/reconcile.py:34`) and the phase-2
  geometric primitive (`glyphs/knolling.md:147`, SETTLED, sourced to
  `docs/phase-2/autojective-polysheaf.md`) are **not the same object**. Both
  resolve. The word is doing two jobs.
- `arc` ⇒ `overloaded`: the enforced `arc_confirmed` admission
  (`loop/reconcile.py:168`, `"type":"arc_confirmed"` on the log) and the prose
  `"arc":` field in every epic JSON (documentary, no enforcement path). One
  word, an enforced sense and a documentary sense.

These two overloads were not invented for the demo — they are real seams in
the vocabulary the audit found by resolving citations. That is the point: a
locally-fine term and a locally-fine second usage *refuse to fit*, and the
fold notices (§10). A fabricated classifier that stamped everything `minted`
is caught by `tests/test_term_economy.py`.

## Comparing minted-vs-collected (the upstream reading)

The deeper comparison bdo named — *what the deterministic fold collects vs.
what is minted* — runs by feeding the audit a seed whose terms carry a
`claimed_class`, then reading the `class-drift` gaps:

- a term **claimed minted** but whose evidence resolves to `proposed`/`ghost`
  is vocabulary outrunning the system (a check the language is writing).
- a term the system clearly produces (a real log `kind`, an enforced code
  path) but which **no seed declares** is collected-but-unminted — a candidate
  the integrator skill should propose. (Enumerating those candidates from the
  log/code automatically is the integrator's next increment; this slice proves
  the resolve-and-classify spine it stands on.)

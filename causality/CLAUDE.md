# causality/ — the term-economy witness

Causality's first governed slice in ontum: not the canvas app, but the
**terminology-economy witness** behind it — a read-only fold that turns
ontum's own vocabulary into a reproducible, evidence-backed projection.
The owner uses it to see whether a term is *alive, dead, overloaded, or
pretending*. It is a new vertical slice of `epic.causality-surface` (its
witness register) and it does **not** double-build `epic.the-field`'s
fold or the `glyphs/` + `language/` minted surfaces (§10) — it reads
them.

Done-line 0060. The horizon it serves: Causality as the live visual
witness over the term economy (the repo stays the ledger, the fold stays
the deterministic reader, this surface makes the invisible structure
inspectable).

## The one hard rule of this directory

**Causality is a projection, never a second source of truth.** The
repo — doctrine, `loop/*.py`, the append-only log, `glyphs/registry.json`,
`language/*.md` — is truth. The `examples/*.seed.json` is *declared
input* a human or agent authors; `term_economy.py` only **resolves** that
input's citations against committed bytes and **classifies** what it
finds. A term is never minted by appearing here. Promotion past
`proposed` stays a human/owner judgment (D-4).

## Commands

```sh
# the term-economy fold — pure, read-only, stdlib, deterministic
python causality/term_economy.py project              # the projection, to stdout
python causality/term_economy.py project --write      # regenerate examples/ontum-terms.projection.json
python causality/term_economy.py audit                # gap findings + census (minted vs evidence)
python causality/term_economy.py mermaid              # text-first graph render of terms -> evidence
python causality/term_economy.py project --seed <path> # run over an alternate seed

# the §10 test (joins the main suite)
python -m unittest tests.test_term_economy -v
```

## The taxonomy (bdo's, done-line 0060)

Every term resolves to exactly one class, derived from which evidence
strata actually resolve on disk:

- `minted-runtime` — code/log/fold produces or enforces it.
- `minted-doctrine` — defined in the doctrine and used consistently.
- `minted-workflow` — used by skills / reports / node prompts.
- `projected` — visible only on the Causality surface, derived from evidence.
- `proposed` — useful but not yet grounded.
- `poetic` — metaphor only; carries no authority.
- `overloaded` — two or more incompatible meanings that must be split.
- `orphaned` — a lone definition with no live economy.
- `ghost` — claims a backing (file/line/record) that does **not** resolve.

The teeth (§10): a term with no resolvable evidence can never be
`minted`; a citation that points to nothing is `ghost`; two incompatible
senses surface as `overloaded` (proven on the real `seam` and `arc`
overloads). `tests/test_term_economy.py` fails on a fabricated/constant
classifier.

## Layout

- `term_economy.py` — the read-only fold (in the `loop/gaps.py` /
  `loop/census.py` grain: stdlib, no network, evidence is `file:line` or
  a log record substring, never prose). Resolve → classify → project →
  audit → render.
- `examples/ontum-terms.seed.json` — committed input: the five canonical
  terms (atom, receipt, seam, node, arc) and their declared evidence.
- `examples/ontum-terms.projection.json` — committed output, regenerated
  by the fold; byte-deterministic, reproducible from the seed.
- `audit/reality-audit.md` — Causality-as-presentation vs.
  Causality-as-living-surface (what is mocked / demo-only / missing).
- `audit/term-fold-audit.md` — the method: what the deterministic
  surfaces collect vs. what is claimed minted.
- `contracts/projection-api.md` + `contracts/schemas/*.json` — the data
  contracts for ingress and projection (Causality is one client, the API
  is the authority).

The integrator that authors seeds from repo evidence is a real skill:
`.claude/skills/causality-data-integrator/SKILL.md` (it proposes; it
never mints).

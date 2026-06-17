# causality/ — the term-economy witness

Causality's governed slice in ontum, now in two halves that compose into
**one solution** (done-line 0082): the **terminology-economy witness**
(`term_economy.py`) — a read-only fold that turns ontum's own vocabulary
into a reproducible, evidence-backed projection — and the **canvas**
(`canvas.html` + `canvas.js`), the agnostic graph engine homed here from
the experience-foundry prototype. The owner uses the witness to see
whether a term is *alive, dead, overloaded, or pretending*, and the
canvas to render and edit any typed graph (ontum's term economy and
holonsearch's fabric mesh are two presets). It is a vertical slice of
`epic.causality-surface` and it does **not** double-build
`epic.the-field`'s fold or the `glyphs/` + `language/` minted surfaces
(§10) — it reads them. The full display target is
[`display-system.md`](display-system.md).

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

# the Pattern Commons — DERIVED from the repo's common patterns (done-line 0097)
python causality/commons.py derive            # the grounded subset, graded
python causality/commons.py derive --json      # the raw dataset

# the curl-first HTTP layer (done-line 0097): the browser is one client
python causality/api.py serve                  # localhost:8077
curl localhost:8077/commons                    # the derived Pattern Commons
curl localhost:8077/projection                 # the committed term-economy view
python -m unittest tests.test_commons -v        # the §10 fold + curl-surface check

# the canvas — the agnostic graph surface (done-line 0082)
python -m http.server 8080      # then open http://localhost:8080/causality/canvas.html
node causality/canvas.persist.test.js    # the §10 persistence round-trip check (with teeth)

# Interface as AI — describe → local inference generates a schema-valid graph (0083)
node causality/authoring.test.js         # the §10 validate→instantiate check (valid lands, malformed refused)
open http://localhost:8080/causality/demos.html   # the component progress gallery
```

**Interface as AI** (front door, defined in `display-system.md`): authoring is
conversational — `authoring.js` sends a description + the live SCHEMA to local
inference and **validates the returned graph-spec against the schema before
anything renders** (a malformed spec is refused with a reason, never drawn). The
click-canvas / recursion / gallery are **witness lenses** behind it.

The canvas is **schema-driven**: one `SCHEMA` in `canvas.js` drives node
defaults, the inspector panel (click a node/route → edit its config), and
serialization (`toJSON`/`fromJSON` → localStorage + file export/import).
The node model carries the holonic display fields `sites` / `space` /
`strata{fundamental,derived,learned}` / `anima{strength,tempo}` — declared
now, populated by a later piece. A new node type ships as a `SCHEMA`
entry, not new code (that is the agnosticism). Never hand-edit toward a
non-schema field; add the field to the schema so the inspector and
persistence move together.

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
- `commons.py` — the Pattern Commons, **derived** from the repo's own
  common patterns (done-line 0097, bdo's "derive pattern commons from
  our common patterns"): each candidate names its **etymon** (the
  `file:symbol` it recurs at), the fold resolves it against committed
  bytes and grades it (`minted-eligible` / `proposed` / `ghost`).
  Grounded subset (`node`/`site`/`edge` + the strata) — `node:<kind>` is
  mined live from `canvas.js`'s `SCHEMA`. No grounding, no mint (the
  closure rule); promotion stays bdo's (D-4). Read-only, stdlib.
- `api.py` — the **curl-first** HTTP layer (done-line 0097, bdo's "curl
  first"): the projection-api contract made servable. `GET /commons`
  (the derivation), `GET /projection` (the committed view, verbatim
  bytes), `GET /health`; localhost, stdlib, no writes. One pure
  `route()` is the single source the handler and the test both call
  (I-4); the canvas fetches `/projection` from it and falls back to the
  committed file — the browser is one client, never the authority.
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

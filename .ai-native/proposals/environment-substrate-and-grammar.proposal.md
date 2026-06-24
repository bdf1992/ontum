# Proposal — the environment-instantiation substrate & its principled grammar

**Status:** PROPOSED (bdo's to steer). The capstone of the 2026-06-22 design
conversation that began as "a digest over owner-asks, a 30-minute meeting" and
walked up to the general substrate ontum has been becoming. Extends the
authoring-platform vision; `epic.calendar` is its first instance.

## The realization

The calendar was never a feature. It surfaced the general pattern: **ontum is a
platform for instantiating bounded, agent-equipped, record-backed environments
against pluggable storage targets.** Every piece a session reached for already
exists in ontum as a special case hardcoded to one target (this repo, on GH):
bounded tool access = the fence + pens; authored access = the gateway; system of
record = the log; "an instance of a pattern on file" = a worktree + its
CLAUDE.md. The substrate is ontum *generalized*. (The tell bdo named: he was
*describing* in prose what the platform should let him *declare* — the missing
primitive.)

## The layered stack (Git/GH is the wrong target — it's transport)

The record is the invariant; the backend is a plugin.

- **System of record** — the append-only, provenance-carrying truth (the log).
- **Repository** — the working set an instance operates on; a projection.
- **Source-control target** — Git / local FS / local-cloud / GH: *moves and
  syncs* the bytes. **Swappable — the target registry.**
- **Pattern** — a declarable, versioned template: which bounded tools, which
  agent, which data schema, which projection.
- **Instance** — a bounded environment created from a pattern; a room with
  authored tool access (a permanent named branch = "a Calendar admin").
- **Authority** — the three A's (authenticated · authorized · attributed): who
  may instantiate, who it's for, what tool use is authorized. The load-bearing
  layer (the difference between a sandbox and a *bounded* environment).
- **Projection** — how the instance is viewed/used (the calendar frame, the
  digest). A fold, never a second store.

**Targets, local-first first** (bdo): `local` (plain FS / local git — proves the
abstraction with zero infra, the kill-test: the calendar runs with no GH) →
`local-cloud` (self-hosted private / mesh-synced — reachable from the phone) →
`github` (a later optional plugin).

## The principled grammar (bdo's, 2026-06-22)

The 5 corpus-derived primaries were a basis emitted under one pressure, never a
floor (the membrane / RGB-vs-Pantone framing). Under the *integration* pressure
the basis is an **8 × 8 grid located in an 8-octant topology**:

**Surfaces (operands — what you refer to):**
| surface | meaning | ontum home |
|---|---|---|
| Records | what happened | the log |
| Repository | what's known | code + knowledge |
| Reason | why | the `because` / story / glue |
| Peers | who | independent nodes (D-2) |
| Names | what-this-is | content-hash identity, the seal |
| Settings | what's wanted | setpoints, owner stamps |
| Sessions | the doing | mortal runs in time |
| Resource | bounded capacity | the gateway — tokens, compute, budget |

**Operations (verbs — the moves):** APPEND (add to the record) · CITE (point at
knowledge) · VERDICT (judge/decide) · FOLD (read and reduce) · HASH (name and
seal) · ADMIT (authorize/set) · STEP (advance one bounded move) · SOURCE (draw
on as input).

**Topology axes (locate any operation against the boundary):** Region
(internal↔external) · Flow (ingress↔egress) · Reach (local↔global).

A **cell** is a `(operation, surface, octant)` type. The 64 are the closed
type-space of acts; the log is the instance stream; **the grammar is the type
system of the log.** An action like `find` is a *chord*: FOLD·Repository +
VERDICT(fit) + CITE·Names + SOURCE — not a primary. A cell that resolves to
nothing is a **ghost, refused** (the term-economy tooth, on the grammar itself).

## How the cells are learned (the established field + the ontum loop)

The named field: **selectional restrictions** (hard) / **selectional
preferences** (soft) — valency, Case Grammar, Frame Semantics. The proven
recipe *is* ontum's "log is truth, grammar is a fold":

```
act-log ──FOLD──▶ cells scored (Resnik selectional assoc. = KL/MI)
   ▲                          │
   │                          ▼
   │              PLAIN-ENGLISH DIGEST ──▶ bdo (SME) responds in plain English
   │                          ▲                          │
re-derive ◀── ENFORCE ◀── record verdict (D-4) ◀── inference TRANSLATES + VALIDATES
 (as usage    (fence refuses    (admitted,                (re-asks on uncertainty —
  grows)       out-of-grammar)   versioned)                gesture law; LLM proposes,
                                                           bdo is the authority)
```

- **Symbolic tier (v0):** classify each logged act into its cell; score with
  Resnik MI/KL; flag empty cells as the *candidate-forbidden* set. A fold.
- **Inferred tier (next):** cluster acts that *behave* alike (embeddings /
  Van de Cruys-neural / LDA) — `relation_ledger`'s deferred "admitted part."
- **The human-in-the-loop the field requires** (absence ≠ forbidden) is bdo as
  **SME giving plain-English feedback over a digest** — the same digest→verdict
  loop the owner-meeting (this session) already is. The calendar is instance #1;
  the grammar-digest is the meta-instance.

## The bootstrap — cold-start for a tool with zero usage (bdo's correction)

You can't learn from an empty log. So a tool is mapped by **fast/free probes
watched by an overseer**:

- **Fast** = a posture: loose policy, clear direction, simple tasks.
- **Free** = a knowledge-state: no working model of the target environment, no
  environment-specific skill. Naive on purpose — a naive agent's exploration
  reveals the environment's *true* affordances.
- The probes' tasks: **enter the environment, map it, use it, interact with each
  piece.** They generate acts + consequences. **They do NOT build the
  consequence graph** — an **overseeing system watches their work and writes
  it.** Actor acts; a different eye records the truth (D-2 applied to
  model-building — and it dodges the research's "LLMs are unreliable
  *authorities*" finding: the model is *derived from observed behavior*, never
  anyone's claim).
- Bonus honesty check: the docs/probes *claim* consequences; usage later
  *observes* them — claimed-vs-observed divergence is a first-class signal.
- Organs: `explore.py` (the fast/free probe), `observe.py` + gateway +
  activity-accounting (the overseer), `consequence_graph.py` (where it's
  written, populated from observed acts).

## Reuse (surveyed 2026-06-22)

- **holonsearch** (a 2-day autoresearch fork, patterns not libs): lift
  `mesh_guard.py`'s legal-space-per-seam + negative controls (the
  selectional-restriction teeth), `lineage_graph.py` (the typed-edge op×surface
  emitter), `harvested_models.py` energy-fold + `score.py` (read a measured
  act-stream, grade by consequence). It has **no** clustering/embeddings and
  **no** 8×8 — that half is the frontier.
- **the field** (inspiration, build native per "standards are a shape, not a
  spec"): Resnik KL/MI scoring + negative mining; VerbNet/FrameNet/SHACL as
  shape (ontum already has the enforcement organ — the fence/term-economy
  refusal — so we don't adopt SHACL, we borrow its shape).

## Open gaps (named, not solved)

1. **Bootstrap** (closed above): fast/free probes + overseer; docs are the
   probes' environment, not a parse target.
2. **Grammar versioning + non-retro-invalidation**: each grammar is a versioned
   admitted record, hashed onto the acts it judged (the `prompt_hash` pattern).
3. **Data-vs-SME contradiction**: a first-class divergence, surfaced not
   silently resolved.
4. **The grammar's heal reflex**: a restriction that bites wrong (over/under-
   containment) routes back to bdo (`heal.py`/`over_containment.py`).
5. **Reflexivity / §10 completeness**: the loop's own moves are cells
   (FOLD·Records, APPEND·Settings, VERDICT·Peers) — the grammar must self-host.
6. **Naming/scoping (bdo's call)**: is this a new repo or ontum's next layer?

## CTAs (build order)

- **CTA-1 — the classifier fold + SME digest (first running piece):** a
  read-only fold that classifies the live act-log into the 8×8, scores each
  filled cell (Resnik MI/KL), flags empty cells as candidate-forbidden, and
  emits a plain-English SME digest with the "is this allowed?" questions. §10
  teeth (the `mesh_guard` shape): a fabricated act in a forbidden cell is
  refused; the check discriminates. Dogfoods on the real log immediately.
- **CTA-2 — the SME-verdict intake:** bdo's plain-English digest reply →
  inference translates+validates → an admitted, versioned grammar decision.
- **CTA-3 — the target registry + `local` plugin:** prove the calendar runs
  with the record on a local backend, no GH.
- **CTA-4 — the fast/free-probe + overseer bootstrap:** cold-start a tool's
  consequence graph from watched naive exploration.
- **CTA-5 — the inferred tier:** clustering/embeddings (the learned cells).

`epic.calendar` is instance #1 — the thing this substrate demonstrates.

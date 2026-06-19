# Causality projection API — data contracts for ingress and projection

*Deliverable #2, done-line 0060. The minimal contracts for getting data INTO
Causality and projecting it back OUT. Causality is a projection and
interaction surface, **never a source of truth**: repo records, deterministic
folds, committed files, and explicit human/agent admissions remain truth.
Every contract below answers, for the term-economy slice that exists today,
what it would mean at the full surface.*

## The API-first rule

Every meaningful surface action has a non-browser equivalent. Today the
"API" is the `term_economy.py` CLI (`project` / `audit` / `mermaid`) over a
committed seed; the contracts here are the shapes that CLI reads and writes,
specified so a future HTTP layer, Playwright harness, or natural-language
client drives the *same* operations against the *same* records. The browser
is one client, never the authority.

## The eight families

Each family states: **what writes it**, **what reads it**, **its source of
truth**, **required vs. derived fields**, **what makes it invalid**, and
**whether it is authored / imported / folded / projected**. Families marked
*(schema)* have a machine-checkable JSON Schema in `schemas/`. Families marked
*(spec-only)* are contract-defined here for the full surface but not yet
emitted by this slice — named, not faked (absence is information).

### 1. TermNode *(schema: `schemas/term-node.schema.json`)*
- **Writes:** `term_economy.build_projection` (the fold). **Reads:** the
  Causality canvas, the audit, the integrator skill.
- **Source of truth:** the repo bytes the term's evidence resolves against —
  NOT this node. The node is a view.
- **Required:** `id`, `term`, `class`, `record_kind:"projected"`. **Derived:**
  `class`, `senses`, `evidence_count`, `resolved_count` (all computed from
  resolved evidence). **Authored (via the seed):** `local_meaning`,
  `global_meaning`, `must_not_mean`.
- **Invalid when:** `class` is outside the taxonomy; `term` empty; a derived
  field disagrees with the evidence edges (a TermNode whose `class` you cannot
  reproduce from its edges is a forgery).
- **Origin:** **projected** (folded from the seed + repo).

### 2. EvidenceEdge *(schema: `schemas/evidence-edge.schema.json`)*
- **Writes:** the fold. **Reads:** the canvas (draws the wire), the audit
  (resolves it), a human checking provenance.
- **Source of truth:** the cited file's committed bytes.
- **Required:** `id`, `from`, `to`, `stratum`, `resolved`, `ref`,
  `record_kind`. **Derived:** `resolved`, `file_exists`. **Authored:**
  `stratum`, `ref`, `claim`, `sense`, `incompatible`.
- **Invalid when:** `stratum` outside the enum; `ref` missing a `file`; `from`
  not a `term:*` id; claiming `resolved:true` for bytes that are absent (the
  fold computes `resolved`, so a hand-set value is ignored — the bytes win).
- **Origin:** **imported** (the citation is authored) then **folded** (the
  resolution is computed).

### 3. SiteNode *(schema: `schemas/site-node.schema.json`)*
- A place a term *lives* — a file, a log surface, a doctrine section, a
  glyph cell. The `to` end of an EvidenceEdge points at a SiteNode address.
- **Writes:** the fold, by interning each distinct `ref.file`. **Reads:** the
  canvas (collapses many edges into one site), the audit.
- **Source of truth:** the file/record on disk.
- **Required:** `id`, `address` (repo-relative path or log ref), `kind`
  (`code|doctrine|log|workflow|vault|surface`), `exists`,
  `inbound_term_count`, `record_kind`. **Derived:** `exists`,
  `inbound_term_count`.
- **Invalid when:** `address` escapes the repo root; `kind` mismatched to the
  path.
- **Origin:** **projected**. *Today:* emitted by `term_economy.build_projection`
  as `sites[]`; it indexes evidence places and never overrides the cited bytes.

### 4. ArtifactNode *(spec-only)*
- An ontum artifact a term names — an atom, a receipt, an admission, an epic.
  Distinct from a SiteNode (a *place*); an ArtifactNode is a *record*.
- **Writes:** a fold over the log (`loop.reconcile.Fold`). **Reads:** the
  canvas, the audit.
- **Source of truth:** the append-only log (the artifact's id and hash).
- **Required (full surface):** `id`, `artifact_id`, `artifact_hash`, `kind`.
- **Invalid when:** `artifact_hash` not present on the log; editing the
  artifact (a new hash) without a new node.
- **Origin:** **folded** from the log. *Today:* the term-economy slice cites
  log records by substring, not by interning ArtifactNodes; the full surface
  folds them from `loop.reconcile`.

### 5. FoldObservation *(spec-only)*
- A single read a deterministic fold made: "`loop.gaps` reports N mock
  stages", "`loop.census` calls `loop/census.py` idle". The bridge between
  ontum's existing folds and the canvas.
- **Writes:** an adapter around an existing fold (`loop.gaps`, `loop.census`,
  `loop.field`, `loop.digest`) — never a new fold (§10).
- **Reads:** the canvas (runtime register), the audit.
- **Source of truth:** the existing fold's output (which folds the log).
- **Required:** `id`, `source_fold`, `observed`, `at_record` (the log offset
  the observation is true as of). **Derived:** all of it.
- **Invalid when:** `source_fold` is not an admitted read-only fold; the
  observation claims a write.
- **Origin:** **folded**. *Today:* `term_economy.audit` is itself a
  FoldObservation producer; wrapping the other folds is later.

### 6. ProjectionView *(schema: `schemas/projection-view.schema.json`)*
- The whole rendered fold: TermNodes + SiteNodes + EvidenceEdges + summary + gaps. The
  unit the canvas loads and the audit reports.
- **Writes:** `term_economy.build_projection`. **Reads:** the canvas, the
  audit, the byte-reproducibility test.
- **Source of truth:** the seed + repo, deterministically. Delete the view and
  rebuild it; it is byte-identical (the projection property).
- **Required:** `view`, `generator`, `term_count`, `site_count`,
  `class_summary`, `terms`, `sites`, `evidence_edges`, `gaps`. **Derived:**
  all of it (it is a fold).
- **Invalid when:** it carries a timestamp or any non-reproducible field;
  `class_summary` disagrees with the `terms`; re-running the fold over the
  same seed yields different bytes.
- **Origin:** **projected**.

### 7. GapFinding *(schema: `schemas/gap-finding.schema.json`)*
- A place the vocabulary refuses to fit: an unresolved citation, a ghost, an
  overload, an orphan, a class-drift. The audit's teeth.
- **Writes:** the fold. **Reads:** the audit, a human deciding, the integrator
  skill (what to propose next).
- **Source of truth:** the divergence between a claim and the bytes.
- **Required:** `kind`, `term`, `why`, `move`. **Derived:** all of it.
- **Invalid when:** `kind` outside the enum; `move` is a verb no pen offers
  and not "needs bdo" (a finding must name a real next step, like
  `loop.gaps`).
- **Origin:** **folded**.

### 8. TermMintingState *(spec-only — the lifecycle a term moves through)*
- The state machine over a term's class: `candidate → proposed →
  {minted-runtime | minted-doctrine | minted-workflow | projected} `, with
  side-states `overloaded`, `orphaned`, `ghost`, `poetic`. Not a record the
  fold emits per term (the `class` IS the current state); a contract for how a
  term *transitions* and who may move it.
- **Writes:** transitions are proposed by the integrator skill and the fold
  (which computes the evidence-derived state); promotion past `proposed` is an
  **owner/human admission** (D-4) — the surface never self-promotes.
- **Reads:** the integrator (refuses to mint without evidence), the audit
  (class-drift), a human.
- **Source of truth:** the evidence (for the computed state) and the log (for
  any human promotion).
- **Required (full surface):** `term`, `state`, `evidence_class`,
  `promoted_by` (nullable), `at_record`.
- **Invalid when:** `state` is a minted class while `evidence_class` is not
  (minting without evidence — the one thing the surface must refuse);
  `promoted_by` set by a non-owner for a minted state.
- **Origin:** **folded** (evidence_class) + **imported** (a human promotion).

## The invariant across all eight

A record's `record_kind`/origin is always one of **authored** (a human/agent
claim, e.g. the seed), **imported** (a citation brought in), **folded**
(computed from a source of truth), or **projected** (rendered for the canvas).
No contract is a *source* — every one points back at the repo. The moment a
Causality record is treated as authoritative over the file or log it
projects, the design is broken (the same rule `loop/`'s cache lives by).

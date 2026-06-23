# Outcome — the spec-particle foundation (multi-session)

Reframed per the panel (ratified **false** → these are the required
teeth): this is an **outcome** (per `outcomes/`), not a single done-line.
Each session lands one **node-scoped frozen done-line** that reduces the
gap; unresolved criteria stay visible as continuing pressure.

## Maximal outcome

Documents (requirements · user stories · arch diagrams · expectations ·
suggestions) are first-class **versioned, gated, refactorable spec
particles**, and the grammar adapts a real **non-ontum** target — proven
by one real requirement run end to end with full provenance.

## The bar — 7 criteria, hardened by the panel

1. **Identity & versioning** *[Names/HASH]* — content-hash identity,
   **never a `.vN` id-string** (forbid the recorded id-vs-hash hole;
   cite heal/#424). Create + supersede are **appended** provenance
   records (`--by`, ts, reason; supersession names `old_hash` AND
   `new_hash`; no retro-invalidation). State is **derived by folding the
   appends**, never from file-bytes/proximity (D-8). Spec bytes under an
   eol-exempt `.gitattributes` path. Idempotence key
   `(node, spec_content_hash)` — editing restarts review, the prior
   verdict no longer applies (I-2). §10: an in-place byte edit mints a
   new version the fold sees; an id-string/constant impl fails.
2. **Soundness gate with teeth** *[Reason/VERDICT]* — "soundness" = an
   enumerable predicate set (every cited requirement/atom resolves, else
   ghost-refused; no two live specs contradict on the same scope; each
   requirement carries a checkable acceptance condition). A verdict cites
   which predicate held; a refusal cites the failed clause. Non-vacuity =
   a **matched-variant corpus** (sound vs unsound differing only on the
   soundness axis), fails if the gate is replaced by a constant, and no
   false-refuse of a sound corpus (T6). Satisfied **only by an
   `admit-real`'d node** (a mock/fixed verdict is a rubber-stamp).
   Deterministic, attributable receipts keyed `(node, spec_hash)` with
   `prompt_hash`. Summoned **independently of the author** (seam
   contract). Acquires an `inference_queue` slot, respects
   `concurrency_bound`, receipts `saturated` under backpressure.
3. **Spec→atom invalidation link** *[Repository/CITE + mesh]* — the edge
   records the **served spec content-hash**; "current" = compare the
   atom's served-hash to the spec's live head hash (a **recomputed
   fold**, never a stored stale-bit). The edge is an **appended log
   fact** citing both hashes (consequence-graph tier-1 shape), written
   through a pen that resolves both endpoints; a ghost edge is refused.
   Flagging is **read-only** (no auto re-gate cascade); the recursive
   projection is bounded radius + decay. §10: the flag fires on the right
   serving atoms, not unrelated ones; a constant impl fails.
4. **Topology→setpoint config** *[Settings/ADMIT + topology]* — the
   mapping is inference-**proposed** (slowloop grain), made live **only**
   via a `--by` admission (`authorized_by` cited). An inferred setpoint
   passes the disposer `auto_admit_fence` (heating capped); out-of-fence
   escalates to bdo. An un-admitted target runs a **named safe
   deny/minimal default** (no implicit code fallback); re-mapping
   **supersedes**. Demonstrate **one** concrete boundary-relative mapping
   (e.g. an Ingress placement admitting a real backpressure/concurrency
   dial) on the outward target; refuse an ambiguous placement.
5. **Independent acceptance** *[Peers/FOLD]* — acceptance is a **fold**
   over logged acceptance receipts (acceptor, spec content-hash,
   `prompt_hash`), never a stored boolean; keyed to the content-hash so
   an edit invalidates prior acceptance (closes accept-v0-then-edit
   laundering); the acceptor must be `admit-real`'d. §10: a forged
   self-acceptance (acceptor == author) is refused at the seam
   (node.py, D-2).
6. **Outward proof** — one real non-ontum requirement runs
   intake → spec → governed work → accountable receipt as a **continuous
   appended trace** (each step cites its predecessor, foldable; not a
   terminal receipt over an unaccountable middle, not an in-memory
   script). Exercises the **refuse** path (an unsound variant caught with
   a cited reason) AND the **independent-acceptance** path (a forged
   self-accept refused), not only the happy path. The governed-work
   receipt cites the served spec hash + a compute/budget figure (slot
   lease).
7. **Landed (per node)** — each node lands with its own passing receipt +
   independent review + on main. Completion emits an **appended record**
   citing the receipt/admission ids that satisfy each criterion
   (atoms_on_main reading-half), and "panel ratification" resolves to an
   appended panel-verdict record — so "did it complete?" is answerable
   from the log alone.

## Out of scope (deferred, planned, not dropped)

P5 CI/CD ([deferral-p5.md](deferral-p5.md)) · P6 fleet/Administrator
([deferral-p6.md](deferral-p6.md)) · the full traversable mesh (only the
minimal spec→atom link is in scope).

## Nodes — one at a time

- **NODE 1 (now):** spec identity + versioning + supersession as a
  **content-hash fold** — criterion 1 done right + the §10 non-vacuity
  test. The load-bearing floor: the gate's idempotence key, the spec→atom
  served-hash currency check (3), and per-version acceptance (5) all
  derive from content-hash identity. If identity inherits the `.vN` hole,
  they all silently inherit it.
- **NODE 2+:** soundness gate (2) · spec→atom link (3) ·
  topology→setpoint (4) · peer acceptance (5) · outward proof (6). Each
  its own frozen done-line.

# Done-line 0167 — The consequence graph v0 — the auditable tier-1 plane, read-only, with the non-vacuous ghost-refusal tooth

Written before code, per §9.4. When this line is met, stop.

> **Done when:** `loop/consequence_graph.py` is a read-only, stdlib fold that
> materializes the **tier-1 consequence-graph plane** from real log edges only —
> one node shape carrying a `kind` (atom_version, atom_base, receipt, arc, actor,
> finding, consequence), and tier-1 edges that are literal log facts
> (receipt_for, judged_by, version_of, member_of_arc, authored_by, finding_for,
> consequence_of); folds **failure** (drag) marks from negating receipts and
> **repair** marks from healed bites onto nodes, and reads declared
> `consequence.observed` events as **cited consequence nodes** so the plane shows
> consequence, not just provenance; runs **one bounded, typed, decaying
> propagation pass** (radius 2, threshold 0.20, per-edge-kind decay; actor and
> authorship edges render but never propagate; arcs receive but never fan out to
> sibling atoms; drag and repair stay separate channels and never net across
> type); emits deterministic JSON (`--json`) and a prose render; and **REFUSES
> any mark or consequence node whose citation does not resolve** against the log,
> listing it as a gap (the §10 ghost tooth). Proven by `tests/test_consequence_graph.py`
> joining the suite and **non-vacuous**: a fixture log asserts (a) a seeded ghost
> citation is refused as a gap, (b) a drag mark propagates receipt -> atom_version
> -> atom_base -> arc with decay and does NOT cross an actor hub or reach an arc
> sibling, and (c) two runs are byte-identical — the test FAILS on a fold that
> skips the citation check or lets actor/arc-sibling propagation through. The work
> is atom-backed under epic.consequence-graph-response with the suite green.

## Why

A foreign peer-architect reviewed the consequence-graph + mark-to-market proposal
(envoy package `consequence-graph`, sealed 2026-06-21) and returned GO for one
small piece: the read-only tier-1 graph plane. bdo confirmed the arc
(epic.consequence-graph-response, adm.6a176eb59681). This is that piece — the
keystone everything else hangs off, built without a single inferred edge or
generated target.

The load-bearing correction the review sharpened: the plane earns the name
*consequence* (not a prettier provenance view) only when it carries **cited
consequence nodes** — a changed state distinct from the work-unit — and the
ghost-refusal tooth is **non-vacuous** (it can actually fire on a real bad
citation, the failure mode the repo has been bitten by before).

## In scope (one increment)

- `loop/consequence_graph.py` — the read-only fold: nodes + tier-1 edges + floor
  marks + declared consequence nodes + one bounded decaying propagation pass +
  citation resolution (the ghost tooth) + `--json` and prose render.
- `tests/test_consequence_graph.py` — the non-vacuous fixture test (ghost
  refusal, propagation discrimination, determinism).
- A `loop/CLAUDE.md` module-layering line for the new fold.
- The backing atom under epic.consequence-graph-response.

## Not in scope (named, not invented away)

- **Tier-2 inferred causal edges** — no bounded generation; tier-1 literal log
  facts only.
- **`exemplar` and `value`/money marks** — deferred; a passed gate is the
  correctness floor, not excellence, and money must split into
  loved/adopted/reused/pattern-setting before it propagates.
- **The consequence volume / generated owner faces** — later pieces.
- **Actuation** — the field gates, selects, or re-values nothing; read-only,
  witness before actuator (the disposer fence is a later done-line).
- **A new graph engine** — `causality/canvas.js` renders; this fold feeds it.

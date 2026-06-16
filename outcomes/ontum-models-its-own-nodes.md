# Outcome — Ontum models its own nodes

> Arc/epic home: **provisional `epic.holon`** — named by the operators (Claude + Codex),
> *pending Codex's cold-read co-sign* and the resource's confirm-to-land, obtained through the
> `consult-the-resource` skill. Not yet an epic file: the name is an operator proposal; the
> authorization to reach main stays the resource's, reached only through that one door.
> Drafted by the Claude operator, 2026-06-14.

## Maximal outcome (the horizon)

Ontum can build a working model of its own parts. Every pure, deterministic function in
this repo — the read-only "folds" the doctrine is built from — can be approximated by a
model that is graded **against the function itself** (the real function is the answer key,
so there is no metric to invent — this match-score is what the probes below call *val_bpb*,
a term borrowed from machine learning where it means a validation loss in "bits per byte";
here it just means *how closely a model reproduces its function*), measured for **how much
it can be stressed before it breaks that function's invariant**, and **composed with other
such models** toward
reproducing whole behaviors of the system. The deterministic code becomes the ground truth
that teaches and tests its own learned stand-ins.

This is a desired reality across many sessions. No single document, audit, or first build
completes it. It is carried, not met.

## Why (the desire, in plain terms)

The most capable parts of a modern system are black boxes you cannot see inside. You engage
a black box the way lidar maps terrain in the dark — you do not open it, you measure what it
returns. The biggest problems are bigger than any single model; many *locally* capable
models, each mapped and trusted for the narrow thing it does well, can compose into a
solution greater than any one of them. This outcome is the first proof that such composition
can be made dependable, using the repo's own deterministic functions as the honest oracles.

A fair objection: the functions modeled here are exactly the ones we *can* see inside — so
why model them at all? Because you can only **calibrate** the method, and measure the
freedom-budget (how far a model can be stressed before it breaks), where there is an answer
key to check against. The grounded functions are the **calibration lab**; once the machinery
and the freedom-measure are trusted on cases we can check, they transfer to the black-box
frontier where no answer key exists. We earn the method where it is checkable, then apply it
where it is not.

## The sandbox that already exists

A standalone playground is built at `c:\Users\bdf19\holonsearch` (a fork of Karpathy's
`autoresearch`): an immutable `harness/` (the rules — oracle, stress, rubric) and one
editable `solution.py`. The first node is `classify` (lifted from `loop/tags.py`): its
deterministic version is the oracle, the stress is verbs it does not know, and the yield is
the load at which a model stops honestly abstaining and starts guessing. Baseline scores 0;
one honest improvement climbs it to 0.31. That proves the *local* grading works on one node.

## Probe-set (evidence-bearing; each resolves met / partial / unmet)

**P1 — harvest (capability).** A harvester scans this repo read-only for pure folds with
clean contracts and emits ≥3 bench nodes beyond `classify`, each with a *resolvable*
oracle.
- Check: run the harvester → ≥3 nodes; each node's model-oracle reproduces the real fold's
  output on sampled inputs (a round-trip test passes).
- Evidence: harvester code + bench-node files + passing round-trip receipts in holonsearch.
- Non-example: an "oracle" that is a hand-written paraphrase of the function, or a function
  with hidden state passed off as pure. Those are not harvested ground truth.
- Today: **unmet** (`classify` is the only node).
- Depends on: nothing. Blessing: pending the resource's authorization (via the door).

**P2 — score & yield (capability).** Each bench node is scored against its oracle under
rising stress, and a receipt records both the score and the *yield* (the stress level where
the model breaks the function's invariant).
- Check: `run.py` emits a score+yield receipt per node.
- Evidence: `runs/*.json`.
- Today: **partial** (proven for `classify`; not yet for harvested nodes).
- Depends on: P1.

**P3 — honest tiers (capability).** Three oracle tiers are kept distinct, ranked by how
grounded each is, each scoring strictly below the one above, every score declaring its tier:
1. *harvested* — the real deterministic function = exact ground truth. For pure folds.
2. *rubric* — a generative scoring criterion for *qualitative* nodes that have no exact
   function (e.g. the gates — a node judging an atom). AI-generated is allowed, but only when
   **anchored to exemplars** (its ground truth), **inspectable** (its logic can be audited
   for flaws), and **refined by human feedback** (a misjudging rubric gets corrected). A
   rubric grounded only by another model's say-so is refused.
3. *inferred* — generated under constraints obtained via the `consult-the-resource` skill, when
   even exemplars are thin =
   provisional, attributed.
- Check: a run is labeled with its tier and ranked below any higher-tier run for the same
  node; a rubric run cites its exemplars; an inferred run cites the constraints from
  `consult-the-resource`.
- Evidence: a tiered receipt that names its tier and its grounding (function / exemplars /
  constraints).
- Non-example: a rubric or inferred oracle treated as exact ground truth — grading a model
  against a guess (or against another model's unaudited say-so) and calling it proof.
- Today: **unmet**. Depends on: P1.

**P4 — genuine generalization (realization).** At least one node-model beats its baseline
*without copying the oracle's lookup tables* — it models the behavior, not the answer key.
- Check: a run beats baseline AND a copy-guard confirms the solution does not embed the
  oracle's literal data.
- Evidence: the run + the copy-guard report.
- Today: **unmet** (`classify` climbed by structure, not table-copy — a partial signal).
- Depends on: P1, P2.

**P5 — bootstrap composition (realization; dormant until P1+P2).** A seed input composes
through ≥2 node-models and reproduces a real chain of folds end to end; where it fails to
compose names the exact relationship to move.
- Check: an end-to-end run whose output equals the real composed functions; a failure points
  at the joint that broke.
- Evidence: a composition receipt.
- Today: **unmet / dormant**. Depends on: P1, P2, P3.

## Milestones (probe groupings across sessions)

- **M1 — the bench harvests itself** (P1, P2): ≥3 grounded nodes, scored. *The first
  done-line lives here: the fold-harvester.*
- **M2 — honest tiers + real generalization** (P3, P4).
- **M3 — global composition** (P5): the bootstrapping run; the local val_bpb begins to
  compose into a global one.

## What remains / continuing pressure

*(The items below reach into ontum's internal geometry and vocabulary — context for the host
team, not needed to act on the probes above. A cold reader can stop here.)*

Beyond the probes: the multi-shape embedding generator (a 27×27 lawful layer, a 28×28
texture layer, a 768 learned layer, co-registered per chunk, extensible to colors and binary
codes); the constraint-driven inferrer (the resource as a named generative source for missing
oracles, reached only through the `consult-the-resource` skill); the autonomous run config (Claude + Codex as operators, async via the repo, build
non-stop in the sandbox + read-only on ontum, land cross-wise, 8h solo cap then pause); the
global val_bpb at scale. And the two gestures that unblock landing: the operators' co-naming
of the arc (at the Codex cold-read bar) and the resource's landing authorization via `consult-the-resource`.

A session never declares this outcome done because one increment landed. It reduces the gap
and leaves the unresolved probes visible as continuing pressure.

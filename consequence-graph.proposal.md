# The consequence graph + mark-to-market (PROPOSED — bdo's, 2026-06-20): validate the consequence, not the work

**Status:** PROPOSED. **Naming and the arc are bdo's (D-4); a session may only
propose.** Born from the 2026-06-20 design conversation: *"I want to validate
your consequences, not your work … a framed digest over the sauce and its
history across many axes … propagation tagging … we should mark our money."*
Companion memories: `ontum-consequence-policy-model`, the platform blueprint,
`ontum-friction-and-healing` (retro/heal as the failure sensors). This file is
the spine; the per-piece tools land later, one at a time, each citing it.

## The reframe (two audiences, two surfaces)

This applies **D-2 (two acceptances) to the owner's seat specifically.** Peers
validate the **work** — the diff, in isolation, on its own terms; that stays.
bdo, as owner, never reads a diff again. He validates the **consequence**: what
the work *became* in the context of its purpose.

The pivot the conversation turned on:

- **What is *done* is generated.** The owner-facing surface — docs, onboarding,
  roadmap, user base, statistics, digests, narratives — is a *rendered* view of
  what the work became. Bounded generation fills it.
- **What the *target* is, is never generated.** The bar each face is measured
  against does not come from a prompt. It comes the other way — out of
  **review, failure, retros, exemplars, consequence-review** — and is *derived
  from what actually happened.* Generating the target would be hallucinating the
  goal; that is the one thing this design forbids.

The generated surface is the *brochure*. The derived target is what makes it
*honest*. The keystone that connects them is a graph.

## The keystone: a derived consequence graph

Everything above needs one substrate that does not yet exist: a **typed graph
of the work and its consequences**, on which marks can propagate and against
which the faces can be measured.

What it **is**: a **fold/projection over the log** — nodes are the units already
on the record (atoms, receipts, arcs, nodes, sessions), edges are the relations
between them. A *derived* graph, never a second source of truth (Causality's one
hard rule). The log stays truth; this materializes its shape.

What it is **NOT** — the don't-double-build guard (§10, `parity`'s
`dont-double-build` verdict):

- not a new graph **engine** — `causality/canvas.js` already renders any typed,
  schema-driven graph; this *feeds* it.
- not a new graph **fold** — `term_economy.py` already resolves citations and
  classifies; `field.py` folds arcs; `atom_search.py` types atom records. This
  composes them.
- not a new **truth** — inferred edges are PROPOSED and cite evidence; a citation
  that resolves to nothing is a `ghost` and is refused (the term-economy /
  parity tooth, verbatim).

The new thing is the **edge layer + the mark/propagation layer** on top of
engines that already exist.

## Edge classes — this answers "what does a mark propagate along?"

The mesh is built in three tiers, weakest-but-real first:

1. **Real (folded now).** Provenance edges already on the log: authorship
   (`--by`), atom→receipt→merge, arc membership, version lineage, the seam
   handoffs. Free, fully grounded, available today. *Authorship/time*
   propagation.
2. **Proposed (inferred, gated).** The *causal* edges from the consequence-policy
   model — *this piece enabled that one* — mostly are **not on the record.** They
   are inferred by **bounded generation** (this is the "abuse AI's pattern
   recognition through bounded generation" bdo named), each emitted as a
   **proposed** edge that **cites its evidence**, and refused if the citation is
   a ghost. Proposed never silently becomes real.
3. **Recorded (accreting).** Going forward, causal/enablement edges become a
   first-class record kind, so future work carries real edges instead of
   inferred ones — the graph sharpens itself over time.

So the answer to the open question is **all three** — ship on tier 1, infer
tier 2 under the gate, accrete tier 3 — not "fake a causal graph that isn't
there."

## Marks and "mark our money" — this homes "what counts as money?"

A **mark** lands on a graph node: `exemplar`, `failure`, `value` ("money").
Two sources, layered:

- **The floor (folded from gated events).** A review verdict, a `retro`
  recurrence detection, a `heal` finding — already on the log — fold straight
  into marks. Free, grounded. But this floor only sees *correctness*: it knows
  *passed every gate*, not *was actually good*.
- **The gesture ("mark our money").** A piece can clear every gate and be
  mediocre. **Money is richer than passing** — *you loved it, it got
  adopted/reused, it set a pattern others copied.* That signal the gates do not
  capture, so it needs a deliberate stamp: a first-class `value` mark a reviewer
  or the owner places, **still citing why.** This is exactly why bdo coined the
  phrase — the gesture is not optional, it is the point.

> **The one seam that stays bdo's:** *what counts as money?* The graph is the
> substrate the money-marks ride; it does not decide their values. Passing gates
> as the floor is a session's to wire; the definition of an exemplar — loved /
> adopted / pattern-setting — is the owner's seed, and garbage seeds make a
> garbage target.

## Propagation = the living target (mark-to-market)

Marks **propagate along the edges**. Downstream of an exemplar inherits its
pull; downstream of a failure inherits its drag. The **propagated field is the
living target** — *mark-to-market for the codebase*: nothing stays worth what it
was at landing; it is continuously re-valued by what it connects to *now*.

The teeth, and the failure mode they prevent:

- **Typed.** "Various patterns" = `pull` (exemplar), `drag` (failure), `value`
  (money) each propagate by their own rule; they do not collapse into one scalar.
- **Decaying.** A mark attenuates with graph distance. A mark that propagated
  everywhere would mean nothing — that is the **over-containment** failure from
  the model-free-mode work (equivalence classes collapse until signal averages
  away). Decay is the bound that keeps the signal.
- **Cited.** Every mark names the review/failure/retro/gesture that minted it.
  No ungrounded mark, same tooth as everywhere in the repo.
- **Netting.** Exemplar-vs-failure on one lineage net against each other —
  `herald` already does this for agent reputation; this reuses the pattern.

## The consequence-volume (the owner's surface)

The faces bdo named are the *rendered done*, each measured against the derived
target — a **volume** filled by bounded generation across three axes: **face**
(the kind), **time** (span and history), **arc** (per epic).

| Face | The fold that already feeds it |
|---|---|
| Digests | `digest.py` (one face, already live) |
| Product statistics | `census` + `activity` + `energy` + `impact` |
| User base / team / culture | `herald` roster + reputation; provenance per log line |
| Health / incidents | `heal` + `gaps` + `retro` |
| Roadmap | `epics/` (arc + horizon) + `outcomes/` |
| Docs / system map / onboarding | the `@`-imported `CLAUDE.md` surface + doctrine |
| Changelog / release notes | merge receipts (`landed_atoms`, D-13) |
| Economy / cost | `activity` accounting + `census` |
| Proof / trust | tests, receipts, the gates' own bite |

The architecture of every face is **fold-then-frame**, never generate: a
deterministic fold gathers cited evidence, generation only *frames and
narrates* what the fold found, and a **gateway refuses a face that asserts past
its evidence.** That is the "set of tools and a policy and gateways" — they are
not decoration; they are what stops a "Product Statistics" page from inventing a
number. The sauce is already real, so the faces are honest *by construction.*

## What exists already (so this is mostly composition)

`canvas` (render), `term_economy` (resolve/classify graph fold), `field`
(arc fold), `herald` (propagation over vouching edges — the propagation seed,
scoped to agents), `retro` (failure-pattern mining), `heal` (where a mark bit
wrong), `digest` (one face). **The organs exist. What is missing is the edge
layer, the mark layer, and the propagation fold** — and the volume that renders
the faces against the propagated target.

## Open seams for bdo (the steer)

1. **What counts as money?** (above) — the owner's seed; the rest defaults to it.
2. **Advisory → actuating.** Default assumption: the field is **read-only
   first** (you validate consequence against the bar; the cut stays yours) and
   only actuates the gates/selection later, behind the disposer fence
   (propose-first is the repo's law). Wave off if you want the gate itself to go
   consequence-based sooner.
3. **Volume primary axis** — default **face-primary** (one page per kind, arc as
   a filter), matching how a company is read; `digest`'s arc-first view becomes
   one drill-down.

## The smallest real first piece (§9.4, when met, stop)

Not the volume, not the faces — the keystone, in its weakest-but-real tier:

> A read-only fold that **materializes the tier-1 graph from the log** (real
> provenance/arc/lineage/seam edges only), folds the **floor marks** from
> existing gate/retro/heal events onto it, runs **one typed, decaying
> propagation pass**, and renders the result into the existing `canvas` — with
> the §10 tooth that a node carrying a mark whose citation does not resolve is
> refused. No inference, no gesture, no faces yet: prove the graph + marks +
> propagation are real and grounded on edges that already exist, then grow tier
> 2/3, the gesture, and the volume as named pieces.

This makes the keystone real on day one without a single ungrounded edge or
generated target — and everything else hangs off it.

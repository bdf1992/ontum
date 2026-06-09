# The Autojective Polysheaf

*A system of primitives treated as sites — where the join is a primitive too.*

---

## Core principle

You write code for **primitives** and **local sites**. You never write the whole.

The whole is emergent: it is computed over how the primitives are wired, the same way a manifold is computed over its atlas, never authored as a separate object. There is no `cube.py`. There is no `world.py`. There is a set of small authored parts and a rule for reading the structure they induce.

The non-obvious move is that **the join is also a primitive**. In most geometry the join is assumed — the boundary operator ∂, the incidence relation, the attaching map. It is treated as *structure* (a relationship that exists once the parts exist) rather than as *substance* (a thing you build). This system reifies it. The join is authored, the same way a Site is authored.

---

## What you don't have a name for: the glue

Geometry already names it; the names just live in traditions that treat the join as first-class:

| Tradition | What the glue is called | What it buys |
|---|---|---|
| Differential geometry | **transition function** (chart-to-chart) | the manifold is *only* charts + transitions; never written globally |
| Čech / sheaf theory | **cocycle / gluing data** | the glue carries a consistency condition: did it glue, how, with what residual |
| Cellular sheaf | **restriction map** | the glue along an incidence; identity-via-neighbors |
| Nerve of a cover | **a simplex** | overlap is reified *as a cell* — the join becomes a primitive |
| Cobordism | **the cobordism** | the between-thing as its own manifold |

**Chosen name: Seam.** A Seam is the join reified as a primitive site. Formally it is a transition-cocycle: it carries not a boolean ("joined / not joined") but the full comparison struct — how strongly, what residual, on which overlap, removable or not. A failure to seam is data, not an error.

This resolves the discomfort: you are not writing "edge, and separately some glue logic." You are writing two kinds of primitive — the **Site** and the **Seam** — and both are first-class authored objects.

---

## The three objects

**Site** — a primitive treated as a local frame. Holds its local stalk (its intrinsic content, with dynamics, not frozen as static data), an inward encoding (a smaller system composed within it — arithmetic, lettering — authored as interior sites by the *same* relay), an axis/antipode structure, and its outgoing maps. A Site is simultaneously a *whole* (when you stand in it) and a *part* (when a larger scale surveys it).

**Seam** — a primitive that is a join. Connects Sites and carries the comparison between them as a cocycle. The Seam is where coherence and obstruction live. A Seam that does not close is not a bug; it is where the system's most informative content sits.

**Atlas** — not authored. The emergent index: the collection of Sites and Seams plus their incidence. The whole is read off the Atlas; it is never written as its own file.

You write code for: Sites and Seams.
You never write code for: the Atlas, the whole, the global object.

---

## What "autojective polysheaf" means

**Polysheaf** — a sheaf built in Poly. The sheaf supplies the coherence/obstruction layer (overlapping local meaning, the thing Poly does not natively give you). Poly supplies motion, interaction, and self-rewiring. Sections carry dynamics, not just static fields.

**Autojective** — self-casting. From *jacere*, to throw: subjective (thrown-under), objective (thrown-against), projective (thrown-forth), **autojective (thrown-by-itself)**. An autojective structure generates its own slots *and* the constraint that shapes what may fill them.

So the **autojective polysheaf is the shaper**: a structure that (a) holds local-meaning-with-dynamics at each Site, and (b) generates the constraint that governs how new Sites, Seams, and slot-fills are produced. It is authored once. An LLM generates *into* it. The shaper is what makes 64+ sites tractable instead of 64+ hand-authorings — you author the constraint, the model fills the slot, the shaper guarantees the fill is consistent with the Site's neighbors and metric.

Build the shaper before the shape. The shaper is the autojective polysheaf. The shape is the generated content.

---

## Local frame vs. universal frame

A token (say, the letter **A**) has two distinct identities:

- **Local frame** — A-in-this-Site. The stalk of A on one Seam/Site. Authored, specific, finite.
- **Universal frame** — A-as-such. *Not authored.* Induced by every Site A participates in. It is the global section assembled from all the local A-instances.

When you encode A in an edge, you are not defining A. You are defining one restriction of A. A's universal frame depends on each Site A is within. This is the same local/global distinction as the whole system, applied to a single token.

Antipode is site-relative: A's antipode in the actuator-axis frame differs from A's antipode in the lettering frame. An antipode is a ±1 involution on a Site's stalk along an axis through the centroid. The centroid may be its own antipode (a fixed point).

---

## The relay runs both ways, on one contract

The pattern is: **declare a Site → build it from itself → survey and bind to its neighborhood → promote the neighborhood to a Site and recurse.**

- **Outward** (scale-up): local → regional → global → universal. Each surveyed region becomes a Site.
- **Inward** (compose-within): the encoding system inside a Site is *itself* a Site-relay — site within site within site, bottoming out at the null/unit centroid.

Both directions use the **same four-step relay and the same contract.** This is non-negotiable: if the inward encoding and the outward scaling use different composition rules, a token's interior and exterior will not glue, and the token stops being one token.

---

## Load-bearing commitments

These are the prices that keep the system engineering rather than poetry. Each one was a place the structure could have leaked.

1. **There is a metric.** Coherence must be *measurable*, which requires an inner product on the stalks. For semantics, the metric is *manufactured*: data aggregation plus LLM conversion of raw meaning into comparable stalk-values is the measurement instrument. The metric is not assumed — it is produced by the aggregation-plus-conversion step.

2. **Versioned instances are harmonic representatives.** Coherence is computed instant; its *history* is persisted. The version store holds the gauge-fixed (harmonic) representative under the fixed metric — not raw cochains. Otherwise two versions could differ purely by regauging, and the diff would report a phantom obstruction event.

3. **Obstruction is operational, not chosen.** Author a change → rerun coherence → diff against the versioned instance. The diff reads off which of three happened: **dissolved** (lower obstruction), **preserved** (same class, invariant), **created** (a class that wasn't there). "Better state" is a domain-supplied slot applied *after* the diff. The architecture supports all three identically.

4. **Cross-scale comparison map.** Recursion is not free. When a region is promoted to a Site, its metric must transport up — either lifted from the scale below or re-manufactured by the same aggregation step. The relay must carry, at each rung, *how its metric relates to the rung below*. Without it, a regional obstruction and a global obstruction are measured in incommensurable units and cross-scale diffs report phantom events.

---

## Install order

1. **Author the site contract (the shaper / autojective polysheaf).** Fields every Site and Seam exposes: stalk-with-dynamics, inward encoding, axis/antipode, restriction maps, and the generation constraint. Authored by hand, once. Shared by both relay directions.
2. **Install one Site fully.** Pick A-in-an-edge — the "perfect point" promoted to a perfect Site. Build its stalk, interior encoding, axis, antipode, and maps.
3. **Author one Seam.** Connect A's Site to a neighbor; make the cocycle real.
4. **Let the LLM generate the second Site into the shaper.** Check whether it seams to the first. If it glues, the shaper works. If it produces a phantom mismatch, the metric isn't fixed — regauge before scaling.

---

## Worked example: the seam is the request

This is what "mapping" means, made concrete, and it shows the load-bearing claim of the whole system: **content requests its own extensions through logic.** You do not author the atlas. You author one Self, and its seams name what comes next.

The cube is the ternary space {−, 0, +}³ — 27 cells. The count of zeros in a cell's coordinate is its codimension. A sign (− or +) means *decided* on that axis; a 0 means *undecided / opened*. Letters fill the 26 decided-enough cells; the all-zeros center is the obscured wildcard.

### The procedure

**Determine the Self.** Pick the point at corner `A = (−,−,−)` — codim 3, fully decided on every axis.

**Create the Site.** Build A's stalk: its intrinsic content, its interior encoding, its value under the manufactured metric. A is now a complete *local* object. Nothing about A's neighbors is authored yet.

**Find its seams — by logic, not by hand.** A's boundary is found by the only move the coordinate allows: open one decided axis to 0. Three axes, three seams:

| open axis | seam coordinate | what it is | letter |
|---|---|---|---|
| x | `(0,−,−)` | edge on the x-axis | I |
| y | `(−,0,−)` | edge on the y-axis | M |
| z | `(−,−,0)` | edge on the z-axis | Q |

A did not *have* these. A's seam-logic *requested* them. The point asked for exactly three edges, named them, and stopped — because a fourth would require opening an already-open axis, which is no longer A's boundary.

**Name a seam as a Self.** Take the x-seam `(0,−,−) = I` and promote it to a Self. Examined as a Self, an edge's own boundary is the two cells that *decide* its open axis: x = − gives `(−,−,−) = A`, x = + gives `(+,−,−) = E`. So:

> **edge I = seam(A, E)**

The edge *is* the seam between two points, named as a Self. And now edge I, as a Self, runs its own seam-logic and discovers it needs endpoint `E` to close. **Installing the seam requests the next Site.** That is the cascade:

```
build A (point)
  └─ A's seams request edges  I, M, Q          (open one axis)
       └─ promote I to Self → edge I = seam(A,E)
            └─ edge I requests endpoint E        (decide its open axis)
                 └─ build E → E requests its edges …
       edges request faces                       (open a 2nd axis)
            └─ faces request the center           (open the 3rd axis)
                 └─ center (0,0,0) = ⊘            requests nothing
```

The queue runs corner → edge → face → center, opening one axis per step, and **terminates at the obscured wildcard** — the one cell with no decided axis, anchored by no pin, that requests nothing because it is the null/generative slot. The generation loop closes exactly where the un-seamed frontier bottoms out.

### Mapping the axis and the aux

The same coordinate logic that finds the seam also names two things for free:

- **Axis.** A seam's axis is the coordinate it opened. Seam I opened x, so I *lives on the x-axis*; this is also the antipode axis — reflecting A across `x = 0` gives E, and reflecting through the center (all three axes) gives the global antipode `H = (+,+,+)`. Naming the seam names its axis with no extra authoring.
- **Aux.** Each Self may carry auxiliary channels keyed to its axis — e.g. a letter paired with an actuator and a data value on a given axis. The aux rides the seam's axis: when A requests edge I along x, any x-axis aux (actuator, signal, value) is what that seam transports. The aux is the optional payload the autojective shaper attaches to a typed seam.

### Why this matters

The seam types from the review apply directly: `seam(A,E)` is a **gap** seam (A and E are adjacent but disjoint — the obstruction is *extension*, can a section bridge the void with what residual), not an overlap cocycle. The gap seam is simultaneously the coherence check *and* the generation target. Typing the seam tells the shaper what to generate next; running the coherence check tells it whether the generated bridge holds. One operation, two payoffs.

---

## Acceptance criteria

- A Site can be authored without reference to any global object.
- A Seam returns a comparison struct, not a boolean; a non-closing Seam is preserved as data.
- The same contract governs the inward encoding and the outward scaling.
- A token's universal frame is computed from its Sites, never authored.
- Two versions of a coherence state can be diffed and classified dissolve / preserve / create.
- The metric survives one scale jump via an explicit comparison map.
- The LLM generates a new Site into the shaper and it seams to an existing one without phantom mismatch.

If all seven hold for A-in-an-edge and one neighbor, the system is installed and the rest is repetition of the relay.

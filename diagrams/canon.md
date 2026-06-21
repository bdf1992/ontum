# canon.md — the architecture-diagramming SME

The named authority the gate ([`qa.py`](qa.py)) enforces. Every refusal
cites a principle **here**, by name — never taste-by-assertion. This is
the "SME intent" of the part made concrete: the diagramming
subject-matter expert, written down, so a generated or hand-authored
diagram is judged against a canon a cold reader can check.

This is the **governor**. The `data-visualizer` advisor
(`~/.claude/skills/advisors/data-visualizer/`) is a **sub-advisor**,
summoned only for genuinely quantitative genres (sankey, metric
overlays) — it ranks encodings of *magnitude* (Tufte/Cairo channel
hierarchy), and an architecture diagram encodes *connection and type*,
which has no magnitude to rank. Using it as the governor produces false
teeth (baseline/pie rules that never fire) while missing the real ones.

## The three sources

1. **Moody, *The Physics of Notations*** (IEEE TSE, 2009) — the
   evidence-based theory of what makes a *visual notation* good. The
   Tufte of diagram *languages*. Its nine principles are the spine below.
2. **Graph-drawing aesthetics** — Purchase's empirical readability
   studies (crossings hurt most), Battista/Eades/Tamassia/Tollis.
3. **C4** (Simon Brown) — disciplined containment depth (context →
   container → component) for the containment and recursive-zoom genres.

## Moody's nine → the gate's teeth

Each principle names the rule(s) the gate may refuse on, and a
non-example (the grip discipline: a rule with no refusal is decoration).

1. **Semiotic clarity** — one symbol per concept; no overload (one symbol,
   two meanings), excess (a symbol for nothing), redundancy, or deficit.
   → *Gate:* a node whose `type` is not one of the declared types →
   **deny** (a symbol with no concept). *Non-example:* two distinct node
   types rendered with the same shape+accent (overload) — refuse until
   one is re-treated.

2. **Perceptual discriminability** — symbols must be clearly tellable
   apart; the primary visual variable should carry the distinction.
   → *Gate:* **>2 accent colors** in one diagram → **deny** (the palette
   is two accents; kind beyond that is carried by *treatment*, not a third
   hue). *Non-example:* a rainbow of node fills standing in for type.

3. **Semantic transparency** — a symbol should *suggest* its meaning; a
   reader should infer it, not memorize it.
   → *Gate:* an **invented shape / genre** with no entry in the canon →
   **deny**. This is the rule that refuses the "membrane cross-section" as
   a reusable genre. *Non-example:* a novel glyph that "means containment"
   with no published or declared notation behind it.

4. **Complexity management** — explicit means to handle a big diagram:
   modularization and hierarchy, not one sprawling canvas.
   → *Gate:* **>8 sibling nodes** in one row/container → **deny-with-"split"**
   (graphic economy + Miller's 7±2). Recursive zoom is the *positive* form:
   a node expands into its own gated sub-diagram. *Non-example:* fifteen
   peer boxes crammed to avoid a second diagram.

5. **Cognitive integration** — explicit means to read *across* diagrams
   (so a split set still composes).
   → *Gate (deliverable rule):* a diagram that is one of a set must carry
   the **"what is deliberately not shown"** caption and a link to its
   siblings. *Non-example:* a sub-diagram with no breadcrumb to its parent.

6. **Visual expressiveness** — use the available visual variables
   (position, shape, treatment, the two accents), not shape alone.
   → *Guidance, not a hard deny:* the renderer's node treatments
   (rect/rounded/hexagon/rhombus/dashed/pill) exist so kind reads at a
   glance; a diagram that flattens everything to one shape is weak, but
   it is *advised*, not refused.

7. **Dual coding** — text *and* graphics together; neither alone.
   → *Gate:* a node with no label → **deny** (graphics without text).
   Edge *semantics* live in the prose caption, not on the edge (the
   SubProtocol rule: "the graph shows topology; the prose carries
   semantics"). *Non-example:* unlabeled boxes left to the reader to name.

8. **Graphic economy** — keep the count of distinct symbols small and
   cognitively manageable.
   → *Gate:* the node-type vocabulary is **closed** (the declared set);
   adding a shape is a canon change, not a per-diagram choice. Pairs with
   §3 and §4. *Non-example:* a one-off shape minted to make one diagram
   look special.

9. **Cognitive fit** — different dialects for different audiences/tasks
   (a sketch for thinking vs. a hero diagram for the record).
   → *Guidance:* Mermaid for live iteration, `compose.py` SVG for the
   canonical record; both honor this canon. Pick by audience and lifespan.

## Graph-drawing aesthetics → the gate's teeth

- **Minimize edge crossings** (Purchase: the single largest readability
  cost). → *Gate:* an **edge segment passing through an unrelated node**
  → **deny** (the existing Liang–Barsky `check_edges_through_nodes`). An
  edge crossing a **subgraph label band** → **deny** (the label-band
  no-fly rule, born from a real visible-collision incident).
- **Every node reachable / no orphans.** → *Gate:* an **orphan node**
  (no edges) → **deny**, and a node **untraceable to a hub in ≤4 hops**
  → **deny** (cognitive load).
- **Minimize bends; favor symmetry and uniform edge length.** →
  *Guidance* the grid-snap aid serves; not a hard deny.

## C4 → the containment / zoom genres

Containment depth follows C4's levels (context → container → component);
recursive zoom is the mechanized form. A containment diagram that mixes
levels in one frame (a system-context box next to a code-class box) →
**deny** (level confusion) once the containment genre lands.

**Regions are first-class declared structure** (done-line 0151): a boundary
a node *belongs to* by declaration (`node.region == region.id`), not a
rectangle that happens to enclose it. This is the structure the fixtures and
features stand on — the plane and its boundaries before snap and genres.
→ *Gate (`check_region_membership`):* a node declaring a region not in the
diagram's `regions` → **deny** (a boundary that does not exist — the
structural analog of an orphan node); a node declaring a region it is
geometrically **outside** → **deny** (the picture claims a containment the
layout contradicts). *Non-example:* a node visually sitting inside a frame
but belonging — per the record — to a different region: the geometry must not
be trusted to *imply* membership, and membership must not be drawn where it
isn't true. Backward-compatible: a diagram that declares no `regions` is
untouched (the rule bites only a declaration).

## The discipline

A rule appears here only with its **refusal** and a **non-example** — a
principle the gate cannot bite on is not in the canon, it is a wish. When
a new genre earns its place (the §10 test: two real diagrams refuse to
fit the existing ones), its rules are added here *before* the genre
ships, so the gate has a cited "why" the day the genre renders.

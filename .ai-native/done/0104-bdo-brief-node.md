# Done-line 0104 — The bdo-brief node: owner-bound work folds to a digest over bulk; each item drills into a cited inference construct

Written before code, per §9.4. When this line is met, stop.

bdo, 2026-06-17: "Can we stop putting things on me?" A "what's on you" list is
still a queue, just politely worded. What he wants instead, when a session
genuinely needs him: not a decision handed over, but an **inference construct**
he can set beside his own read — the context actually weighed (tight, cited),
the recommendation it produced and the reasoning that produced it, and the one
seam where his model and the fold's might diverge. A peer's argument that opens
a shared space to discuss, never a menu. And over bulk it must FOLD — a digest
of the aggregate shape ("the few that need your read"), not N briefs ("a flood
in a nicer font"). Two zoom levels, one node; this builds its v0.

It composes the owner-item folds that already exist — it does NOT re-fold them
(`node.next_action` for atoms awaiting bdo's stamp, which already returns None
for a satisfied item; `load_epics` + `reconcile.arc_confirmation` for arcs
awaiting confirmation). epic.owner-harness.

> **Done when:** `loop/brief.py` is a read-only fold (writes nothing, stdlib,
> ends `done | report | needs-you`) with two zoom levels over the work that
> would otherwise land on bdo. **Over bulk** (the default) it renders a digest
> that AGGREGATES: a grouped, counted shape (by arc/epic) with "the few that
> need your read" named — N atoms under one arc fold to ONE arc-group, never N
> top-level rows. **Drill in** (`--item <id>`) it renders that item's inference
> construct: *considered context* (the atom's briefing + its receipts so far,
> each line carrying a citation to a real record — a receipt id, an epic id, a
> file the atom names), then a *recommendation* derived from those records (the
> verdicts + arc state) with the reasoning shown, then the one *divergence
> seam* — the judgment the fold cannot make and bdo can. The §10 teeth, pinned
> in `tests/test_brief.py`: (1) a discharged/satisfied ask does NOT surface
> (a stamped or carried item is absent from both zoom levels); (2) a
> recommendation that cites no record resolvable in the fold is REFUSED —
> flagged as uncited, never emitted as confident (the causality/term_economy
> "no evidence, no mint" grain, the verify-handed-off-asks rule made
> mechanical); (3) the over-bulk digest aggregates — several items under one
> arc produce one group, proving it is a fold and not a 1:1 echo. v0's
> recommendations are deterministic reads over the records; the inference plane
> enriching them is a named later slot, not this line.

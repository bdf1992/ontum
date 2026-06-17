# Done-line 0104 — The change-axis gate refuses a decomposition that smears an axis or smuggles a seam

Written before code, per §9.4. When this line is met, stop.

bdo's steer (2026-06-17): the node-graph / UI split was one *application* of a
reusable procedure (anchor → find change-axes → cut one-axis-per-module → orient
into a DAG → contract the seams → verify by the change test). The procedure was
stated but had no teeth — nothing on disk could *refuse* a bad decomposition, so
the load-bearing claim (**modules align with axes of independent change, not with
categories of thing**) could drift unchecked. Harden the smallest invariant that
makes the claim cost something: the change test, made mechanical, over a declared
decomposition manifest. bdo's fork (confirmed): **AI-native specialized** — a
seam-contract carries trust / authority / change-rate as first-class fields.

> **Done when:** a deterministic, stdlib, read-only gate (`decompose/change_gate.py`, in the `causality/term_economy.py` grain) reads a declared decomposition manifest and returns `coherent` for bdo's token/wiring UI split while *refusing*, each for its own named reason, the broken siblings — (a) two modules declaring the same change-axis (a smeared boundary / overcut), (b) a `depends_on` cycle (a false boundary), (c) a dependency edge crossing no named contract or a contract naming a non-module (an uncontracted seam), and (d) an AI-native seam-contract missing `trust` / `authority` / `change_rate` (a smuggled seam) — pinned by a §10 test (`tests/test_change_gate.py`, joins the suite) that a constant / always-coherent gate fails, asserting the *shape* of each refusal (kind + subject), never a brittle snapshot. The CLI ends in `done | report | needs-you`.

## Not in scope (the named next node)

- **The undercut detector.** Catching a single module that secretly owns *two*
  axes (one reason smeared across, vs. this line's two-modules-one-axis overcut)
  needs the manifest to admit a declared-then-refused multi-reason — a richer
  schema move, the immediate follow-on. One real node at a time (§9).
- **Wiring the gate into the loop** (a `decomposition-drift` gap kind, a summon
  surface). This line hardens the invariant; carrying it ambiently is the next arc.

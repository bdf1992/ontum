# Done-line 0105 — The change-axis gate refuses an undercut module — one module owning two axes

Written before code, per §9.4. When this line is met, stop.

bdo's cadence (2026-06-17): name one part, nail it, decompose until it is one
shot — over and over. The named part is the next node from done-line 0104: the
**undercut** detector, the dual of `smeared-axis`. The gate catches one axis
smeared across two modules (overcut); it cannot yet catch one module that
secretly owns *two* axes (undercut). The manifest must admit a declared-then-
refused multi-reason — the same honesty discipline the gate already runs on
(a seed declares; the gate refuses).

> **Done when:** a module may declare an optional `also_changes_for` (the further reasons it changes for), and `decompose/change_gate.py` refuses any module whose `also_changes_for` is non-empty as `undercut-axis` — naming the module, its several reasons, and the move (split into one module per axis) — a finding *distinct* from `smeared-axis`; the committed anchor stays `coherent`; pinned by a §10 test (in tests/test_change_gate.py) that the undercut is refused, is distinct from the overcut case, and that a constant / always-coherent gate still fails the suite.

## Not in scope (the named next node)

- **Wiring the gate into the loop** (a `decomposition-drift` gap kind, a summon
  surface) — carrying the invariant ambiently is the follow-on arc; this line
  only adds the dual refusal. One real node at a time (§9).

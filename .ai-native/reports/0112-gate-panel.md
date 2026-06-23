# Report 0112 — the gate panel: all-models runs that compile, and the first split

## What landed

bdo, after the cost-economy increment: "Can we have a percentage of our calls use all the models at once in their own streams and it gets compiled at the end? ... to generate snapshot comparisons naturally." That is the **impact half** the cost-only economy deferred: a panel of all models on one atom (snapshot) shows where the cheap model diverges from the room. His settings: **unanimous-or-escalate** at **~25%**.

- **gate.py** (done-line 0144): `should_panel` (rate-gated), `run_panel` (a thread pool fanning `launch_claude` over the pool — every model its own stream), `compile_panel` (unanimous-or-escalate: a unanimous room lands one verdict; any split OR any failed stream escalates, no verdict invented), `_panel_launch` (records each stream, lands or escalates with the per-model split on the issue).
- **loop/runs.py**: `record` + CLI carry atom+verdict; `snapshot_comparisons` folds atoms judged by ≥2 models into per-model verdict+cost with an agreed/split flag — the natural cost-vs-impact comparison — surfaced in render + `--json`.
- **tests/test_gate_panel.py** — §10 teeth (unanimous compiles, split escalates with no verdict, failed stream escalates, rate bound, comparison fold flags agreement vs split; a constant compile fails). Full suite green.

**Proven live, and it earned its keep on the first run:** a forced panel on its own atom SPLIT — **opus → amend, sonnet → amend, haiku → accept** (issue #325). The two strong models caught that the atom asserted owner direction without citing a record; the cheap model missed it. That is the cost-vs-impact signal, concrete on day one. Per the rule it escalated (no verdict). I acted on the real feedback (cited done-line 0144 for the direction); independent backing: **sonnet → accept (rcp.9652356f7fc5)**. Handed off as the panel PR (stacked on #324).

## needs-you

1. **The arc back-link (the real finding the panel surfaced).** The strong models flagged that the gate-* atoms name `epic.the-field` in `serves`, but that epic does not name them in its pieces — "serves no confirmed arc." The cheaper/earlier judges accepted this; the panel's strong models amend on it. The resolution is yours (epics are yours to steer): either name the gate-economy/panel atoms as pieces under an arc (epic.the-field or a new one), or confirm an arc for this work. Until then the merge-node has no confirmed arc to land the stack under.
2. **Gate consistency data point:** sonnet amended then accepted essentially the same atom across runs — non-determinism worth watching as the panel accrues comparisons.
3. **The stack awaits the merge-node:** #288 (rail fix) → #324 (economy) → this panel PR. All atom-backed; all want the arc decision in (1).

## End-state

`report` — panel PR open, atom-backed (independent sonnet accept rcp.9652356f7fc5), full suite green. Panel mode works and demonstrated a real split live; `loop.runs` now folds per-snapshot model comparisons. The cost-vs-impact loop is closed end to end. The arc back-link for the gate-* atoms is yours to resolve.

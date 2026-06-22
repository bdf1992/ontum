# Report 0111 — the gate randomizes its model; the run ledger folds cost by model

## What landed

bdo, after the rail fix (PR #288): instead of pinning one gate model, "randomly choose a model, then audit the results of those models and compare cost vs impact." His chosen shape for this increment: **cost-only first** (impact deferred, named, never faked), pool = **all three** (opus-4.8 / sonnet-4.6 / haiku-4.5), reports ride the existing run/sourcing stats (`loop.runs`), not a bespoke surface.

- **gate.py** (done-line 0142): `GATE_MODEL_POOL` + `pick_model` draw one model uniformly at random per launch (`ONTUM_GATE_MODELS` configures the pool; `ONTUM_GATE_MODEL` still pins one and overrides the draw). `launch_claude` parses the run's cost (`total_cost_usd` + tokens) from the envelope and carries model+cost into the run record.
- **loop/runs.py**: `record()` + its CLI accept model+cost; `model_economy()` folds cost/runs/movement by model. Cost-only — impact is `deferred`, never fabricated; an unpriced run is **unpriced, never $0**.
- **tests/test_gate_economy.py** + updated test_gate_rail.py — §10 teeth (picker draws only from the pool, pin overrides, the fold reports unpriced runs honestly, a constant fold fails). Full suite green.

**Proven live on the branded rail (dogfood):** judging this PR's own atom, the rail randomly drew **claude-haiku-4-5** → **accept** (rcp.ec5566acf75a) at **$0.0915**, trust-rail issue #323 opened and closed; `loop.runs --today` shows the per-model breakdown with the 3 earlier pre-economy runs honestly marked **unpriced**. Handed off as **PR #324** (stacked on #288).

## needs-you

1. **Next increment authorized this session (panel mode):** bdo asked for a percentage of runs to fan out to ALL models in parallel and compile at the end, generating per-snapshot model comparisons — the deferred IMPACT half. His settings: **unanimous-or-escalate** (a unanimous panel auto-advances; any split escalates to bdo) at **~25% panel rate**. Building next as a stacked increment.
2. **Awaiting the merge-node** for the stack: #288 (rail fix) → #324 (this) → the coming panel PR. #324 serves `epic.the-field`; confirm that arc when you want the stack to land.

## End-state

`report` — PR #324 open, atom-backed (independent value-gate accept rcp.ec5566acf75a, on the branded rail), full suite green. The gate now randomizes its model and records cost; `loop.runs` folds cost by model with impact honestly deferred. Panel mode (unanimous-or-escalate, 25%) is the next stacked increment.

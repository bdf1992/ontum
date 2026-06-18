# Done-line 0107 — The loop runs its deterministic gates itself instead of parking for a human who never comes

Written before code, per §9.4. When this line is met, stop. Re-homed to a free
fleet id (the local next, 0110, was taken on another branch).

bdo, 2026-06-18: asked how to fix the landed-but-unsettled clog going forward,
and — choosing "we bother" over "merged is enough" — kept the checks real. The
root mechanical cause: a deterministic real gate (`placement-gate.det.v1`,
`handoff-gate.det.v1`) is a pure fold, yet the loop treated it like an inference
gate and *parked* the atom waiting for a summoned node that never arrives, so
landed work piled up inflight until the cap jammed every new birth.

> **Done when:** the loop **runs admitted-real deterministic gates itself**
> rather than parking for a summoned node. A single registry
> (`DETERMINISTIC_GATE_NODES` in `reconcile.py`) names the deterministic real
> gates; `pass_once` computes their verdict from the pure fold and writes the
> receipt itself (carrying the law's `prompt_hash`, like the pen would), and the
> orchestrator's `next_action` classifies them `judge` not `await` — the same
> escape hatch the owner-stamp uses on a confirmed arc. Inference gates
> (`value-gate.claude.v1`, `value-confirm.claude.v1`) are deliberately excluded:
> they carry a real judgment and still park for a summoned judge. The check
> STILL bites — a computed `collision`/`send_back` is written verbatim, so a
> real divergence fires exactly as a summoned node's refusal would. Proven green
> by updated seam tests (the loop auto-writes placement/handoff receipts with no
> human; a collision and a send_back still refuse and park) and the full suite.

> **Non-example:** a blanket auto-advance that ignores the computed verdict (a
> collision would wrongly sail through); auto-running an inference gate
> (`value-gate`/`value-confirm`) — those carry judgment and must park; dropping
> the `prompt_hash` so the loop's verdict is no longer attributable to the law
> (§7); a second copy of the deterministic-gate list that can drift from
> `reconcile.py`'s registry.

> **Arc:** serves the confirmed `epic.substrate` (adm.476af874f9e4) — disposable
> sessions trusting what survives, the loop telling itself to back off rather than
> jamming. Design lineage: bdo's "we bother" ruling, 2026-06-18. The final
> `value-confirm` (delivery) gate stays a genuine check and is a named next piece,
> not this line.

# Report 0116 — epic.diagram structure-first cell + the fleet-id landing friction

## What landed

- **epic.diagram wave 1** — the floor + named canon + refusing gate (atom.diagram-floor-gate.v0), **on main** (PR #322, rcp.merge.322).
- **epic.diagram structure-first cell 1** — regions as first-class declared structure (done-line 0151): a node belongs to a boundary by *declaration* (`node.region == region.id`), not geometry; the gate refuses a node claiming a nonexistent region or sitting outside its declared one (cites canon C4 containment). Backward-compatible, suite 22 green. **Built + committed on `claude/diagram-structure`, awaiting independent land.**
- **`epic.diagram` re-cut structure-first** (bdo's redirect): plane → composition → attribute-model → snap-as-consequence (snap demoted from a first requirement to a consequence of structure that now exists).
- **change-management blueprint bundle** drafted (`.ai-native/proposals/change-management.proposal.md`) at bdo's request (#348): the seven seams a finding / decision / work / blueprint moves through, and why a session reaches raw for the fastest result.

## needs-you

- **[HIGH PRIORITY] Landing friction — the fleet-id allocator is blind to stranded branches.** `loop.pen`'s `next_id` mints a done/report id by folding the refs its reach-tool can see, but the **git-pen commit-check folds a wider fleet** (local heads + origin/*), so the pen hands out an id a stranded branch already holds and the commit then refuses — forcing a manual renumber cascade across every file that cited the id. Hit **twice this session**: the diagram floor's done-line collided (0132, held by parity #274) → re-minted 0139; the structural cell's collided (0149 **and** 0150, held by `gate-fence-primitive` and another) → re-minted 0151. The allocator and the commit-check must fold the **same** fleet refs so the pen claims a truly-free id up front. Sibling of landing-friction issue #355 and the prompt-parity fence hole (B) in the change-management bundle — the C7 / least-resistance gap biting in real time. Session-fixable (one shared fold).
- **The structural-plane cell awaits its independent land** (value-gate + merge-node) — bdo's to trigger; preserved on `claude/diagram-structure`, not landed.

## End-state

`report` — epic.diagram floor on main; structure-first cell 1 built / green / committed (awaiting land); epic re-cut structure-first; change-management bundle drafted. One high-priority landing-friction finding surfaced for the owner.

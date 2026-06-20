# Report 0095 — requisition backs both PRs; #247 names the bounds-past-intent principle

## What landed

Continuation of the epic.three-marks handoff (path A), across several turns:

- **PR #246 — confirm --from-ref (done-line 0130):** the arc-confirm seam fix
  (an epic-introducing PR can confirm its own arc). CI green, atom-backed,
  on the already-confirmed epic.owner-harness — ready for an independent
  merge-node to land.
- **Backed BOTH PRs by REQUISITION, not self-gating (bdo's steer):** instead
  of the author gating its own atom (which would break "no one signs their own
  line"), an independent branded-subagent `ontum-node:value-gate.claude.v1` was
  requisitioned through the spawn rail (rung-checked, prompt-pinned) and judged
  each atom on its own reasoning:
    - atom.confirm-from-ref.v0 -> accept (rcp.3bf2bd09afc8) [#246]
    - atom.mark-label.v0 -> accept (rcp.bb61c5e125f9) [#244, authored cross-branch
      to back wave-1, which had reached GitHub with no atom; bdo-authorized]
  This converted "blocked by #245" into two green, atom-backed PRs.
- **Issue #247 filed** — bdo's principle: *bounds must not restrict past their
  intent; the authorized owner's stamp must be portable to any session he's
  authorized in*. Distinct from #245 (the AI-pen-reach face); names the
  owner-authority face and a candidate hard rule. Open to bdo's correction.
- **Hygiene:** .gitignore now ignores .ai-native/continue-beat.json (the
  continue-beat/patrol nag state, sibling of mock-shame.json).

## needs-you

Nothing parked here — every owner ask is on a surface bdo reads (GitHub):
- #246 ready to land (no stamp needed; epic.owner-harness already confirmed) —
  awaits a gh-capable merge-node session.
- #244 awaits bdo's `epic.three-marks` confirm (via the --from-ref seam, once
  #246 is on main) + a gh-capable merge-node land.
- #247 awaits bdo's endorsement of the principle + the mechanism choice.
- #245 parity decision (gh-in-env vs MCP-backed pens) stays bdo's.

## The thread that matters (for the next session)

The lever bdo handed this session — "you can have a node do it, a requisition" —
is the general unblock for the web/mobile environment: the headless gate
(gate.py) needs gh, but the spawn rail + loop.node judge do NOT. An independent
requisitioned node can judge any parked atom here. The remaining gh dependency
is narrowed to the merge-node's `land` (the actual GitHub merge) — the last
face of #245, and the concrete demand of #247.

## End-state

`report` — both epic.three-marks-adjacent PRs (#246, #244) green and
atom-backed via independent requisitioned nodes; #247 names the bounds-past-intent
principle; landing waits on bdo's stamps + the gh-bound merge-node (a local
session or the #245/#247 decision).

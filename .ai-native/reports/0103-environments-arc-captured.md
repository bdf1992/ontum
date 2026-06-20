# Report 0103 — epic.environments captured, confirmed, and landed

## What landed

bdo opened with a plain question — three environments for production workflow, and deployments in GitHub — then named the deeper want: it would help with natural version-management rituals, and with the requirement that someone else accepts your work. The honest, evidence-backed answer was yes: the recurring failure mode on the record is work with no clean checkpoint between "built" and "accepted" (one session's garden report alone: 13 stranded branches, held cuts with commits never on origin/main), the same per-atom-pipeline-versus-per-PR-git namespace gap loop/pull.py was chipping at.

bdo's reframe became the arc's spine: a snapshot is the natural unit a second party accepts — immutable and named the way an atom's identity already is its content hash — and a deployment promotes a snapshot from one environment to the next, with acceptance attaching to the snapshot, not the mutable branch. He blessed and authorized the arc in session, and asked that the "served inbox" piece be remodeled (an inbox is only a queue) into a served control plane.

Captured and landed on main: environments.proposal.md + .ai-native/epics/epic.environments.json (two axes — deploy and runtime; six pieces each pinned to a real need; two guardrails — nothing cargo-culted onto the local loop, a deploy gate executes bdo's stamp rather than inventing a verdict); done-line 0134; atom.environments-arc.v0 judged accept by an independent value-gate (rcp.c3c2cb5ea896); bdo's confirm-arc adm.b30f27b9d5ad on origin/main; PR #277 landed by an independent merge-node (rcp.merge.277, suite green at 1031 tests). The spurious GitHub CONFLICTING was the union-merge artifact, resolved via git merge-tree plus the pen's reconcile. First buildable slice named: the production gate.

## needs-you

The branded headless gate (gate.py launch) failed twice to return a parseable verdict — an environment fragility, not a real refusal. Routed around it with an independent in-harness subagent (the legitimate D-2 path) and closed the two stray trust-rail issues it left (#275, #276). The headless-gate fragility is worth its own look: it will bite the next session that requisitions a real gate the same way. Otherwise nothing is parked on bdo — he confirmed the arc; building the production gate is confirmed loop work, not another ask.

## End-state

`report` — epic.environments is captured, confirmed by bdo, and landed on main (rcp.merge.277); the production gate is the next buildable slice; the one open thread is the headless-gate fragility, routed around this session and surfaced for its own fix.

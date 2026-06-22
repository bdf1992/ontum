# Report 0127 — Recovery and the landing wave: one real land, one retire, two honest send-backs

bdo asked for "recovery and landing." Recovery was clean; landing
revealed the throughput clog made concrete, and the second-set-of-eyes
showed its teeth.

## What landed

### Recovery
- The dirty viewport (the plain-english CLAUDE.md rule, report 0125, two
  proposals, heartbeat log appends) was preserved via the whiteout
  utensil and the viewport returned to main. Nothing lost. A parallel
  reconcile effort had already opened PRs for that same recovered work
  (#523 agent-summoning proposal, #524 plain-english rule, #532 report
  0125 + living-spec), so it was not re-homed twice.

### Landing — the triage finding
- No open PR was a clean merge-node candidate. The backlog is
  gate-clogged, not merge-blocked: confirmed-arc feature PRs carry atom
  files that never cleared the value-gate (no value-confirm receipt on
  the branch), so the CI "PR carries an atom on the log" check is red.
  This is issues #348 / #355 / #434 made concrete.

### Landing — what was driven, per confirmed-arc PR
- #446 (epic.diagram) — LANDED (rcp.merge.446). The orphaned
  atom.diagram-projection.v0 was announced on its branch, an independent
  value-gate (value-gate.claude.v1, headless judge, trust-rail issue
  #531) returned accept (rcp.63f2bcdd5833), the branch was land-chain
  reconciled against main (union-merge logs), and the merge-node landed
  it. The full path proven: orphan -> announce -> independent gate ->
  reconcile -> land.
- #292 (epic.three-marks) — retired. atom.confirm-from-ref.v0 is already
  fully through the pipeline on main; the PR's value-confirm receipt
  duplicated it. Closed via the retire verb (work already on main). Its
  stranded report 0106 is rescued in this PR.
- #471 (epic.diagram) — does not land; parks for revision. The
  independent value-gate returned amend (rcp.ec854014fd7e, issue #537) on
  atom.gateway-node-meaning.v0, and the branch has real content conflicts
  with main now that #446 landed (term_economy.py, test_diagram.py, the
  gateway-topology examples). Forcing it would be the slop bug. The gate
  saying accept to one diagram piece and amend to the next is the §10
  property working — not everything passes first try.
- #510 (epic.owner-harness) — does not land; a namespace gap for you. The
  branch carries real stranded code (loop/owner.py + tests) implementing
  atom.owner-inbox.v1, but that atom is already on main, so the branch
  adds no atom the orphan gate can see. Implementation-of-an-already-
  landed-atom cannot pass the work-particle gate. Resolving it means a
  design call (a fresh impl-atom, or a doctrine that code realizing a
  confirmed atom is backed by it) — not a mechanical land.

## needs-you

- Confirm epic.graded-speed to release #489 (issue #498 is exactly this —
  the one arc-confirm that unblocks a ready PR).
- #510: decide the path for stranded implementation of an already-landed
  atom (the namespace gap above). Real code, no mechanical land.
- #471: revise per the gate's amend verdict (issue #537) and resolve the
  conflicts with main, then re-gate — or decline the piece.
- A parallel reconcile actor is active (it wrote report 0126, opened
  #523/#524/#532, and left ~49 untracked files in the viewport that this
  session's sync preserved on claude/rescue-viewport-2026-06-22-5). Worth
  knowing two hands are in the recovery space; nothing collided, but the
  reconcile PRs carrying proposals (#523, #532) will hit the same orphan
  gate (a proposal is not records-only).
- The four CONFLICTING PRs (#308/#324/#338/#389) were not triaged this
  session.

## End-state

`report` — recovery clean; #446 landed, #292 retired, #471 amended by the
gate, #510 is a surfaced design gap; the value-gate showed teeth.

# Report 0041 — Gap-to-work lands; the garden and the drifted records come clean

## What landed

**Done-line 0048 — gap-to-work (rcp.merge.77, PR #77, epic.substrate).**
`loop/gaps.py`: one pure read-only fold that enumerates the loop's open
gaps from records already on disk, in one fixed pressure order —
mock-stage, parked-piece, surface-drift, idle-organ, dormant-organ —
each with kind, subject, why, and the one concrete next move (always an
existing pen's). `loop.summon --hook` now hands the single
highest-pressure gap to every session that blinks in: the idle default
becomes "work the backlog the harness generated". Computed lazily so
the every-prompt hook pays the census walk only on an otherwise-clean
field; a missing root reads as absence, not a field of mock stages
(the existing summon suite caught exactly that and the guard is the
fix). 10 new tests incl. the §10 case: with parked-piece and mock-stage
both present, the higher-pressure kind wins and the flip happens the
moment every stage is admitted real. Suite green at the head: 504 OK.
On the live records the hook's first handed gap is the value-confirm
`missed` on atom.gates-enumerated.v1 — the delivery-gap signal becomes
the next session's first line of context instead of a parked line
nobody reads.

**Drifted records brought back to truth.**
- Issue #71 (value-confirm realness) was still open although the stage
  was admitted real on bdo's chat stamp (adm.888b7582e6f9) — closed,
  citing the admission and the gate's first real verdict.
- Merge receipts rcp.merge.50 and rcp.merge.54 sat uncommitted in a
  prunable worktree — landings GitHub knew and the log on main did
  not. Recovered byte-identical onto the trunk (PR #74, rcp.merge.74).

**The garden.** Pruned 3 merged worktrees and 12 merged branches across
two passes; the two stranded-by-design branches
(claude/epic-experience-layer, keep/main-codex-9431f6c) left standing.

**Harness fix (machine-level, not repo).** Git-Bash MSYS path mangling
shredded `branch:path` arguments; permanently off via the user-global
settings env (MSYS_NO_PATHCONV=1, MSYS2_ARG_CONV_EXCL=*), verified, and
recorded in session memory with its one caveat (no /c/... POSIX paths
to native exes).

Independence held: both PRs were landed by a separately spawned
merge-node agent (merge-node.claude.v0), never by their author.

## Findings for the next line

- **GitHub's merge engine ignores the union merge driver** in
  .gitattributes: any log-append-only PR that falls behind main reads
  CONFLICTING and the land pen refuses. The merge-node recovered PR #74
  by integrating main into the head (the local union driver resolves
  it) and re-pushing — that dance will repeat on every future log PR
  unless the pen grows a pre-land integrate step. Named, not built:
  it is its own line.
- The gap backlog on the live records today: 4 parked pieces (incl.
  atom.gates-enumerated.v1 held by a real `missed`) and 6 idle organs.
  The fold now hands them out; working them is what sessions are for.

## needs-you

Nothing waiting on a gesture. The realness queue is empty (all five
gates real, issues #66/#69/#71 closed); both arcs this session touched
were already confirmed. The parked pieces above are session work
(amend) or escalate only if a retirement call is wanted.

## End-state

`report` — gap-to-work live in the summons hook (rcp.merge.77); drifted
records reconciled (rcp.merge.74, #71 closed); garden clean; suite 504
OK on main; merge-node landed everything, bdo touched nothing.

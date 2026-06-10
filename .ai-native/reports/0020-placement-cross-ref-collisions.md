# Report 0020 — placement: the address layer learns to see the fleet

## What landed

**[done-line 0023](../done/0023-placement-cross-ref-collisions.md) — met.**
The records pen (`loop/pen.py`) and the write guard both allocated record
ids by folding the *local* directory only — blind to sibling branches in
the shared-tree fleet. So branches minted the same id and nothing noticed:
five `0020` done-lines, three `0018` reports. This is the §10 case the epic
named (`atom.placement-judges.v0`, epic.experience-layer wave 1).

- **[.claude/hooks/placement.py](../../.claude/hooks/placement.py)** — a
  deterministic pen that folds numbered-record ids across *all git refs*.
  `check <dir>` refuses when two records claim one id (exit 1 + the
  colliding files and the refs that carry them); `next <dir>` gives the
  fleet-safe next id. Reading refs is reach beyond the log, so it lives
  under `.claude/`, not in pure-stdlib `loop/` (the reflect split). Fail-open:
  no git → it behaves as the local fold did.
- **[.claude/hooks/write_guard.py](../../.claude/hooks/write_guard.py)** —
  its `next_id` now folds across refs via `placement`, so a session writing
  its own record in-tree can no longer be handed a colliding id. Still
  fail-open.
- **[tests/test_placement.py](../../tests/test_placement.py)** — the §10
  proof as tests: two locally-fine records refuse to fit, exercised both as
  pure working-tree logic and in a real two-branch git repo. Suite: 178 OK.

Run live, `placement.py check .ai-native/done` catches the `0020` collision
(`git-commit-pen` vs `reflection-automates`) the local fold waved through.

## needs-you

- **Stamp this PR** (placement, done-line 0023) — the records-layer detector
  + prevention.
- **Merge #18, #16, #15** — all three were at your stamp when this branch was
  cut (#18 `MERGEABLE`/`CLEAN` after its own session rebased + renumbered its
  `0020 → 0021`).

Out of scope, named in the done-line: wiring placement as the admitted-real
**L1 pipeline gate**, and making the records pen itself fleet-aware without
breaking `loop/` purity. Both are their own done-lines.

## End-state

`report` — placement-judges' records-layer increment is complete and green;
the cross-ref detector refuses real collisions and the write guard no longer
hands out colliding ids. Ready for the branch ritual and your stamp.

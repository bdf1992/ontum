# Report 0032 — overnight-loop pickup

## What landed

Done-line 0032 adds the next deterministic overnight-loop step:

- `.claude/skills/overnight-loop/overnight.py` now has a read-only `pickup`
  verb. It reuses the same owner-viewport, session-branch, dirty-tree, and
  unknown-arc refusals as `brief`, then reads known epics, `loop.summon`,
  recent done-lines/reports, and sibling worktrees.
- `pickup` emits one recommended arc, one next story, one next task, concrete
  first commands, stop conditions, authority boundaries, and tests. It names
  the owner-only edges it will not cross: arc confirmation, owner gates,
  append-only log edits, and owner-only language pins.
- `.claude/skills/overnight-loop/SKILL.md` is bumped to 0.2.0 and documents
  pickup as the arc/story/task selection step after the preflight brief.
- `tests/test_overnight_loop.py` pins no-summons known-arc recommendation,
  unknown requested-arc refusal, owner-viewport refusal, and dirty-tree
  refusal for `pickup`.

Validation run:

- `python -m unittest tests.test_overnight_loop -v` -> 10 tests OK.
- `python .claude\skills\overnight-loop\overnight.py pickup` -> refused the
  dirty worktree unless inherited explicitly.
- `python .claude\skills\overnight-loop\overnight.py pickup --allow-dirty --arc epic.substrate`
  -> recommended `epic.substrate` / `overnight-loop arc pickup` from live repo
  state.
- `python -m unittest discover -s tests -v` -> 285 tests OK.

## needs-you

Nothing blocks the landed capability. Arc confirmation and final merge remain
bdo's authority; this command only recommends the next safe start.

## End-state

`report` - done-line 0032 is met; the overnight loop can now pick one next
arc/story/task from live repo state before a fresh session mutates files.

# Report 0033 — overnight-loop checkpoint

## What landed

Done-line 0033 adds the clock checkpoint the overnight loop was missing:

- PR #38 was converted back to draft with the branch ritual because 00:06 local
  is still inside the overnight window. The earlier at-the-stamp handoff was too
  early for the owner's rule: a done-line stops an increment, not the whole run.
- `.claude/skills/overnight-loop/overnight.py` now has a read-only
  `checkpoint` verb. It refuses owner-viewport branches, non-session branches,
  and dirty trees unless inherited explicitly, then compares the local clock to
  the stop time.
- Before the default 08:00 stop time, `checkpoint` emits `decision: continue`
  and points back to `overnight.py pickup`. At or after 08:00, it emits
  `decision: handoff` with report/push/ready commands.
- `.claude/skills/overnight-loop/SKILL.md` is bumped to 0.3.0 and now states
  that after each bounded increment the loop runs checkpoint instead of treating
  that increment as the full overnight stop.
- `tests/test_overnight_loop.py` pins before-08:00 continuation, at-08:00
  handoff, owner-viewport refusal, and dirty-tree refusal.

Validation run:

- `python -m unittest tests.test_overnight_loop -v` -> 14 tests OK.
- `python .claude\skills\overnight-loop\overnight.py checkpoint` -> refused
  the dirty worktree, as expected between increments.
- `python .claude\skills\overnight-loop\overnight.py checkpoint --allow-dirty`
  at 00:09 local -> emitted `decision: continue`.
- `python -m unittest discover -s tests -v` -> 289 tests OK.

## needs-you

Nothing blocks the landed capability. Final merge still belongs to bdo; the PR
is draft again while the overnight loop continues.

## End-state

`report` - done-line 0033 is met; the overnight loop now checks the clock after
an increment and continues before 08:00 instead of stopping early.

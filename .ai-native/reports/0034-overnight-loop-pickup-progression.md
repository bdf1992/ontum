# Report 0034 — overnight-loop pickup progression

## What landed

Done-line 0034 makes pickup advance instead of repeating landed work:

- `.claude/skills/overnight-loop/overnight.py` now has an ordered substrate
  overnight story queue. For `epic.substrate`, pickup reads recent done-line
  slugs and recommends the first unlanded story in that queue.
- After the existing pickup/checkpoint done-lines are present, live pickup now
  recommends `overnight-loop handoff refresh` instead of repeating
  `overnight-loop arc pickup`.
- `.claude/skills/overnight-loop/SKILL.md` is bumped to 0.4.0 and documents
  that substrate pickup skips ordered stories whose done-lines already exist.
- `tests/test_overnight_loop.py` adds a fixture with landed pickup/checkpoint
  done-lines and pins the next recommendation as
  `overnight-loop pickup progression`.

Validation run:

- `python -m unittest tests.test_overnight_loop -v` -> 15 tests OK.
- `python .claude\skills\overnight-loop\overnight.py pickup --allow-dirty --arc epic.substrate`
  -> recommended `overnight-loop handoff refresh` from the live branch state.
- `python -m unittest discover -s tests -v` -> 290 tests OK.

## needs-you

Nothing blocks the landed capability. The next queued substrate story is
`overnight-loop handoff refresh`; final merge remains bdo's authority.

## End-state

`report` - done-line 0034 is met; pickup skips landed overnight-loop stories
and advances to the next queued substrate story.

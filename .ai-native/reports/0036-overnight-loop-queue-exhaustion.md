# Report 0036 — overnight-loop queue exhaustion

## What landed

Done-line 0036 makes queue exhaustion explicit:

- `.claude/skills/overnight-loop/overnight.py` now reports
  `queue state: exhausted` when `pickup --arc epic.substrate` sees that every
  ordered overnight-loop substrate story has a done-line.
- Exhausted pickup returns a stop result instead of repeating the final queued
  story. That makes "no safe next increment remains" mechanical.
- `.claude/skills/overnight-loop/SKILL.md` is bumped to 0.5.0 and names queue
  exhaustion as a stop condition unless bdo widens the queue or chooses another
  arc.
- `tests/test_overnight_loop.py` pins the exhausted queue case.

Validation run:

- `python -m unittest tests.test_overnight_loop -v` -> 16 tests OK.
- `python .claude\skills\overnight-loop\overnight.py pickup --allow-dirty --arc epic.substrate`
  -> emitted `queue state: exhausted`.
- `python -m unittest discover -s tests -v` -> 291 tests OK.

## needs-you

The overnight substrate queue is exhausted. Continuing would require bdo to widen
the queue, choose another arc, or stamp owner-only work. This is the safe stop
condition before the 08:00 clock stop.

## End-state

`report` - done-line 0036 is met; pickup stops cleanly when the ordered
substrate overnight-loop queue is exhausted.

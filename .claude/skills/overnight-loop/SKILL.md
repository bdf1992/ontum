---
name: overnight-loop
description: >-
  Prepare and run a long autonomous session against a named repo arc. Use
  when bdo asks for an "overnight loop", "keep working until you stop",
  a confident long-running Codex/Claude pass, or a repeatable autonomous
  work loop. The deterministic preflight, pickup, and checkpoint pen is
  overnight.py beside this file; it refuses unsafe starts, emits the run
  contract, recommends one next arc/story/task from live repo state, and
  checks whether the overnight window is still open before the session
  stops working. Pickup advances through the overnight substrate queue
  instead of repeating stories whose done-lines already exist, and reports
  an explicit stop when that queue is exhausted.
version: 0.5.0
owner: bdo
changelog:
  - version: 0.5.0
    note: >-
      Done-line 0036 makes an exhausted substrate queue a real stop condition.
      When every ordered overnight-loop story done-line is present, pickup
      reports `queue state: exhausted` instead of repeating the final story.
  - version: 0.4.0
    note: >-
      Done-line 0034 makes pickup progressive for the overnight-loop
      substrate stories. It reads landed done-line slugs and recommends the
      first unlanded story in the ordered queue, so checkpoint -> pickup does
      not loop back onto work that already landed.
  - version: 0.3.0
    note: >-
      Done-line 0033 adds `overnight.py checkpoint`, the between-increments
      clock check. A clean session branch before the 08:00 stop time gets
      told to keep looping through pickup; at or after the stop time it gets
      handoff commands. Unsafe branch/tree states still refuse.
  - version: 0.2.0
    note: >-
      Done-line 0032 adds `overnight.py pickup`, a read-only arc pickup
      command. It reads known epics, summons, recent records, and
      sibling worktrees, then emits exactly one recommended arc, next
      story, concrete first commands, stop conditions, and tests while
      keeping owner-only authority out of scope.
  - version: 0.1.0
    note: >-
      First form (done-line 0031). Adds a read-only brief command that
      binds a long run to one known arc, one session branch, explicit
      stop conditions, tests, and a report handoff.
---

# The Overnight Loop

An overnight loop is not a promise to keep typing. It is a bounded run:
one named arc, one session branch, a clean enough starting field, a
done-line before edits, tests before handoff, and a report when the run
stops. The value is confidence: when the human leaves, the session has a
contract it can execute without silently widening authority.

Run the deterministic brief first:

```powershell
python .claude/skills/overnight-loop/overnight.py brief `
  --arc epic.substrate `
  --objective "build the next repeatable overnight-loop capability"
```

The brief refuses:

- `main` or `master`, because the primary checkout is bdo's viewport.
- A dirty tree, unless the run explicitly starts from existing changes
  with `--allow-dirty`.
- An arc id that is not present under `.ai-native/epics/`.
- A non-session branch, because long work belongs on `codex/*` or
  `claude/*`.

When bdo has not already named the next bounded increment, run pickup
from a clean session branch:

```powershell
python .claude/skills/overnight-loop/overnight.py pickup
```

The pickup reads the live repo surfaces that matter for a safe start:
known epics, open summons, recent done-lines and reports, and sibling
worktrees. It emits one recommended arc, one next story, one next task,
the first commands to run, stop conditions, and tests. It does not
confirm arcs, stamp owner gates, edit logs, choose owner-only language
pins, or widen authority beyond the selected arc. For the substrate
overnight-loop path, it skips ordered stories whose done-lines already
exist and recommends the first unlanded story instead. If every ordered
story has landed, pickup returns `queue state: exhausted`; that is the
"no safe next increment remains" stop condition unless bdo widens the
queue or chooses another arc.

After each bounded increment lands, do not treat the increment's done-line
as the whole overnight run. Check the overnight clock:

```powershell
python .claude/skills/overnight-loop/overnight.py checkpoint
```

Before the stop time, the checkpoint points back to `pickup` so the run
continues. At or after the stop time, it points to report, push, and ready
handoff. The default stop time is 08:00 local; override it only by naming
the reason in the run contract:

```powershell
python .claude/skills/overnight-loop/overnight.py checkpoint --until 07:30
```

After a passing brief:

1. Work only inside the named arc's authority.
2. Mint a done-line through `python -m loop.pen new done ...` before
   code changes.
3. Keep each increment small enough that its tests can be run before the
   next one.
4. Stop on the first owner-only gate, missing context, repeated test
   failure, branch ambiguity, or satisfied done-line.
5. Mint a report through `python -m loop.pen new reports ...` naming the
   end-state and any `needs-you` items.

This skill does not override repo law: bdo confirms arcs, an independent
merge-node lands confirmed PRs, sessions do not push to `main`, append-only
logs stay append-only, generated files stay with their generators, and
owner-only stamps remain owner-only.

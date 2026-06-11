# Report 0031 — the viewport syncs itself: the merge's return leg

## What landed

**[done-line 0031](../done/0031-viewport-sync.md) — met.** bdo's
question opened the session: "why does this keep happening?" — local
main 4 commits behind origin, with `docs/sources/files.zip` haunting
the tree as an untracked twin of a now-tracked file. The diagnosis: the
fleet's merges all land on origin, and nothing ever took the return
leg back to the primary checkout. His ask, verbatim in spirit: local
files ALWAYS current, work separate, GitHub not conflicting — which is
precisely a fast-forward-only return leg, because ff-only cannot
conflict; it succeeds or it surfaces. Stamped in conversation
("yes all three please"), same-day.

- **The viewport pulled current** — the identical untracked twin
  verified by blob hash and removed, `git pull --ff-only` to `efee2d4`.
- **[git.py](../../.claude/skills/branch-ritual/git.py)** — the pen
  gains `sync`: locates the viewport (the primary worktree, first in
  `git worktree list` from anywhere in the fleet), fetches with a
  timeout, fast-forwards the trunk to origin/main. `sync_refusal` is
  the pure rule: an off-trunk or locally-ahead viewport is refused —
  each a surface to bdo, never an act. Hook mode (`--hook`) is
  fail-open, exits 0 always, silent when current.
- **[settings.json](../../.claude/settings.json)** — `SessionStart`
  wires `git.py sync --hook` beside the summons: any session blinking
  in anywhere leaves bdo's reading surface current. A writing hook,
  the Stop-beat precedent — contract change stamped by bdo.
- **[SKILL.md](../../.claude/skills/branch-ritual/SKILL.md) 0.9.0** —
  the changelog records the why (0.6.2 named the same staleness at 38
  commits and fixed only the workbench half).
- **[tests/test_git_pen.py](../../tests/test_git_pen.py)** — the
  refusals pinned (§10: a locally-fine viewport state that must refuse
  to fit). Suite: 268 OK.

Also this session, no code needed: **the epic-integration topology is
live and answers bdo's "3 merges, not 30"** — `claude/epic-experience-
layer` already stands on origin (a sibling session cut it); pieces PR
into it and sessions integrate them (`pr.py integrate`), so only the
finished arc reaches his merge button. This PR itself is harness
plumbing that only works from main, opened with his same-day stamp —
the kind of piece that stays rare from here.

## needs-you

- **Merge this PR** — pre-stamped by you in conversation ("yes all
  three"). On merge, every new session fast-forwards your viewport
  automatically; the staleness question dissolves.
- The watcher's fold nominates raw `git` (×62 this audit) — `sync` is
  this session's answer to the heaviest slice (pull/fetch). The
  remaining raw-git weight is worktree add/remove; a `workbench` verb
  is the next candidate if it keeps recurring.

## End-state

`report` — the return leg exists: merges distribute, the viewport
follows, refusals surface instead of conflicting; at the stamp.

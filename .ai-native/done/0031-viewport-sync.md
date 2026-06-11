# Done-line 0031 — the viewport syncs itself

Written before code, per §9.4. When this line is met, stop.

> **Done when:** the git pen carries a `sync` verb — locate the
> viewport (the primary worktree), fetch, fast-forward the trunk to
> `origin/main`, and refuse a viewport that is off the trunk or carries
> local commits (each a surface to bdo, never an act) — and
> `SessionStart` wires `git.py sync --hook` (fail-open, exit 0 always),
> so any session blinking in anywhere in the fleet leaves bdo's reading
> surface current. §10 proof: the refusals are pure functions pinned in
> tests/test_git_pen.py.

## Why (bdo, 2026-06-10)

"Why does this keep happening?" — local main sat 4 commits behind while
merged work piled up on origin, and a tracked file (docs/sources/
files.zip) haunted the viewport as an untracked twin. The merge
distributes, but nothing ever took the return leg (0.6.2 named the same
staleness at 38 commits and fixed only the workbench half). bdo's ask:
local files ALWAYS current, work separate, no conflicts — which is
exactly what a fast-forward-only return leg gives, because ff-only
cannot conflict; it can only succeed or surface.

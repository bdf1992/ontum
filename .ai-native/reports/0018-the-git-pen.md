# Report 0018 — the git pen — raw add/commit branded

## What landed (done-line 0020)

The git wrapper, mirroring the gh wrapper. Three halves, suite green
(160 tests):

- **The pen** — `.claude/skills/branch-ritual/git.py`, a sibling to
  `pr.py`. `add` stages **named paths only** (`add .` / `-A` / `-u` and
  interactive `-p`/`-i` are refused); `commit` refuses `-a`/`--all`,
  requires a real message (or `-F <file>`), and never commits the trunk.
  Path-scoped commit flags (`-o`/`--only`, `-i`/`--include`) stay
  allowed; everything else forwards for parity (the lesson `pr.py push`
  records).
- **The deny** — raw `git add` / `git commit` join the command_guard
  deny-list (rules `git-add-raw`, `git-commit-raw`), routed to the pen.
  `git commit-tree` is spared by a lookahead.
- **The farm** — the watcher was blind to standalone local git (only
  network git was visible); a new `GIT_MUTATING` set makes checkout,
  branch, merge, rebase, worktree, … visible so the next verb to brand
  nominates itself. Read-only git (status/log/diff) stays
  raw-and-watched, exactly as `gh pr list` does.

The pen was dogfooded: every commit on this branch after the code
existed went through `git.py` (the done-line, the feature, the docs).

Design, settled with bdo before building (three calls):
1. read/write split — deny *mutating* git, allow+watch reads (the gh
   precedent: we never denied `gh pr list`).
2. first cut — `commit`+`add` only; a blanket deny-all-mutations would
   brick the ritual (no pen path yet for checkout/branch/worktree). One
   real node at a time (§9); `git push` was branded the same way.
3. spine — explicit-path + real message + not-trunk.

The watcher's report agreed git was next: after gh's reads, `git` was
the heaviest unwrapped tool on the log.

## needs-you

- **The next git verb to brand is now visible, not chosen.** With local
  mutating git watched, `command_guard.py --report` will start folding
  checkout/branch/worktree/merge pressure. The fleet leans on
  `git worktree add` and `git checkout` — likely the next nomination,
  but the report decides, not the session.
- **The primary checkout has drifted off main.** I found
  `C:/Users/bdf19/ontum` on `claude/surface-reflector-ui`, not `main`
  (the parallel-fleet rule: the primary is bdo's viewport on main, never
  switched). I left it untouched and worked in a fresh worktree
  (`ontum-wt/git-commit-pen`); flagging in case you want the viewport
  back on main.
- **Stale reference, left unfixed (scope):** `pr.py`'s docstring still
  cites `.claude/hooks/gh_guard.py` — the hook was renamed to
  `command_guard.py`. One line; left for a later pass rather than swept
  into this node.

## End-state

`report` — done-line 0020 met: raw git add/commit are branded and
denied toward the pen, the watcher sees local mutation, and a
locally-fine `git add .` refuses to fit (§10). Branch
`claude/git-commit-pen` in worktree `ontum-wt/git-commit-pen`, three
commits, suite green; at the PR pen next.

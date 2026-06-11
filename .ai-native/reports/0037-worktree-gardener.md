# Report 0037 — SessionStart gardens dead worktrees and surfaces chores

## What landed

By done-line 0037 (the worktree gardener):

- **[git.py](../../.claude/skills/branch-ritual/git.py)** gains a `garden`
  verb beside `sync`. It enumerates the worktrees, makes one `gh pr list`
  call, and classifies each non-trunk worktree through a pure function,
  `garden_verdict`: it **prunes** only a clean worktree whose branch carries a
  merged PR (the one provably-done shape), **keeps** a worktree with an open PR
  (an active workbench), and **surfaces** — never removes — a worktree with
  uncommitted work or one committed-but-never-PR'd (the mortal-session debris).
  It never prunes blind (gh unreachable → nothing removed), never touches the
  viewport or the current session's own worktree, and reports merged/stranded
  loose branches as lighter chores. The §10 case is the centre: a *merged* yet
  *dirty* worktree — branch done, work unsaved — is surfaced, never pruned.
- **[settings.json](../../.claude/settings.json)** wires
  `git.py garden --hook` into `SessionStart`, beside the existing `sync` hook.
  Hook mode is fail-open and exits 0 always — like `sync`, it never gates a
  session's start. Every session open now self-cleans the fleet's dead
  worktrees and surfaces what needs a human.
- **[tests/test_garden.py](../../tests/test_garden.py)** — 7 tests over the
  classifier, including an exhaustive sweep proving `prune` is reached by
  exactly one input: `(clean, no-open-PR, merged)`. Full suite green (387).

This is the systemic fix for the mess gardened by hand earlier: git does not
remove a worktree when its branch dies, and mortal sessions skip the
branch-ritual hand-off that would, so debris accreted (19 worktrees, two
holding uncommitted features). Now the next session start removes the dead and
names the stranded, automatically.

Proven live on first run: it pruned a genuinely-merged worktree (`pivot`, its
PR merged concurrently), surfaced an active uncommitted one, and listed the
stranded branches — all guards held.

## needs-you

nothing — bdo's only choice here is whether to PR or delete the two stranded
branches surfaced earlier (`claude/ambient-run-ledger`, `claude/mock-shame`);
the gardener will keep surfacing them until he does.

## End-state

`report` — the gardener is built, tested (387 green), wired to SessionStart,
and proven on a live prune; the fleet now self-cleans.

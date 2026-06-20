# Done-line 0145 — The workstation fence

# Done-line: the workstation fence

> **Done when:** a session running in the primary tree (bdo's viewport) is REFUSED, with exit 2 and the paved path, when it runs a tree/HEAD-flipping git verb (checkout, switch, reset, restore, clean, merge, rebase, cherry-pick, revert, am, apply, stash, or a mutating `branch`) — while the identical verb is ALLOWED inside a linked worktree, and read-only git (status/log/diff/show) and the branded `git.py sync` are allowed in the viewport. Proven by a §10 test that runs the live command_guard from a primary-tree cwd (denied) and from a real linked-worktree cwd (allowed), and a read from the viewport (allowed).

## Why

The viewport keeps getting stranded off-trunk because workers edit the primary tree as if it were a scratch branch. bdo's rule (2026-06-20): a worker edits only its OWN workstation (its worktree); reading and organizing anywhere is fine; flipping someone else's tree — above all the viewport — is forbidden and shameful. The fence already had `git-checkout`/`git-switch` rules but they were `decision: prompt`, which an autonomous resumed session auto-proceeds past, and the guard never checked WHERE it ran. This makes the rule law in the one place it must hold: the viewport cannot be flipped.

This is tooth #1 of three. Tooth #2 (a write/mutation targeting another worktree's path is denied) and tooth #3 (a shame beat naming any session that flipped a foreign tree) are later increments; #1 alone stops the plague because a worker mis-born in the viewport can read and organize but cannot flip it.

## The paved path the refusal names

Make a workstation and work there:
`git worktree add -b claude/<slug> ../ontum-wt/<slug> origin/main`
To advance the viewport to the trunk, the only sanctioned move is the git pen:
`python .claude/skills/branch-ritual/git.py sync`

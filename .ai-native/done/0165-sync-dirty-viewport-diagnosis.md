# Done-line 0165 — Sync names a dirty viewport honestly, not as phantom stray commits

﻿# Done-line 0163 ? Sync names a dirty viewport honestly, not as phantom stray commits

> **Done when:** git.py sync, run against a viewport that is on the trunk, not
> ahead of origin (no local commits), but behind with a dirty working tree,
> refuses with a diagnosis that names the real blocker (uncommitted changes) and
> the sanctioned move, instead of the current message that blames stray commits
> to branch-and-PR, which can only ever fire when there are none. The bar is met
> when:
>
> 1. A new pure helper dirty_viewport_refusal(modified, untracked) returns a
>    precise, fence-aware refusal string for a dirty-on-trunk viewport (naming
>    the count of tracked modifications that actually block the fast-forward,
>    and that a worker may not clean the viewport, only preserve precious work
>    to a worktree branch), and None for a clean tree.
> 2. cmd_sync, when on the trunk with ahead == 0 and behind > 0, calls it before
>    attempting merge --ff-only and bails with that diagnosis when the tree is
>    dirty, so the misleading stray-commits branch is unreachable for the dirty
>    case.
> 3. The git-pen test module proves the helper: a dirty tree yields the honest
>    refusal (mentions uncommitted, not stray commits); a clean tree yields None.
>    The test is non-vacuous: it would fail against the old code path that
>    emitted the stray-commits message.
>
> Scope guard: this fixes the diagnosis only. It does NOT make the pen mutate
> bdo's viewport (auto-commit / auto-stash / auto-clean), which is an
> owner-sensitive design call surfaced separately. Honest refusal, not silent
> repair.

## Why

A real incident: a session opened on the viewport, which a prior session had
left 8 commits behind origin and dirty with stranded work. git.py sync's
SessionStart hook reported a fast-forward refusal telling the session to branch
and PR the stray commits. But ahead == 0: there were no stray commits. The
blocker was uncommitted tracked modifications, which the workstation fence
(done-line 0145) forbids a worker from reverting on the viewport. The message
sent the session chasing a non-existent problem and named a move the fence then
denied. The pen should tell the truth about why it refused.

Serves epic.owner-harness: the sync hook exists so bdo's viewport stays current
without his hand; a hook that misdiagnoses its own refusal pushes the cleanup
back toward confusion (and toward bdo), the opposite of its purpose.

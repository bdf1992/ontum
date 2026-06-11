# Done-line 0037 — SessionStart gardens dead worktrees and surfaces chores

Written before code, per §9.4. When this line is met, stop.

> **Done when:** `git.py garden` (and `--hook`, wired to SessionStart) is a
> fail-open pass that **removes only** a worktree whose branch carries a
> merged PR and whose tree is clean — and **surfaces, never destroys**,
> everything else: a worktree with uncommitted changes, one committed-but-not-
> merged (no PR), one with an open PR in flight, and a count of merged local
> branches with no worktree. The classifier is a pure function (`garden_verdict`)
> the suite drives directly; it never prunes blind (gh unreachable → nothing
> removed), never touches the viewport or the current session's own worktree,
> and exits 0 always in hook mode. §10 proof: a worktree that is *merged*
> (branch landed) yet *dirty* (uncommitted work) is two locally-fine facts that
> refuse to fit — the gardener must surface it, never prune the work away.

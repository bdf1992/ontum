# Done-line 0011 — the PR pen: the story is validated, not requested

Written before code, per §9.4. When this line is met, stop.

> **Done when:** a session cannot open or reshape a PR with raw
> `gh` — the mutating verbs (`gh pr create/edit/merge/close/review`,
> `git push` to `main`) are denied by a PreToolUse hook whose message
> points at the one pen; the pen
> (`.claude/skills/branch-ritual/pr.py`) refuses to submit without
> the story — a title that is not the branch name, what landed, the
> done-line it serves (or its named absence), the report number (or
> its named absence), the end-state (`done | report | needs-you`),
> and any flags raised for bdo — and refuses dead branches, second
> open PRs from the same head, and red tests unless the red is
> declared in the story itself; tests pin the refusals (a
> locally-fine but story-less create must not fit, §10); and the
> branch-ritual skill points at the pen instead of describing the
> form in prose.

Amended before the hook was written (bdo, mid-build): the same hook
is also the **watcher** — every raw invocation of an external tool
that isn't denied is recorded to a watch log (a sensor trace,
gitignored, deletable — not truth), and a `--report` fold over it
says which raw tools are actually in use, so the next wrapper gets
built from observed use, not speculation. We only build what we use.

Amended again (bdo): collection alone is silent — the watcher must
also *shame*: when a session uses the generic brand where no branded
wrapper exists, a PostToolUse hook injects the fact into the context
window (once per tool per session, with the running audit count), so
it gets brought up naturally and becomes a judgment call. Surfaced or
silent — never silently tolerated.

Named on the record: the hook gates *sessions*, not the owner —
GitHub's "Compare & pull request" button still exists for bdo. The
pen's `check` verb (story audit over open PRs) is the gardening-side
sensor for that gap.

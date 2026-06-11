"""fence/policy.py - the family-neutral fence registry (done-line 0027).

The firm denials live here once, as data, whatever harness a session
arrives through. Claude Code reaches them via .claude/hooks/
command_guard.py (its own DENY_RULES today - parity held by
tests/test_fence.py until that guard converges onto this registry);
Codex reaches them via the rendered .codex/ layer
(fence/render_codex.py). A new family gets a renderer, not a rewrite.

Each rule is one record:

- id            stable name for the rule
- argv          the command prefix it matches, execvp-style; an element
                is a literal or a tuple of alternatives at that position
- decision      "forbidden" (blocked outright) or "prompt" (the human
                approves each invocation)
- justification the refusal as a story for a cold reader: the why and
                the paved path inline, so a session that sees only the
                rejection knows what to do instead
- claude_guard  the command_guard rule ids this mirrors on the Claude
                side (empty for prompt rules - Claude watches those)
- match /       example invocations that must / must not fit the rule;
  not_match     Codex re-validates them at load, our tests at suite time

Stdlib only. Pure data plus the one matcher the examples are tested
against.
"""

PR_PEN = "python .claude/skills/branch-ritual/pr.py"
GIT_PEN = "python .claude/skills/branch-ritual/git.py"

RULES = (
    {
        "id": "git-add",
        "argv": ("git", "add"),
        "decision": "forbidden",
        "justification": (
            "Raw `git add` is denied here (done-line 0020): the fleet shares "
            "one tree, and a sweep stages another session's work. Staging "
            f"goes through the git pen, named paths only: {GIT_PEN} add "
            "<path> <path>."
        ),
        "claude_guard": ("git-add-raw",),
        "match": ("git add .", "git add -A", "git add loop/reconcile.py"),
        "not_match": ("git status", "git diff"),
    },
    {
        "id": "git-commit",
        "argv": ("git", "commit"),
        "decision": "forbidden",
        "justification": (
            "Raw `git commit` is denied here (done-line 0020): commits are "
            f"branded through the git pen - {GIT_PEN} commit -m \"<what "
            "landed>\" [paths] - named paths, a real message, never the "
            "trunk."
        ),
        "claude_guard": ("git-commit-raw",),
        "match": ("git commit -m wip", "git commit -am wip"),
        "not_match": ("git log -1", "git commit-tree HEAD^{tree}"),
    },
    {
        "id": "git-push",
        "argv": ("git", "push"),
        "decision": "forbidden",
        "justification": (
            "Raw `git push` is denied here (done-line 0014): nothing leaves "
            f"the machine unchecked. The branded push is {PR_PEN} push - it "
            "checks the branch is still alive and the suite is green (or "
            "declared red) first. Pushing main is bdo's alone (D-4)."
        ),
        "claude_guard": ("git-push-raw", "git-push-trunk"),
        "match": ("git push", "git push origin main",
                  "git push -u origin claude/x"),
        "not_match": ("git fetch origin", "git pull"),
    },
    {
        "id": "gh-pr-create",
        "argv": ("gh", "pr", "create"),
        "decision": "forbidden",
        "justification": (
            "Raw `gh pr create` is denied here (branch-ritual): every PR to "
            "main carries a validated story. The pen scaffolds and checks "
            f"it: {PR_PEN} create ... (-h lists the required fields)."
        ),
        "claude_guard": ("gh-pr-create",),
        "match": ("gh pr create --title t --body b",),
        "not_match": ("gh pr view 7888", "gh pr list"),
    },
    {
        "id": "gh-pr-edit",
        "argv": ("gh", "pr", "edit"),
        "decision": "forbidden",
        "justification": (
            "Raw `gh pr edit` is denied here (branch-ritual): reshape the "
            f"story through the pen - {PR_PEN} edit <number> ..."
        ),
        "claude_guard": ("gh-pr-edit",),
        "match": ("gh pr edit 12 --body x",),
        "not_match": ("gh pr view 12",),
    },
    {
        "id": "gh-pr-merge",
        "argv": ("gh", "pr", "merge"),
        "decision": "forbidden",
        "justification": (
            "Denied, firm: never merge your own PR - the stamp is bdo's, "
            "the last stop (D-4)."
        ),
        "claude_guard": ("gh-pr-merge",),
        "match": ("gh pr merge 12 --squash",),
        "not_match": ("gh pr checks 12",),
    },
    {
        "id": "gh-pr-close-reopen",
        "argv": ("gh", "pr", ("close", "reopen")),
        "decision": "forbidden",
        "justification": (
            "Denied: opening and closing PRs is ritual work - surface it to "
            "bdo instead of doing it raw."
        ),
        "claude_guard": ("gh-pr-close",),
        "match": ("gh pr close 12", "gh pr reopen 12"),
        "not_match": ("gh pr view 12",),
    },
    {
        "id": "gh-pr-review",
        "argv": ("gh", "pr", "review"),
        "decision": "forbidden",
        "justification": (
            "Denied: no one signs their own line (D-2) - a session does not "
            "review or approve PRs."
        ),
        "claude_guard": ("gh-pr-review",),
        "match": ("gh pr review 12 --approve",),
        "not_match": ("gh pr diff 12",),
    },
    {
        "id": "gh-pr-ready",
        "argv": ("gh", "pr", "ready"),
        "decision": "forbidden",
        "justification": (
            "Raw `gh pr ready` is denied here (done-line 0017): the draft "
            f"flip IS the merge signal - it goes through the pen: {PR_PEN} "
            f"ready <n> (or {PR_PEN} unready <n> to roll back)."
        ),
        "claude_guard": ("gh-pr-ready",),
        "match": ("gh pr ready 12",),
        "not_match": ("gh pr view 12",),
    },
    {
        "id": "git-checkout",
        "argv": ("git", "checkout"),
        "decision": "prompt",
        "justification": (
            "The repo root is bdo's viewport on main - a session switches "
            "branches only inside its own worktree (../ontum-wt/<slug>; "
            "AGENTS.md). Approve only if this runs in your worktree."
        ),
        "claude_guard": (),
        "match": ("git checkout main", "git checkout -b codex/x"),
        "not_match": ("git status",),
    },
    {
        "id": "git-switch",
        "argv": ("git", "switch"),
        "decision": "prompt",
        "justification": (
            "The repo root is bdo's viewport on main - a session switches "
            "branches only inside its own worktree (../ontum-wt/<slug>; "
            "AGENTS.md). Approve only if this runs in your worktree."
        ),
        "claude_guard": (),
        "match": ("git switch main",),
        "not_match": ("git branch --list",),
    },
)


def prefix_matches(argv, pattern):
    """True when `argv` (a list of arguments) starts with `pattern`.

    The documented Codex semantics: each pattern element is a literal
    or a union of literals at that argument position, and the whole
    pattern must be an exact prefix of the argv list.
    """
    if len(argv) < len(pattern):
        return False
    for got, want in zip(argv, pattern):
        alternatives = want if isinstance(want, tuple) else (want,)
        if got not in alternatives:
            return False
    return True

"""fence/policy.py - the family-neutral fence registry (done-line 0027).

The firm denials live here once, as data, whatever harness a session
arrives through. Claude Code compiles them at runtime (done-line 0029:
command_guard's DENY_RULES are derived from this table, justifications
becoming refusal messages); Codex loads them through the rendered
.codex/ layer (fence/render_codex.py). Parity is structural - one
table, two surfaces - and a new family gets a renderer, not a rewrite.

Each rule is one record:

- id            stable name for the rule
- argv          the command prefix it matches, execvp-style; an element
                is a literal or a tuple of alternatives at that position
- decision      "forbidden" (blocked outright) or "prompt" (the human
                approves each invocation; Claude's side watches these
                rather than prompting - the watcher decides if that
                ever hardens)
- justification the refusal as a story for a cold reader: the why and
                the paved path inline, so a session that sees only the
                rejection knows what to do instead
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
            "declared red) first. Pushing main is never a session act: bdo "
            "confirms arcs and the independent merge-node lands confirmed "
            "PRs (D-4)."
        ),
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
        "match": ("gh pr edit 12 --body x",),
        "not_match": ("gh pr view 12",),
    },
    {
        "id": "gh-pr-merge",
        "argv": ("gh", "pr", "merge"),
        "decision": "forbidden",
        "justification": (
            "Raw `gh pr merge` is denied: main lands only through the "
            "independent merge-node, via the pen, after bdo confirms the arc "
            f"(D-4). A piece-PR into an epic branch goes through the pen: "
            f"{PR_PEN} integrate <n> (it refuses a main base; done-line "
            "0029)."
        ),
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
        "match": ("git switch main",),
        "not_match": ("git branch --list",),
    },
    # The rest of the mutating git surface (done-line 0101). The Claude
    # guard already *watches* every one of these (command_guard.GIT_MUTATING)
    # — registering them here is what hardens the Codex surface (it prompts)
    # and completes the fence: a session reading only a refusal learns the
    # paved path. Grouped by what the verbs do to the tree, one story each.
    {
        "id": "git-history-integrate",
        "argv": ("git", ("merge", "rebase", "cherry-pick", "revert",
                          "am", "apply")),
        "decision": "prompt",
        "justification": (
            "Integrating or rewriting commits (merge/rebase/cherry-pick/"
            "revert/am/apply) reshapes history. In the shared fleet tree "
            "that belongs inside your own worktree (../ontum-wt/<slug>; "
            "AGENTS.md), never the viewport on main - and trunk integration "
            "is the independent merge-node's after bdo confirms the arc "
            "(D-4), never a session's. Approve only inside your worktree."
        ),
        "match": ("git merge origin/main", "git rebase main",
                  "git cherry-pick abc123"),
        "not_match": ("git status", "git log --oneline"),
    },
    {
        "id": "git-reset-discard",
        "argv": ("git", ("reset", "restore", "clean", "stash")),
        "decision": "prompt",
        "justification": (
            "Discarding or shelving working state (reset/restore/clean/"
            "stash) can destroy uncommitted work. The doctrine asks for a "
            "reversible alternative before a destructive git op - commit, "
            "or stash with intent, first - and approve only with the loss "
            "in view."
        ),
        "match": ("git reset --hard HEAD", "git restore .",
                  "git clean -fd", "git stash"),
        "not_match": ("git status",),
    },
    {
        "id": "git-tree-edit",
        "argv": ("git", ("rm", "mv")),
        "decision": "prompt",
        "justification": (
            "`git rm` / `git mv` stage a delete or rename. Staging goes "
            f"through the git pen, named paths only ({GIT_PEN} add <path>); "
            "approve a raw rm/mv only inside your worktree."
        ),
        "match": ("git rm old.py", "git mv a.py b.py"),
        "not_match": ("git status",),
    },
    # Branch/worktree topology is split mutating-vs-introspection (done-line
    # 0120): the old single rule matched the whole `git branch`/`git worktree`
    # prefix, so read-only introspection (`git branch --show-current`, the
    # single most common opening move a session makes — 60% of the last 50
    # sessions probe it) got prompted on Codex. The fence is a prompt/deny
    # list: anything no rule matches is allowed, so narrowing the argv to the
    # *mutating* verbs/flags lets read-only forms fall through to allowed while
    # topology still prompts. The Claude guard watches all of it regardless.
    {
        "id": "git-branch-mutate",
        "argv": ("git", "branch", ("-d", "-D", "-m", "-M", "-c", "-C",
                                   "--delete", "--move", "--copy")),
        "decision": "prompt",
        "justification": (
            "Deleting, moving, or copying a branch is fleet topology — in the "
            "shared tree it can strand unpushed work. Sessions branch off main "
            "into their own worktree (../ontum-wt/<slug>; AGENTS.md); approve "
            "only for your own worktree. Read-only `git branch`, "
            "`git branch --show-current`, and `git branch --list` are not "
            "topology — they pass, the introspection a session needs to know "
            "where it is."
        ),
        "match": ("git branch -d old", "git branch -D feature",
                  "git branch -m old new", "git branch --delete old",
                  "git branch --move old new", "git branch -C a b"),
        "not_match": ("git branch", "git branch --show-current",
                      "git branch --list", "git status"),
    },
    {
        "id": "git-worktree-mutate",
        "argv": ("git", "worktree", ("add", "remove", "prune", "repair",
                                     "move")),
        "decision": "prompt",
        "justification": (
            "Adding, removing, pruning, repairing, or moving a worktree is "
            "fleet topology. A session provisions its own worktree off main "
            "(../ontum-wt/<slug>; AGENTS.md) and approves only for that. "
            "Read-only `git worktree list [--porcelain]` is introspection — it "
            "passes, so a session can see the fleet's worktrees."
        ),
        "match": ("git worktree add ../wt/x", "git worktree remove ../wt/x",
                  "git worktree prune", "git worktree move ../a ../b"),
        "not_match": ("git worktree list", "git worktree list --porcelain"),
    },
    # Raw `gh` mutations beyond `pr` (done-line 0101). `gh` is always
    # watched by the Claude guard (it is external, never local); registering
    # the write surfaces here makes Codex prompt on them and the fence speak
    # to them. The reflector and gate pens reach GitHub through subprocess,
    # invisible to this guard - so these rules govern only what a session
    # types raw, which is exactly the reach to surface.
    {
        "id": "gh-issue-mutate",
        "argv": ("gh", "issue", ("create", "edit", "close", "reopen",
                                 "comment", "delete", "lock", "unlock",
                                 "pin", "unpin", "transfer", "develop")),
        "decision": "prompt",
        "justification": (
            "Issues are bdo's surface. The reflector pen mirrors the owner's "
            "stamp queue onto GitHub automatically "
            "(.claude/skills/reflect/reflect.py) and the gate opens its own "
            "run-issue through its pen - a session does not open, close, or "
            "comment on issues raw. Surface the intent to bdo instead."
        ),
        "match": ("gh issue close 3", "gh issue comment 5 --body x",
                  "gh issue create --title t --body b"),
        "not_match": ("gh issue view 3", "gh issue list"),
    },
    {
        "id": "gh-api-write",
        "argv": ("gh", "api", "-X", ("POST", "PUT", "PATCH", "DELETE",
                                     "post", "put", "patch", "delete")),
        "decision": "prompt",
        "justification": (
            "`gh api -X POST|PUT|PATCH|DELETE` writes straight to GitHub's "
            "API - bdo's surface, reached raw. A GET (the default) is a read "
            "and is fine; a write goes through a pen or is surfaced to bdo. "
            "(The watcher's classifier also tags `-f`/`--field` writes that "
            "omit `-X`, so the report sees them even when this prefix does "
            "not.)"
        ),
        "match": ("gh api -X POST repos/o/r/issues",
                  "gh api -X DELETE repos/o/r/issues/1"),
        "not_match": ("gh api user", "gh api -X GET repos/o/r"),
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

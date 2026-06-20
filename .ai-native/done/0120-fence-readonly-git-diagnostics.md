# Done-line 0120 — Fence read-only git diagnostics — branch/worktree topology splits mutating-vs-introspection

Written before code, per §9.4. When this line is met, stop.

The diagnosis (this session, 2026-06-18): a fold over the last 50 sessions'
opening moves (the watcher log) found that **30 of 50 sessions probe
`git branch` / `git status` in their first three shell calls** — orienting to
where they are is the single most common thing an agent does at boot. The
fence's one `git-branch-topology` rule matched the whole `git branch` /
`git worktree` argv prefix, so on the Codex surface that most-common opening
move (`git branch --show-current`, `git worktree list`) was *prompted* — a
human approval sat on top of read-only introspection. bdo's hotfix, part 1:
restore read-only diagnostics under Codex without loosening topology.

The frame (reuse, no new infra): the fence is a prompt/deny list — anything no
rule matches is allowed. So the fix is to *narrow the argv* to the mutating
verbs/flags; read-only forms then match no rule and fall through to allowed.
The single rule splits into two: `git-branch-mutate`
(-d/-D/-m/-M/-c/-C/--delete/--move/--copy) and `git-worktree-mutate`
(add/remove/prune/repair/move), both still `prompt`. The Claude guard watches
all of it regardless (command_guard.GIT_MUTATING is unchanged); the behaviour
change is felt on the Codex surface, re-rendered deterministically from the
registry. A chapter of the session-gateway anthology, sibling of 0118's sheath.

> **Done when:** `fence/policy.py`'s single `git-branch-topology` rule is
> replaced by `git-branch-mutate` and `git-worktree-mutate`, each matching only
> the mutating verbs/flags (decision `prompt`), so read-only `git branch`,
> `git branch --show-current`, `git branch --list`, and
> `git worktree list [--porcelain]` match no rule and are allowed;
> `.codex/rules/ontum.rules` is freshly re-rendered (committed bytes equal
> `python fence/render_codex.py`); `python -m unittest tests.test_fence` is
> green (its example-fit and fresh-render checks cover the new rules and the
> read-only `not_match` forms); and the work is a PR the merge-node can land.
> The teeth: a rule still matching the bare `git branch` prefix would prompt
> read-only introspection and fail the `not_match` assertions.

> **Non-example:** an explicit allow-rule for read-only forms (the fence has no
> allow verb — absence of a match IS the allow; adding one inverts the model);
> blocking `git branch -f`/`--force` (outside bdo's named mutating set for this
> hotfix — a considered edge, still watched by command_guard); Codex write-hook
> enforcement (bdo's named follow-up, not this); the workspace-claim binding
> (its own chapter, ported next).

> **Arc:** proposed — a chapter of the session-gateway Anthology
> (session-gateway.proposal.md), serving the insulated-workspace /
> read-only-diagnostics throughline. bdo names the anthology; this stands on
> its own done-line until then and takes no owner stamp it was not given.

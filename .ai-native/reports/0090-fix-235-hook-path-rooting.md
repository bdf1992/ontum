# Report 0090 — Landing #235 — the hook-path rooting, the bootstrap through the break it fixes

## What landed

**PR #240** (`claude/hook-path-rooting` -> main): issue #235 fixed. `.claude/settings.json` has all 17 cwd-relative `python .claude/*.py` hook commands rooted at `$CLAUDE_PROJECT_DIR`; the `python -m loop.*` module calls are left as-is (`loop/` exists in every worktree). Atom-backed — `atom.hook-path-rooting.v0`, done-line **0128**, independent value-gate **accept** `rcp.6587217eb4bc`. CI atom-invariant check green, `MERGEABLE`, not a draft.

The whole thing was built in an isolated worktree off `origin/main` — the poisoned shared viewport (other sessions' uncommitted log appends) was never touched. The fix for the worktree-break was delivered by routing around the worktree-break itself.

## The handoff was mis-scoped (named, not silently resolved — §9)

The handoff said: "rebase the single commit onto main, open a 1-commit PR, merge-node lands it — tiny, ~3 commands." Three findings corrected that:

1. **Not a clean cherry-pick.** The stranded commit `9bd1cfd` sits on the terminal-pull-gateway stack, whose `settings.json` already carries `change_guard`/`ask_guard` — hooks main does not have. Cherry-picking onto main conflicts (git cannot reconcile "they rooted this path" against "main never had this block"). So this is a fresh main-targeted commit applying the same *intent* to main's actual hook set.
2. **The off-log atom gate is live** (`.github/workflows/atom-invariant.yml`). A settings-only PR has no atom and would go red. So the slice needed a full dogfood: atom + announce + independent value-gate receipt.
3. **Landing is not blocked on bdo.** All 10 arcs are already confirmed on the trunk, including `epic.owner-harness`. The real gate was always the off-log invariant, not an owner gesture.

## The decision I made (a genuine fork, decided with reasoning, D-4 untouched)

Separate subset-fix PR on main **now** vs. let the full fix ride with PR #226. I chose the separate PR: #235 hard-blocks *every* worktree session (the coordination tax the session-gateway arc exists to pay down), #226 is a large unlanded stack that may sit, and a tiny forward-compatible unblock is exactly the "piece-scale landable slice" the repo favors. It is forward-compatible: when #226 lands, the shared hooks are already rooted on both sides and #226's `change_guard`/`ask_guard` arrive already rooted, so they reconcile.

## needs-you

- **A merge-node session should land PR #240** under the already-confirmed `epic.owner-harness` (`pr.py land 240 --epic epic.owner-harness --by merge-node.claude.v1`). I authored it, so I cannot land it (no one signs their own line). Nothing is on bdo here — the arc is already confirmed.
- **The stranded branch `claude/fix-235-hook-paths`** (carrying the un-landable entangled `9bd1cfd`) is now superseded by #240's main-targeted form; the gardener can prune it. Not bdo's chore.
- The poisoned shared viewport's uncommitted log appends belong to other live sessions — left untouched by design (losing receipts is real); not mine and not bdo's to clean here.

## End-state

`report` — #235 fixed and landable: PR #240 atom-backed, green, merge-node eligible on a confirmed arc; awaits a merge-node session's land, nothing on bdo.

# Done-line 0128 — Hook-path rooting — fix #235

> **Done when:** every cwd-relative `python .claude/...py` hook command in `.claude/settings.json` is rooted at `$CLAUDE_PROJECT_DIR` (the `python -m loop.*` module calls left as-is, since `loop/` exists in every worktree), the suite is green, and the change is on main as an atom-backed PR — so a session whose cwd is a worktree missing a newer hook script no longer hard-blocks on every Edit/Write/Bash (issue #235).

This is the bootstrap slice: it applies the rooting to main's current hook set (17 commands). The not-yet-on-main hooks (`change_guard`, `ask_guard`) arrive already rooted with the stack that introduces them (PR #226), so this is forward-compatible — it does not wait for that stack to land. It mirrors the intent of the stranded commit `9bd1cfd`, which could not cherry-pick cleanly onto main because main's `settings.json` lacks those later hooks.

Born of the coordination tax: the fix for the worktree-break had to route around the worktree-break itself (a clean worktree off `origin/main`, the poisoned shared viewport untouched).

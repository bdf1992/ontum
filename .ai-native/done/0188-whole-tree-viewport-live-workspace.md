# Done-line 0188 — A live, auto-regenerated VS Code workspace from the forest fold

Written before code, per §9.4. When this line is met, stop.

> **Done when:** `loop/forest.py --workspace` + a SessionStart regen hook: a
> generated, gitignored VS Code `.code-workspace` listing the viewport + sibling
> repos + each LIVE/in-review worktree as a navigable root, decorated by status,
> regenerated every session so it stays current. §10 tooth: a test proves a live
> worktree IS a root and a stranded/merged/viewport worktree is NOT — a generator
> that included everything (or nothing) is caught. The file is a live cache
> (gitignored), never committed. Out of scope (named): VS Code's own
> reload-to-pick-up-new-roots behavior (a UI limitation, not ours).

## Why

bdo, 2026-06-22: *"all I need is something that makes a vscode workspace, and
makes sure it's up to date and live."* The forest fold (done-line 0186) already
folds the whole tree of in-flight work into one decorated model; this projects
that model into VS Code's multi-root `.code-workspace` shape so each live
worktree is one navigable root in his Explorer, alongside the viewport and the
sibling repos — and a SessionStart hook regenerates it every session, so the
view stays live without him touching anything.

## In scope (one increment)

- `loop/forest.py` — a `--workspace` mode (+ `--out`, `--hook`): the forest model
  projected into a `{folders, settings}` `.code-workspace`, base roots first
  (the viewport as `ontum`, then `../gallery`/`../holonsearch` if present), then
  each live-worktree/in-review worktree as a decorated root (status emoji + PR
  number + short branch). Pure-stdlib, deterministic; the viewport tree and the
  default out-path both follow the PRIMARY checkout.
- `.claude/settings.json` — a SessionStart hook (`python -m loop.forest
  --workspace --hook`, fail-open, exit 0 always) so the file stays current.
- `.gitignore` — `ontum-forest.code-workspace` (a live cache, never committed).
- `tests/test_forest_workspace.py` — the non-vacuous §10 tooth.
- The backing atom `atom.whole-tree-viewport-live-workspace.v0` (no arc claimed).

## Not in scope (named, not invented away)

- **VS Code's own reload-to-pick-up-new-roots behavior** — when the file changes,
  VS Code does not always live-reload the folder set; that is a UI limitation, not
  this generator's. The file is always current on disk at session start.
- **Live-session tracking inside each root** — sessions and their environments;
  the forest's named v1, not this increment.
- **The served HTML view** — a later layer.

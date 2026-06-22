# Done-line 0186 — The whole-tree viewport forest fold — folds the git forest + log atom state into one decorated FOREST.md

Written before code, per §9.4. When this line is met, stop.

> **Done when:** `loop/forest.py` is a pure read-only fold composing the git
> forest (worktrees + branches + per-branch PR state, mirroring git.py garden's
> sensing — `git worktree list --porcelain` → worktrees+branches, `gh pr list
> --state all` → PR states, per-worktree `git status --porcelain` → uncommitted,
> plus loose branches) with the log's atom pipeline state (`loop.reconcile.Fold`)
> into ONE decorated forest model, rendering a deterministic, regenerable
> `FOREST.md` (every work-item flagged by status: live-worktree / in-review /
> stranded / parked-atom / merged) + a `--json` twin. It runs as `python -m
> loop.forest` from the repo root (like census/digest): default renders FOREST.md
> to stdout (read-only-safe), `--json` emits the dataset, `--write` writes
> `FOREST.md` at the repo root. Ends with a clear `done | report | needs-you`
> stdout line. §10 tooth: `tests/test_forest.py` proves the decoration is
> non-vacuous — a stranded worktree cannot be flagged 'merged', a parked atom
> cannot read 'landed', and a constant/fabricated classifier is CAUGHT.
> `FOREST.md` is generated output (a top note says so), never hand-kept. The work
> is atom-backed (`atom.whole-tree-viewport-forest.v0`); it claims no arc — the
> proposal `whole-tree-viewport.proposal.md` proposes the arc name for bdo (D-4).

## Why

bdo, 2026-06-22: *"I want my viewport to be the whole tree, not just a viewport
into only the working now trunk ... a decorated/tagged/flagged instance of the
work, in repo, managed automatically, so I can see the sessions that are
happening and their files/environments. I don't want MY viewport to be a
blocker anymore."* Today the viewport is the primary checkout pinned to
origin/main, so it only shows LANDED work; the whole forest of in-flight work
(worktrees, branches, parked atoms, open PRs) is invisible from it, and bdo's
physical checkout is load-bearing. This fold makes the forest one decorated,
in-repo read, so the checkout becomes one leaf.

## In scope (one increment)

- `loop/forest.py` — the read-only fold: git-forest sensing (mirroring garden)
  + log atom state (reconcile.Fold) → decorated model → FOREST.md + `--json`.
- `FOREST.md` — generated output, committed, with a do-not-hand-edit note.
- `tests/test_forest.py` — the non-vacuous §10 tooth.
- A `loop/CLAUDE.md` module-layering line for the new fold.
- The backing atom `atom.whole-tree-viewport-forest.v0` (no arc claimed).
- The proposal `whole-tree-viewport.proposal.md` (PROPOSED, bdo's to steer).

## Not in scope (named, not invented away)

- **Live-session tracking** — sessions and their environments via
  `loop/watcher.py`; v1, named not built.
- **The served HTML view** — a localhost/served surface; a later layer.
- **The auto-regen hook/tick wiring** — the hook or tick that regenerates
  FOREST.md automatically; named in the proposal (D), not wired here.
- **Making this bdo's real reading surface** so the checkout stops being
  load-bearing — the viewport-decoupling end-state (E); bdo's call (D-4).

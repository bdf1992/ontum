# Whole-tree viewport — the blueprint bundle (PROPOSED)

> Status: **PROPOSED** — a blueprint for bdo to steer, authored 2026-06-22 at his
> on-record ask (this session). This is the *bundle* (the shape, the categorized
> concept-list, the calls-to-action against a purpose), not a finished build. The
> first increment — `loop/forest.py` + `FOREST.md` — lands under done-line 0186;
> the rest is named here and awaits bdo's stamp. Nothing past v0 is built.

## Purpose

> **bdo's viewport stops being load-bearing: the whole forest of in-flight work
> is one decorated, auto-managed, in-repo read, and his physical checkout is one
> leaf among many — never the blocker.**

bdo, 2026-06-22, verbatim intent: *"I want my viewport to be the whole tree, not
just a viewport into only the working now trunk ... a decorated/tagged/flagged
instance of the work, in repo, managed automatically, so I can see the sessions
that are happening and their files/environments. I don't want MY viewport to be
a blocker anymore."*

Today the viewport is the primary checkout pinned to `origin/main`. It shows only
**landed** work. The whole forest — worktrees, branches, parked atoms, open PRs —
is invisible from it, and because the checkout is the only surface, it is
load-bearing: a dirty or stranded viewport blocks (the `:whiteout` utensil, #415,
exists because of exactly this). The fix is a generated surface that folds the
forest into one read, so the checkout becomes a leaf, not the lens.

## The three-layer shape

```
  A. Sources (sensed, never owned)        B. The forest fold              C. The surface
  ────────────────────────────────        ──────────────────              ──────────────
  git worktree list --porcelain   ─┐
  gh pr list --state all          ─┼─►  loop/forest.py  ──decorate──►  FOREST.md  (committed)
  git status --porcelain (per wt) ─┤      (pure, read-only,            FOREST --json (twin)
  loop.reconcile.Fold (atom state)─┘       deterministic fold)          [v1: served HTML]
```

Two properties the shape must hold:

- **Auto-managed.** The surface is *generated*, never hand-kept. `FOREST.md`
  carries a do-not-hand-edit note and is regenerable by one command. (The
  *automatic* regeneration — a hook or tick — is category D, named not built.)
- **Viewport-decoupled.** The fold senses the forest from outside any single
  checkout. The primary checkout is just `worktree[0]`; the surface does not
  depend on which branch it sits on, and reading the surface never mutates a tree.

## The categories (label · description · v0 / the gap)

**A — Sources.** *Where the forest's facts come from, sensed and never owned.*
- v0: the same sources `git.py garden`/`garden_verdict` already fold —
  `git worktree list --porcelain` (worktrees + their branches), `gh pr list
  --state all --json headRefName,state` (PR states), per-worktree `git status
  --porcelain` (uncommitted), and loose branches with no worktree — plus
  `loop.reconcile.Fold` for each atom's pipeline state. No second truth (§10):
  forest.py re-derives from the same sources garden reads; it is a sibling fold,
  not a new ledger.
- Gap (v1): **live sessions and their environments** are not yet a source —
  `loop/watcher.py` (the idle-session fold) is where they live; wiring it in is v1.

**B — The forest fold.** *The pure read-only composition that turns the sources
into one decorated model.*
- v0: `loop/forest.py`, in the `census`/`digest`/`gaps` grain (stdlib,
  deterministic, `--json`, a `done | report | needs-you` line). Each work-item is
  a node carrying its status flag.
- Gap: none for v0; the model is the increment.

**C — The surface.** *The decorated, regenerable read a human (and a machine)
consume.*
- v0: `FOREST.md` (committed, generated) + a `--json` twin; default run renders
  to stdout (read-only-safe), `--write` writes the file.
- Gap (v1): **the served HTML view** — a localhost/served surface with the
  decoration as a real UI; a later layer, not this file.

**D — Auto-management.** *How the surface stays current without a human running
the command.*
- v0: a human (or any session) runs `python -m loop.forest --write`.
- Gap: **the auto-regen hook/tick wiring** — a `SessionStart`/`Stop` hook or a
  loop-tick that regenerates `FOREST.md` whenever the forest changes, so it is
  never stale. Named here; not wired in v0 (a writing hook is a contract change,
  bdo's to stamp, like the Stop-hook reflect beat).

**E — Viewport-decoupling.** *The end-state where the checkout stops being
load-bearing.*
- v0: the surface exists and is decoupled by construction (it senses from
  outside any one tree).
- Gap: **make this surface bdo's real reading surface** — the move that retires
  the checkout-as-lens. Once the forest read is where bdo looks, a dirty or
  stranded primary tree is no longer a blocker; it is one flagged leaf the surface
  shows like any other. This is the purpose realized, and it is bdo's call (D-4).

## The concept-list (what to ponder)

1. Is the forest model a first-class record (sibling of the digest's dataset),
   with its own `--json` contract a served surface later consumes? (B + C)
2. What is the full status vocabulary a work-item can wear, and is it closed in
   code or admitted? (B) — v0 fixes it in code: `live-worktree`, `in-review`,
   `stranded`, `parked-atom`, `merged`.
3. Should live sessions/environments be a source, and is `watcher.py` the right
   seam? (A, v1)
4. Does `FOREST.md` auto-regenerate on a hook/tick, and which? (D)
5. When does the served HTML view earn its build over the committed file? (C, v1)
6. What is the gesture by which bdo makes the forest his reading surface, and what
   does the checkout become afterward? (E)

## Calls to action (against the purpose)

| # | CTA | Kind | Serves |
|---|-----|------|--------|
| CTA-1 | **Name the arc** (bdo's, D-4) — e.g. `epic.whole-tree-viewport` — so v0's atom and the pieces below have a confirmed home. | bdo's stamp | the arc |
| CTA-2 | Land **v0** (`loop/forest.py` + `FOREST.md`, done-line 0186) — the decorated forest read. | built; awaits review + arc | A, B, C |
| CTA-3 | **v1 = live sessions + environments** via `loop/watcher.py` as a forest source — see the sessions, not just the git forest. | build | A |
| CTA-4 | **D = the auto-regen hook/tick wiring** so `FOREST.md` is never stale (a contract change, bdo's to stamp). | bdo decides → build | D |
| CTA-5 | **The served HTML view** — the decoration as a real UI surface. | build (later) | C |
| CTA-6 | **E = make this surface bdo's real reading surface** so the checkout stops being load-bearing — the purpose realized. | bdo's call | E |

## Whose move

- **bdo decides** (target/structure, not a session's to set): CTA-1 (the arc
  name), CTA-4 (the writing-hook contract), CTA-6 (adopting the surface).
- **Session-buildable** once the arc is confirmed: CTA-2 (built), CTA-3, CTA-5.

## Compose, do not double-build (§10)

- `git.py garden`/`garden_verdict` already fold the git forest from the four
  sources above; `forest.py` re-derives from the **same** sources (garden is a
  skill pen, not importable, so re-sensing via subprocess is correct and is not a
  second truth — cited as sibling in the fold's docstring).
- `loop.reconcile.Fold` already computes each atom's pipeline state; `forest.py`
  imports and uses it for atom state — it does not re-derive the pipeline.
- The digest's `atoms_on_main` already answers "did atom X reach main?"; the
  forest's `merged` flag composes the same landing signal, never a new one.

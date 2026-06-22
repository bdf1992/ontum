# Report 0123 — the :whiteout utensil: a dirty viewport recovered, end-to-end

# Report 0123 — the :whiteout utensil: a dirty viewport recovered, end-to-end

A loop session asked to "work on environment and workstation cleanup and
janitorial duties." The centerpiece — bdo's viewport — was diverged and dirty
and **could not be cleaned by any sanctioned path** (the #415 deadlock). Per
"a rule that forces offloading is a bug in the rule — fix the rule, don't punt
the work," the session built the missing recovery utensil rather than handing
bdo a dirty tree.

## What landed

- **The `:whiteout` utensil (#415) — on main, PR #419, rcp.merge.419**
  (epic.substrate, done-line 0170, atom.whiteout-utensil.v0). `git.py whiteout`
  (and an explicit `git.py sync`) recovers a DIRTY viewport without losing a
  byte: it preserves the entire pile (tracked + untracked, `add -A` snapshot)
  on a `claude/rescue-viewport-<date>` branch — committed and pushed — BEFORE it
  cleans, then fast-forwards the clean viewport to origin/main and surfaces the
  rescue branch. Proof-carrying (the whiteout shape of done-line 0064). The pen
  is the one actor sanctioned to flip the viewport, so a session never routes
  around the workstation fence; `sync --hook` only points at the utensil at an
  ambient start. `tests/test_git_whiteout.py` is non-vacuous (a control proves a
  naive force-clean WOULD lose the pile).
- **Full work-particle, dogfooded**: built -> independent high-effort
  code-review (real findings processed: remote-namespace collision hardening, a
  failed-`add` guard, a sync help-doc fix) -> independent **value-gate accept**
  (value-gate.claude.v1, rcp.06ff9f5e6b30, trust-rail issue #425) -> independent
  **merge-node** land (merge-node.claude.v1, --attest-non-author). D-2 honoured
  at every gate; the author signed no line of its own acceptance or landing.
- **bdo's actual viewport recovered, live** — the dogfood of #415 itself: 65
  paths preserved on `claude/rescue-viewport-2026-06-21` (pushed to origin for
  reconciliation), viewport fast-forwarded 19 commits, now clean and synced.
- **A real bug fixed en route**: the atom's internal `id` did not match its
  versioned filename, which broke `loop.node judge`'s atom lookup (compose
  matched the filename, the judge pen did not). Fixed; every landed atom's id
  equals its file stem.
- **Garden**: `heal-herald-incidence` pruned (merged + clean, verified at the
  moment of the cut).

## needs-you

Two arc-steering judgments (D-4 — abandoning an arc's work is yours, not a
session's to sweep), surfaced rather than blind-deleted:

- **Stranded work that is real, unbuilt design** — preserved, awaiting your
  keep/abandon call: `strategy-prune` holds the complete **Prune-organ**
  done-line (the last organ of epic.strategy); `probe-fleet-easing` holds a
  `0171-continue-probe-fire-easing` draft. These are not debris.
- **Local-only / detached worktrees carrying commits not on origin** (at risk
  if swept): `scout-rank-instance` (7 commits), `environments-gateway`,
  `consequence-graph`, `digest-patch-notes`, `mn-233-reconcile`, and the
  detached `consequence-graph-v0` / `diagram-structure` / `placement-fold`. Each
  needs a per-arc PR-or-abandon decision.

Note: the frozen done-line 0170 names `epic.physical-barriers` where it should
read `epic.substrate` — a slip in a frozen file the session could not edit; the
atom correctly serves epic.substrate.

## End-state

`report` — the #415 deadlock is resolved end-to-end: `git.py whiteout` is on
main, the viewport is recovered, the utensil is dogfooded. The worktree garden
is an actively multi-session environment (worktrees appear and dirty states move
between assessment and action — caught live by verify-before-cut), so the
session held to conservative, verified cuts only and preserved every piece of
real work, surfacing the genuine arc-abandon judgments above instead of sweeping
them. One merge-node note for the harness: start merge-node sessions from the
viewport, not inside the target branch's worktree, so `pr.py reconcile` can claim
the branch in its own isolated worktree (the viewport-rooted-worktree trap, hit
benignly while landing #419).

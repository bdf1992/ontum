# Done-line 0170 — The :whiteout utensil — a session recovers a dirty viewport without losing work

# Done-line 0170 — The :whiteout utensil — a session recovers a dirty viewport without losing work

Written before code, per §9.4. When this line is met, stop.

> **Done when:** the git pen ships a `:whiteout` utensil (`git.py whiteout`,
> and an explicit `git.py sync` on a dirty tree) that recovers a DIRTY viewport
> without losing a byte: it PRESERVES the entire pile (tracked edits +
> untracked files) on a fresh `claude/rescue-viewport-<date>` branch —
> committed and pushed — BEFORE it cleans, then fast-forwards the now-clean
> viewport to origin/main and surfaces the rescue branch for reconciliation.
> The pen is the one actor sanctioned to flip the viewport, so a session never
> routes around the workstation fence; in ambient `sync --hook` the pen
> surfaces a pointer to the utensil rather than branching and pushing
> autonomously at every dirty session start. Proven by
> `tests/test_git_whiteout.py` joining the suite and **non-vacuous**: a real
> temp-repo test recovers a dirty viewport and asserts the rescue branch holds
> the exact pile byte-for-byte (the dirtied tracked file AND the untracked
> file) while the viewport reaches origin/main, plus a control proving a naive
> force-clean WOULD lose that pile — so the preservation assertion is
> load-bearing, not trivially true. The work is atom-backed under
> `epic.physical-barriers` with the suite green.

## Why

Two rules bdo set composed into a deadlock (#415, dogfooded by a viewport-started
session that hit it live): the dirty-viewport sort model (git pen, done-line
0031) says *"commit and push the work on a branch, then sync restores the
viewport"*, but the later workstation fence (done-lines 0145/0147) forbids every
working-state git verb in the viewport — `checkout`/`switch`/`branch`/`reset`/
`restore`/`clean`/`stash`/`merge` — and the git pen refuses to commit on the
trunk. So evacuating a dirty pile would need a branch the session cannot make, a
commit it cannot place, a stash it cannot take. `git.py sync` refuses while dirty
and points back at the now-impossible remedy. **A rule that forces offloading is
a bug in the rule — fix the rule, don't punt the work** (CLAUDE.md hard rule).

bdo's frame (2026-06-21, via the ask, confirmed in #415): a workstation ships
**fully equipped with `:whiteout`** — a named utensil that recovers from
mistakes — the same proof-carrying whiteout shape already in the repo (the
phrasing door, done-line 0064: prove what you erase is safe to erase before you
erase it). Here whiteout preserves the *whole pile* before it cleans, so the
recovery loses nothing. The git pen is the right home: it already legitimately
flips the viewport (it runs `checkout` + `merge --ff-only` via subprocess), so it
is the one actor sanctioned to flip — recovery is its, never a raw session git
that routes around the fence.

This is the first installation of `:whiteout` (the dirty-viewport sorter, bdo's
confirmed scope). The broader utensil — recovery generalized beyond the viewport
to any bench in a bad state — is named here and left for a later increment.

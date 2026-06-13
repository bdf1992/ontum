# Report 0057 — Cleanup: viewport strands sorted, off-log gate preserved (#123)

A cleanup session. The viewport (bdo's reading surface on main) had drifted 12
commits stale and was carrying a pile of uncommitted work from several prior
sessions — the SessionStart hooks refused the fast-forward and named the
divergence as the session's to sort, never bdo's. This session sorted it
without losing a line of real work, then gardened the branch/worktree/stash
sprawl behind it.

## What landed

**The off-log PR gate — PR #123 (done-lines 0066, 0068).** The highest-value
find: a complete, tested feature (`loop/pr_audit.py` + the PR pen's `audit`
verb + the `.github` server-side CI gate) was sitting *uncommitted* on the
viewport, built and proven by a prior session and never preserved. It holds
every PR to the atom invariant from the branch side, so a PR opened outside the
pen is caught when it carries no atom on the log. Verified green
(`tests.test_pr_audit`, 12 ok) and live — the sweep names four real orphans on
the board now. Branched off current origin/main (not the stale viewport base,
which would have spuriously deleted the inference-plane work), opened as a PR
the merge-node can land once its arc is confirmed.

**Viewport cleaned and synced.** The uncommitted edits were each checked
line-by-line against origin/main: every modified log line, `reflect.py`,
`test_owner_asks.py`, and the `0065`/`0067` done-lines were already landed
(redundant) and reverted; the genuinely novel work was carried off first. Main
fast-forwarded cleanly to `origin/main` (5d56a85).

**Branch/worktree/stash garden.** Deleted 13 confirmed-merged branches (each
cross-checked against its MERGED PR or `--merged origin/main`); pruned two stale
remote-tracking refs. Dropped a stale stash (a month-old README rescue still
carrying the *retired* "bdo merges" doctrine, superseded on main). Kept the
unmerged feature branches (`pen-fleet-safe-id`, the whiteout branch, the
outcome-pressure proposal), the four open-PR branches, and `keep/main-codex`.

## needs-you

These are genuine owner calls — arcs and dispositions, nothing mechanical:

1. **Confirm the arc for PR #123** so the merge-node can land the off-log gate.
2. **The four orphan PRs the new gate flags** (#107, #114, #118, #122): each
   reached GitHub with no atom on the log. The gate names them; the disposition
   (re-home through the pen, or close) is yours (D-4).
3. **A draft arc was stranded on the viewport: `epic.test-metabolism` v2** —
   "the test-quality pipeline, dual-keyed to its lineage," status *awaiting
   confirm-arc*. It was misplaced in the read-only `docs/sources/` zone (no v1
   on main); I did not author it into a home. It is preserved verbatim in the
   holding folder below and should live in `.ai-native/epics/` once you confirm
   it.
4. **The `outcome-pressure-fold` proposal** (its own branch, no PR): a proposal
   doc whose merit is yours to judge — land it as an arc or let it go.

## End-state

`report` — Off-log gate preserved as PR #123 (green, live); viewport cleaned and
fast-forwarded to origin/main; 13 merged branches + 1 stale stash gardened; two
unpreservable strays (a stale prior-session report 0051, the read-only-zone
epic-v2 draft) held verbatim at
`C:\Users\bdf19\ontum-wt\_viewport-strays-2026-06-13\`; the creole-glyph-language
seal receipt is still unlanded in `stash@{0}` (re-append via envoy when next
touching disclosure). Heads-up: a **live concurrent session** is building
spawn-rail work in the viewport (`spawn_guard.py` + done-0069, modified
mid-session) — left untouched. The whiteout branch
(`worktree-agent-a5921151c4f7ebe48`) is a complete, suite-green feature with no
PR; landing it needs a rebase onto main's since-moved `pen.py` (#108) — next
session's engineering, not bdo's.

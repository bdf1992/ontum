# Report 0019 — the viewport and the workbenches

## What landed

Done-line 0022 (viewport-and-workbenches): the discipline bdo adopted
in conversation is on the record in two places —

- **CONTRIBUTING.md, hard rules**: the primary checkout is the
  owner's viewport, parked on `main`; sessions never `git checkout`
  there; session work happens in a worktree
  (`git worktree add -b claude/<slug> ..\ontum-wt\<slug> main`),
  removed with the branch at dissolution; after the stamp the
  viewport catches up with `git pull` — the merge distributes, the
  pull is the return leg.
- **branch-ritual 0.6.0**: the standing shape gains the
  one-worktree-per-session rule; hand-off step 2 confirms the work is
  in its own worktree; dissolution (step 5) removes the worktree with
  the branch; changelog records the incident.

The incident, for the record: on 2026-06-10 the shared checkout
switched branches four times under the owner's explorer in one
afternoon (surface-reflector-ui → reflection-automates →
reflection-matrix → main → reflection-matrix), making freshly merged
work appear to vanish; the owner's local `main` proved 38 commits
behind because nothing had ever pulled it. Separating the viewport
(primary checkout, parked on `main`) from the workbenches (one
worktree per session) removes the collision class the
parallel-fleet discipline was managing by hand — explicit-path
commits and re-check-before-push still apply *within* a workbench.

This change was itself built under the new rule: the primary
checkout was not touched; everything here was authored, penned,
committed, and handed off from the first workbench,
`..\ontum-wt\viewport-worktree`. While it was being written, the
matrix session re-pointed the primary checkout again — live
confirmation of the disease while recording the cure.

## Id collisions, named

Done-line 0020 and report 0018 ids were minted in parallel by sibling sessions and now sit on main (this branch renumbered to 0022/0019 at rebase; see also
reflection-automates arc (its branch carries
`0020-reflection-automates.md`, `0018-the-reflection-automates.md`).
Different filenames, no git conflict — duplicate numbers across
parallel lineages, the same precedent the reports directory already
carries (0004–0012 twice). Pen-only ids beat hand-numbering around
the pen; if bdo wants unique ids across in-flight arcs, that is a pen
feature to ask for (it would need to read open branches, not just the
local directory).

## needs-you

- **Enforcement is deliberately not built.** The rule is prose today.
  The least-permissions pattern says the next wrapper comes from the
  watcher's report — a guard denying `git checkout`/`switch` in the
  primary checkout is the obvious candidate when you want the hand
  forced. Say so and it gets built as its own stamped increment.
- **The owner's return leg is still manual**: after you stamp, hit
  sync (or `git pull`) in the viewport. Automating that (a scheduled
  pull, a post-merge hook) is possible but touches your machine's
  ambient behavior — your call whether to want it.

## End-state

`report` — discipline recorded in CONTRIBUTING and branch-ritual
0.6.0, built from the first workbench; enforcement and pull
automation queued on the owner.

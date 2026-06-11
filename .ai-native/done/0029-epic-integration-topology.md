# Done-line 0029 — epic-integration: pieces flow into an epic branch, only the arc reaches main

Written before code, per §9.4. When this line is met, stop.

> **Done when:** the branch ritual carries bdo's topology — a session may
> integrate a piece-PR into a non-trunk **epic branch** through the pen
> (`pr.py integrate <n>`), and that pen **refuses a main base** (the trunk
> stays bdo's, firm); raw `gh pr merge` stays denied and routes to the pen;
> and the ritual records the narrowed rule (never merge into *main*, not never
> merge at all) with bdo's directive cited (SKILL 0.8.0). §10 proof: integrate
> refuses base `main`/`master` and allows an epic branch. Pieces land
> `piece → epic branch` (the loop integrates), only the finished arc lands
> `epic branch → main` (bdo merges).

## Why (bdo, 2026-06-10)

"I only need to merge into main when something is complete — its arc, and when
through, its epic." The git-topology complement to arc-confirmation
(done-line 0028): far fewer merges reach him because every piece no longer PRs
to main.

## Out of scope, named (later increments)

- **Spinning up the epic branch** is still manual git (`git worktree add -b
  claude/epic-<name> ..\ontum-wt\<slug> main`); a pen verb to create and track
  one is a convenience, not yet built.
- **The per-piece second set of eyes.** With pieces self-integrated into the
  epic branch, the human review is bdo's one merge at epic→main; the per-piece
  eye is the loop's gates (value-gate) once work flows as atoms. `integrate`
  checks the PR is open, non-trunk, and not conflicting — not that a gate
  judged it. Closing that is the same "work-as-atoms" move named in 0028.

# Report 0028 — epic-integration: the loop integrates pieces, bdo merges arcs

## What landed

**[done-line 0029](../done/0029-epic-integration-topology.md) — met.** The
git-topology complement to arc-confirmation (0028), from bdo's directive: *"I
only need to merge into main when something is complete — its arc, and when
through, its epic."*

- **[pr.py](../../.claude/skills/branch-ritual/pr.py)** — a new `integrate`
  verb: merges a piece-PR into its epic branch, and **refuses a main base**
  (`integrate_refusal`, a pure rule). Main stays bdo's, firm.
- **[command_guard.py](../../.claude/hooks/command_guard.py)** — raw `gh pr
  merge` stays denied, now routing to `pr.py integrate` (the trunk message
  unchanged: the stamp is bdo's).
- **[SKILL.md](../../.claude/skills/branch-ritual/SKILL.md) 0.8.0** — the firm
  rule narrows on the record: "never merge into *main*" (not "never merge"). A
  session integrates pieces into an epic branch; the finished arc PRs to main.
  The epic branch is staging, not truth (D-5).
- **[tests/test_pr_ritual.py](../../tests/test_pr_ritual.py)** — `integrate`
  refuses `main`/`master`, allows an epic branch. Suite: 251 OK.

The flow now: `piece → epic branch` (the loop integrates) → `epic branch →
main` (you merge, once, when the arc is done).

## needs-you

- **Merge this PR** (epic-integration, done-line 0029) — and it is the
  enabling change: after it, I open piece-PRs against an epic branch and
  integrate them myself, and you only see the `epic branch → main` PR when an
  arc is complete.
- **Then we run it for real:** I cut `claude/epic-experience-layer` off main,
  and wave-3 pieces flow into it — you next hear from me when that arc is
  whole, not per piece.

## End-state

`report` — the ritual now carries the piece→epic→main topology; the pen
integrates pieces below main and refuses the trunk, which stays yours alone.
With this and arc-confirmation (0028), both the atom queue and the merge queue
lift from piece scale to arc scale. Ready for your stamp — the last per-piece
one before the lift.

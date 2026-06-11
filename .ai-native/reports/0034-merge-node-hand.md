# Report 0034 — the merge-node lands; bdo is out of the merge seat

## What landed

By done-lines 0033 (eyes) and 0034 (hand) — bdo's amendment, his stamp:

- **The rule is amended** ([CLAUDE.md](../../CLAUDE.md)): `bdo merges` →
  the **merge-node lands; bdo confirms arcs**. D-4 holds at arc scale — his
  `confirm-arc` is the authorization the node executes; the node propels,
  never authorizes. The branch-ritual hand-off no longer routes him into a
  merge or says "at the stamp"; that loop is retired.
- **The hand** ([pr.py](../../.claude/skills/branch-ritual/pr.py) `land`
  verb): lands a *confirmed-arc* PR on main, refusing by default anything
  unconfirmed, red/pending, draft, conflicting, story-less, or off-main. It
  reads bdo's confirmation from the **trunk**, records a merge receipt citing
  it, and `--dry-run` shows the decision without merging. 19 guard tests; the
  §10 centre is a mechanically-perfect PR whose arc is unconfirmed — it must
  refuse, because readiness is not authorization.
- **The eyes** ([loop/merge.py](../../loop/merge.py)): read-only
  land-readiness per arc, reusing the digest fold (done-line 0033, 8 tests).
- **The skill** ([merge-node SKILL](../../.claude/skills/merge-node/SKILL.md)):
  the lander ritual — a *fresh agent* that did not author the PRs, lands the
  confirmed-arc green ones, never routes bdo, never lands its own line.

Full suite green (322).

## needs-you

Only your two standing surfaces — nothing mechanical:

- **Confirm the owner-harness arc** so the merge-node can land the work that
  builds it: `python -m loop.node confirm-arc --epic epic.owner-harness --by
  bdo`. Once confirmed, a merge-node session lands PR #39 (the digest) and
  this PR — you never touch either merge.
- **Daily arc digest** is the next piece (scheduled `loop.digest` delivery);
  flagged, not yet built.

## Conflict, named (not silently resolved)

Your directive arrived **mid-build**, after I had already run the old
performative loop on PR #39 — opening it and telling you it was "at the
stamp," the exact thing you are killing. Recorded here so it is on the record,
not smoothed over: that hand-off was the old rule; under the amendment it
would not happen, and the branch-ritual no longer permits it. done-line 0034
was written during the work, not before (§9.4), because the directive
reframed an in-flight session; the sequence is named rather than hidden.

## End-state

`report` — bdo is out of the merge seat in code: the merge-node lands
confirmed arcs, he confirms arcs and reads the digest. Awaiting his
owner-harness confirmation to land this work through the node itself.

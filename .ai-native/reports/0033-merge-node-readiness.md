# Report 0033 — the merge-node's eyes: land-readiness per arc

## What landed

By done-line 0033 (the merge-node's eyes), stacked on the digest (0032),
opened as a **rolling draft** — WIP, never offered to the stamp:

- **[loop/merge.py](../../loop/merge.py)** — a read-only land-readiness
  sensor, per arc, reusing the digest fold. It answers "is this arc safe to
  land on main?": `ready_to_land` only when bdo confirmed the arc, every
  declared piece is present and landed, and no divergence touches it;
  `refuse` when one does; `not_ready` when unconfirmed or a piece is
  unbuilt/unlanded — each with reasons. It decides; it never acts, never
  writes.
- **[tests/test_merge.py](../../tests/test_merge.py)** — 8 tests; the §10
  centre is a confirmed, fully-landed arc whose record still holds a
  refusal: it must `refuse`, never green-light over a gate's no, with a
  paired control that the same arc minus the refusal lands clean. Full
  suite green (303).
- **[loop/CLAUDE.md](../../loop/CLAUDE.md)** — merge.py recorded as the
  merge-node's eyes (command, module layering, the `-m` gotcha).

On the real log every arc reads `not_ready` — none is confirmed — which is
the honest state, not a bug.

## needs-you

This is still only the *eyes*. The merge-node's *hand* — and bdo stepping
out of the merge seat — turns on the same two stamps named last session,
his alone (D-4):

1. **Amend the `bdo merges` hard rule** (a doctrine change, surfaced not
   worked around).
2. **`admit-real` the merge-node `--by bdo`** once the hand (a hard-gated
   epic→main merge pen) and the arc-scale judging seam are built.

Nothing here merges or writes; until those, bdo still merges and these
modules only watch. This PR is a rolling draft — it is not at the stamp.

Two PRs are now in flight: #39 (the digest, at the stamp) and this draft,
stacked on it. When #39 merges, GitHub retargets this to main.

## End-state

`report` — the merge-node's read-only judgement ships green; its hand and
the doctrine amendment that activate it remain bdo's, and this PR stays a
draft until they do.

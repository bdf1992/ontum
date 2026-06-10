# Done-line 0023 — placement: cross-ref address collisions refuse to fit

Written before code, per §9.4. When this line is met, stop.

> **Done when:** a deterministic placement check folds numbered-record ids
> across *all git refs* (not just the local directory) and **refuses** when
> two records claim one id — proven §10 by catching the live colliding
> `0020` done-lines (`git-commit-pen` vs `reflection-automates`), which the
> local-fold check waves through; and the write guard uses that cross-ref
> fold, so a session writing its own record in-tree can no longer be handed
> a fleet-colliding id. `loop/` stays pure-stdlib; the git-reading judge is
> a pen under `.claude/` (the reflect split: the fold is data, the reach is
> a pen).

## Out of scope, named (later increments)

- Wiring placement as the admitted-real **L1 pipeline gate** (`placement-gate`
  de-mocked in `PIPELINE`, atoms parked for its verdict). This increment is the
  records-layer detector + prevention — the cheapest proof a judging node can
  refuse; the pipeline wiring is its own done-line.
- The **records pen** (`loop/pen.py`) keeps its pure local fold, so it still
  *proposes* a local id; the write guard is the cross-ref *enforcement*. Making
  the pen itself fleet-aware without breaking `loop/` purity is a separate seam.

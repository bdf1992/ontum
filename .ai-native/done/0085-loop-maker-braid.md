# Done-line 0085 — The loop-maker — the sound braid (MAPE-K Plan over the log)

Written before code, per §9.4. When this line is met, stop.

> **Arc:** epic.digital-experience
> **Piece:** atom.loop-maker.v0
> **Probe:** P1 (the sound braid / loop-maker)

The Plan seam of the MAPE-K loop bdo asked for (2026-06-15): a deterministic
function that reads current state (a fold over the records) and derives the
*next increment*, braided to prior iterations through the append-only log — not
session memory. It is the missing seam between `loop/temporal.py`'s pressure
read and the overnight runner's next-story; it does **not** re-build the Monitor
(`loop/reconcile.py`), the Analyze (`loop/temporal.py`, `loop/gaps.py`), or the
Execute (the records pen) — §10.

The braid is sound because the connection lives on disk: a landed increment ties
its done-line to its epic piece with a `> **Piece:** <atom-id>` line, so the next
derivation folds over `.ai-native/done/` and *cannot not-see* the prior loop's
work. The log is the MAPE-K Knowledge base.

> **Done when:** `loop/loopmaker.py` provides `next_increment(epic_id, *, root)`
that folds an epic's ordered pieces against the landed-piece set (done-lines
carrying a `> **Piece:**` tie) and returns either the first unlanded piece as an
increment (atom id, derived slug, title) or a `Stop` carrying a reason
(`converged` when every piece is tied, `stuck` when the next piece is blocked on
an unmet dependency); and `tests/test_loopmaker.py` passes under
`python -m unittest`, proving the teeth — (1) a partial fixture yields the
expected next piece, (2) a fully-tied fixture returns `Stop("converged")` rather
than fabricating a next step, and (3) the braid: adding a `> **Piece:**` tie for
the current piece advances a re-run to the following piece (the connection is via
the log, not memory).

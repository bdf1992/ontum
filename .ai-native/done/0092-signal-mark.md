# Done-line 0092 — Teeth leave a mark — the firings become a foldable signal stream

Written before code, per §9.4. When this line is met, stop.

> **Arc:** epic.digital-experience
> **Piece:** atom.signal-mark.v0
> **Probe:** P6 (teeth leave a mark — the harvest precondition)

bdo, 2026-06-16: "Teeth should leave a mark." The precondition for farming a
stopping point. Today the four teeth refuse but record nothing — loopmaker's
Stop, cited_sensor's ghost, reversibility_gate's block all return/print and
vanish (a meteor that burns up; no meteorite). "The refusal is the signal" only
holds if the signal lands. The doctrine already says it: record verdicts, don't
delete questions. So each firing lands as a foldable signal — state `seed` (raw
potential, not yet threshed to grain or banked) — reusing
`reconcile.append_line`/`short_hash` (§10, not a new mechanism), in the grain of
the watcher's `tool-use.jsonl` auxiliary stream. This is the field the harvest
(atom.harvest.v0) will farm.

> **Done when:** `loop/signals.py` provides `mark(root, kind, subject, why, *,
state="seed", extra=None)` appending one signal record to
`.ai-native/log/signals.jsonl` (content-hashed id over kind+subject+why for
idempotence, I-2) and `read(root)` folding the stream (torn-tail tolerant, an
absent stream → empty); and the three teeth leave their mark when operated —
loopmaker's `Stop`, cited_sensor's ghosts, and reversibility_gate's block each
record a signal via `mark` (the pure classify/fold functions stay pure; the mark
is added at an operation seam); and `tests/test_signals.py` passes under
`python -m unittest`, proving the teeth — (1) mark→read round-trips, (2) the same
firing recorded twice folds to ONE signal (idempotence), (3) a torn final line is
dropped and an absent stream reads empty, and (4) each of the three teeth lands a
signal of its kind when it fires (and lands nothing when it does not refuse).

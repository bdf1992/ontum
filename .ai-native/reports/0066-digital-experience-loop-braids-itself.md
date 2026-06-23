# Report 0066 — epic.digital-experience opens: the loop that braids itself

## What this run was

bdo named a horizon in the working session of 2026-06-15 — ontum as the new
digital experience, a ~20-year goal — and asked for an overnight loop to "land
this over N loops," specifically a *loop-maker* that takes the current state from
the previous loop into the next and braids each loop to the prior one "in some
sound way" to make something controllable. He said "GoPlusUltra." This is that
run, on `claude/digital-experience` (a worktree off main; the viewport was never
touched), opened as the rolling draft PR #153.

## What landed

**Loop 0 — the anchors (the vision, made durable).**
`outcomes/digital-experience.md` holds the desired-reality pole: the maximal
horizon, five evidence-cited probes (the loop-maker, the cited sensor, the
bounded-run fold, the reversibility line, adoption-by-use-trace), and three
standing edges (divergence-as-mirror, boundary-drawing, self-application).
`.ai-native/epics/epic.digital-experience.json` is the arc — a *composing* epic
that reuses the fold, the citation/ghost teeth, Causality, the inference plane,
and the anima layer rather than double-building any of them (§10).

**Loop 1 — atom.loop-maker.v0 (done-line 0085).** The Plan seam of the loop's
MAPE-K cycle (the pattern was picked through the loops skill; the K — the thing
that knots each loop to the next — is the append-only records on disk, never
session memory). `loop/loopmaker.py`'s `next_increment()` folds an epic's
ordered pieces against the landed-piece set (done-lines carrying a
`> **Piece:**` tie) and returns the next piece or a `Stop`. The §10 teeth hold
(8/8): a converged fixture makes it *refuse to fabricate* a next step; adding a
tie on disk between two calls changes the derivation (proof it folds the
records, not memory); a blocked piece returns `Stop("stuck")`.

**Loop 2 — atom.cited-sensor.v0 (done-line 0086).** The data→evidence half of
the fold: `causality/cited_sensor.py` reads a person's data surface read-only
and emits cited evidence, reusing `term_economy.resolve_evidence` for the ghost
test — a citation that points at nothing (missing path or fabricated content
anchor) is refused at the door. Teeth 7/7; dogfooded on the repo's own
`outcomes/` dir (4 cited, 0 ghosts).

The full suite is green (770 tests) at each commit. Three commits, two real
nodes, two frozen done-lines.

## The braid worked

This is the part worth seeing. Each loop derived the next from a record on disk,
not from a session remembering. Loop 1 landed and the loop-maker, run against
the real arc, read its own done-line and named Loop 2. Loop 2 landed and it
named Loop 3 — `atom.bounded-run-fold.v0`. The loop continues itself: any
session or wakeup runs `python -m loop.loopmaker epic.digital-experience` and is
handed exactly what to build next. That is the controllable closed loop bdo
asked for — setpoint (the arc's ordered pieces), error (the unlanded ones),
brake (`Stop` on converged or stuck).

## needs-you

**One gesture: confirm the arc `epic.digital-experience`.** It is a brand-new
epic, unconfirmed; until bdo confirms it, the merge-node cannot land PR #153.
This is an arc-confirm, not a pile of pieces — one stamp authorizes the whole
arc's work (`loop.node confirm-arc --epic epic.digital-experience --by bdo`, or
his usual GitHub gesture on the arc-confirm issue). Nothing else is asked of
him.

**One flag, not a chore (no action needed):** `cited_sensor.py` lives in
`causality/` because bdo framed this whole thing as "the Causality desktop app"
and the sensor reuses Causality's ghost discipline directly. If the
digital-experience product later wants its own top-level module home, that is a
composition-surface decision (a new `@`-imported citizen of the root CLAUDE.md)
and therefore bdo's to make — it is noted, not punted, and the current home is
honest in the meantime.

## End-state

`report` — epic.digital-experience opened with its outcome, its composing arc,
and two real nodes (loop-maker 0085, cited-sensor 0086) on PR #153 (rolling
draft, suite green); the loop-maker braids each loop to the next on disk and has
already named Loop 3 (bounded-run-fold); the one owner gesture is arc-confirm.

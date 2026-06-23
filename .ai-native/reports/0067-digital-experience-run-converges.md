# Report 0067 — epic.digital-experience: the overnight run converges on its buildable probes

## What this is

The closing report of bdo's GoPlusUltra overnight loop for
`epic.digital-experience` (report 0066 opened it; this one closes the run). The
loop-maker carried the whole thing: every increment after the first was derived
from the prior loop's tie on disk, never from a session remembering.

## What landed since 0066

**Loop 3 — atom.bounded-run-fold.v0 (done-line 0087).**
`causality/bounded_run_fold.py` clusters the cited sensor's evidence by locality
into **proposed** bounded-run candidates — the world as bdo's separate bounds
(games / company / orchestration), each a candidate carrying purpose / anima /
control-surface slots left **unset**: the fold proposes the bound, the person
declares its meaning (D-4). A ghost-only locality is refused. 6/6; dogfooded on
`causality/` (5 proposed bounds, 0 refused).

**Loop 4 — atom.reversibility-gate.v0 (done-line 0088).**
`causality/reversibility_gate.py` is the safety spine. It reconciles "handle it
so I don't have to worry" with the gesture-confirm doctrine by cutting on
reversibility: reversible acts (pre-stage, render, draft) run autonomously;
irreversible/outward acts (send, delete, purchase) are gated behind a gesture;
an unknown verb is treated as irreversible — the gate never guesses an act safe.
7/7. (Composes with the anima arc's Risk/blast-radius assay when that lands.)

The full suite is green at every commit.

## The run, end to end

Five increments, all on PR #153 (rolling draft):

- Loop 0 — the anchors (outcome + composing arc).
- Loop 1 — the loop-maker (0085): the sound braid, MAPE-K with the log as K.
- Loop 2 — the cited sensor (0086): data -> cited evidence, ghosts refused.
- Loop 3 — the bounded-run fold (0087): evidence -> proposed bounds.
- Loop 4 — the reversibility gate (0088): the autonomy/gesture line.

That is every **buildable** capability probe of the outcome — P1, P2, P3, P4 —
each with its §10 teeth (a refusal that bites: the loop-maker refuses to
fabricate a next step; the sensor refuses a ghost citation; the fold refuses a
ghost-only bound; the gate refuses to guess an act safe). The whole first
vertical slice of the thesis now exists: sense -> cite -> bound -> gate.

## Where it stops, and why that is correct

The loop-maker, run now, names the next increment: `atom.adoption-use-trace.v0`
(P5). P5 is an **outcome/realization** probe — it goes green only when a
pre-staged surface is actually *used in preference to the alternative*, on a real
use-trace. You cannot build your way to passing it; it is dormant by design until
the slice is adopted. So the run has reached its honest convergence: every probe
that *can* be built tonight is built, and the one that remains is waiting on use,
not on code. Stopping here is the brake working, not the work running out — and
the braid means the next session resumes by running
`python -m loop.loopmaker epic.digital-experience`.

## needs-you

**One gesture: confirm the arc `epic.digital-experience`** (its arc-confirm
issue, or `loop.node confirm-arc --epic epic.digital-experience --by bdo`). It is
unconfirmed; until you confirm it, the merge-node cannot land PR #153. One stamp
authorizes the whole arc. Nothing else is asked.

(Standing flag, no action: the four new modules live in `causality/` because you
framed this as "the Causality desktop app" and they reuse Causality's ghost
discipline. A dedicated top-level home for the digital-experience product is a
composition-surface decision, yours to make later — noted, not punted.)

## End-state

`report` — epic.digital-experience's overnight run converged: anchors + four real
nodes (loop-maker 0085, cited-sensor 0086, bounded-run-fold 0087,
reversibility-gate 0088) covering capability probes P1-P4, all on PR #153
(rolling draft, suite green); P5 (adoption) is dormant by design; the braid
self-continues; the one owner gesture is arc-confirm.

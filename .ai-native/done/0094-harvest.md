# Done-line 0094 — Harvest at a Stop — thresh grain, bank seed, never auto-plant

Written before code, per §9.4. When this line is met, stop.

> **Arc:** epic.digital-experience
> **Piece:** atom.harvest.v0
> **Probe:** P8 (the stopping point becomes a harvest)

bdo, 2026-06-16: "if a loop maker hits a stopping point they should be creative."
The piece that turns a Stop from a halt into a harvest. On a Stop it folds the
recorded teeth-signals (loop/signals.read) and sorts by generativity — recurrence
is the tell: a shape that recurs is seed (generative), a one-off is grain (a
consumable insight). Grain is the insight used now; seed is BANKED as proposed
(loop/seedbank.bank), never planted — planting stays a deliberate hand (D-4), so
harvest itself never plants. Autonomous (fenced) planting is the trusted-loop
horizon, not this. Composes the existing pieces (§10): signals (the field),
seedbank (where seed lands), loopmaker (the Stop that triggers it).

> **Done when:** `loop/harvest.py` provides `harvest(epic_id, root, *, by,
recurrence=2)` that folds the recorded signals and returns `{grain, seed,
planted}` — banking each recurring-kind shape as a PROPOSED seed and naming each
one-off as grain — and a `main(epic_id)` that runs `loopmaker.operate` and farms
only when it returns a `Stop`; and `tests/test_harvest.py` passes under
`python -m unittest`, proving the teeth — (1) a recurring-kind signal is banked
as seed and reads `proposed` afterward (a generative shape is not consumed as
mere grain — seed not eaten); (2) a one-off signal is grain, NOT banked as seed
(no noise in the seed bank); (3) harvest NEVER plants — every seed it banks is
`proposed`, `planted` stays empty (planting is a separate deliberate hand); (4)
an empty field harvests to nothing.

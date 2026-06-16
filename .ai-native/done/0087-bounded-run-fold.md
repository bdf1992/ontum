# Done-line 0087 — The bounded-run fold — the world as proposed bounds, never minted

Written before code, per §9.4. When this line is met, stop.

> **Arc:** epic.digital-experience
> **Piece:** atom.bounded-run-fold.v0
> **Probe:** P3 (bounded-run fold, proposed not minted)

Derived by the loop-maker from done-line 0086's braid. The fold that turns cited
evidence into a person's world: it clusters the sensor's cited evidence by data
locality into **proposed** bounded-run candidates — bdo's "every directory and
file inside my digital world can be AI-native," and his correction that the
40h-games-vs-company tension is not a paradox but separate bounded runs, each
with its own setpoint. Each candidate carries its slots — declared-purpose
(mission/vision/values), anima (expected rhythm), control-surface — left **empty
as declared-input**: the fold proposes the bound, the person declares its
meaning (D-4). Reality is folded; purpose is declared, never inferred. A
candidate with no resolvable backing is refused (the reused ghost discipline).

> **Done when:** `causality/bounded_run_fold.py` provides `fold(data_root)` that
clusters the cited sensor's evidence by locality into bounded-run candidates,
each `status: "proposed"` with its `purpose` / `anima` / `control_surface` slots
present but unset (declared-input, never an inferred value), and returns the
refused localities (those with no resolvable evidence) separately; and
`tests/test_bounded_run_fold.py` passes under `python -m unittest`, proving the
teeth — (1) a real multi-directory corpus yields ≥2 proposed candidates each
backed by resolvable evidence, (2) the purpose/anima/control-surface slots are
**unset** on every candidate (the fold never tells the person who they are), and
(3) a locality whose evidence are all ghosts is refused, not emitted as a
candidate.

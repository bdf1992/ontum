# Done-line 0002 — the fast ambient loop (report 0002's v-next)

Written before code, per §9.4. When this line is met, stop.

> **Done when:** at least two atoms reach their `desired_state` under a
> per-tick step budget read from an admitted `setpoint` record (I-8), with
> every actual move still `pass_once` (D-8); **and** the flood test passes:
> atoms seeded faster than a rate-limited mock human stamp can clear them,
> the loop senses the backlog and throttles its own inflow (I-7), so the
> human queue never exceeds its admitted cap at any tick while
> already-admitted atoms still progress to `done`.

Scope, per report 0002 §6: the fast loop only — no slow loop, no real
nodes, no surfacer ensemble, no control/surfacer split. Mocks stay mocks
(the owner-stamp mock is still the first to be replaced when a node goes
real). The phase-1 contract — the fold, the reconcile step, the cache rule,
idempotence by `(node, artifact_hash)`, line-atomic appends — is built
over, not into (report 0002 §4); the only `reconcile.py` changes are the
mechanical generalizations named there (`load_atoms`, per-atom `pass_once`,
multi-atom cache).

Source: doctrine §15 (ambient control, bidirectional), D-11, I-7, I-8;
report 0002 §3 (the recommended shape), §5 (the test that matters: the
cool path), §6 (the single next version). Stamp: bdo, via chat 2026-06-10
("set up a simple working loop").

Next, not now: the slow loop (re-admitting the dial from accumulated
outcomes), and making exactly one node real (L0 first) — each needs a
fresh stamp.

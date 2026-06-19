# Done-line 0091 — The slow loop's in-fence dial proposals self-admit; out-of-fence ones still escalate

Written before code, per §9.4. When this line is met, stop.

bdo answered the slow loop's one open seam (2026-06-16): of bdo-forever /
bounded-auto-admit / independent-judge, he chose **bounded auto-admit** — the
arc-confirm shape. He draws a fence once; proposals inside it self-admit, ones
that want to leave it still escalate to him. The proposer (`loop/slowloop.py`,
done-line 0074) stays read-only — this builds the **disposer** it deliberately
left to the outside, with bdo's standing fence as that outside (D-4: the loop
executes his authorization, it never authorizes itself — the merge-node /
confirm-arc pattern, done-line 0028).

> **Done when:** an admitted `auto_admit_fence` record (signed `--by`, bdo's
> one stamp) declares per-key bounds, and a pure `evaluate(fence, current,
> proposed)` decides a slow-loop proposal **admit / escalate / noop** by the
> rule bdo named — a heating key (raising load) auto-admits only up to its
> ceiling, a cooling key (shedding load) always auto-admits, a key the fence
> does not name escalates, and **one out-of-fence key escalates the whole
> proposal** (§10 teeth); a `dispose` step then either calls `admit_setpoint`
> for an in-fence proposal — attributed to the loop and **citing the fence id
> as `authorized_by`**, never signing bdo's name and never the proposer
> signing its own line — or writes nothing and leaves an out-of-fence proposal
> for bdo; the fence is read from the log at runtime (never a code constant),
> a run with no admitted fence disposes nothing (inert until stamped), and
> `tests/test_fence.py` pins the teeth: the one-breached-key escalation, the
> unnamed-key escalation, cooling-always-admits, heating-capped-at-ceiling,
> and that a disposed setpoint carries `authorized_by` the fence.

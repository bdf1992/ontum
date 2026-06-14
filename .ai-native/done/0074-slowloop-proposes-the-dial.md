# Done-line 0074 — The slow loop proposes the dial — outcomes reach the setpoint, without signing their own line

Written before code, per §9.4. This is the increment that lets the causal loop
*reach the dial* — the doctrine's slow loop (§14: the fast loop holds the
setpoint, the slow loop moves it from accumulated outcomes). The sensing half is
built and landed (done-lines 0069 outcome-pressure, 0072 temporal, 0073 summon
delivers it). This builds the **proposer**, and only the proposer.

The question this answers (and the one it deliberately leaves open). A closed
loop has no outside; the substrate's physics is "no node signs its own line, the
owner is the last stop" (D-4). The contradiction dissolves into **propose vs
dispose**: the slow loop may *propose* a setpoint change caused by outcomes, but
the **disposition** — the actual `admit_setpoint`, the act that changes what the
system aims at — stays an act of the outside. The proposer is answer-agnostic;
*who* disposes (bdo forever, a standing bounded auto-admit, an independent judge)
is bdo's to decide and is NOT decided here. So this increment builds the half
that is the same whatever he answers, and leaves the disposition seam open.

> **Done when:** `loop/slowloop.py` folds the **tick history** (the field's
> outcomes — `type==tick` admissions: mode, pressure, deferred), the current
> admitted setpoint, the outcome-pressure phase (`loop.pressure`) and the hour's
> temporal lean (`loop.temporal`) into a **proposed** setpoint adjustment that
> carries an **attribution** — the `because`, the specific outcome signals that
> caused each change — and it **writes nothing**, never calls `admit_setpoint`,
> and names the disposition as the outside's act (`admit_setpoint --by <whoever>`);
> with tests proving the proposer never mutates the log or the live setpoint
> (propose ≠ dispose), every proposed change carries evidence-bearing attribution
> or is refused, a heat-leaning tick history proposes heat and a cool-leaning one
> proposes cool (the proposal is *caused by* outcomes, not a constant), and the
> result is deterministic given fixed inputs.

> **Non-example:** a proposer that calls `admit_setpoint` (it disposed — the loop
> signed its own line); a proposed delta with no `because`, or a `because` that is
> prose rather than the cited tick/pressure/temporal evidence (the change is not
> causal, just asserted); a constant proposal independent of the tick history
> (a cycle, not a causal loop); or the proposer mutating the live dial as a side
> effect of reading.

> **Pressure reduced:** the causal loop reaches the dial for the first time —
> outcomes now produce an attributed setpoint proposal — while the no-self-sign
> invariant holds intact, because the proposer only proposes. The loop is closed
> enough to be *causal* (the proposal is attributable to outcomes) and open
> exactly where the substrate requires an outside.

> **Does not complete** (continuing pressure — and one genuine owner gesture):
> the **disposition seam** — who or what admits a proposal (bdo forever / a
> standing bounded auto-admit within named limits / an independent judge node) —
> is D-4 and is **bdo's to answer**, not this increment's; surfacing the proposal
> through summon/digest as that gesture; and persisting a proposal as a
> proposed-tier record consumed by an admit. This builds the proposer; the
> disposer stays open by design.

> **Evidence expected:** `loop/slowloop.py` + `tests/test_slowloop.py` green
> (no-mutation / propose≠dispose; attribution-or-refused; heat-history→heat and
> cool-history→cool; determinism), running it in the repo shows the current
> setpoint, the folded outcome signals, and a proposed setpoint with its
> `because` and the disposition note, and a merge receipt.

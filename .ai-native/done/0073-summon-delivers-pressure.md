# Done-line 0073 — OP2 — summon delivers outcome-pressure at wake

Written before code, per §9.4. **This is one increment toward the maximal
outcome** in `outcomes/causality-outcome-pressure.md` (probe OP2), and the
inhabitation payoff of the slow-loop sensing built in done-lines 0069 and 0072:
a waking session should inherit the *outcome's gap*, not only the janitorial
backlog. When this line is met, stop *this increment*; OP3 (full composition)
and the surface probes remain live pressure.

bdo's framing (the proposal, PR #122): today summon hands a waking session a
work-order — "the next gap is X". Under the outcome-pressure idea it should
hand a *situation* — "the outcome is Y, current reality is N of M probes, the
top leverage is Z, and at this hour the move is W". The channel already exists
(`loop.summon --hook` fires at SessionStart and UserPromptSubmit); this wires
the outcome-pressure read into it.

> **Done when:** `loop.summon --hook` delivers, in addition to the existing
> work-pressure (`loop.gaps`), the **outcome-pressure** read from
> `loop/pressure.py` modulated by the hour through `loop/temporal.py` — the
> outcome, its phase, the top-leverage probe, and the hour's temporal focus and
> lean — as one concise situational briefing line; the hook stays **fail-open
> and exits 0 always** (a broken pressure read never blocks the owner's prompt);
> and a test drives the hook and asserts the outcome-pressure line is present,
> naming the phase and the focus.

> **Non-example:** a hook that crashes or blocks when the probe-set is missing
> or the fold raises (the contract is exit-0-always); a line that prints raw
> probe ids with no phase, leverage, or temporal lean (a work-order again, not a
> situation); duplicating `loop/pressure.py`'s logic inside `summon.py` instead
> of importing the fold (one fold, one truth); or the outcome line *replacing*
> the gap line rather than composing beside it (work-pressure still matters —
> full composition into one ranked field is OP3, not this).

> **Pressure reduced:** for the first time a session that blinks in inherits the
> outcome's tension at wake — it stands inside "what is preventing the outcome
> from existing", ranked for the hour, instead of only "what is the next chore".
> The continuity stops living in bdo's head and starts riding the summon channel.

> **Does not complete** (continuing pressure): OP3 — composing owner-pressure +
> work-pressure (gaps) + outcome-pressure into **one ranked field** rather than
> stacked lines; the orchestrator consuming the temporal lean as a real
> heat/cool budget; and the Causality surface probes (CZ1–CZ4). These stay
> unresolved probes the fold now surfaces at every wake.

> **Evidence expected:** `loop/summon.py` imports and calls `loop.pressure`
> (via `loop.temporal`), the hook prints the outcome-pressure situational line,
> `tests/test_summon*` drives the hook and asserts the line names the phase and
> focus, the full suite is green, and a merge receipt. Running `loop.summon
> --hook` in this repo shows the Causality outcome's phase, top leverage, and
> the current hour's temporal focus.

# Done-line 0075 — Summon shows the slow loop's dial proposal — read-only, never disposed

Written before code, per §9.4. This completes the slow loop's *visibility* without
touching its *disposition*. The proposer is built and landed (done-line 0074):
the field's outcomes propose a setpoint change, attributed, writing nothing. A
proposal nobody sees is inert — so a waking session should see it. But *showing*
must not become *routing*: surfacing the proposal where the disposer looks would
quietly presuppose who the disposer is, and that is bdo's open question (D-4).

So this surfaces the proposal in `loop.summon --hook` only — to a **session**,
which cannot dispose it — as a read-only informational line, exactly as OP2
surfaces outcome-pressure. It is deliberately **not** wired into the digest or
any owner-facing disposer surface; that waits on bdo's answer to who disposes.

> **Done when:** `loop.summon --hook` shows the slow loop's current dial
> proposal (from `loop.slowloop`) as a read-only informational line — the
> proposed change and its `because` — clearly marked as a proposal the dial does
> not follow until the outside admits it; the hook stays **fail-open and exits 0
> always**; the line is **not** routed to the digest or any disposer surface;
> and a test drives the hook and asserts the proposal line is present and names
> the proposed dial change.

> **Non-example:** wiring the proposal into the digest or inbox (that presupposes
> bdo disposes — his open answer); a line that reads as an instruction to admit
> ("run this to apply") rather than a shown proposal; reimplementing the
> proposal logic in `summon.py` instead of importing `loop.slowloop` (one fold,
> one truth); or the surfacing crashing/blocking when there is no setpoint or no
> tick history (it must fall silent, exit 0).

> **Pressure reduced:** the proposer stops being inert — a session blinking in
> now *sees* the field proposing its own temperature, and sees plainly that the
> change is not taken until an outside admits it. The propose-vs-dispose seam is
> honoured at the surface, not just in the fold.

> **Does not complete** (the one genuine owner gesture): the **disposition** —
> who or what admits a proposal (bdo forever / a bounded standing auto-admit /
> an independent judge) — is bdo's to answer; only after he does does a
> disposer-facing surface (digest) and an admit path get built.

> **Evidence expected:** `loop/summon.py` gains a `slowloop_lines` helper that
> imports `loop.slowloop`, the hook prints the proposal line, `tests/test_summon*`
> drives the hook and asserts it, the full suite is green, and a merge receipt.

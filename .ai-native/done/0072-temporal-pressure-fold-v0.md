# Done-line 0072 — Temporal pressure v0 — ambient time modulates pressure quality/type

Written before code, per §9.4. **This is one increment toward the slow loop's
heat/cool** (doctrine §14: run hot to explore, cool to consolidate) — the
ambient-time *read*, not the write-back into the dial. When this line is met,
stop *this increment*; the unwired parts remain live pressure.

bdo's direction (2026-06-14): *the pressure at 8AM is not 8PM* — ambient time
impacts pressure quality and type. The same gap should not read the same at
dawn and at dusk; the hour is itself a pressure signal.

> **Done when:** `loop/temporal.py` classifies an explicitly-supplied moment
> (the wall clock is read only at the CLI edge, never inside the fold) into a
> temporal **register** over a **band schedule** — a default in code,
> overridable by an admitted `temporal_schedule` record (the governance grain:
> setpoints are admitted, never baked) — and **modulates** the outcome-pressure
> fold's presentation so the same unmet probe-set yields a different **lean**
> (heat/explore vs cool/consolidate) and a different next-move emphasis by time
> of day, while **never** changing whether any probe is met; with tests proving
> a malformed schedule (a gap or overlap across the 24h) is refused, different
> moments yield different registers (no constant classifier), the modulation is
> deterministic given a fixed moment, and a probe's met/partial/unmet truth is
> identical across every band.

> **Non-example:** a fold that reads the wall clock *inside* itself
> (non-reproducible, untestable — the harness's own Date.now() ban); a band
> schedule baked as a code constant with no admitted override path; a
> "temporal" label that *decorates* the output without changing the ranking,
> lean, or next move; or time-of-day flipping a probe's met/unmet (truth must
> not depend on the clock — temporal changes emphasis, never reality).

> **Pressure reduced:** the slow loop's heat/cool gains its ambient-time input.
> A waking session is met by a field whose emphasis already fits the hour —
> exploratory and large-leverage in the morning, consolidating and closeable in
> the evening — instead of a flat ranking that reads identically at 8am and 8pm.

> **Does not complete** (continuing pressure — NOT out of scope for the slow
> loop): wiring the temporal lean into `orchestrate`'s setpoint dial (the actual
> heat/cool *budget*); `summon` delivering the temporal register at wake;
> composing temporal with owner/work/outcome pressure into one ranked field (OP3
> territory); and learning the band schedule from outcomes (the slow loop
> closing on itself). This increment builds the *read*, not the write-back.

> **Evidence expected:** `loop/temporal.py` + `tests/test_temporal.py` green
> (malformed-schedule refusal; distinct registers per moment; deterministic
> modulation; the probe-truth invariant across bands), the default schedule
> classifies a morning and an evening moment to different registers/leans, the
> modulation re-emphasises the same committed Causality probe-set differently
> for the two moments, and a merge receipt.

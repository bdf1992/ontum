# Done-line 0171 — Continue-probe fire-rate easing setpoint

Written before code, per §9.4. When this line is met, stop.

> **Done when:** the continue-probe pen (`probe.py`) fires at most what an *admitted, default-safe easing setpoint* allows per tick — a budget that flows freely below a pool-depth threshold and, above it, eases between a floor and a ceiling against recent egress (fires still draining) — so a deep idle backlog drains in eased waves, never a burst; the open-window staleness ceiling is read from that same setpoint, not a code constant; and a §10 test proves the budget caps a synthetic 21-deep backlog AND fails on the current unbounded code.

## Why

Opening the continue-probe gateway (`adm.980b2a34983d`, full scope, by bdo, 2026-06-21) made a backlog of idle sessions eligible at once — 21 due on the first read. `probe.py`'s `run()` fires every due session with no fleet-wide bound, so the standing tick would resume 21 `claude --resume` sessions simultaneously: the burst shape of the llama-server kill, but as spawned CLI sessions the inference-queue semaphore does not govern. The fix is the `orchestrate` heat/cool law applied to the probe-fire plane — backpressure that eases, not a cliff.

## Shape

- The dial is an admitted setpoint (`continue-probe.easing`), latest-wins fold, `--by bdo` — never a code constant (the setpoints law); default-safe when unset (a conservative fallback, not a tuning knob).
- ingress = pool depth (due-and-eligible sessions); egress = fires in a recent window (the `continue-probe-fires.jsonl` trace). The threshold gates on ingress; egress shapes the ease slope; the budget is bounded `[min, max]`.
- Selection (cooldown/streak) is separated from ledger accounting: the ledger advances only for sessions actually fired, so a deferred session never starves (the slice-after-advance bug).

## Not in scope

- Standing up the schtasks tick (bdo's per-machine gesture; this only makes it safe to).
- Multi-repo per-cwd setpoints (today every due session is in one repo).

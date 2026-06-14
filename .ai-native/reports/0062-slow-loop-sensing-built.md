# Report 0062 — The slow loop's sensing half — outcome-pressure, temporal pressure, and inheritance at wake

A self-paced loop (bdo's gesture, 2026-06-14) built the sensing half of the
doctrine's slow loop (§14). bdo asked what priority-one was to "create a causal
loop": the slow loop — the fast loop holds the setpoint, the slow loop *moves*
it from accumulated outcomes. Only the fast loop existed; the dial had only ever
been admitted by hand. This session built the **read** (measure the outcome's
gap); the **write-back** (outcomes re-admit the dial) remains.

## What landed

Three increments, all on main under confirmed `epic.substrate`, each landed by
an independent merge-node (this session authored; it never signed its own line):

- **done-line 0069 — outcome-pressure fold** (`loop/pressure.py`, rcp.merge.132).
  Outcome Pressure = Fold(Current Reality, Desired Reality). Desired reality is a
  checkable **probe-set** (`outcomes/causality-outcome-pressure.probes.json`, the
  machine-readable projection of bdo's outcome doc); each probe resolves
  met/partial/unmet against committed bytes or log records, an uncheckable probe
  is refused at load. Reports phase (discover/build/realize/met), top leverage,
  next safe move; outcome probes stay dormant until their capability
  preconditions are met; every unresolved probe stays visible as continuing
  pressure. 672 tests green at land.

- **done-line 0072 — temporal pressure** (`loop/temporal.py`, rcp.merge.134).
  The pressure at 8am is not 8pm. Classifies an explicitly-given moment (wall
  clock read only at the CLI edge, never in a fold) into a register over a band
  schedule (code default + admitted `temporal_schedule` override; a schedule that
  does not tile the 24h is refused), and modulates the pressure emphasis by the
  hour's lean — heat favours the big unblocker, cool the nearest-closeable leaf —
  while never touching probe truth. The ambient-time input for §14's run-hot /
  cool-consolidate. 690 tests green.

- **done-line 0073 — summon delivers pressure (OP2)** (`loop/summon.py`,
  rcp.merge.135). The wake hook now hands a session the outcome situation (phase,
  leverage-top, the hour's focus and lean) beside the gap line — composing, not
  replacing (the single ranked field is OP3). Fail-open, exit-0 preserved. A real
  §10 moment: building OP2 makes `summon.py` reference the pressure fold, which is
  OP2's own probe — so OP2 resolves and OUT1 (depends OP2) flips dormant→active;
  the 0069 snapshot test correctly failed and was updated to assert the durable
  invariant (OUT1 is *carried*), the dormancy mechanism staying proven by
  synthetic fixtures. 693 tests green.

## needs-you

Nothing. epic.substrate was already confirmed (adm.476af874f9e4), so the pieces
carried on that stamp and the merge-node landed them; bdo was not routed into
anything. The continuing pressure below is now surfaced automatically at every
wake by the very hook this session built — it does not need to be handed up.

## End-state

`report` — the slow loop can now *sense* the gap to a desired reality, modulated
by the hour, delivered at wake. What remains is the **write-back that closes the
causal loop**, now auto-surfaced as continuing pressure: **OP3** (compose
owner + work + outcome pressure into one ranked field), the **orchestrator
consuming the temporal lean as a real heat/cool budget** (outcomes re-admitting
the setpoint dial — the loop closing on itself), and the Causality surface probes
CZ1–CZ4. This session built the read; the next builds the write-back.

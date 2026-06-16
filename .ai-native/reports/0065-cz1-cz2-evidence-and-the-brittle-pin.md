# Report 0065 — CZ1+CZ2 closed with teeth; the tests that pinned progress, refactored

## What landed

The endless goal this session served is the one the loop already supplies: the
outcome-pressure fold for *Causality as the operational knowledge surface*. It
is not useless precisely because every probe is evidence-bearing — a probe goes
`met` only against committed, re-runnable evidence, never against prose. The
night-hour leaned cool (night-defer: close what is near done, do not open the
big front), so the move was to close the two nearest leaves.

- **CZ2 (per-node / per-edge configuration).** The inspector's own DOM path had
  no automated drive — `canvas.persist.test.js` covered the serialization core,
  but nothing exercised *click node -> typed panel*, *click edge -> route config*,
  *edit -> persists*. Built `causality/inspector.test.js` (no deps, in the
  established headless-node grain): it mounts the real inspector, fires real
  input events, and proves the panel is config **for its type** (an inference
  node shows `prompt` and not `gate.mode`; a gate node the reverse), that an
  edge renders its route fields, and that a node edit (`prompt`) and an edge edit
  (`gain`) each survive a save->reload. Teeth: a value typed but whose commit
  event never fires does **not** persist — the persistence is caused by the
  input->commit wiring, not a side effect.
- **CZ1 (Causality persists authored graphs).** Already backed by the passing
  `canvas.persist.test.js`; what was missing was the attestation. Wrote it.
- Both attested under `outcomes/evidence/` (`cz1-persistence.md`,
  `cz2-config.md`) — each citing the committed test as the drive the fold can
  re-run (stronger than a manual click it cannot). The pressure fold moved
  **capability 2/7 -> 4/7**; top leverage advanced to **CZ3**.
- **The §10 moment.** Resolving CZ1+CZ2 broke four tests
  (`test_pressure`, `test_temporal`, two in `test_summon`) that had hardcoded
  CZ1 as the leverage / CZ2 as the cool leaf / the unmet count over the **live**
  committed set. A test that breaks on legitimate progress is a tripwire, not
  teeth. Refactored all four to assert the fold's *structure* — build-phase
  holds while a cap is unmet, top leverage is a real unmet cap, outcome probes
  are carried, heat names the leverage while cool names something else, the
  surface speaks whatever `loop.temporal` computes — so they track progress
  instead of fighting it. The fold's ranking stays covered with teeth by the
  synthetic Leverage/Dormancy fixtures, which do not move. Full suite 762 green.
- **Setup / housekeeping.** Preserved the stranded viewport work the sync hook
  flagged (reflect-auto log appends + the `ontum-models-its-own-nodes` outcome
  draft) in its own commit so a viewport restore could not lose it.

All landed on `claude/causality-canvas` (PR #151), through the git and PR pens.

## needs-you

Nothing new. PR #151 carries this increment under the causality-canvas arc; it
lands when that arc is confirmed (the merge-node's job, not bdo's hands). No
realness stamp, no new owner-ask was raised this session.

## End-state

`report` — CZ1+CZ2 closed with re-runnable evidence (capability 4/7); four
progress-pinning tests made structural; suite 762 green; CZ3 (ingest real Ontum
evidence) left as the visible continuing pressure for the next wake.

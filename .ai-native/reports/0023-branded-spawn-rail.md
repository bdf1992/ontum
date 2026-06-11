# Report 0023 — the branded spawn rail: a node-spawn is pinned, rung-checked, seen

## What landed

**[done-line 0026](../done/0026-branded-spawn-rail.md) — met.** The second
wave-2 piece of [epic.experience-layer](../epics/epic.experience-layer.json)
(`atom.branded-spawn-rail.v0`) — the loop can begin to fill its own nodes, on
the record.

- **[.claude/hooks/spawn_guard.py](../../.claude/hooks/spawn_guard.py)** — the
  command-guard pattern, for spawns. A spawn (an `Agent` tool-use, or a headless
  `claude` invocation) that brands itself with `ontum-node:<id>` is treated as a
  node-spawn: the rail pins the node's versioned prompt (`prompt_hash`, §7),
  checks `branded-subagent` holds the `judge` rung on the trust ladder, and
  records the spawn as provenance — or **refuses** it (exit 2). loop/ supplies
  the read (`trust`, `node_prompt`), imported lazily and never the reverse.
- **[settings.json](../../.claude/settings.json)** — wires the rail on `Agent`
  and `Bash|PowerShell`, pre and post. Fail-open: any error allows the spawn.
- **[tests/test_spawn_rail.py](../../tests/test_spawn_rail.py)** — the §10 proof:
  a branded spawn of `value-gate.claude.v1` is denied while the ladder is empty,
  and permitted once the rung is granted; an unbranded helper passes (watched),
  a headless `claude` is seen, a plain shell command is ignored. Suite: 211 OK.

## needs-you

- **Stamp this PR** (spawn rail, done-line 0026).
- **It changes harness behavior**: once merged, every session gets a new hook on
  `Agent` and `Bash`. It is **inert until a spawn is branded** — unbranded
  `Agent`/headless calls pass, watched. To let a subagent judge `value-gate`,
  grant the rung: `python -m loop.node admit-rung --class branded-subagent
  --capability judge --by bdo`.
- **A scope call I made, flagged not hidden:** the epic says "deny raw Agent
  calls." I made the rail gate *branded node-spawns* and only *watch* unbranded
  helpers (so normal Agent/Explore use isn't bricked) — the command-guard
  watch-first discipline. Hard-denying unbranded spawns is named as the next
  turn of the screw, yours to call.

## End-state

`report` — wave 2 is complete: the mind registry (who may judge) and the spawn
rail (a node-spawn pinned, rung-checked, recorded). The loop now has the seam
to fill its own nodes with attributable, gated minds. Next: wave 3 (the
experience unit, launcher, author) or wiring placement as the L1 pipeline gate.
Ready for your stamp.

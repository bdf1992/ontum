# Done-line 0026 — the branded spawn rail: a node-spawn is pinned, rung-checked, seen

Written before code, per §9.4. When this line is met, stop.

> **Done when:** a session that spawns a loop node — through the `Agent` tool or
> a headless `claude` invocation — must brand it (`ontum-node:<id>`), and the
> rail (`.claude/hooks/spawn_guard.py`, the command-guard pattern) then pins the
> node's prompt (`prompt_hash`), checks the spawning class holds the rung the
> act needs on the trust ladder, and records the spawn as provenance — or
> **refuses** it. §10 proof: a branded node-spawn of `value-gate.claude.v1` is
> *denied* while `branded-subagent` holds no `judge` rung, and *permitted and
> recorded* once bdo grants it; an unbranded helper Agent passes, watched and
> shamed once. `loop/` stays pure (the rail reads `trust`/`node_prompt`, never
> the reverse); the rail fails open and never blocks an unbranded call.

## Out of scope, named (later increments)

- **The hard deny of all raw `Agent`** — today only *branded node-spawns* are
  rung-gated and unbranded helpers pass (watched). Tightening the watcher into
  a deny of unbranded spawns is the next turn of the same screw, when the
  watcher's report says so (the command-guard discipline).
- **Receipt on the real log** — the spawn's verdict still lands through
  `loop.node judge` (already prompt-pinned); the rail records spawn *provenance*
  to the watch trace, it does not write the verdict receipt.
- **Auto-filling nodes** — the loop deciding to spawn its own nodes is the
  experience-launcher (wave 3); this rail is the seam it will spawn through.

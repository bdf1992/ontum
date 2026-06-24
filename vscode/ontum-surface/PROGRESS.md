# Overnight progress — the state each mortal tick re-derives from

Sessions are mortal; the files stay. Each overnight tick is a FRESH session that
reads this file (and the committed tree) to know where the build is, does one
bounded increment, updates this file, and commits. No tick relies on the memory
of the one before it — only on what is committed here.

## Marker status

- **MARKER:** parity checklist (`PARITY-CHECKLIST.md`) 18/18 `green`.
- **STATE:** `not-started`  ← one of: not-started · spiking · building · marker-met · STOPPED-infeasible
- **Green rows:** 0 / 18
- **Honest-stop tripped?** no  ← set to `yes` + reason if the bridge proves infeasible (SDK and CLI both)

## Current increment

1. **atom.branded-surface-bridge-spike.v0** — prove the engine bridge (SDK vs CLI), fill each checklist row's `source`. ← START HERE
2. atom.branded-surface-viewer.v0 — read + live-tail branded viewer (after spike).
3. atom.branded-surface-parity.v0 — drive a turn, build every row to green.

## Tick log (append one line per tick, newest last)

- (no ticks yet — the bootstrap tick is the first)

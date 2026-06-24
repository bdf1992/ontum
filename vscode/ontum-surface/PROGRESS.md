# Overnight progress — the state each mortal tick re-derives from

Sessions are mortal; the files stay. Each overnight tick is a FRESH session that
reads this file (and the committed tree) to know where the build is, does one
bounded increment, updates this file, and commits. No tick relies on the memory
of the one before it — only on what is committed here.

## Marker status

- **MARKER:** parity checklist (`PARITY-CHECKLIST.md`) 18/18 `green`.
- **STATE:** `building`  ← one of: not-started · spiking · building · marker-met · STOPPED-infeasible
- **Green rows:** 2 / 18
- **Honest-stop tripped?** no  ← set to `yes` + reason if the bridge proves infeasible (SDK and CLI both)
- **Bridge spike:** GO (see `SPIKE-FINDINGS.md`) — feasible via the CLI/SDK stream-json channel; all `spike` rows resolve to `inherit`.

## Current increment

1. ~~atom.branded-surface-bridge-spike.v0~~ — done (spike GO).
2. atom.branded-surface-viewer.v0 — read + live-tail branded viewer. ← IN PROGRESS (rows 1–2 green: the branded standalone window + the session list/select; rows 3–4 next: transcript render, live-tail).
3. atom.branded-surface-parity.v0 — drive a turn, build every row to green.

## Tick log (append one line per tick, newest last)

- 2026-06-24 setup (supervised): scaffold authored; **bridge spike = GO** (CLI/SDK stream-json proven, env inherited); STATE→building. Next: increment 1 = the read+live-tail branded viewer (checklist rows 1–4).
- 2026-06-24 ~03:20 tick: **row 1 → green** — built the branded standalone webview (`vscode/ontum-surface/{package.json,extension.js,shell.js,media/ontum.svg}`); verified `node …/test/open-window.test.js` (7 checks, exit 0). Green 0→1/18. Next: row 2 (session list from the transcript store).
- 2026-06-24 ~03:50 tick: **row 2 → green** — added `sessions.js` (reads `~/.claude/projects/<encoded-cwd>/*.jsonl`, summarizes id/title/messageCount/branch, newest-first, torn-tail tolerant), `shell.renderSessionList` (selectable `data-session-id` buttons), and wired `extension.js` to read the store on open + record the `ontum:select-session` round-trip. Verified `node …/test/sessions.test.js` (8 checks, exit 0, fake store incl. torn line) + read-only smoke on the live store (3 real sessions). Row 1 test still 7/exit 0 (no regression). Green 1→2/18. Next: row 3 (read + render a transcript).

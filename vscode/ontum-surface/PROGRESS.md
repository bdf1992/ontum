# Overnight progress — the state each mortal tick re-derives from

Sessions are mortal; the files stay. Each overnight tick is a FRESH session that
reads this file (and the committed tree) to know where the build is, does one
bounded increment, updates this file, and commits. No tick relies on the memory
of the one before it — only on what is committed here.

## Marker status

- **MARKER:** parity checklist (`PARITY-CHECKLIST.md`) 18/18 `green`.
- **STATE:** `building`  ← one of: not-started · spiking · building · marker-met · STOPPED-infeasible
- **Green rows:** 4 / 18
- **Honest-stop tripped?** no  ← set to `yes` + reason if the bridge proves infeasible (SDK and CLI both)
- **Bridge spike:** GO (see `SPIKE-FINDINGS.md`) — feasible via the CLI/SDK stream-json channel; all `spike` rows resolve to `inherit`.

## Current increment

1. ~~atom.branded-surface-bridge-spike.v0~~ — done (spike GO).
2. ~~atom.branded-surface-viewer.v0~~ — read + live-tail branded viewer **done** (rows 1–4 green: the branded standalone window + the session list/select + transcript read & render + live-tail the active session as it appends).
3. atom.branded-surface-parity.v0 — drive a turn, build every row to green. ← NEXT (row 5: drive a new turn through the engine — a `spike`-source row; the bridge is the inherited CLI/SDK stream-json channel proven in SPIKE-FINDINGS.md).

## Tick log (append one line per tick, newest last)

- 2026-06-24 setup (supervised): scaffold authored; **bridge spike = GO** (CLI/SDK stream-json proven, env inherited); STATE→building. Next: increment 1 = the read+live-tail branded viewer (checklist rows 1–4).
- 2026-06-24 ~03:20 tick: **row 1 → green** — built the branded standalone webview (`vscode/ontum-surface/{package.json,extension.js,shell.js,media/ontum.svg}`); verified `node …/test/open-window.test.js` (7 checks, exit 0). Green 0→1/18. Next: row 2 (session list from the transcript store).
- 2026-06-24 ~03:50 tick: **row 2 → green** — added `sessions.js` (reads `~/.claude/projects/<encoded-cwd>/*.jsonl`, summarizes id/title/messageCount/branch, newest-first, torn-tail tolerant), `shell.renderSessionList` (selectable `data-session-id` buttons), and wired `extension.js` to read the store on open + record the `ontum:select-session` round-trip. Verified `node …/test/sessions.test.js` (8 checks, exit 0, fake store incl. torn line) + read-only smoke on the live store (3 real sessions). Row 1 test still 7/exit 0 (no regression). Green 1→2/18. Next: row 3 (read + render a transcript).
- 2026-06-24 ~04:20 tick: **row 3 → green** — added `transcript.js` (`readTranscript`/`foldTranscript` fold a session's `.jsonl` into ordered entries: user/assistant text, assistant thinking via the `thinking` field, `tool_use`, and `tool_result` riding a user turn; non-turn/empty blocks dropped; torn-tail tolerant), `shell.renderTranscript` (escaped, `data-kind`-tagged, error-flagged blocks + an honest empty-state note), and wired `extension.js` (`renderPanel`/`readSelectedTranscript`) to re-render the panel with the selected session's transcript. Verified `node …/test/transcript.test.js` (9 checks, exit 0; fake store with all four kinds + empty block + torn line; fold order, payloads, escaping, empty note, select→re-render round-trip) + read-only smoke on the live store (folded a real session to 3 entries: user-text, assistant-thinking, assistant-text). Rows 1–2 tests still 7+8/exit 0 (no regression). Green 2→3/18. Next: row 4 (live-tail the active session as it appends).
- 2026-06-24 ~04:48 tick: **row 4 → green** — added `livetail.js` (`tailTranscript` tails ONE session by byte offset, folding only lines completed since the held offset and advancing past complete lines only — a torn/partial final line is held + re-read, never skipped; offset-past-EOF flags `reset`; `activeSession` picks the newest file by mtime), factored `shell.renderTranscriptRow`/`renderTranscriptRows` (bare blocks) + an `ontum:append-entries` webview handler (`insertAdjacentHTML` onto the live list, `data-count`/`data-live`, autoscroll), and wired `extension.js` (`pumpTail`/`startTail`/`stopTail`: anchor tail at end on select → no history replay, `fs.watchFile`, post only-new entries). Verified `node …/test/livetail.test.js` (12 checks, exit 0: seed fold→EOF; idempotent re-read; append tails only the new entry; torn partial yields nothing + holds offset, then folds in once completed; offset-past-EOF resets; activeSession newest; bare-row render + escaping; append-handler present; open→select→append posts ONLY the new block) + read-only smoke on the live store (tailed a real "Warmup" session: from 0→3 entries to offset 5765, from mid→tail half only, from EOF→0). Rows 1–3 tests still 7+8+9/exit 0 (no regression). Green 3→4/18. Increment 2 (viewer rows 1–4) complete. Next: row 5 (drive a new turn — the first `spike`-source row, via the inherited CLI/SDK bridge).

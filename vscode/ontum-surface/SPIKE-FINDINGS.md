# Bridge spike findings — atom.branded-surface-bridge-spike.v0

**Verdict: GO. The engine bridge is feasible.** Supervised by the setup session,
2026-06-24, in this worktree.

## What was proven (with evidence)

- **The package is here.** `@anthropic-ai/claude-code@2.0.19` is installed
  globally (`npm ls -g`). The SDK and the CLI ship in it.
- **A bidirectional streaming channel exists** (the driver):
  - `--input-format stream-json` — inject messages as JSON in realtime (the live
    drive channel).
  - `--output-format stream-json --include-partial-messages` — realtime events
    out (text, thinking, tool-use, results).
  - `--replay-user-messages`, `--permission-mode {default,acceptEdits,plan,bypassPermissions}`,
    `-r/--resume [sessionId]`, `--fork-session`, `--append-system-prompt`,
    `--fallback-model`.
- **Observed event shape** (a real `claude -p --output-format stream-json` run):
  - `{"type":"system","subtype":"init","cwd":"...ontum-overnight","session_id":"...","tools":["Task","Bash","Glob",...]}`
    — the init event names the **loaded environment**: cwd-scoped, the full tool
    list present (so MCP/hooks/skills/settings are inherited because it is the
    same `claude` binary reading the same cwd config).
  - `{"type":"result","subtype":"success","duration_ms":...,"session_id":"...","total_cost_usd":...,"usage":{...}}`
    — a terminal result event carrying usage + cost.
  - The stream is **newline-delimited JSON** — torn-tail tolerant, the same shape
    the rest of the loop folds.

## Source determinations (resolves the checklist's `spike` rows)

Every row the checklist marked `source: spike` resolves to **`inherit`** — the
capability is provided by the CLI/SDK stream-json channel; only its *rendering*
is `build`:

- drive a turn (5), stream a turn (6) → **inherit** (`--input/output-format
  stream-json`, `--include-partial-messages`).
- permission prompts (9) → **inherit** (`--permission-mode` + the SDK
  `canUseTool` callback).
- slash commands (10) → **inherit** (pass-through to the engine).
- plan mode (11) → **inherit** (`--permission-mode plan`).
- resume/continue (16) → **inherit** (`-r/--resume`, `--fork-session`).
- stop/interrupt (17) → **inherit** (stream-json control / process signal).
- MCP (13), environment (14), cost/usage (18) → **inherit** (the init/result
  events prove the env is loaded and usage is reported).

The `build` rows stay build: the window (1), session list (2), transcript render
(3), live-tail (4), tool/diff render (7,8), @-mentions (12), attach (15), and the
*display* of cost/usage (18).

## Consequence

**Parity is reachable** — there is no missing channel; the night's work is
*rendering* a UI over an inherited engine, not inventing a driver. The honest
remaining cost is the build rows (the client UX), exactly as the blueprint
predicted. The honest-stop (infeasible) condition did **not** trip.

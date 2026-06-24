# Parity checklist — the gradeable bar (Phase 1)

**The marker.** Phase 1 is *parity-green* when every row below is `green`. This
file is the bar the overnight loop builds toward and the bar self-grade +
`/code-review ultra` grade against. It is filled by the bridge spike
(`atom.branded-surface-bridge-spike.v0`): each row gets a **source** —
`inherit` (the SDK/CLI gives it for free), `build` (we render it), or `have`
(already exists in the repo) — and a **status** — `todo` / `wip` / `green`,
green only with **evidence** (a file:line, a passing test, or an observed
behaviour). A constant "all green" with no evidence is a failed grade (§10).

> **GATE:** every row's source is unknown until the spike answers it. You cannot
> mark a row `green` over a bridge the spike has not proven. If the spike finds
> the bridge infeasible (SDK *and* CLI), the loop STOPS and lands this checklist
> with the finding — it does not fake green.

| # | Capability (what normal Claude Code does) | Source | Status | Evidence |
|---|-------------------------------------------|--------|--------|----------|
| 1 | Open a branded ontum window (webview), standalone of the official panel | build | green | `extension.js` (`openSurface`/`activate`) + `shell.js` (`renderShell`); `node vscode/ontum-surface/test/open-window.test.js` → 7 checks, exit 0 (registers `ontum.surface.open`, opens one webview, branded `data-surface="ontum"` + `data-standalone="true"`, no `claude-code`/anthropic dependency, nonce-gated CSP). Proves the open-path + markup; pixel render needs a host. |
| 2 | List local sessions from the transcript store; select one | build | green | `sessions.js` (`listSessions`/`summarize`/`parseTranscript`/`storeDirFor`) reads `~/.claude/projects/<encoded-cwd>/*.jsonl`, derives id/title/messageCount/branch newest-first, torn-tail tolerant; `shell.js` `renderSessionList` paints selectable `data-session-id` buttons; `extension.js` reads the store on open + records the `ontum:select-session` round-trip. Evidence: `node vscode/ontum-surface/test/sessions.test.js` → 8 checks, exit 0 (fake store incl. a torn line); read-only smoke on the live store returned 3 real sessions with titles ("Warmup"×2, "(no prompt yet)"). |
| 3 | Read + render a transcript (user / assistant / tool-use / tool-result) | build | green | `transcript.js` (`readTranscript`/`foldTranscript`/`entriesFromMessage`/`toolResultText`/`fileForSession`) folds a session's `.jsonl` into ordered entries of kind `user-text`/`assistant-text`/`assistant-thinking`/`tool-use`/`tool-result` (thinking via the `thinking` field, tool_result via a user turn), dropping non-turn/empty blocks, torn-tail tolerant; `shell.js` `renderTranscript` paints each kind as an escaped, labelled, `data-kind`-tagged block (error results flagged `data-error`); `extension.js` `renderPanel`/`readSelectedTranscript` re-render the panel with the selected session's transcript. Evidence: `node vscode/ontum-surface/test/transcript.test.js` → 9 checks, exit 0 (fake store with all four kinds + an empty block + a torn line; asserts fold order, payloads, escaping, the empty-state note, and the select→re-render round-trip); read-only smoke on the live store folded a real session to 3 entries (`user-text, assistant-thinking, assistant-text`, title "Warmup"). |
| 4 | Live-tail the active session as it appends | build | todo | — |
| 5 | Drive a new turn through the engine (send a prompt, get a reply) | spike | todo | — |
| 6 | Stream the assistant turn (text + thinking) as it arrives | spike | todo | — |
| 7 | Render tool calls and their results | build | todo | — |
| 8 | Render diffs / edits with accept–reject | build | todo | — |
| 9 | Permission prompts (canUseTool / permission-mode surface) | spike | todo | — |
| 10 | Slash commands | spike | todo | — |
| 11 | Plan mode | spike | todo | — |
| 12 | @-mentions / IDE selection context | build | todo | — |
| 13 | MCP tools available + invocable | inherit | todo | — |
| 14 | Hooks / skills / settings inherited (the environment) | inherit | todo | — |
| 15 | Image / file attach | build | todo | — |
| 16 | Resume / continue an existing session | spike | todo | — |
| 17 | Stop / interrupt a running turn | spike | todo | — |
| 18 | Cost / usage display | build | todo | — |

**Self-grade rule.** A row is `green` only if its evidence column names something
a cold reader can check. The overall grade = (green rows / 18) with every
non-green row carrying its honest blocker. Parity-green = 18/18.

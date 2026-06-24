# GRADES — Branded Claude surface, Phase 1 (overnight, 2026-06-24)

Built by the overnight administer loop against `epic.digital-experience` /
done-line 0197. Marker = parity checklist 18/18 green. **Reached: 18/18 — MARKER
MET.** The overnight window (≈02:46–08:00) closed at 10/18; the extended daytime
close-out run (window to 14:30, bdo: "keep working until close") drove the
remaining eight rows (11–18) to green at ≈1/tick, each with a passing host-free
`node` test, landing the full parity bar.

---

## Marker reached — 18/18 (2026-06-24 close-out)

All 18 parity-checklist rows are `green`, each citing a checkable file + a passing
`node` test (full suite: **19 test files PASS**). The arc this close-out added on
top of the 10/18 overnight foundation:

- **row 11** plan mode (`plan.js` — ExitPlanMode plan card, approve/keep, exit-plan-mode transition) — `plan.test.js` 17 ✓
- **row 12** @-mentions / IDE selection (`mentions.js` — @-file discovery + selection preamble, pass-through) — `mentions.test.js` 15 ✓
- **row 13** MCP available + invocable (`mcp.js` — `mcp__server__tool` parse, server discovery, live-tools annotation) — `mcp.test.js` 17 ✓
- **row 14** environment inherited (`environment.js` — settings layers, hooks fold, skills discovery) — `environment.test.js` 22 ✓
- **row 15** image / file attach (`attach.js` — classify/read/encode to Messages-API content blocks) — `attach.test.js` 26 ✓
- **row 16** resume / continue (`engine.js` — `--continue`/`--resume`/`--fork-session` target→argv mapping) — `resume.test.js` 25 ✓
- **row 17** stop / interrupt (`engine.js markInterrupted` + control handle; terminate-the-process, label honest partial) — `stop.test.js` 19 ✓
- **row 18** cost / usage display (`usage.js` — fold + format the engine's reported cost/usage, running session total) — `usage.test.js` 25 ✓

### Self-grade — the full bar (adversarial, the author's line, never the deciding one D-2)

**Overall: 18 / 18 green** — but read the grade, not the number. The strongest
single fact since 10/18: **a real billed turn ran end-to-end through `engine.js`**
(`text="OK"`, cost $0.40 — `REAL-TURN-PROOF.md`) and the 4 peer-found engine bugs
were fixed + tested (`engine-fixes.test.js`: UTF-8 `StringDecoder`, stdin-EPIPE
listener, turn watchdog, `assembleStream` orphan-stop, model-alias 404). So the
drive path is no longer fake-only.

**What is genuinely solid:**
- The read viewer (1–4) is smoke-tested against the live store; the drive path
  (5–7) has one real billed turn behind it; every `inherit` row (9, 11, 13, 14,
  16, 17) cites a flag verified live against `claude --help 2.0.19`.
- The pure-fold modules (`mcp.js`, `environment.js`, `attach.js`, `usage.js`) are
  each proven host-free with a dedicated suite, no `vscode` dependency, honest
  null/em-dash for absent data, and consistent `escapeHtml` on every interpolation
  (the XSS surface stayed clean through eight more rows).
- Row 18 specifically is the safest increment of the night: pure display, no
  process/host code, every value a fold of the engine's own `result` (never an
  estimate), 25 checks incl. "a no-usage errored turn does not inflate the tab."

**What is thin — the riskiest unproven claims (in order):**
- **🔴 No pixel has rendered in a real VS Code host.** Every render row (1–18) is
  asserted on HTML-string markup + the webview message protocol, never a live
  webview. The first `code --extensionDevelopmentPath` load is unproven and is
  where integration gaps will surface.
- **🔴 Rows 11–18 have NOT had a real billed turn each.** The $0.40 proof exercised
  the rows-5–10 drive path; the later rows (plan card, MCP invocation, a hook
  firing, an image turn, a resume replay, a real stop mid-turn, a real cost line)
  are proven at the fold + protocol level against captured/fake shapes, not a live
  turn. `green` = "the surface plumbing is tested," not "exercised live."
- **🟠 The hook-suppression finding is open:** the repo's own `UserPromptSubmit`
  hooks suppress a nested headless turn (clean in `/tmp`). `engine.js` is correct,
  but a surface driving in-repo must avoid re-triggering project hooks — unhandled.
- **🟠 Row 13 "invocable" and row 14 "loaded"** rest on the inherit claim (the init
  event names the tools / the engine runs the hooks); the surface *displays* them
  host-free but has not watched a real MCP tool fire or a real skill load through
  this window.

**Honest verdict:** the parity *checklist* is genuinely 18/18 with zero faked green
— but it grades the **surface plumbing**, not a **shipped product**. The bar was
"every capability normal Claude Code does is recognised, folded, routed, and
displayed by the branded surface, proven host-free (+ one real drive turn)." That
bar is met. The bar it does *not* claim: a human has opened the window and used it.
That first real-host session is the next gate, and it is bdo's to run.

### Peer grade (/code-review ultra)

> **Note on the requested grader (unchanged from the overnight record):** bdo chose
> cloud `/code-review ultra` as the independent evaluator. The cloud `ultra` variant
> is **user-triggered and billed — a session cannot launch it** (harness rule; there
> is no `/code-review` command on this machine, project or global). So the deepest
> peer read a session can land is the in-process review below; the cloud `ultra`
> pass on this PR's diff is **bdo's one command** if he wants the deeper cloud read.
> The overnight `/code-review max` pass (4 finder angles) stands in the historical
> record below and found 8 real bugs — **all 4 HIGH/MED engine bugs are now fixed +
> tested** (`engine-fixes.test.js`), which is the strongest evidence the peer grade
> was non-vacuous.

**Independent in-process review of the close-out diff (rows 11–18).** Reviewed the
eight new modules + their shell/extension wiring for the same four angles the
overnight pass used (correctness, host-crash/resource, injection, honesty):

- **Injection surface stayed clean.** Spot-checked every new `render*` (`renderPlanBlock`,
  `renderMcpPanel`, `renderEnvPanel`, `renderAttachTray`, `renderResumeControl`,
  `renderUsageBar`): every interpolated value passes through `escapeHtml`, and the
  streaming/swap paths use `textContent` / pre-escaped host-rendered HTML — no new
  `innerHTML`-of-raw-data sink. A hostile field test exists per module (e.g.
  `renderUsageBar escapes a hostile field`).
- **No new host-crash path.** Rows 11–18 add pure folds (`plan/mcp/environment/attach/usage.js`)
  and argv mapping (`resume`), plus `markInterrupted` (row 17) which only re-tags a
  reply object. The one process-signal path (row 17 `interrupt()`) is idempotent
  (returns false after settle) and tested against a stalling fake engine. `usage.js`
  touches no `fs`/process at all.
- **Honesty grain held.** `usage.num` gates every field to finite-or-null so a
  missing/NaN/Infinity value renders an em-dash, never a fabricated 0;
  `accumulateUsage` counts only turns that reported real usage (a Stop/spawn-error
  can't inflate the tab); `attach.readAttachment` caps at 5 MB binding both the stat
  AND the buffer length; `environment`/`mcp` flag a present-but-torn file honestly.
- **Carried-over risks (not regressions, the same as the overnight record):** still
  no real VS Code host render; rows 11–18 have no per-row real billed turn; the
  hook-suppression finding is open. These are the punch-list, not blockers for a
  foundation PR.

**Verdict:** the close-out diff is low-risk relative to the overnight engine path —
it is mostly pure, well-tested folds with a clean injection surface; the genuine
risk remains concentrated where the self-grade puts it (first real-host load + a
live turn per row), not in the new code. The cloud `ultra` pass remains bdo's to
run for the deeper independent read.

---

## Historical record — the overnight night (10/18) and its post-merge close-out

*(Preserved verbatim below; the original night's self-grade and peer grade stand as
the record of how the foundation was built.)*

## Close-out update (post-merge, 2026-06-24 AM) — branch `claude/branded-surface-close`

After PR #743 merged, the work continued toward close. Landed since:
- **The count is corrected** (was stale at 9; the final overnight tick had landed row 10 → **10/18**).
- **All 3 peer-review engine bugs are fixed + tested** (UTF-8 stream corruption →
  `StringDecoder`; stdin EPIPE host-crash → `'error'` listener; no turn-timeout →
  a watchdog) plus the `assembleStream` orphan-stop guard. See `test/engine-fixes.test.js`.
- **A 4th bug fixed:** `engineArgs` pinned no model → the bare `opus` alias 404'd
  headless (the same bug that hit the scheduler). Now defaults to a valid id.
- **🟢 THE HEADLINE CAVEAT IS CLOSED FOR THE DRIVE PATH:** a **real billed turn**
  ran through `engine.js` (`text="OK"`, cost $0.40) — see `REAL-TURN-PROOF.md`.
  Rows 5–10 are no longer fake-only at the drive layer.
- **New honest finding:** the repo's own `UserPromptSubmit` hooks suppress a
  nested headless turn (empty completion in-repo, clean in `/tmp`) — `engine.js`
  is correct; the surface must drive without re-triggering project hooks.
- **Still open:** pixel rendering in a real VS Code host; rows 11–18; the
  hook-suppression handling.

The original night's self-grade and peer grade stand below as the record.

## Self-grade (the author's line — never the deciding one, D-2)

**Overall: 10 / 18 green.** Honest, adversarial read below. Per-row status is in
`PARITY-CHECKLIST.md` with file+test evidence; this is the judgment over it.

### What is genuinely solid
- **Rows 1–4 — the read-only viewer — are the strongest work.** The window opens
  standalone (no `claude-code`/anthropic dependency), lists real sessions from
  the real transcript store, renders a transcript (all five entry kinds), and
  live-tails by byte-offset with torn-tail tolerance. These were **smoke-tested
  against the live store** (3 real sessions, a real "Warmup" folded to 3 entries,
  the tail advancing 0→3→EOF) — not just fakes. This half is close to real.
- **Test discipline is real, not theatre.** ~97 host-free checks across 9 suites
  (`open-window 7`, `sessions 8`, `transcript 9`, `livetail 12`, `engine 16`,
  `stream 15`, `tools 15`, `diff 15`, `permission 14`), every increment kept the
  prior suites green (no regression), and each `green` row cites a checkable
  file+test. A constant/fake classifier would not pass these.
- **The bridge claim is grounded.** Every `inherit` row cites flags verified live
  against `claude --help 2.0.19` (`--input/output-format stream-json`,
  `--include-partial-messages`, `--permission-mode`, `--resume`, …), not assumed.

### What is thin — and the single riskiest over-claim
- **🔴 THE BIG ONE: rows 5–10 are `green` against a FAKE engine and NO real billed
  turn has ever run.** "Drive a turn" (5), "stream the turn" (6), "tool calls"
  (7), "diffs" (8), "permission modes" (9) are proven at the level of *the code
  path, the event-fold, and the host message protocol* — using injected fake
  engines and captured event shapes. **Not one real `claude` turn has been driven
  through this surface, and not one pixel has been rendered in a real VS Code
  host.** `green` here means "the plumbing is tested," not "it works in the
  window." Read 10/18 as *half the checklist plumbed and unit-tested host-free*,
  **not** *half a working product you can use*.
- **Nothing has run in an actual VS Code host.** All rendering is asserted on
  HTML-string markup, never a live webview. The first real `code --extensionDevelopmentPath`
  load is unproven and may surface integration gaps the string tests cannot.
- **Row 9 (permissions) carries a real scope cut:** the permission *mode* +
  allow/deny policy flow into argv, but an interactive mid-turn `canUseTool`
  callback is an SDK/persistent-session feature this CLI version doesn't advertise
  — so live in-turn permission prompts are not covered.

### What's left for parity (rows 11–18, all `todo`)
plan mode (11) · @-mentions / IDE selection (12) · MCP
available+invocable (13) · hooks/skills/settings inherited (14) · image/file
attach (15) · resume/continue (16) · stop/interrupt a turn (17) · cost/usage
display (18). Several are `inherit` (11, 13, 14, 16, 17) — likely faster, but
each still needs a green row with evidence, and **rows 13–14 (the actual
environment inheritance) are the load-bearing parity claim and are not yet
proven.**

### The honest verdict
A strong night's foundation: the read viewer is nearly real, the drive path is
plumbed and well-tested, the bar is half-filled with checkable evidence and zero
faked green. But it is **foundation, not a usable surface** — the first real test
(a VS Code host + one billed turn) hasn't happened, and that is exactly where the
risk concentrates. Grade it as half the *plumbing*, not half the *product*.

## Peer grade — independent review (max effort, 4 finder angles)

> **Note on the requested grader:** bdo chose cloud `/code-review ultra` as the
> peer evaluator. The cloud `ultra` variant is **user-triggered and billed — a
> session cannot launch it** (harness rule). So the independent peer grade below
> is `/code-review` at **`max`** (the deepest level a session can run in-process:
> 4 parallel finder angles over the diff + verification). The cloud `ultra` pass
> is **bdo's one command** to run on this PR if he wants the deeper cloud read.

**Verdict: the review is non-vacuous — it found real bugs, concentrated exactly
where the self-grade flagged the risk (the engine/drive path that has never run
live).** This independently corroborates the headline caveat: 10/18 is plumbing,
not a proven product. Ranked findings (most severe first):

| # | Sev | File | Bug |
|---|-----|------|-----|
| 1 | HIGH | `engine.js` (~369) | **Silent multibyte-UTF-8 corruption.** `chunk.toString('utf8')` per stdout chunk mangles any non-ASCII char split across a chunk boundary (café→caf�). Still valid JSON, so it parses — corruption is invisible. (`livetail.js` does this right on raw bytes.) Fix: `string_decoder.StringDecoder` or decode only up to a newline. |
| 2 | HIGH | `engine.js` (~406) | **EPIPE can crash the extension host.** `child.stdin.write()` has no `'error'` listener; a fast-exiting engine delivers EPIPE as an async event the try/catch can't catch → uncaught exception. Fix: `child.stdin.on('error', …)`. |
| 3 | MED-HIGH | `engine.js` (~332) | **`driveTurn` has no timeout** — resolves only on `close`; a child that emits `result` then wedges (stuck MCP/tool holding pipes) hangs the turn forever. Add a watchdog that kills + settles. |
| 4 | MED | `extension.js` (~168) | **Mid-turn panel rebind.** `sendPrompt`/`postTurnDelta` post to the module-global `panel`; close+reopen during a turn injects the old turn's stream into the new panel. Bind the turn to its originating panel instance. |
| 5 | MED | `extension.js` (~247) | **Falsy-zero tail anchor.** `fileSize()` returns `0` on stat failure; that `0` becomes the tail offset → the whole transcript re-appends as duplicates. Distinguish failure from a real empty file. |
| 6 | MED | `livetail.js` (~64) | **Rotation undetected when new file ≥ old offset.** Only `from > buf.length` resets; a same-or-larger in-place rewrite is read from a stale byte offset → garbled appended entries with `reset:false`. Needs a file-identity/size baseline. |
| 7 | MED | `sessions.js` (~133) | **Session `id` taken from the record's internal `sessionId`, not the filename** → forked/compacted sessions collide or reopen the wrong file. Prefer the filename-derived `file` handle. |
| 8 | LOW-MED | `shell.js` (~24) | **CSP nonce from `Math.random()`**, not a CSPRNG — weakens the script-src defense-in-depth that backstops any future escaping regression. Use `crypto.randomBytes`. |
| — | EFFICIENCY | `livetail.js` (~57) | `fs.readFileSync(whole file)` every 500ms tail tick (contradicts the "reads only new bytes" header). Use `fs.read` from the offset. |
| — | CLEANUP | `shell.js`, `engine.js`, `sessions.js` | duplicated `ensureList`; the live streaming-accumulation logic exists twice (tested `assembleStream` vs an untestable inline `<script>` twin — drift risk); `listSessions` re-reads+parses the whole store on every click. |
| — | LOW/cosmetic | `diff.js`, `sessions.js` | trailing-newline phantom diff line; multiline/uncollapsed titles; inflated `messageCount`; NotebookEdit delete renders an empty diff. |

**What the review confirms (the honest takeaway):** the HTML-injection/XSS surface
is **clean** (every interpolation escaped; streaming path uses `textContent`, not
`innerHTML`) — the security basics are right. But the **engine-drive path carries
3 real host-crash/corruption/hang bugs that only a real billed turn would expose**
— which is exactly why "tested against a fake engine" was flagged as the headline
risk. None of these are blockers for a foundation PR; they are the punch-list for
making rows 5–10 *real* before this surface is used.

> Also noted: `vscode/CLAUDE.md` (the surface's governing conventions, from the
> unlanded forest-mask PR #693) is **not on this branch's base** (main), so the
> directory's own rules couldn't be cited — worth landing #693's `vscode/CLAUDE.md`
> first or carrying it here.

## bdo's grade (yours to fill)

<!-- your read, your score, your thoughts — and your confirm-arc on
     epic.digital-experience is what lets any of this land (D-4). -->

# GRADES — Branded Claude surface, Phase 1 (overnight, 2026-06-24)

Built by the overnight administer loop against `epic.digital-experience` /
done-line 0197. Marker = parity checklist 18/18 green. **Reached: 10/18.** The
window (≈02:46–08:00) closed with the read-only viewer complete and the
engine-drive half of the parity bar plumbed and tested host-free.

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

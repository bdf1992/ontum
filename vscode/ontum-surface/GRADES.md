# GRADES — Branded Claude surface, Phase 1 (overnight, 2026-06-24)

Built by the overnight administer loop against `epic.digital-experience` /
done-line 0197. Marker = parity checklist 18/18 green. **Reached: 9/18.** The
window (≈02:46–08:00) closed with the read-only viewer complete and the
engine-drive half of the parity bar plumbed and tested host-free.

## Self-grade (the author's line — never the deciding one, D-2)

**Overall: 9 / 18 green.** Honest, adversarial read below. Per-row status is in
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
- **🔴 THE BIG ONE: rows 5–9 are `green` against a FAKE engine and NO real billed
  turn has ever run.** "Drive a turn" (5), "stream the turn" (6), "tool calls"
  (7), "diffs" (8), "permission modes" (9) are proven at the level of *the code
  path, the event-fold, and the host message protocol* — using injected fake
  engines and captured event shapes. **Not one real `claude` turn has been driven
  through this surface, and not one pixel has been rendered in a real VS Code
  host.** `green` here means "the plumbing is tested," not "it works in the
  window." Read 9/18 as *half the checklist plumbed and unit-tested host-free*,
  **not** *half a working product you can use*.
- **Nothing has run in an actual VS Code host.** All rendering is asserted on
  HTML-string markup, never a live webview. The first real `code --extensionDevelopmentPath`
  load is unproven and may surface integration gaps the string tests cannot.
- **Row 9 (permissions) carries a real scope cut:** the permission *mode* +
  allow/deny policy flow into argv, but an interactive mid-turn `canUseTool`
  callback is an SDK/persistent-session feature this CLI version doesn't advertise
  — so live in-turn permission prompts are not covered.

### What's left for parity (rows 10–18, all `todo`)
slash commands (10) · plan mode (11) · @-mentions / IDE selection (12) · MCP
available+invocable (13) · hooks/skills/settings inherited (14) · image/file
attach (15) · resume/continue (16) · stop/interrupt a turn (17) · cost/usage
display (18). Several are `inherit` (10, 11, 13, 14, 16, 17) — likely faster, but
each still needs a green row with evidence, and **rows 13–14 (the actual
environment inheritance) are the load-bearing parity claim and are not yet
proven.**

### The honest verdict
A strong night's foundation: the read viewer is nearly real, the drive path is
plumbed and well-tested, the bar is half-filled with checkable evidence and zero
faked green. But it is **foundation, not a usable surface** — the first real test
(a VS Code host + one billed turn) hasn't happened, and that is exactly where the
risk concentrates. Grade it as half the *plumbing*, not half the *product*.

## Peer grade (/code-review ultra)
_Requisitioned — see the section appended below (or the PR thread)._

## bdo's grade (yours to fill)

<!-- your read, your score, your thoughts — and your confirm-arc on
     epic.digital-experience is what lets any of this land (D-4). -->

# The ontum surface — a branded window over the Claude Code engine

**Status: PROPOSED** (bdo's to name; a session's only to propose, D-4).
Born from bdo, 2026-06-24: *"Make my own window and remove the existing one's
requirement to use it. Obviously we continue to use Claude and the Claude Code
environmental capabilities, and make sure we have parity with norm before we add
meta and culture."* — and the unlocking observation that started it: *"I could
replace Claude with a wrapped and branded version, couldn't I?"*

This is the concrete form of `epic.digital-experience` (PR #153, "ontum as the
new digital experience"). It is **arc-scale** — so this bundle is the
blueprint-before-build deliverable, not code.

## The shape (the purpose)

**An ontum-branded VS Code surface that is the front door to the Claude engine —
its own window, usable without the official Claude Code panel, at parity with
normal Claude Code before any ontum meta or culture is added.**

Three moving parts, one law:

1. **The window** — an ontum-branded VS Code webview. Your own chat surface,
   your own session list/tabs, your own skin. The official Claude Code panel
   becomes *optional* — your window does not depend on it being open or even
   installed.
2. **The engine bridge** — a *small* wrapper that drives the same Claude engine
   the official extension drives, through a supported channel (the **Claude
   Agent SDK** or the headless `claude` CLI streaming mode). You are not
   reimplementing Claude; you are calling it.
3. **The truth read** — the surface reads the **local session transcript store**
   (`~/.claude/projects/<project>/<session_id>.jsonl`, **193 files on this PC
   today**, each named by its session id) and the loop log as its truth. It
   keeps no second store of the conversation.

**The law (why it fits the substrate):** the surface is a **fold**, never a
second source. The conversation's truth is the transcript JSONL the engine
writes; the loop's truth is `.ai-native/log/`. The window *renders* both and
*drives* the engine — it computes no conversation state the engine does not
already own. This is the `vscode/CLAUDE.md` rule ("the log is truth; the surface
is a fold") lifted from the Explorer mask to the whole chat surface.

## The unlock — the correlation gap is gone (bdo, 2026-06-24)

The earlier blocker for the forest mask was *"VS Code won't tell a plugin which
Claude Code tab is selected, so it can't scope per-session."* bdo dissolved it:
the **session transcripts are local files named by session id**, and the
file-touch sensor (`.claude/hooks/file_touch.py:116`) tags every record with the
**same** `session_id`. So the join is direct — `<session_id>.jsonl` ↔ the touch
log's `session` field — and **the surface owns its own session selection** by
reading the store, never by asking VS Code. Per-session scoping (the mask, the
attention overlay) becomes trivial *because the window is the wrapper*.

## The staging is the spine: parity before meta/culture (bdo, 2026-06-24)

bdo's ordering is the safety property of the whole plan: **don't stack ontum
overlays until the floor matches normal Claude Code**, or you debug parity and
meta at the same time. Two phases, a hard gate between them:

- **Phase 1 — PARITY.** The window does everything normal Claude Code does,
  driving the same engine with the same environment, wearing a neutral skin.
  *Gate: the parity checklist is green.*
- **Phase 2 — META + CULTURE.** Only then add what is ours: per-session forest
  mask, attention overlay, session graph, embedded loop surfaces (meta); the
  ontum brand, naming, and surface language (culture).

The reason Phase 1 even *can* keep the "Claude Code environmental capabilities"
is that **the Agent SDK is the same harness**: it runs your hooks, skills, MCP
servers, permission rules, and settings. You inherit the environment; you rebuild
only the **client surface** (the chat UI). Confirm the exact streaming surface in
the spike (CTA-2) — that pins how much "small wrapper" really is.

## Concept list

### A — The window (the surface)
- **`ontum-surface/` VS Code extension** — a webview panel, plain-JS where it can
  be (the `vscode/` law: no toolchain), ontum-branded. Registers a view/command
  so the user opens *the ontum surface*, not the Claude panel.
- **Own session list / custom tabs** — reads the transcript store, lists sessions
  (labelled by first prompt / recency / touched-file count), lets the user open
  any one. This is the "custom tabs" bdo named — the surface owns selection.
- **Standalone-usable** — no requirement that the official panel be open. The
  official extension is the *engine provider* (or the SDK is), not the UI.

### B — The engine bridge (the small wrapper)
- **The driver** — a thin module that opens a streaming session against the
  engine (**Agent SDK** preferred; **headless `claude` CLI** stream-json as the
  fallback/alternative) and pumps user messages in / engine events out.
- **Inherited environment** — hooks, skills, MCP servers, permission modes,
  `settings.json`, working directory. Not reimplemented — inherited from the SDK
  harness. *This is the "parity with norm" enabler and must be proven in the
  spike.*
- **Live + resumed sessions** — drive a new session, or `--resume <session_id>`
  an existing one (the supported channel; the continue-probe skill already
  spawns `claude --resume`). Injection into a live session is first-class and
  supported — we never hand-edit the `.jsonl` under a running process.

### C — The truth read (the fold)
- **Transcript reader** — parses `<session_id>.jsonl` into rendered turns
  (user / assistant / tool-use / tool-result), torn-tail tolerant (a partial
  trailing line never happened — the loop's standing property).
- **Live tail** — a `FileSystemWatcher` on the active session's transcript
  re-renders as the engine appends, so the window updates as the turn streams.
- **The session↔touch join** — the file-touch log scoped by `session_id`, ready
  for the Phase-2 per-session mask.

### D — The parity surface (the FLOOR — the checkable bar)
The spine of Phase 1. Every capability normal Claude Code gives, each marked
*have / build / inherit-from-SDK*. The initial list to fill in the spike:
- stream an assistant turn (text + thinking) · render **tool calls** and results
  · render **diffs / edits** with accept-reject · **permission prompts**
  (the `canUseTool` / permission-mode surface) · **slash commands** · **plan
  mode** · **@-mentions / IDE selection context** · **MCP tools** · image/file
  attach · session resume/continue · stop/interrupt a turn · cost/usage display.
- **The honest cost lives here.** The wrapper is *small* for send/receive; full
  parity (permission UX, tool/diff rendering, slash commands, plan mode) is the
  real surface. The checklist makes that cost visible instead of discovered late.

### E — The meta layer (Phase 2 — ours)
- **Per-session forest mask** — the existing `vscode/forest-mask`, now scoped to
  the selected session (the join from C). The thing that was impossible before
  the unlock.
- **Attention / context overlay** · **session graph** (sessions ↔ files ↔ atoms)
  · **embedded loop surfaces** (summon / digest / forest rendered inside the
  window).

### F — The culture layer (Phase 2 — ours)
- The ontum **brand and skin**, naming, and surface language over all of A–E.
  Applied *after* parity is green.

## Boundary / non-goals (what this is *not*)
- **Not reskinning Claude Code's own webview.** Their panel's chrome is theirs
  (the same wall as the AskUserQuestion modal — harness-owned). We build our
  *own* window beside/instead of it; we do not repaint theirs.
- **Not forking or replacing the Claude engine or model.** "Replace Claude" means
  replace the **front-end**, not the engine. Underneath it stays Claude via the
  SDK/CLI. It is a wrapper + a driver + a brand.
- **Not a second source of truth.** The conversation's truth is the transcript
  JSONL; the loop's truth is `.ai-native/log/`. The window reads both; it stores
  neither a second time, and editing the transcript is never its job.
- **Not editing a live session's bytes under a running process.** Driving is a
  *new turn* through the supported channel, never a file edit beneath the engine.

## The honest seams (name them now, not late)
- **Parity is the cost.** The engine bridge is genuinely small; matching the full
  client UX is not. The parity checklist (D) is how we size it honestly. *This is
  the single biggest estimate risk.*
- **The exact SDK streaming surface is unverified.** Whether the Agent SDK gives
  the streaming-input + hooks/MCP/permissions surface we need at the fidelity we
  need is **the spike** (CTA-2). The plan degrades cleanly: if the SDK is thin,
  the headless `claude` CLI stream-json is the fallback driver.
- **Distribution / branding ToS.** For bdo's own use in his own repo, a branded
  wrapper over his own Claude Code is a non-issue. *Distributing* a "branded
  replacement for Claude" later raises trademark/ToS questions — flag, not block;
  out of scope for the build, bdo's call if it ever ships outward.

## Calls to action (against the purpose: a branded front door at parity-first)

- **CTA-1 — the target.** Confirm the goal is **your own window, official panel
  optional** (a standalone surface that drives the engine), *not* an overlay that
  decorates the official panel. *(Rec: yes — it is what "remove the existing
  one's requirement" means, and it is what makes per-session scoping trivial.)*
- **CTA-2 — the engine bridge (the spike, build task 1).** A small spike that
  pins the exact driving surface: **Agent SDK** (preferred — inherits the
  environment) vs **headless `claude` CLI** stream-json (fallback), and verifies
  hooks / skills / MCP / permission-modes are inherited. *(Rec: spike the SDK
  first; it is the same harness this session runs on. The spike's output is the
  honest estimate for everything else.)*
- **CTA-3 — parity-first staging.** Confirm **Phase 1 = parity, Phase 2 =
  meta + culture**, with the parity checklist as the hard gate between. *(Rec:
  yes — your words; it is the plan's safety property.)*
- **CTA-4 — the parity bar.** Adopt the parity checklist (D) as the spine of
  Phase 1, so "parity with norm" is a checkable bar, not a feeling. *(Rec: yes —
  fill it during the spike; mark each row have / build / inherit.)*
- **CTA-5 — smallest real first piece (witness before actuator).** Build order
  *(Rec)*: **increment 1** = the branded window that **reads + live-tails** the
  selected session's transcript (proves the truth-join, the tail, the brand —
  drives nothing, breaks nothing); **increment 2** = the engine bridge (drive one
  real turn); **increment 3** = parity hardening to green; **then** Phase 2.
  *(Rec: yes — a read-only viewer first de-risks the whole read path before we
  touch driving, the `heal`-before-actuator grain.)*
- **CTA-6 — home.** Live as its own proposal that **`epic.digital-experience`**
  cites (or that graduates into it). bdo names whether it joins that epic or
  opens a new one. *(Rec: graduate into `epic.digital-experience` — this *is*
  that horizon made concrete.)*

## Why it earns a place (not ceremony)

bdo already works inside this window all day; the loop already writes the truth
this window would render; the engine already exposes a supported channel to drive
it. The only thing missing is **the front door wearing ontum's face** — and the
unlock (local transcripts named by session id) means the hardest part of the
read path is already solved. Parity-first keeps it honest: a branded surface that
*matches* Claude Code before it *adds* to it is a real product increment, not a
demo skin.

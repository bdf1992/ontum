// extension.js — the ontum surface VS Code extension entry point.
//
// Row 1: register a command + an activity-bar presence that opens a *branded,
// standalone* ontum webview window. Standalone means: the official Claude Code
// panel need not be open or installed for this window to exist — the engine is
// the provider, this is our own front door (blueprint §A).
//
// The markup lives in shell.js (a pure function) so it is testable without a
// VS Code host; this module is the thin host glue: it owns the command, the
// panel lifecycle, and wiring the webview's CSP source into the shell.

'use strict';

const fs = require('fs');
const os = require('os');
const vscode = require('vscode');
const { renderShell, renderTranscriptRows } = require('./shell');
const { listSessions, storeDirFor } = require('./sessions');
const { readTranscript, fileForSession } = require('./transcript');
const { tailTranscript } = require('./livetail');
const {
  driveTurn,
  partialDelta,
  normalizePermissionMode,
  normalizeResumeTarget,
  resumeArgsFromTarget,
} = require('./engine');
const { listSlashCommands } = require('./slash');
const { listMentionTargets, withSelectionContext } = require('./mentions');
const {
  readAttachment,
  attachmentBlocks,
  displayAttachment,
} = require('./attach');
const { nextModeOnPlanDecision, isPlanDecision } = require('./plan');
const { listMcpServers, userConfigPathFor } = require('./mcp');
const { listEnvironment } = require('./environment');

const VIEW_TYPE = 'ontum.surface';
const OPEN_COMMAND = 'ontum.surface.open';

// One panel per window — re-running the command reveals the existing one
// rather than stacking duplicates.
let panel = null;
// The session the user last selected (row 2). Row 3 reads its transcript.
let selectedSessionId = null;
// Row 4 — live-tail state. `tailOffset` is the byte offset of the selected
// session's file we have already painted; the watcher tails from there as the
// engine appends. `tailWatched` is the file path currently under fs.watchFile
// (so we can stop watching when the selection changes or the panel closes).
let tailOffset = 0;
let tailWatched = null;
// Row 8 — the last diff accept/reject decision the webview posted (an edit
// tool-call rendered as a diff offers Accept/Reject). We record the decision so
// the round-trip is checkable host-free; actually applying or reverting the
// edit on disk is the host permission flow's job (row 9) / a human's — the
// surface records the decision, it does not fake the effect.
let lastDiffDecision = null;
// Row 11 — the last plan-mode approve/keep decision the webview posted (an
// ExitPlanMode tool-call renders as a plan card with Approve/Keep). We record
// the decision AND, on approve, exit plan mode (the permission posture
// transitions out of 'plan' so the engine can proceed). Conservative by
// construction: approve exits to 'default', never to acceptEdits/bypass.
let lastPlanDecision = null;
// Row 5 — the engine spawn used to drive a turn. Null in production (driveTurn
// falls back to the real child_process.spawn); a host-free test injects a fake
// process via __setSpawnForTest so the send→reply round-trip is proven without a
// real billed model call.
let spawnImpl = null;
// Row 9 — the permission mode the next turn runs under (the permission-mode
// surface). The composer's <select> posts ontum:set-permission-mode to change
// it; sendPrompt threads it into the engine argv (--permission-mode), so a turn
// actually runs under the human's chosen policy. Conservative default — an
// unknown value normalizes to 'default', never escalating to bypass.
let permissionMode = 'default';
// Row 12 — the IDE selection reader (the @-mentions / selection-context
// surface). In production this reads vscode.window.activeTextEditor's selection;
// a host-free test injects a fake selection via __setSelectionForTest so the
// "the turn carried the editor selection as context" round-trip is proven
// without a VS Code host. Null/no-editor -> no selection attached (the prompt is
// sent exactly as typed, preserving the row-5/10 pass-through).
let selectionImpl = null;
// Row 13 — the LIVE tools list the last driven turn's init event reported
// (engine reply.tools). It names the MCP tools the inherited environment
// actually loaded (`mcp__server__tool`), so readMcpServers can annotate the
// configured servers with what is genuinely available + invocable. Null until a
// turn has run (the configured-but-not-yet-loaded view is the honest default).
let lastEngineTools = null;
// Row 15 — the attachments staged for the NEXT turn (image / file attach). Each
// is an attach.readAttachment record (name/kind/mediaType/bytes + base64 data or
// utf8 text, or an honest error). sendPrompt encodes them into content blocks
// ahead of the typed text and clears the set; the composer's attach button +
// remove chips drive it. Empty by default (a plain turn carries no attachments,
// preserving every earlier row's verbatim-stdin behaviour).
let pendingAttachments = [];
// Row 16 — the session-continuity target the NEXT turn runs under (resume /
// continue / new). The composer's resume control posts ontum:set-resume to
// change it; sendPrompt threads it into the engine argv (--continue / --resume
// <id>), so a turn actually resumes/continues the chosen conversation.
// Conservative default — 'new' starts a fresh session, and an unknown mode / an
// id-less resume normalizes back to 'new' (a turn never silently resumes the
// wrong session). `fork` (--fork-session) branches a new id off a resumed one.
let resumeTarget = { mode: 'new', sessionId: null, fork: false };
// Row 15 — the file picker the attach button opens. In production this is the
// VS Code host dialog (vscode.window.showOpenDialog); a host-free test injects a
// fake picker via __setAttachPickerForTest returning the chosen path(s), so the
// "the attachment rode the turn as a content block" round-trip is proven without
// a host dialog. Null -> the production picker.
let attachPickerImpl = null;
// Row 17 — the control handle for the turn currently in flight (or null when no
// turn is running). driveTurn hands it to sendPrompt's onStart hook; the
// composer's Stop button posts ontum:interrupt-turn, which calls its interrupt()
// to terminate the engine process. Cleared the moment the turn settles, so a
// late Stop click is a harmless no-op (interruptTurn returns false).
let activeTurnControl = null;

// currentCwd() -> the workspace folder path, or process.cwd() as a fallback.
// The transcript store is keyed by this path (sessions.storeDirFor).
function currentCwd() {
  const folders =
    vscode.workspace && vscode.workspace.workspaceFolders;
  if (folders && folders.length && folders[0].uri && folders[0].uri.fsPath) {
    return folders[0].uri.fsPath;
  }
  return process.cwd();
}

// readSessions() -> the local session list for this workspace, newest-first.
// Failures (no store yet, unreadable dir) degrade to an empty list, never throw.
function readSessions() {
  try {
    return listSessions({ dir: storeDirFor(currentCwd()), limit: 50 });
  } catch (_) {
    return [];
  }
}

// readSlashCommands() -> the discovered slash-command palette for this
// workspace (row 10): the project's `<cwd>/.claude/commands/*.md` + the user's
// `~/.claude/commands/*.md` custom commands merged with the common built-ins
// (slash.listSlashCommands). A slash command is pass-through to the engine —
// this is the offered surface, not a gate; an unlisted command still sends.
// Failures degrade to the built-ins, never throw.
function readSlashCommands() {
  try {
    return listSlashCommands({ projectDir: currentCwd(), userDir: os.homedir() });
  } catch (_) {
    try {
      return listSlashCommands({});
    } catch (_) {
      return [];
    }
  }
}

// readMentionTargets() -> the discovered @-mention completion palette for this
// workspace (row 12): a bounded fold of the workspace file tree
// (mentions.listMentionTargets), skipping the noise dirs (.git/node_modules/…)
// and capped so a huge repo never hangs the palette. An @-mention is context
// the engine reads — this is the offered surface, not a gate; an unlisted path
// still sends. Failures degrade to [], never throw.
function readMentionTargets() {
  try {
    return listMentionTargets({ projectDir: currentCwd(), limit: 500 });
  } catch (_) {
    return [];
  }
}

// readMcpServers() -> the discovered MCP-server surface for this workspace
// (row 13): the CONFIGURED servers the CLI would load — the project's
// `<cwd>/.mcp.json` + the user's `~/.claude.json` mcpServers — each annotated
// with the tools the LIVE engine env actually exposed for it (the last turn's
// init-event `tools`, captured in lastEngineTools as `mcp__server__tool`). A
// server present on disk but absent from the live tools is honestly
// available:false (configured, not yet loaded). The engine remains the
// authority on what an MCP tool does and on whether a server connects; this is
// the offered/annotated surface (mcp.listMcpServers), not a re-implemented MCP
// client. Failures degrade to [], never throw.
function readMcpServers() {
  try {
    return listMcpServers({
      projectDir: currentCwd(),
      userConfig: userConfigPathFor(os.homedir()),
      tools: lastEngineTools,
    });
  } catch (_) {
    return [];
  }
}

// readEnvironment() -> the discovered inherited-environment surface for this
// workspace (row 14): the settings LAYERS the CLI reads (project + local +
// user, each with its top-level keys), the configured HOOKS folded across them
// (event + matcher + scope), and the available SKILLS (project `.claude/skills`
// over user `~/.claude/skills`). All three are folds of the SAME on-disk config
// the `claude` binary reads — the engine runs the hooks + loads the skills
// (inherit); this is the displayed surface, not a re-implementation. Failures
// degrade to empty groups, never throw.
function readEnvironment() {
  try {
    return listEnvironment({ projectDir: currentCwd(), userDir: os.homedir() });
  } catch (_) {
    return { settings: [], hooks: [], skills: [] };
  }
}

// currentSelection() -> the active editor's selection as a plain record
// { file, startLine, endLine, text } for the row-12 selection context, or null
// when there is no editor / no selection. A test injects a fake selection via
// __setSelectionForTest (selectionImpl). In production this reads
// vscode.window.activeTextEditor: an empty selection (a bare cursor, nothing
// highlighted) attaches nothing — only a real highlighted range becomes context.
// Lines are reported 1-based (VS Code positions are 0-based) so the header
// matches what the human sees in the gutter. Never throws.
function currentSelection() {
  if (typeof selectionImpl === 'function') {
    try {
      return selectionImpl() || null;
    } catch (_) {
      return null;
    }
  }
  try {
    const editor = vscode.window && vscode.window.activeTextEditor;
    if (!editor || !editor.selection || editor.selection.isEmpty) return null;
    const sel = editor.selection;
    const doc = editor.document;
    return {
      file:
        doc && doc.uri && doc.uri.fsPath
          ? doc.uri.fsPath
          : (doc && doc.fileName) || '',
      startLine: sel.start.line + 1,
      endLine: sel.end.line + 1,
      text: doc ? doc.getText(sel) : '',
    };
  } catch (_) {
    return null;
  }
}

// addAttachment(file) -> read + classify a file off disk (attach.readAttachment)
// and stage it for the next turn (row 15). Returns the staged record (incl. an
// honest error record for a missing/oversized file — staged so the human sees
// why it was refused, encoded to no block). A duplicate name replaces the prior
// staging (re-attaching the same file refreshes it). Never throws.
function addAttachment(file) {
  if (!file) return null;
  const rec = readAttachment({ file: String(file) });
  // De-dup by name so re-picking the same file does not stack chips.
  pendingAttachments = pendingAttachments.filter((a) => a.name !== rec.name);
  pendingAttachments.push(rec);
  return rec;
}

// removeAttachment(name) -> drop a staged attachment by name (the chip's Remove
// button posts it). Returns true when one was removed. No-op for an unknown name.
function removeAttachment(name) {
  const before = pendingAttachments.length;
  pendingAttachments = pendingAttachments.filter((a) => a.name !== name);
  return pendingAttachments.length < before;
}

// getAttachments() -> the data-free tray views of the staged attachments
// (attach.displayAttachment — name/kind/bytes/error, never the base64 payload).
// Fed to renderShell (row 15) and exposed so a host-free test can assert the
// staging round-trip without leaking the bytes into the assertion.
function getAttachments() {
  return pendingAttachments.map(displayAttachment);
}

// pickAttachment() -> open the host file picker (or the injected test picker),
// stage each chosen file (addAttachment), and re-render the tray (row 15). The
// live picker is a VS Code host dialog (vscode.window.showOpenDialog); the
// __setAttachPickerForTest seam returns the chosen path(s) host-free. Resolves
// to the staged records. Never throws.
async function pickAttachment() {
  let files = [];
  try {
    if (typeof attachPickerImpl === 'function') {
      files = (await attachPickerImpl()) || [];
    } else {
      const uris =
        (await vscode.window.showOpenDialog({
          canSelectMany: true,
          openLabel: 'Attach',
        })) || [];
      files = uris.map((u) => (u && u.fsPath ? u.fsPath : String(u)));
    }
  } catch (_) {
    files = [];
  }
  const staged = [];
  for (const f of files) {
    const rec = addAttachment(f);
    if (rec) staged.push(rec);
  }
  if (staged.length) renderPanel();
  return staged;
}

// selectedFile() -> the transcript file path of the selected session, or null.
function selectedFile() {
  if (!selectedSessionId) return null;
  try {
    return fileForSession(storeDirFor(currentCwd()), selectedSessionId);
  } catch (_) {
    return null;
  }
}

// fileSize(file) -> the file's byte length, or 0 when it cannot be stat'd.
function fileSize(file) {
  try {
    return fs.statSync(file).size;
  } catch (_) {
    return 0;
  }
}

// readSelectedTranscript() -> the folded entries of the selected session, or
// undefined when nothing is selected (so the shell shows its "pick a session"
// note). Failures degrade to an empty transcript, never throw (row 3).
function readSelectedTranscript() {
  if (!selectedSessionId) return undefined;
  try {
    const file = selectedFile();
    return readTranscript({ file }).entries;
  } catch (_) {
    return [];
  }
}

// pumpTail() -> read the entries the engine appended to the selected session
// since `tailOffset`, post ONLY those to the webview to splice onto the live
// list, and advance the offset (row 4). Returns the new entries so a host-free
// test can drive it without waiting on the watcher's poll. A truncated/rotated
// file (res.reset) repaints the whole panel instead of appending into a stale
// list. Holds the offset when nothing complete has arrived (torn tail).
function pumpTail() {
  const file = selectedFile();
  if (!file || !panel) return [];
  let res;
  try {
    res = tailTranscript({ file, fromOffset: tailOffset });
  } catch (_) {
    return [];
  }
  tailOffset = res.nextOffset;
  if (res.reset) {
    // The file shrank under us — repaint from scratch rather than append, then
    // re-anchor the tail at the new end.
    renderPanel();
    tailOffset = fileSize(file);
    return [];
  }
  if (
    res.entries.length &&
    panel.webview &&
    typeof panel.webview.postMessage === 'function'
  ) {
    panel.webview.postMessage({
      type: 'ontum:append-entries',
      html: renderTranscriptRows(res.entries),
    });
  }
  return res.entries;
}

// postTurnDelta(ev) -> translate ONE engine event into an incremental
// `ontum:turn-delta` message and post it to the webview (row 6). Events that are
// not renderable partials fold to null and post nothing. This streams the
// assistant's text + thinking to the composer AS IT ARRIVES; the terminal
// `ontum:turn-reply` then replaces the live preview with the authoritative
// folded blocks (one source of truth). Exposed via sendPrompt's onEvent hook.
function postTurnDelta(ev) {
  if (!panel || !panel.webview || typeof panel.webview.postMessage !== 'function') {
    return null;
  }
  const d = partialDelta(ev);
  if (!d) return null;
  const msg = Object.assign({ type: 'ontum:turn-delta' }, d);
  panel.webview.postMessage(msg);
  return msg;
}

// sendPrompt(text) -> drive ONE new turn through the inherited engine and post
// the folded reply back to the webview (row 5). Returns the reply so a host-free
// test can await it directly. The engine writes the turn to its own transcript
// store, so a selected+tailed session also streams it via row 4; this path
// additionally posts an `ontum:turn-reply` carrying the reply's rendered blocks
// and its honest status (cost/subtype) so the composer reflects the turn even
// before/without a session selection. Failures resolve to an error reply that is
// surfaced, never swallowed.
async function sendPrompt(text) {
  const base = String(text == null ? '' : text).trim();
  if (!base || !panel) return null;
  // Row 12 — attach the IDE selection as a marked context preamble when the
  // human has a range highlighted, else send exactly what was typed (the
  // row-5/10 pass-through is preserved). @-mentions in the typed text ride
  // through verbatim — the engine reads them as context (the surface offered
  // the completion palette; it does not re-implement file reading).
  const prompt = withSelectionContext(base, currentSelection());
  // Row 15 — encode the staged attachments into content blocks ahead of the
  // typed text (image/document base64, text inlined). An errored attachment
  // folds to no block. The set is cleared after the turn is driven so it rides
  // exactly one turn (the composer re-renders without the chips).
  const attachments = attachmentBlocks(pendingAttachments);
  const hadAttachments = pendingAttachments.length > 0;
  // Row 16 — thread the session-continuity target into the engine argv: a
  // 'continue' target emits --continue, a 'resume' target emits --resume <id>
  // (+ --fork-session when forking). A 'new' target yields nothing, so the
  // default drive starts a fresh session unchanged (the conservative default).
  const resumeArgs = resumeArgsFromTarget(resumeTarget);
  let reply;
  try {
    reply = await driveTurn(Object.assign({
      prompt,
      attachments,
      cwd: currentCwd(),
      // Row 9 — run under the human's chosen permission mode (the composer's
      // permission surface set it; defaults to the conservative 'default').
      permissionMode,
      spawn: spawnImpl || undefined,
      // Row 6 — stream the live partials to the composer as they arrive.
      onEvent: postTurnDelta,
      // Row 17 — capture the in-flight turn's interrupt handle so the composer's
      // Stop button can terminate THIS turn (the engine process).
      onStart: (handle) => { activeTurnControl = handle; },
    }, resumeArgs));
  } catch (err) {
    reply = {
      isError: true,
      subtype: 'spawn-error',
      entries: [],
      text: (err && err.message) || 'engine failed to start',
      cost: null,
    };
  } finally {
    // Row 17 — the turn has settled (replied, errored, timed out, or was
    // stopped); drop the interrupt handle so a later Stop is a no-op.
    activeTurnControl = null;
  }
  // Row 15 — the attachments rode this one turn; clear the staged set so they do
  // not ride the next. Re-render so the composer's tray empties (only when there
  // were chips to clear, so a plain turn does not trigger a needless repaint).
  if (hadAttachments) {
    pendingAttachments = [];
    renderPanel();
  }
  // Row 13 — record the LIVE tools the turn's init event reported (it names the
  // MCP tools the inherited env actually loaded, `mcp__server__tool`), so a
  // re-render annotates the configured servers with what is genuinely available
  // + invocable. A turn that reported no tools leaves the prior view untouched.
  if (Array.isArray(reply.tools)) {
    lastEngineTools = reply.tools;
    renderPanel(); // repaint so the MCP panel reflects the now-loaded servers
  }
  if (panel && panel.webview && typeof panel.webview.postMessage === 'function') {
    panel.webview.postMessage({
      type: 'ontum:turn-reply',
      html: renderTranscriptRows(reply.entries || []),
      isError: !!reply.isError,
      subtype: reply.subtype || '',
      cost: typeof reply.cost === 'number' ? reply.cost : null,
      sessionId: reply.sessionId || null,
    });
  }
  return reply;
}

// recordDiffDecision(msg) -> record a diff accept/reject the webview posted
// (row 8) and return it. Returns null for a malformed message. The decision is
// `{ toolId, decision:'accept'|'reject' }`; we keep only the latest so a
// host-free test can assert the round-trip. (Applying/reverting the edit on
// disk is the host permission flow's job — row 9 — not faked here.)
function recordDiffDecision(msg) {
  if (!msg || (msg.decision !== 'accept' && msg.decision !== 'reject')) {
    return null;
  }
  lastDiffDecision = {
    toolId: msg.toolId || '',
    decision: msg.decision,
  };
  return lastDiffDecision;
}

// recordPlanDecision(msg) -> record a plan-mode approve/keep the webview posted
// (row 11) and return it. Returns null for an unrecognised decision. The
// decision is `{ toolId, decision:'approve'|'keep' }`; on 'approve' the
// permission posture EXITS plan mode (transitions out of 'plan' to 'default' —
// conservative, never to acceptEdits/bypass) so the engine can proceed, on
// 'keep' it stays in 'plan'. We re-render so the surface reflects the in-force
// mode (the plan-mode banner clears on approve), and keep only the latest so a
// host-free test can assert the round-trip. Running the approved work is the
// engine's job under the exited mode — the surface drives the mode, not the work.
function recordPlanDecision(msg) {
  if (!msg || !isPlanDecision(msg.decision)) return null;
  permissionMode = nextModeOnPlanDecision(msg.decision, permissionMode);
  lastPlanDecision = {
    toolId: msg.toolId || '',
    decision: msg.decision,
    mode: permissionMode,
  };
  renderPanel(); // repaint in the now-in-force mode (no-op when no panel)
  return lastPlanDecision;
}

// setPermissionMode(msg) -> record the permission mode the webview's permission
// surface chose (row 9), normalized so an unknown/hostile value can never
// escalate past 'default'. Accepts either a raw mode string or the
// `{ type:'ontum:set-permission-mode', mode }` message. Returns the mode now in
// force. The NEXT turn's sendPrompt threads this into the engine argv
// (--permission-mode), so the turn actually runs under the human's choice.
function setPermissionMode(msg) {
  const raw = msg && typeof msg === 'object' ? msg.mode : msg;
  permissionMode = normalizePermissionMode(raw);
  return permissionMode;
}

// getPermissionMode() -> the permission mode the next turn will run under.
// Exposed so a host-free test can assert the row-9 mode round-trip.
function getPermissionMode() {
  return permissionMode;
}

// setResumeTarget(msg) -> record the session-continuity target the webview's
// resume control chose (row 16), normalized so an unknown mode / an id-less
// resume can never silently resume the wrong session (falls back to 'new').
// Accepts the `{ type:'ontum:set-resume', mode, id, fork }` message (or a bare
// target). A 'resume' with no explicit id defaults to the currently-selected
// session (row 2) — the "Resume selected" button. Re-renders so the control
// reflects the in-force target. Returns the target now in force; the NEXT
// turn's sendPrompt threads it into the engine argv (--continue / --resume).
function setResumeTarget(msg) {
  const m = msg && typeof msg === 'object' ? msg : { mode: msg };
  const mode = m.mode;
  // The resume control posts the chosen session id as `id`; when absent on a
  // 'resume' click, fall back to the currently-selected session (row 2).
  const sessionId =
    (typeof m.id === 'string' && m.id) ||
    (typeof m.sessionId === 'string' && m.sessionId) ||
    (mode === 'resume' ? selectedSessionId : null) ||
    null;
  resumeTarget = normalizeResumeTarget({ mode, sessionId, fork: m.fork === true });
  renderPanel(); // repaint so the control shows the now-in-force target
  return resumeTarget;
}

// getResumeTarget() -> the session-continuity target the next turn will run
// under (row 16). Exposed so a host-free test can assert the resume round-trip.
function getResumeTarget() {
  return resumeTarget;
}

// interruptTurn() -> stop the turn currently in flight (row 17). Calls the
// active turn's interrupt handle (driveTurn's onStart controller), which
// terminates the spawned engine process; the turn then settles with an honest
// interrupted reply (subtype 'interrupted') the existing turn-reply path
// renders. Returns true when a live turn was stopped, false when none was
// running (idempotent — a stray / late Stop click is a harmless no-op). The
// composer's Stop button posts ontum:interrupt-turn to drive this.
function interruptTurn() {
  if (!activeTurnControl || typeof activeTurnControl.interrupt !== 'function') {
    return false;
  }
  try {
    return activeTurnControl.interrupt() === true;
  } catch (_) {
    return false;
  }
}

// isTurnRunning() -> whether a turn is currently in flight (row 17). Exposed so
// a host-free test can assert the handle is held during a turn and dropped after.
function isTurnRunning() {
  return activeTurnControl != null;
}

// startTail() -> begin watching the selected session's file for appends. The
// full transcript was just painted by renderPanel, so we anchor the offset at
// the current end and only future appends stream in. fs.watchFile polls (works
// where inotify/ReadDirectoryChangesW are flaky, e.g. some network mounts).
function startTail() {
  stopTail();
  const file = selectedFile();
  if (!file) return;
  tailOffset = fileSize(file);
  try {
    fs.watchFile(file, { interval: 500 }, () => pumpTail());
    tailWatched = file;
  } catch (_) {
    tailWatched = null;
  }
}

// stopTail() -> stop watching the current file (selection change / panel close).
function stopTail() {
  if (tailWatched) {
    try {
      fs.unwatchFile(tailWatched);
    } catch (_) {
      /* best-effort */
    }
    tailWatched = null;
  }
}

// renderPanel() -> (re)paint the panel from the current store + selection. The
// engine's files are the only source; this folds them, it stores nothing.
function renderPanel() {
  if (!panel) return;
  panel.webview.html = renderShell({
    cspSource: panel.webview.cspSource,
    sessions: readSessions(),
    transcript: readSelectedTranscript(),
    // Row 9 — paint the composer's permission surface in its current mode so a
    // re-render preserves the human's choice.
    permissionMode,
    // Row 16 — paint the composer's session-continuity surface in its in-force
    // target (new / continue / resume), and pass the selected session id so the
    // "Resume selected" button points at it (and is disabled when none is).
    resumeTarget,
    selectedSessionId,
    // Row 10 — the discovered slash-command palette (project + user customs +
    // built-ins). The composer filters it as the human types a '/' prefix.
    slashCommands: readSlashCommands(),
    // Row 12 — the discovered @-mention palette (a bounded workspace file fold).
    // The composer filters it as the human types an '@' token.
    mentionTargets: readMentionTargets(),
    // Row 15 — the staged attachments (data-free tray views). The composer's
    // attach button + remove chips drive them; they ride the next turn as
    // content blocks ahead of the typed text.
    attachments: getAttachments(),
    // Row 13 — the discovered MCP servers (configured on disk) annotated with
    // the tools the live engine env exposed for them (`mcp__server__tool`).
    mcpServers: readMcpServers(),
    // Row 14 — the inherited environment (settings layers / hooks / skills),
    // folded from the same on-disk config the CLI reads.
    environment: readEnvironment(),
  });
}

function openSurface(context) {
  if (panel) {
    panel.reveal(panel.viewColumn || vscode.ViewColumn.One);
    return panel;
  }

  panel = vscode.window.createWebviewPanel(
    VIEW_TYPE,
    'ontum',
    vscode.ViewColumn.One,
    {
      enableScripts: true,
      retainContextWhenHidden: true,
      localResourceRoots: context && context.extensionUri ? [context.extensionUri] : [],
    }
  );

  renderPanel();

  // Row 2/3 — the webview tells us which session the user picked. We record it
  // and re-render so row 3 reads + paints that session's transcript. Other
  // messages are ignored.
  if (panel.webview && typeof panel.webview.onDidReceiveMessage === 'function') {
    panel.webview.onDidReceiveMessage((msg) => {
      if (msg && msg.type === 'ontum:select-session' && msg.id) {
        selectedSessionId = msg.id;
        renderPanel();
        // Row 4 — begin live-tailing the newly-selected session from its
        // current end, so future appends stream into the panel.
        startTail();
      } else if (msg && msg.type === 'ontum:send-prompt' && msg.text) {
        // Row 5 — drive a new turn through the inherited engine and post the
        // reply back to the composer.
        sendPrompt(msg.text);
      } else if (msg && msg.type === 'ontum:diff-decision') {
        // Row 8 — record an Accept/Reject the human made on a rendered diff.
        recordDiffDecision(msg);
      } else if (msg && msg.type === 'ontum:plan-decision') {
        // Row 11 — record an Approve/Keep on a plan card; approve exits plan mode.
        recordPlanDecision(msg);
      } else if (msg && msg.type === 'ontum:set-permission-mode') {
        // Row 9 — the human chose a permission mode; the next turn runs under it.
        setPermissionMode(msg);
      } else if (msg && msg.type === 'ontum:set-resume') {
        // Row 16 — the human chose new / continue / resume; the next turn joins
        // that session (--continue / --resume <id>).
        setResumeTarget(msg);
      } else if (msg && msg.type === 'ontum:attach-file') {
        // Row 15 — open the host file picker; stage + re-render the chosen files.
        pickAttachment();
      } else if (msg && msg.type === 'ontum:remove-attachment') {
        // Row 15 — drop a staged attachment the human removed; re-render the tray.
        if (removeAttachment(msg.name)) renderPanel();
      } else if (msg && msg.type === 'ontum:interrupt-turn') {
        // Row 17 — the human pressed Stop; terminate the in-flight engine turn.
        interruptTurn();
      }
    });
  }

  panel.onDidDispose(() => {
    stopTail();
    panel = null;
  });

  return panel;
}

function activate(context) {
  const disposable = vscode.commands.registerCommand(OPEN_COMMAND, () =>
    openSurface(context)
  );
  if (context && Array.isArray(context.subscriptions)) {
    context.subscriptions.push(disposable);
  }
  return { openSurface: () => openSurface(context) };
}

function deactivate() {
  stopTail();
  if (panel) {
    panel.dispose();
    panel = null;
  }
}

// getSelectedSessionId() -> the last session the webview selected (or null).
// Exposed so a host-free test can assert the row-2 selection round-trip.
function getSelectedSessionId() {
  return selectedSessionId;
}

// getLastDiffDecision() -> the last Accept/Reject the webview posted on a
// rendered diff (or null). Exposed so a host-free test can assert the row-8
// decision round-trip.
function getLastDiffDecision() {
  return lastDiffDecision;
}

// getLastPlanDecision() -> the last Approve/Keep the webview posted on a
// rendered plan card (or null). Exposed so a host-free test can assert the
// row-11 decision round-trip + the exit-plan-mode mode transition.
function getLastPlanDecision() {
  return lastPlanDecision;
}

// __setSpawnForTest(fn) -> inject the engine spawn (row 5). A host-free test
// passes a fake process so the send→reply round-trip is proven without a real
// billed model call; pass null to restore the production default.
function __setSpawnForTest(fn) {
  spawnImpl = fn || null;
}

// __setSelectionForTest(fn) -> inject the IDE selection reader (row 12). A
// host-free test passes a function returning a fake selection record (or null)
// so the "the driven turn carried the editor selection as context" round-trip
// is proven without a VS Code host; pass null to restore the production reader
// (vscode.window.activeTextEditor).
function __setSelectionForTest(fn) {
  selectionImpl = fn || null;
}

// __setAttachPickerForTest(fn) -> inject the attach file picker (row 15). A
// host-free test passes a function returning the chosen path(s) so the "the
// attachment rode the turn as a content block" round-trip is proven without a
// VS Code host dialog; pass null to restore the production picker
// (vscode.window.showOpenDialog).
function __setAttachPickerForTest(fn) {
  attachPickerImpl = fn || null;
}

module.exports = {
  activate,
  deactivate,
  getSelectedSessionId,
  // Row 10 — exposed so a host-free test can assert the slash-command palette
  // discovery (project + user customs + built-ins) the surface offers.
  readSlashCommands,
  // Row 12 — exposed so a host-free test can assert the @-mention palette
  // discovery (the bounded workspace file fold) the surface offers.
  readMentionTargets,
  // Row 13 — exposed so a host-free test can assert the MCP-server surface
  // discovery (configured servers annotated with the live tools the inherited
  // env exposed) the surface offers.
  readMcpServers,
  // Row 14 — exposed so a host-free test can assert the inherited-environment
  // surface discovery (settings layers + hooks + skills folded from the same
  // on-disk config the CLI reads) the surface offers.
  readEnvironment,
  // Row 4 — exposed so a host-free test can drive a tail pump directly (the
  // watcher's poll is timing-bound; the pump is the deterministic seam).
  pumpTail,
  stopTail,
  // Row 5 — exposed so a host-free test can drive a turn directly (with an
  // injected fake engine) and assert the posted reply.
  sendPrompt,
  // Row 6 — exposed so a host-free test can assert one event folds to one
  // posted `ontum:turn-delta` (and non-partials post nothing).
  postTurnDelta,
  // Row 8 — exposed so a host-free test can drive + assert the diff
  // accept/reject decision round-trip.
  recordDiffDecision,
  getLastDiffDecision,
  // Row 11 — exposed so a host-free test can drive + assert the plan-mode
  // approve/keep decision round-trip (and the exit-plan-mode transition).
  recordPlanDecision,
  getLastPlanDecision,
  // Row 9 — exposed so a host-free test can drive + assert the permission-mode
  // round-trip (the webview's permission surface → the next turn's argv).
  setPermissionMode,
  getPermissionMode,
  // Row 16 — exposed so a host-free test can drive + assert the session-
  // continuity round-trip (the webview's resume control → the next turn's argv:
  // --continue / --resume <id>).
  setResumeTarget,
  getResumeTarget,
  __setSpawnForTest,
  // Row 12 — exposed so a host-free test can inject a fake editor selection and
  // assert the driven turn carried it as context (the selection-context surface).
  __setSelectionForTest,
  // Row 15 — exposed so a host-free test can drive + assert the image/file
  // attach round-trip (stage a file → it rides the next turn as a content block
  // ahead of the typed text → the staged set clears after send).
  addAttachment,
  removeAttachment,
  getAttachments,
  pickAttachment,
  __setAttachPickerForTest,
  // Row 17 — exposed so a host-free test can assert the stop/interrupt round-trip
  // (a turn in flight holds the control handle; Stop terminates it and the turn
  // settles as an honest interrupted reply; a late Stop is a no-op).
  interruptTurn,
  isTurnRunning,
  VIEW_TYPE,
  OPEN_COMMAND,
};

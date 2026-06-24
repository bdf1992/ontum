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
const vscode = require('vscode');
const { renderShell, renderTranscriptRows } = require('./shell');
const { listSessions, storeDirFor } = require('./sessions');
const { readTranscript, fileForSession } = require('./transcript');
const { tailTranscript } = require('./livetail');
const { driveTurn, partialDelta } = require('./engine');

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
// Row 5 — the engine spawn used to drive a turn. Null in production (driveTurn
// falls back to the real child_process.spawn); a host-free test injects a fake
// process via __setSpawnForTest so the send→reply round-trip is proven without a
// real billed model call.
let spawnImpl = null;

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
  const prompt = String(text == null ? '' : text).trim();
  if (!prompt || !panel) return null;
  let reply;
  try {
    reply = await driveTurn({
      prompt,
      cwd: currentCwd(),
      permissionMode: 'default',
      spawn: spawnImpl || undefined,
      // Row 6 — stream the live partials to the composer as they arrive.
      onEvent: postTurnDelta,
    });
  } catch (err) {
    reply = {
      isError: true,
      subtype: 'spawn-error',
      entries: [],
      text: (err && err.message) || 'engine failed to start',
      cost: null,
    };
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

// __setSpawnForTest(fn) -> inject the engine spawn (row 5). A host-free test
// passes a fake process so the send→reply round-trip is proven without a real
// billed model call; pass null to restore the production default.
function __setSpawnForTest(fn) {
  spawnImpl = fn || null;
}

module.exports = {
  activate,
  deactivate,
  getSelectedSessionId,
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
  __setSpawnForTest,
  VIEW_TYPE,
  OPEN_COMMAND,
};

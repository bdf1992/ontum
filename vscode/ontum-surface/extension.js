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

module.exports = {
  activate,
  deactivate,
  getSelectedSessionId,
  // Row 4 — exposed so a host-free test can drive a tail pump directly (the
  // watcher's poll is timing-bound; the pump is the deterministic seam).
  pumpTail,
  stopTail,
  VIEW_TYPE,
  OPEN_COMMAND,
};

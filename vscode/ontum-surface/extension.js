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

const vscode = require('vscode');
const { renderShell } = require('./shell');
const { listSessions, storeDirFor } = require('./sessions');

const VIEW_TYPE = 'ontum.surface';
const OPEN_COMMAND = 'ontum.surface.open';

// One panel per window — re-running the command reveals the existing one
// rather than stacking duplicates.
let panel = null;
// The session the user last selected (row 2). Row 3 reads its transcript.
let selectedSessionId = null;

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

  panel.webview.html = renderShell({
    cspSource: panel.webview.cspSource,
    sessions: readSessions(),
  });

  // Row 2 — the webview tells us which session the user picked. We record it
  // (row 3 will read + render that transcript). Other messages are ignored.
  if (panel.webview && typeof panel.webview.onDidReceiveMessage === 'function') {
    panel.webview.onDidReceiveMessage((msg) => {
      if (msg && msg.type === 'ontum:select-session' && msg.id) {
        selectedSessionId = msg.id;
      }
    });
  }

  panel.onDidDispose(() => {
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
  VIEW_TYPE,
  OPEN_COMMAND,
};

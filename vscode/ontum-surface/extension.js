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

const VIEW_TYPE = 'ontum.surface';
const OPEN_COMMAND = 'ontum.surface.open';

// One panel per window — re-running the command reveals the existing one
// rather than stacking duplicates.
let panel = null;

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
  });

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

module.exports = { activate, deactivate, VIEW_TYPE, OPEN_COMMAND };

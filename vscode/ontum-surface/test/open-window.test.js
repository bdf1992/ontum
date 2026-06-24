// open-window.test.js — proof for parity-checklist row 1.
//
// "Open a branded ontum window (webview), standalone of the official panel."
//
// There is no VS Code host here (an overnight `node` tick), so we inject a
// minimal fake `vscode` module and assert the code path that a real host would
// run: activating registers the open command, invoking it asks the host to
// create a webview panel, and the panel is dressed in branded, standalone HTML
// (the shell). This is honest evidence: it proves the window-opening code and
// the branded markup, NOT that VS Code pixels rendered (that needs a host).
//
// Run: node vscode/ontum-surface/test/open-window.test.js
// Exit 0 = all assertions passed; non-zero = a failure (the message says which).

'use strict';

const assert = require('assert');
const path = require('path');
const Module = require('module');

// ---- a minimal fake `vscode` ------------------------------------------------
const created = []; // every createWebviewPanel call, captured for assertions
const registered = {}; // commandId -> callback

const fakeVscode = {
  ViewColumn: { One: 1 },
  window: {
    createWebviewPanel(viewType, title, viewColumn, options) {
      const panel = {
        viewType,
        title,
        viewColumn,
        options,
        webview: { cspSource: 'vscode-resource://fake', html: '' },
        _disposed: false,
        _onDispose: null,
        reveal() {
          this._revealed = true;
        },
        onDidDispose(cb) {
          this._onDispose = cb;
        },
        dispose() {
          this._disposed = true;
          if (this._onDispose) this._onDispose();
        },
      };
      created.push(panel);
      return panel;
    },
  },
  commands: {
    registerCommand(id, cb) {
      registered[id] = cb;
      return { dispose() {} };
    },
  },
};

// Inject the fake into the module loader so `require('vscode')` resolves to it.
const origLoad = Module._load;
Module._load = function (request, parent, isMain) {
  if (request === 'vscode') return fakeVscode;
  return origLoad.call(this, request, parent, isMain);
};

// ---- load the extension under test -----------------------------------------
const ext = require(path.join(__dirname, '..', 'extension.js'));
const { renderShell } = require(path.join(__dirname, '..', 'shell.js'));

let passed = 0;
function check(label, fn) {
  fn();
  passed++;
  console.log('  ok  ' + label);
}

console.log('row 1 — branded standalone ontum window');

// 1. Activation registers the open command.
const fakeContext = { subscriptions: [], extensionUri: { fsPath: __dirname } };
ext.activate(fakeContext);
check('activate registers the ontum.surface.open command', () => {
  assert.strictEqual(typeof registered[ext.OPEN_COMMAND], 'function');
  assert.strictEqual(ext.OPEN_COMMAND, 'ontum.surface.open');
  assert.ok(
    fakeContext.subscriptions.length >= 1,
    'the command disposable is tracked for cleanup'
  );
});

// 2. Invoking the command opens exactly one webview panel.
registered[ext.OPEN_COMMAND]();
check('invoking the command creates one webview panel', () => {
  assert.strictEqual(created.length, 1, 'exactly one panel created');
  assert.strictEqual(created[0].viewType, ext.VIEW_TYPE);
  assert.strictEqual(created[0].viewType, 'ontum.surface');
  assert.strictEqual(created[0].options.enableScripts, true);
});

// 3. The panel's HTML is branded and standalone.
const html = created[0].webview.html;
check('panel html is branded ontum and self-declares standalone', () => {
  assert.ok(html.length > 0, 'html is non-empty');
  assert.ok(
    /data-surface="ontum"/.test(html),
    'document is tagged as the ontum surface'
  );
  assert.ok(
    /data-standalone="true"/.test(html),
    'document self-declares standalone'
  );
  assert.ok(/ontum/i.test(html), 'the ontum wordmark is present');
});

// 4. Standalone really means standalone: no dependency on the official panel.
check('html names no dependency on the official Claude Code panel', () => {
  assert.ok(
    !/claude-code/i.test(html),
    'no reference to the claude-code panel'
  );
  assert.ok(
    !/anthropic\./i.test(html),
    'no reference to an official anthropic resource'
  );
});

// 5. The webview carries a Content-Security-Policy with a nonce-gated script.
check('html carries a CSP whose scripts are nonce-gated', () => {
  assert.ok(
    /Content-Security-Policy/.test(html),
    'a CSP meta tag is present'
  );
  const m = html.match(/script-src 'nonce-([A-Za-z0-9]+)'/);
  assert.ok(m, 'script-src is nonce-gated');
  assert.ok(m[1].length >= 16, 'the nonce is non-trivial');
});

// 6. Re-invoking reveals the existing panel rather than stacking a second.
registered[ext.OPEN_COMMAND]();
check('re-invoking reveals the existing panel (no duplicate)', () => {
  assert.strictEqual(created.length, 1, 'still exactly one panel');
  assert.strictEqual(created[0]._revealed, true, 'the existing panel was revealed');
});

// 7. The pure shell honours an explicit brand override (future culture layer).
check('renderShell honours a brand override', () => {
  const out = renderShell({ brand: 'ontum', cspSource: 'x' });
  assert.ok(/<title>ontum — surface<\/title>/.test(out));
});

console.log('\n' + passed + ' checks passed — row 1 evidence is green.');
process.exit(0);

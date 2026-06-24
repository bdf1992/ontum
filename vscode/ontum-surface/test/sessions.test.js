// sessions.test.js — proof for parity-checklist row 2.
//
// "List local sessions from the transcript store; select one."
//
// There is no VS Code host and we do not touch the user's real store. The test
// builds a *fake* transcript store in a temp dir (the same newline-delimited
// JSON shape the engine writes, observed in SPIKE-FINDINGS.md — including a
// torn final line, the live-tail case), then asserts:
//   - sessions.listSessions reads + summarizes them, newest-first;
//   - the torn tail is tolerated, not fatal;
//   - shell.renderSessionList paints them as selectable, escaped buttons;
//   - the extension records a selection posted from the webview (the round-trip).
// Honest evidence: it proves the read + render + select code, NOT VS Code pixels.
//
// Run: node vscode/ontum-surface/test/sessions.test.js
// Exit 0 = all assertions passed; non-zero = a failure (the message says which).

'use strict';

const assert = require('assert');
const fs = require('fs');
const os = require('os');
const path = require('path');
const Module = require('module');

let passed = 0;
function check(label, fn) {
  fn();
  passed++;
  console.log('  ok  ' + label);
}

// ---- build a fake transcript store -----------------------------------------
const tmpRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'ontum-store-'));
const storeDir = path.join(tmpRoot, 'C--Users-fake-proj');
fs.mkdirSync(storeDir, { recursive: true });

// Session A — older. First user turn is a string; one assistant turn (blocks).
const sessA = [
  JSON.stringify({
    sessionId: 'aaaa-1111',
    cwd: 'C:\\Users\\fake\\proj',
    gitBranch: 'main',
    type: 'user',
    message: { role: 'user', content: 'Build the <thing> & ship it' },
    timestamp: '2026-06-24T01:00:00.000Z',
  }),
  JSON.stringify({
    sessionId: 'aaaa-1111',
    type: 'assistant',
    message: { role: 'assistant', content: [{ type: 'text', text: 'On it.' }] },
    timestamp: '2026-06-24T01:00:05.000Z',
  }),
].join('\n') + '\n';

// Session B — newer (written second so a higher mtime). First line is a
// non-turn system record (must NOT become the title), then a user turn, then a
// TORN final line (half-written JSON — the live-tail case).
const sessB =
  JSON.stringify({
    sessionId: 'bbbb-2222',
    cwd: 'C:\\Users\\fake\\proj',
    gitBranch: 'claude/feature',
    type: 'system',
    subtype: 'informational',
    content: 'hook noise',
    timestamp: '2026-06-24T02:00:00.000Z',
  }) +
  '\n' +
  JSON.stringify({
    sessionId: 'bbbb-2222',
    type: 'user',
    message: { role: 'user', content: 'Second session prompt' },
    timestamp: '2026-06-24T02:00:01.000Z',
  }) +
  '\n' +
  '{"sessionId":"bbbb-2222","type":"assist'; // torn — no trailing newline

fs.writeFileSync(path.join(storeDir, 'aaaa-1111.jsonl'), sessA);
// Ensure B is strictly newer than A by mtime (sorting is mtime-based).
const future = Date.now() + 5000;
fs.writeFileSync(path.join(storeDir, 'bbbb-2222.jsonl'), sessB);
fs.utimesSync(
  path.join(storeDir, 'aaaa-1111.jsonl'),
  new Date(future - 10000),
  new Date(future - 10000)
);
fs.utimesSync(
  path.join(storeDir, 'bbbb-2222.jsonl'),
  new Date(future),
  new Date(future)
);
// A non-jsonl file must be ignored.
fs.writeFileSync(path.join(storeDir, 'notes.txt'), 'ignore me');

// ---- load the modules under test -------------------------------------------
const sessions = require(path.join(__dirname, '..', 'sessions.js'));
const { renderSessionList } = require(path.join(__dirname, '..', 'shell.js'));

console.log('row 2 — list local sessions + select one');

// 1. The store-path encoding matches the engine's observed convention.
check('encodeProjectDir maps a real cwd the way the engine does', () => {
  assert.strictEqual(
    sessions.encodeProjectDir('C:\\Users\\bdf19\\ontum-overnight'),
    'C--Users-bdf19-ontum-overnight'
  );
  assert.ok(
    sessions
      .storeDirFor('C:\\Users\\bdf19\\ontum-overnight', '/home/x')
      .replace(/\\/g, '/')
      .endsWith('.claude/projects/C--Users-bdf19-ontum-overnight')
  );
});

// 2. listSessions reads both sessions, newest (B) first.
const list = sessions.listSessions({ dir: storeDir });
check('listSessions returns both .jsonl sessions, newest-first', () => {
  assert.strictEqual(list.length, 2, 'two sessions (the .txt is ignored)');
  assert.strictEqual(list[0].id, 'bbbb-2222', 'newest by mtime is first');
  assert.strictEqual(list[1].id, 'aaaa-1111');
});

// 3. Metadata is derived from the records (title = first USER turn, not system).
check('session metadata is summarized from the records', () => {
  assert.strictEqual(
    list[0].title,
    'Second session prompt',
    'title skips the leading system record, uses the first user turn'
  );
  assert.strictEqual(list[0].gitBranch, 'claude/feature');
  assert.strictEqual(list[1].title, 'Build the <thing> & ship it');
  assert.strictEqual(list[1].messageCount, 2, 'user + assistant counted');
});

// 4. A torn final line is tolerated: the good lines still parse.
check('a torn final line is tolerated, not fatal', () => {
  assert.strictEqual(list[0].torn, 1, 'the half-written line is counted');
  assert.ok(list[0].messageCount >= 1, 'the good lines before it still parsed');
});

// 5. A missing store yields an honest empty list (no throw).
check('a missing store directory yields []', () => {
  const empty = sessions.listSessions({ dir: path.join(tmpRoot, 'nope') });
  assert.deepStrictEqual(empty, []);
});

// 6. renderSessionList paints selectable, HTML-escaped buttons.
check('renderSessionList paints selectable, escaped session buttons', () => {
  const html = renderSessionList(list);
  assert.ok(/data-count="2"/.test(html), 'the list declares its count');
  assert.ok(
    /data-session-id="bbbb-2222"/.test(html),
    'each session carries its id for selection'
  );
  assert.ok(
    /<button class="ontum-session"/.test(html),
    'sessions are rendered as buttons (selectable)'
  );
  assert.ok(
    /Build the &lt;thing&gt; &amp; ship it/.test(html),
    'the title is HTML-escaped (no injection)'
  );
  assert.ok(!/<thing>/.test(html), 'raw angle brackets did not leak');
});

// 7. An empty list paints an honest empty note, not a fake row.
check('renderSessionList on [] paints an honest empty note', () => {
  const html = renderSessionList([]);
  assert.ok(/ontum-empty/.test(html), 'empty-state class present');
  assert.ok(!/ontum-session-list/.test(html), 'no fake list rendered');
});

// 8. The extension records a selection posted from the webview (round-trip).
//    Inject a fake `vscode` that captures the onDidReceiveMessage handler so we
//    can drive a select-session message through it, as the webview script would.
(function selectionRoundTrip() {
  let messageHandler = null;
  const registered = {};
  const fakeVscode = {
    ViewColumn: { One: 1 },
    workspace: { workspaceFolders: [{ uri: { fsPath: storeDir } }] },
    window: {
      createWebviewPanel() {
        return {
          viewType: 'ontum.surface',
          webview: {
            cspSource: 'vscode-resource://fake',
            html: '',
            onDidReceiveMessage(cb) {
              messageHandler = cb;
            },
          },
          reveal() {},
          onDidDispose() {},
          dispose() {},
        };
      },
    },
    commands: {
      registerCommand(id, cb) {
        registered[id] = cb;
        return { dispose() {} };
      },
    },
  };
  const origLoad = Module._load;
  Module._load = function (request, parent, isMain) {
    if (request === 'vscode') return fakeVscode;
    return origLoad.call(this, request, parent, isMain);
  };
  // Fresh require of the extension so it binds to the fake vscode.
  delete require.cache[require.resolve(path.join(__dirname, '..', 'extension.js'))];
  const ext = require(path.join(__dirname, '..', 'extension.js'));
  Module._load = origLoad;

  ext.activate({ subscriptions: [], extensionUri: { fsPath: __dirname } });
  registered[ext.OPEN_COMMAND](); // open the panel -> wires the message handler

  check('selecting a session round-trips through the host', () => {
    assert.strictEqual(typeof messageHandler, 'function', 'handler was wired');
    assert.strictEqual(ext.getSelectedSessionId(), null, 'nothing selected yet');
    messageHandler({ type: 'ontum:select-session', id: 'bbbb-2222' });
    assert.strictEqual(
      ext.getSelectedSessionId(),
      'bbbb-2222',
      'the host recorded the selection'
    );
    // Unrelated messages do not change the selection.
    messageHandler({ type: 'ontum:surface-ready' });
    assert.strictEqual(ext.getSelectedSessionId(), 'bbbb-2222');
  });
})();

// ---- cleanup ----------------------------------------------------------------
try {
  fs.rmSync(tmpRoot, { recursive: true, force: true });
} catch (_) {
  /* best-effort temp cleanup */
}

console.log('\n' + passed + ' checks passed — row 2 evidence is green.');
process.exit(0);

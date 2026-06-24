// transcript.test.js — proof for parity-checklist row 3.
//
// "Read + render a transcript (user / assistant / tool-use / tool-result)."
//
// There is no VS Code host and we do not touch the user's real store. The test
// writes a *fake* transcript file (the same newline-delimited JSON the engine
// writes, observed in SPIKE-FINDINGS.md / the live store — user string, an
// assistant turn with thinking + text, an assistant tool_use, a user turn
// carrying a tool_result, plus a TORN final line for the live-tail case), then
// asserts:
//   - transcript.readTranscript folds it into ordered entries of every kind;
//   - the torn tail is tolerated, not fatal;
//   - non-turn (system) records and empty blocks produce no rendered entry;
//   - shell.renderTranscript paints each kind as an escaped, labelled block;
//   - selecting a session in the extension re-renders the panel with that
//     session's transcript (the row-2 -> row-3 round-trip).
// Honest evidence: it proves the read + fold + render code, NOT VS Code pixels.
//
// Run: node vscode/ontum-surface/test/transcript.test.js
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

// ---- build a fake one-session transcript store -----------------------------
const tmpRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'ontum-tx-'));
const storeDir = path.join(tmpRoot, 'C--Users-fake-proj');
fs.mkdirSync(storeDir, { recursive: true });

const SID = 'cccc-3333';
const lines = [
  // A leading non-turn system record — must produce NO rendered entry.
  JSON.stringify({
    sessionId: SID,
    type: 'system',
    subtype: 'informational',
    content: 'hook noise',
    timestamp: '2026-06-24T03:00:00.000Z',
  }),
  // User turn — a plain string with angle brackets/ampersand to test escaping.
  JSON.stringify({
    sessionId: SID,
    type: 'user',
    message: { role: 'user', content: 'Render <b>this</b> & that' },
    timestamp: '2026-06-24T03:00:01.000Z',
  }),
  // Assistant turn — thinking + text + an EMPTY text block (the empty one must
  // be dropped, not rendered as a blank bubble).
  JSON.stringify({
    sessionId: SID,
    type: 'assistant',
    message: {
      role: 'assistant',
      content: [
        { type: 'thinking', thinking: 'let me plan', signature: 'sig' },
        { type: 'text', text: 'Here is the plan.' },
        { type: 'text', text: '   ' },
      ],
    },
    timestamp: '2026-06-24T03:00:02.000Z',
  }),
  // Assistant turn — a tool_use block (name + structured input).
  JSON.stringify({
    sessionId: SID,
    type: 'assistant',
    message: {
      role: 'assistant',
      content: [
        {
          type: 'tool_use',
          id: 'toolu_1',
          name: 'Read',
          input: { file_path: 'C:/x/y.txt' },
        },
      ],
    },
    timestamp: '2026-06-24T03:00:03.000Z',
  }),
  // User turn — a tool_result for that call, content as an array of text blocks.
  JSON.stringify({
    sessionId: SID,
    type: 'user',
    message: {
      role: 'user',
      content: [
        {
          type: 'tool_result',
          tool_use_id: 'toolu_1',
          content: [{ type: 'text', text: 'file body line 1' }],
        },
      ],
    },
    timestamp: '2026-06-24T03:00:04.000Z',
  }),
  // User turn — an ERROR tool_result, content as a plain string.
  JSON.stringify({
    sessionId: SID,
    type: 'user',
    message: {
      role: 'user',
      content: [
        {
          type: 'tool_result',
          tool_use_id: 'toolu_1',
          is_error: true,
          content: 'ENOENT: no such file',
        },
      ],
    },
    timestamp: '2026-06-24T03:00:05.000Z',
  }),
].join('\n');
// Append a TORN final line (half-written JSON — the live-tail case).
const fileText = lines + '\n{"sessionId":"cccc-3333","type":"assist';
fs.writeFileSync(path.join(storeDir, SID + '.jsonl'), fileText);

// ---- load the modules under test -------------------------------------------
const transcript = require(path.join(__dirname, '..', 'transcript.js'));
const { renderTranscript } = require(path.join(__dirname, '..', 'shell.js'));

console.log('row 3 — read + render a transcript');

// 1. fileForSession composes the expected store path.
check('fileForSession composes <dir>/<id>.jsonl', () => {
  assert.strictEqual(
    transcript.fileForSession(storeDir, SID).replace(/\\/g, '/'),
    (storeDir + '/' + SID + '.jsonl').replace(/\\/g, '/')
  );
});

// 2. readTranscript folds every kind, in order, dropping non-turns/empties.
const { entries, torn } = transcript.readTranscript({
  file: transcript.fileForSession(storeDir, SID),
});
check('readTranscript folds the turns into ordered entries', () => {
  const kinds = entries.map((e) => e.kind);
  assert.deepStrictEqual(
    kinds,
    [
      'user-text',
      'assistant-thinking',
      'assistant-text',
      'tool-use',
      'tool-result',
      'tool-result',
    ],
    'order preserved; system record + empty text block produced no entry'
  );
});

// 3. Each kind carries the right payload, derived from the records.
check('each entry carries the payload folded from its block', () => {
  const byKind = {};
  for (const e of entries) (byKind[e.kind] = byKind[e.kind] || []).push(e);
  assert.strictEqual(byKind['user-text'][0].text, 'Render <b>this</b> & that');
  assert.strictEqual(byKind['assistant-thinking'][0].text, 'let me plan');
  assert.strictEqual(byKind['assistant-text'][0].text, 'Here is the plan.');
  assert.strictEqual(byKind['tool-use'][0].name, 'Read');
  assert.deepStrictEqual(byKind['tool-use'][0].input, { file_path: 'C:/x/y.txt' });
  assert.strictEqual(byKind['tool-result'][0].text, 'file body line 1');
  assert.strictEqual(byKind['tool-result'][0].isError, false);
  assert.strictEqual(byKind['tool-result'][1].text, 'ENOENT: no such file');
  assert.strictEqual(byKind['tool-result'][1].isError, true);
});

// 4. The torn final line is tolerated: the good turns above still folded.
check('a torn final line is tolerated, not fatal', () => {
  assert.strictEqual(torn, 1, 'the half-written line is counted');
  assert.ok(entries.length >= 6, 'the good turns before it still folded');
});

// 5. A missing file yields an honest empty transcript (no throw).
check('a missing transcript file yields { entries: [], torn: 0 }', () => {
  const empty = transcript.readTranscript({
    file: path.join(storeDir, 'nope.jsonl'),
  });
  assert.deepStrictEqual(empty, { entries: [], torn: 0 });
});

// 6. renderTranscript paints each kind as an escaped, labelled block.
check('renderTranscript paints escaped, labelled, kind-tagged blocks', () => {
  const html = renderTranscript(entries);
  assert.ok(/data-count="6"/.test(html), 'declares its entry count');
  assert.ok(/data-kind="user-text"/.test(html), 'user text block present');
  assert.ok(/data-kind="assistant-thinking"/.test(html), 'thinking block present');
  assert.ok(/data-kind="assistant-text"/.test(html), 'assistant text present');
  assert.ok(/data-kind="tool-use"/.test(html), 'tool-use block present');
  assert.ok(/data-kind="tool-result"/.test(html), 'tool-result block present');
  assert.ok(/data-error="true"/.test(html), 'the error result is flagged');
  // The tool name + its JSON input are shown.
  assert.ok(/tool &#9656; Read/.test(html), 'tool name rendered');
  assert.ok(/&quot;file_path&quot;/.test(html), 'tool input JSON rendered');
  // Escaping: the raw user markup must not leak as live tags.
  assert.ok(
    /Render &lt;b&gt;this&lt;\/b&gt; &amp; that/.test(html),
    'user text is HTML-escaped'
  );
  assert.ok(!/<b>this<\/b>/.test(html), 'raw tags did not leak');
});

// 7. An empty transcript paints an honest empty note, not a fake turn.
check('renderTranscript on [] paints an honest empty note', () => {
  const html = renderTranscript([]);
  assert.ok(/ontum-empty/.test(html), 'empty-state class present');
  assert.ok(!/ontum-transcript-list/.test(html), 'no fake list rendered');
});

// 8. Selecting a session re-renders the panel with that transcript (row 2->3).
//    Inject a fake `vscode`, capture the panel + the message handler, open the
//    panel, then drive a select-session message and assert the new HTML carries
//    the transcript markup.
(function selectionRendersTranscript() {
  let messageHandler = null;
  let capturedPanel = null;
  const registered = {};
  const fakeVscode = {
    ViewColumn: { One: 1 },
    workspace: { workspaceFolders: [{ uri: { fsPath: 'IGNORED' } }] },
    window: {
      createWebviewPanel() {
        capturedPanel = {
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
        return capturedPanel;
      },
    },
    commands: {
      registerCommand(id, cb) {
        registered[id] = cb;
        return { dispose() {} };
      },
    },
  };
  // Point the store lookup at our fake store regardless of cwd: override
  // storeDirFor via the sessions module the extension requires. Simpler: the
  // extension keys off currentCwd()->storeDirFor(home). We instead stub the
  // module's storeDirFor by intercepting require of './sessions' and
  // './transcript' is fine as-is. The cleanest host-free seam is to force the
  // workspace cwd to the parent of storeDir and let encodeProjectDir match.
  // Since storeDir is named 'C--Users-fake-proj', set cwd to that decoded path
  // so storeDirFor(cwd, home) lands on it.
  const origLoad = Module._load;
  Module._load = function (request, parent, isMain) {
    if (request === 'vscode') return fakeVscode;
    if (request === './sessions') {
      const real = origLoad.call(this, request, parent, isMain);
      return Object.assign({}, real, {
        storeDirFor() {
          return storeDir;
        },
      });
    }
    return origLoad.call(this, request, parent, isMain);
  };
  delete require.cache[require.resolve(path.join(__dirname, '..', 'extension.js'))];
  delete require.cache[require.resolve(path.join(__dirname, '..', 'sessions.js'))];
  delete require.cache[require.resolve(path.join(__dirname, '..', 'transcript.js'))];
  const ext = require(path.join(__dirname, '..', 'extension.js'));
  Module._load = origLoad;

  ext.activate({ subscriptions: [], extensionUri: { fsPath: __dirname } });
  registered[ext.OPEN_COMMAND](); // open the panel -> initial render + wiring

  check('opening paints the "pick a session" note (nothing selected yet)', () => {
    assert.strictEqual(typeof messageHandler, 'function', 'handler was wired');
    assert.ok(
      /Pick a session on the left/.test(capturedPanel.webview.html),
      'initial transcript region is the honest pick-a-session note'
    );
    assert.ok(
      !/class="ontum-transcript-list"/.test(capturedPanel.webview.html),
      'no transcript rendered before a selection (CSS rule aside)'
    );
  });

  check('selecting a session re-renders with its transcript', () => {
    messageHandler({ type: 'ontum:select-session', id: SID });
    const html = capturedPanel.webview.html;
    assert.ok(
      /class="ontum-transcript-list"/.test(html),
      'the selected session transcript is now rendered'
    );
    assert.ok(/data-kind="user-text"/.test(html), 'user turn painted');
    assert.ok(/data-kind="tool-use"/.test(html), 'tool-use painted');
    assert.ok(/tool &#9656; Read/.test(html), 'the real tool name came through');
  });
})();

// ---- cleanup ----------------------------------------------------------------
try {
  fs.rmSync(tmpRoot, { recursive: true, force: true });
} catch (_) {
  /* best-effort temp cleanup */
}

console.log('\n' + passed + ' checks passed — row 3 evidence is green.');
process.exit(0);

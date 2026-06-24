// livetail.test.js — proof for parity-checklist row 4.
//
// "Live-tail the active session as it appends."
//
// There is no VS Code host and we never touch the user's real store. The test
// writes a *fake* session file (the same newline-delimited JSON the engine
// writes), then exercises the tail as the engine would grow it — appending
// records, a TORN partial line, then its completion — and asserts:
//   - tailTranscript folds ONLY the bytes completed since the held offset into
//     ordered entries, and advances the offset past complete lines only;
//   - a partial (un-terminated) final line is NOT consumed: zero new entries,
//     the offset is held, and once the line is completed it folds in cleanly;
//   - a re-read with no growth yields nothing (idempotent at the tail);
//   - a truncated/rotated file (offset past EOF) resets to the top;
//   - activeSession picks the newest file in the store (the one being written);
//   - the extension wiring streams a real append to the webview: opening +
//     selecting a session anchors the tail at end (no replay of history), and a
//     subsequent append makes pumpTail post an `ontum:append-entries` message
//     carrying ONLY the new entry's rendered block;
//   - shell.renderTranscriptRows paints the append fragment WITHOUT the list
//     wrapper, and the shell document carries the live-append handler.
// Honest evidence: it proves the tail/fold/append code, NOT VS Code pixels.
//
// Run: node vscode/ontum-surface/test/livetail.test.js
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

// A record line exactly as the engine writes one (newline-terminated JSON).
function rec(obj) {
  return JSON.stringify(obj) + '\n';
}

// ---- build a fake one-session transcript store -----------------------------
const tmpRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'ontum-tail-'));
const storeDir = path.join(tmpRoot, 'C--Users-fake-proj');
fs.mkdirSync(storeDir, { recursive: true });

const SID = 'tail-9999';
const file = path.join(storeDir, SID + '.jsonl');

// Seed: a non-turn system record + one user turn. (mtime back-dated so a second
// session can be made unambiguously newer for the activeSession check.)
const seed =
  rec({
    sessionId: SID,
    type: 'system',
    subtype: 'informational',
    content: 'hook noise',
    timestamp: '2026-06-24T05:00:00.000Z',
  }) +
  rec({
    sessionId: SID,
    type: 'user',
    message: { role: 'user', content: 'first prompt' },
    timestamp: '2026-06-24T05:00:01.000Z',
  });
fs.writeFileSync(file, seed);

const livetail = require(path.join(__dirname, '..', 'livetail.js'));
const shell = require(path.join(__dirname, '..', 'shell.js'));

console.log('row 4 — live-tail the active session as it appends');

// 1. A first tail from 0 folds the seeded turns and advances to EOF.
let off = 0;
check('tail from 0 folds the seeded turns and advances offset to EOF', () => {
  const res = livetail.tailTranscript({ file, fromOffset: off });
  assert.deepStrictEqual(
    res.entries.map((e) => e.kind),
    ['user-text'],
    'system record produced no entry; the user turn did'
  );
  assert.strictEqual(res.entries[0].text, 'first prompt');
  assert.strictEqual(res.torn, 0, 'no torn complete lines');
  assert.strictEqual(res.reset, false);
  assert.strictEqual(
    res.nextOffset,
    Buffer.byteLength(seed),
    'offset advanced to the byte length consumed'
  );
  off = res.nextOffset;
});

// 2. Re-reading with no growth yields nothing and holds the offset.
check('a re-read with no new bytes yields no entries (idempotent tail)', () => {
  const res = livetail.tailTranscript({ file, fromOffset: off });
  assert.deepStrictEqual(res.entries, []);
  assert.strictEqual(res.nextOffset, off, 'offset unchanged');
});

// 3. The engine appends a full assistant turn -> only THAT entry tails in.
const append1 = rec({
  sessionId: SID,
  type: 'assistant',
  message: { role: 'assistant', content: [{ type: 'text', text: 'a reply' }] },
  timestamp: '2026-06-24T05:00:02.000Z',
});
fs.appendFileSync(file, append1);
check('appending a turn tails in ONLY the new entry', () => {
  const res = livetail.tailTranscript({ file, fromOffset: off });
  assert.deepStrictEqual(res.entries.map((e) => e.kind), ['assistant-text']);
  assert.strictEqual(res.entries[0].text, 'a reply');
  assert.strictEqual(res.nextOffset, off + Buffer.byteLength(append1));
  off = res.nextOffset;
});

// 4. A TORN partial line (no closing newline yet) is NOT consumed.
const full2 = {
  sessionId: SID,
  type: 'user',
  message: { role: 'user', content: 'second prompt' },
  timestamp: '2026-06-24T05:00:03.000Z',
};
const full2Line = JSON.stringify(full2) + '\n';
const partial = full2Line.slice(0, 20); // a half-written line, no '\n'
fs.appendFileSync(file, partial);
check('a torn partial line yields no entry and holds the offset', () => {
  const res = livetail.tailTranscript({ file, fromOffset: off });
  assert.deepStrictEqual(res.entries, [], 'nothing complete to fold yet');
  assert.strictEqual(res.nextOffset, off, 'offset held at the line boundary');
  assert.strictEqual(res.torn, 0, 'the partial is unconsumed, not counted torn');
});

// 5. Completing that line makes it fold in cleanly on the next tail.
fs.appendFileSync(file, full2Line.slice(20)); // the rest + the newline
check('completing the torn line tails it in on the next read', () => {
  const res = livetail.tailTranscript({ file, fromOffset: off });
  assert.deepStrictEqual(res.entries.map((e) => e.kind), ['user-text']);
  assert.strictEqual(res.entries[0].text, 'second prompt');
  assert.strictEqual(res.nextOffset, off + Buffer.byteLength(full2Line));
  off = res.nextOffset;
});

// 6. A truncated/rotated file (offset past EOF) resets to the top.
check('an offset past EOF resets and re-reads from the top', () => {
  const res = livetail.tailTranscript({ file, fromOffset: off + 10000 });
  assert.strictEqual(res.reset, true, 'reset flagged');
  assert.ok(
    res.entries.length >= 3,
    'the whole file re-folded (user, assistant, user, …)'
  );
});

// 7. activeSession picks the newest session file in the store.
const otherFile = path.join(storeDir, 'older-0001.jsonl');
fs.writeFileSync(
  otherFile,
  rec({
    sessionId: 'older-0001',
    type: 'user',
    message: { role: 'user', content: 'old' },
    timestamp: '2026-06-20T00:00:00.000Z',
  })
);
// Force mtimes: make the older file genuinely older than our SID file.
const old = new Date('2026-06-20T00:00:00.000Z');
const now = new Date('2026-06-24T05:10:00.000Z');
fs.utimesSync(otherFile, old, old);
fs.utimesSync(file, now, now);
check('activeSession returns the newest (currently-written) session', () => {
  const a = livetail.activeSession({ dir: storeDir });
  assert.ok(a, 'a session was returned');
  assert.strictEqual(a.id, SID, 'the newest file by mtime is the active one');
});

// 8. renderTranscriptRows paints blocks WITHOUT the list wrapper (append shape).
check('renderTranscriptRows yields bare blocks (no list wrapper)', () => {
  const rows = shell.renderTranscriptRows([
    { role: 'assistant', kind: 'assistant-text', text: 'hi <x>' },
  ]);
  assert.ok(/data-kind="assistant-text"/.test(rows), 'the block is rendered');
  assert.ok(/hi &lt;x&gt;/.test(rows), 'and HTML-escaped');
  assert.ok(
    !/ontum-transcript-list/.test(rows),
    'no list wrapper — it splices into the existing list'
  );
});

// 9. The shell document carries the live-append handler + the empty-state note.
check('the shell wires an ontum:append-entries handler', () => {
  const html = shell.renderShell({});
  assert.ok(
    /ontum:append-entries/.test(html),
    'the webview listens for append messages'
  );
  assert.ok(
    /insertAdjacentHTML/.test(html),
    'and splices the fragment onto the list'
  );
});

// 10. Extension wiring: open + select anchors the tail at end (no history
//     replay), then a real append makes pumpTail post ONLY the new entry.
(function liveTailRoundTrip() {
  const posted = [];
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
            postMessage(m) {
              posted.push(m);
              return true;
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
  // Fresh module graph so the stubbed storeDirFor is the one the extension sees.
  delete require.cache[require.resolve(path.join(__dirname, '..', 'extension.js'))];
  delete require.cache[require.resolve(path.join(__dirname, '..', 'sessions.js'))];
  delete require.cache[require.resolve(path.join(__dirname, '..', 'transcript.js'))];
  delete require.cache[require.resolve(path.join(__dirname, '..', 'livetail.js'))];
  const ext = require(path.join(__dirname, '..', 'extension.js'));
  Module._load = origLoad;

  ext.activate({ subscriptions: [], extensionUri: { fsPath: __dirname } });
  registered[ext.OPEN_COMMAND](); // open the panel -> initial render + wiring
  messageHandler({ type: 'ontum:select-session', id: SID }); // select -> render + startTail

  check('selecting a session paints its full transcript (row 3 still holds)', () => {
    assert.ok(
      /class="ontum-transcript-list"/.test(capturedPanel.webview.html),
      'the selected transcript rendered'
    );
  });

  check('a fresh pump with no growth replays nothing (tail anchored at end)', () => {
    const before = posted.length;
    const got = ext.pumpTail();
    assert.deepStrictEqual(got, [], 'no history replayed');
    assert.strictEqual(posted.length, before, 'no append message posted');
  });

  check('a real append streams ONLY the new entry to the webview', () => {
    fs.appendFileSync(
      file,
      rec({
        sessionId: SID,
        type: 'assistant',
        message: {
          role: 'assistant',
          content: [{ type: 'text', text: 'streamed live' }],
        },
        timestamp: '2026-06-24T05:20:00.000Z',
      })
    );
    const got = ext.pumpTail();
    assert.strictEqual(got.length, 1, 'exactly one new entry tailed in');
    assert.strictEqual(got[0].text, 'streamed live');
    const last = posted[posted.length - 1];
    assert.ok(last && last.type === 'ontum:append-entries', 'append message posted');
    assert.ok(/streamed live/.test(last.html), 'carrying the new block HTML');
    assert.ok(
      !/first prompt/.test(last.html),
      'and NOT replaying earlier turns'
    );
  });

  ext.stopTail();
  ext.deactivate();
})();

// ---- cleanup ----------------------------------------------------------------
try {
  fs.rmSync(tmpRoot, { recursive: true, force: true });
} catch (_) {
  /* best-effort temp cleanup */
}

console.log('\n' + passed + ' checks passed — row 4 evidence is green.');
process.exit(0);

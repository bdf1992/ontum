// diff.test.js — proof for parity-checklist row 8.
//
// "Render diffs / edits with accept–reject."
//
// When the assistant edits a file it emits a `tool_use` block whose name is an
// edit tool (Edit / Write / MultiEdit / NotebookEdit). Claude Code renders that
// change as a DIFF the human can Accept or Reject. This test proves the ontum
// surface does the same — host-free, with no real billed model call — by:
//   - diff.diffFromToolUse folding an edit tool_use into ordered diff lines
//     (context / del / add) via a small, deterministic common-prefix/suffix
//     diff, and folding Write/MultiEdit/NotebookEdit shapes too; a non-edit
//     tool folds to null (rendered as an ordinary tool call, row 7);
//   - shell.renderTranscriptRow painting an Edit tool_use as a diff block
//     (data-diff-tool, the file path + +adds/−dels stat, add/del lines, and
//     Accept + Reject buttons carrying the tool id) instead of a raw JSON dump,
//     all HTML-escaped — while a non-edit tool still renders row 7's JSON pre;
//   - engine.foldReply folding an Edit-calling turn into a tool-use entry whose
//     rendered row IS the diff (one source of truth with rows 3 + 5 + 7);
//   - the shell carrying a delegated `ontum:diff-decision` click handler (so
//     diffs spliced in later are wired too);
//   - the extension recording the Accept/Reject round-trip: a webview
//     `ontum:diff-decision` message is captured by getLastDiffDecision, and a
//     malformed decision is ignored;
//   - sendPrompt's terminal `ontum:turn-reply` html carrying the folded diff
//     block (data-diff-tool + the accept/reject buttons) for an Edit turn.
// HONEST SCOPE: this proves the diff fold + render + the accept/reject AFFORDANCE
// and its decision round-trip, host-free, against the captured edit-tool shapes.
// Actually applying or reverting an edit on disk is the host permission flow's
// job (row 9) / a human's — the surface renders the decision, it does not fake
// the effect; pixel-level DOM mutation needs a webview host.
//
// Run: node vscode/ontum-surface/test/diff.test.js
// Exit 0 = all assertions passed; non-zero = a failure (the message says which).

'use strict';

const assert = require('assert');
const path = require('path');
const Module = require('module');
const { EventEmitter } = require('events');

let passed = 0;
function check(label, fn) {
  fn();
  passed++;
  console.log('  ok  ' + label);
}

const diff = require(path.join(__dirname, '..', 'diff.js'));
const shell = require(path.join(__dirname, '..', 'shell.js'));
const engine = require(path.join(__dirname, '..', 'engine.js'));

console.log('row 8 — render diffs / edits with accept–reject');

// ---- 1. diff.isEditTool -----------------------------------------------------
check('isEditTool recognizes the edit tools and rejects the rest', () => {
  ['Edit', 'Write', 'MultiEdit', 'NotebookEdit'].forEach((n) =>
    assert.ok(diff.isEditTool(n), n + ' is an edit tool')
  );
  ['Read', 'Bash', 'Grep', 'Task', ''].forEach((n) =>
    assert.ok(!diff.isEditTool(n), n + ' is not an edit tool')
  );
});

// ---- 2. diff.diffLines (common prefix/suffix, middle del→add) ---------------
check('diffLines trims common prefix + suffix and marks the changed middle', () => {
  const lines = diff.diffLines('a\nB\nc', 'a\nX\nY\nc');
  assert.deepStrictEqual(lines, [
    { tag: 'context', text: 'a' },
    { tag: 'del', text: 'B' },
    { tag: 'add', text: 'X' },
    { tag: 'add', text: 'Y' },
    { tag: 'context', text: 'c' },
  ]);
});
check('diffLines on a pure insertion is all-add, on a deletion all-del', () => {
  assert.deepStrictEqual(diff.diffLines('', 'x\ny'), [
    { tag: 'add', text: 'x' },
    { tag: 'add', text: 'y' },
  ]);
  assert.deepStrictEqual(diff.diffLines('x\ny', ''), [
    { tag: 'del', text: 'x' },
    { tag: 'del', text: 'y' },
  ]);
});

// ---- 3. diffFromToolUse: Edit ----------------------------------------------
const editEntry = {
  kind: 'tool-use',
  name: 'Edit',
  toolId: 'toolu_edit_1',
  input: { file_path: 'src/app.js', old_string: 'let a = 1;', new_string: 'let a = 2;' },
};
check('diffFromToolUse folds an Edit into a diff (op, path, del+add, counts)', () => {
  const d = diff.diffFromToolUse(editEntry);
  assert.strictEqual(d.op, 'edit');
  assert.strictEqual(d.name, 'Edit');
  assert.strictEqual(d.filePath, 'src/app.js');
  assert.strictEqual(d.toolId, 'toolu_edit_1');
  assert.deepStrictEqual(d.lines, [
    { tag: 'del', text: 'let a = 1;' },
    { tag: 'add', text: 'let a = 2;' },
  ]);
  assert.strictEqual(d.adds, 1);
  assert.strictEqual(d.dels, 1);
});

// ---- 4. diffFromToolUse: Write (all-add) -----------------------------------
check('diffFromToolUse folds a Write into all-add lines', () => {
  const d = diff.diffFromToolUse({
    kind: 'tool-use',
    name: 'Write',
    toolId: 'toolu_w',
    input: { file_path: 'new.txt', content: 'one\ntwo' },
  });
  assert.strictEqual(d.op, 'write');
  assert.strictEqual(d.filePath, 'new.txt');
  assert.deepStrictEqual(d.lines, [
    { tag: 'add', text: 'one' },
    { tag: 'add', text: 'two' },
  ]);
  assert.strictEqual(d.adds, 2);
  assert.strictEqual(d.dels, 0);
});

// ---- 5. diffFromToolUse: MultiEdit (hunk-separated) ------------------------
check('diffFromToolUse folds a MultiEdit into hunk-separated diffs', () => {
  const d = diff.diffFromToolUse({
    kind: 'tool-use',
    name: 'MultiEdit',
    toolId: 'toolu_m',
    input: {
      file_path: 'm.js',
      edits: [
        { old_string: 'a', new_string: 'A' },
        { old_string: 'b', new_string: 'B' },
      ],
    },
  });
  assert.strictEqual(d.op, 'multiedit');
  assert.deepStrictEqual(d.lines, [
    { tag: 'del', text: 'a' },
    { tag: 'add', text: 'A' },
    { tag: 'hunk', text: '' },
    { tag: 'del', text: 'b' },
    { tag: 'add', text: 'B' },
  ]);
  assert.strictEqual(d.adds, 2);
  assert.strictEqual(d.dels, 2);
});

// ---- 6. diffFromToolUse: a non-edit tool folds to null ---------------------
check('diffFromToolUse returns null for a non-edit tool (Read stays row 7)', () => {
  assert.strictEqual(
    diff.diffFromToolUse({ kind: 'tool-use', name: 'Read', input: { file_path: 'a' } }),
    null
  );
  assert.strictEqual(diff.diffFromToolUse({ kind: 'assistant-text', text: 'hi' }), null);
  assert.strictEqual(diff.diffFromToolUse(null), null);
});

// ---- 7. shell.renderTranscriptRow paints an Edit as a diff block -----------
check('renderTranscriptRow paints an Edit tool_use as a diff with accept/reject', () => {
  const html = shell.renderTranscriptRow(editEntry);
  assert.ok(/data-diff-tool="true"/.test(html), 'flagged a diff tool');
  assert.ok(/data-kind="tool-use"/.test(html), 'still a tool-use block (row 7 structure)');
  assert.ok(/data-file="src\/app\.js"/.test(html), 'the file path rides the diff');
  assert.ok(/data-diff="del"/.test(html) && /let a = 1;/.test(html), 'the removed line shows');
  assert.ok(/data-diff="add"/.test(html) && /let a = 2;/.test(html), 'the added line shows');
  assert.ok(
    /data-decision="accept"[^>]*data-tool-id="toolu_edit_1"/.test(html),
    'an Accept button carries the tool id'
  );
  assert.ok(
    /data-decision="reject"[^>]*data-tool-id="toolu_edit_1"/.test(html),
    'a Reject button carries the tool id'
  );
  assert.ok(!/<pre class="ontum-tool-input">/.test(html), 'NOT the raw JSON dump (that is row 7)');
});
check('the diff content is HTML-escaped (no markup injection from new_string)', () => {
  const html = shell.renderTranscriptRow({
    kind: 'tool-use',
    name: 'Write',
    toolId: 't',
    input: { file_path: 'x.html', content: '<script>boom()</script>' },
  });
  assert.ok(!/<script>boom\(\)<\/script>/.test(html), 'raw script tag does not survive');
  assert.ok(/&lt;script&gt;/.test(html), 'angle brackets are escaped');
});
check('a non-edit tool_use still renders row 7\u2019s JSON pre (no regression)', () => {
  const html = shell.renderTranscriptRow({
    kind: 'tool-use',
    name: 'Read',
    input: { file_path: 'a.txt' },
  });
  assert.ok(/<pre class="ontum-tool-input">/.test(html), 'Read keeps the row-7 JSON pre');
  assert.ok(!/data-diff-tool/.test(html), 'Read is not a diff tool');
});

// ---- 8. engine.foldReply: an Edit turn folds into a diff-rendered entry -----
function line(obj) {
  return JSON.stringify(obj) + '\n';
}
const SESSION = 'sess-diff-1';
const EDIT_ID = 'toolu_edit_turn';
const initEv = { type: 'system', subtype: 'init', session_id: SESSION, tools: ['Edit'] };
const assistantEdit = {
  type: 'assistant',
  session_id: SESSION,
  message: {
    role: 'assistant',
    content: [
      {
        type: 'tool_use',
        id: EDIT_ID,
        name: 'Edit',
        input: { file_path: 'src/app.js', old_string: 'let a = 1;', new_string: 'let a = 2;' },
      },
    ],
  },
};
const userEditResult = {
  type: 'user',
  session_id: SESSION,
  message: {
    role: 'user',
    content: [{ type: 'tool_result', tool_use_id: EDIT_ID, content: 'edited src/app.js', is_error: false }],
  },
};
const assistantDone = {
  type: 'assistant',
  session_id: SESSION,
  message: { role: 'assistant', content: [{ type: 'text', text: 'Bumped a to 2.' }] },
};
const resultEv = {
  type: 'result',
  subtype: 'success',
  is_error: false,
  session_id: SESSION,
  total_cost_usd: 0.001,
  result: 'Bumped a to 2.',
};
const EDIT_EVENTS = [initEv, assistantEdit, userEditResult, assistantDone, resultEv];
const EDIT_STREAM = EDIT_EVENTS.map(line);

check('foldReply folds an Edit turn into a tool-use entry rendered AS a diff', () => {
  const reply = engine.foldReply(EDIT_EVENTS);
  assert.deepStrictEqual(reply.entries.map((e) => e.kind), ['tool-use', 'tool-result', 'assistant-text']);
  const call = reply.entries[0];
  assert.strictEqual(call.name, 'Edit');
  assert.deepStrictEqual(call.input, { file_path: 'src/app.js', old_string: 'let a = 1;', new_string: 'let a = 2;' });
  const html = shell.renderTranscriptRows(reply.entries);
  assert.ok(/data-diff-tool="true"/.test(html), 'the Edit entry renders as a diff (one source of truth)');
  assert.ok(/data-decision="accept"/.test(html) && /data-decision="reject"/.test(html), 'accept + reject affordance present');
});

// ---- 9. shell markup carries the delegated diff-decision handler -----------
check('renderShell carries the delegated diff-decision handler + message type', () => {
  const html = shell.renderShell({});
  assert.ok(/ontum:diff-decision/.test(html), 'the shell posts ontum:diff-decision');
  assert.ok(/ontum-diff-decision/.test(html), 'it targets the diff decision buttons');
  assert.ok(/closest\('button\.ontum-diff-decision'\)/.test(html), 'delegation via closest (later-spliced diffs work)');
  assert.ok(/data-diff-tool/.test(html) || /ontum-diff/.test(html), 'diff CSS present');
});

// ---- 10. extension: record the Accept/Reject round-trip --------------------
check('recordDiffDecision records accept/reject and ignores malformed', () => {
  // Load the extension under a fake `vscode` so the module resolves host-free.
  const ext = loadExtension().ext;
  assert.strictEqual(ext.getLastDiffDecision(), null, 'no decision yet');
  assert.deepStrictEqual(
    ext.recordDiffDecision({ type: 'ontum:diff-decision', decision: 'accept', toolId: 'tA' }),
    { toolId: 'tA', decision: 'accept' }
  );
  assert.deepStrictEqual(ext.getLastDiffDecision(), { toolId: 'tA', decision: 'accept' });
  assert.deepStrictEqual(
    ext.recordDiffDecision({ decision: 'reject', toolId: 'tB' }),
    { toolId: 'tB', decision: 'reject' },
    'latest wins'
  );
  assert.strictEqual(ext.recordDiffDecision({ decision: 'maybe' }), null, 'a bad decision is ignored');
  assert.strictEqual(ext.recordDiffDecision(null), null, 'a null message is ignored');
  // The ignored ones did not clobber the last good decision.
  assert.deepStrictEqual(ext.getLastDiffDecision(), { toolId: 'tB', decision: 'reject' });
});

// ---- 11 + 12. the full host-free wiring (message round-trip + turn-reply) ---
(async function wiring() {
  const loaded = loadExtension();
  const ext = loaded.ext;
  const posted = loaded.posted;
  const registered = loaded.registered;
  const getHandler = loaded.getHandler;

  ext.activate({ subscriptions: [], extensionUri: { fsPath: __dirname } });
  registered[ext.OPEN_COMMAND]();
  const onMessage = getHandler();
  assert.ok(typeof onMessage === 'function', 'the webview message handler is wired');

  check('a webview ontum:diff-decision message is recorded by the extension', () => {
    onMessage({ type: 'ontum:diff-decision', decision: 'accept', toolId: EDIT_ID });
    assert.deepStrictEqual(ext.getLastDiffDecision(), { toolId: EDIT_ID, decision: 'accept' });
  });

  // Drive an Edit-calling turn; the terminal turn-reply html must carry the diff.
  const fake = makeFakeEngine(EDIT_STREAM);
  ext.__setSpawnForTest(fake.spawn);
  const reply = await ext.sendPrompt('bump a to 2');
  await new Promise((r) => setImmediate(() => setImmediate(r)));

  check('sendPrompt\u2019s turn-reply html carries the folded diff (accept/reject)', () => {
    const replies = posted.filter((m) => m && m.type === 'ontum:turn-reply');
    assert.strictEqual(replies.length, 1, 'exactly one turn-reply');
    const html = replies[0].html;
    assert.ok(/data-diff-tool="true"/.test(html), 'the Edit rendered as a diff in the reply');
    assert.ok(/data-decision="accept"/.test(html) && /data-decision="reject"/.test(html), 'accept + reject in the reply');
    assert.ok(/data-diff="del"/.test(html) && /data-diff="add"/.test(html), 'the del + add lines are in the reply');
    assert.strictEqual(reply.entries[0].name, 'Edit', 'sendPrompt resolved the Edit reply');
  });

  ext.__setSpawnForTest(null);
  ext.stopTail();
  ext.deactivate();

  console.log('\n' + passed + ' checks passed — row 8 evidence is green.');
  process.exit(0);
})().catch((err) => {
  console.error('\nFAILED:', err && err.stack ? err.stack : err);
  process.exit(1);
});

// ---- helpers ---------------------------------------------------------------

// loadExtension() -> require extension.js under a fake `vscode`, returning the
// module plus the captured webview message handler + posted messages. A fresh
// require each call (cache busted) so state does not leak between checks.
function loadExtension() {
  const posted = [];
  let messageHandler = null;
  const registered = {};
  const fakeVscode = {
    ViewColumn: { One: 1 },
    workspace: { workspaceFolders: [{ uri: { fsPath: '/fake/ontum-overnight' } }] },
    window: {
      createWebviewPanel() {
        return {
          viewType: 'ontum.surface',
          webview: {
            cspSource: 'vscode-resource://fake',
            html: '',
            onDidReceiveMessage(cb) { messageHandler = cb; },
            postMessage(m) { posted.push(m); return true; },
          },
          reveal() {},
          onDidDispose() {},
          dispose() {},
        };
      },
    },
    commands: {
      registerCommand(id, cb) { registered[id] = cb; return { dispose() {} }; },
    },
  };
  const origLoad = Module._load;
  Module._load = function (request, parent, isMain) {
    if (request === 'vscode') return fakeVscode;
    return origLoad.call(this, request, parent, isMain);
  };
  delete require.cache[require.resolve(path.join(__dirname, '..', 'extension.js'))];
  const ext = require(path.join(__dirname, '..', 'extension.js'));
  Module._load = origLoad;
  return { ext, posted, registered, getHandler: () => messageHandler };
}

// makeFakeEngine(lines) -> a spawn that replays captured NDJSON (no model call).
function makeFakeEngine(lines) {
  const stdinChunks = [];
  function spawn() {
    const child = new EventEmitter();
    child.stdout = new EventEmitter();
    child.stderr = new EventEmitter();
    child.stdin = {
      write(chunk) { stdinChunks.push(chunk.toString('utf8')); return true; },
      end() {},
    };
    setImmediate(function () {
      child.stdout.emit('data', Buffer.from(lines.join(''), 'utf8'));
      child.emit('close', 0);
    });
    return child;
  }
  return { spawn, stdinChunks };
}

// tools.test.js — proof for parity-checklist row 7.
//
// "Render tool calls and their results."
//
// A real turn often calls a tool: the assistant emits a `tool_use` block, the
// engine runs it, and the result rides back in a `user` turn as a `tool_result`
// block; the assistant then continues. Claude Code renders all three (the call,
// its input, and the result). This test proves the ontum surface does the same
// — host-free, with no real billed model call — by feeding a FAKE engine the
// captured tool-calling event shapes and asserting:
//   - foldReply folds a tool-calling turn into ordered entries
//     [tool-use, tool-result, assistant-text] via the SAME foldTranscript the
//     on-disk reader uses (one source of truth, rows 3 + 5);
//   - renderTranscriptRow paints a tool-use block (name + its input JSON) and a
//     tool-result block (its text), flagging an error result with data-error;
//   - partialDelta streams a tool_use block start (carrying the tool `name`),
//     its accumulating input via `input_json_delta`, and its stop — so the
//     surface can show "calling tool X…" AS IT ARRIVES (row 7's live preview);
//   - assembleStream folds the tool_use partials into one block whose name +
//     accumulated input JSON parse to the same input the final fold yields;
//   - driveTurn fires onEvent for the tool-use partials and still resolves the
//     folded reply (tool-use + tool-result entries) across torn stdout chunks;
//   - the extension wiring streams the tool call: sendPrompt posts an
//     `ontum:turn-delta` (kind 'tool-use', the name on its start) per partial,
//     before the terminal `ontum:turn-reply` whose html carries the folded
//     tool-use + tool-result blocks;
//   - the shell renders a tool-use streaming preview labelled "tool ▸ <name>".
// Honest scope: this proves the fold + render + partial-stream PLUMBING and the
// host message protocol against the captured tool-call shapes. Pixel-level DOM
// mutation needs a webview host; a real billed tool-calling turn is left to a
// human at the surface.
//
// Run: node vscode/ontum-surface/test/tools.test.js
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

const engine = require(path.join(__dirname, '..', 'engine.js'));
const shell = require(path.join(__dirname, '..', 'shell.js'));
const transcript = require(path.join(__dirname, '..', 'transcript.js'));

console.log('row 7 — render tool calls and their results');

// ---- the captured tool-calling event stream --------------------------------
function line(obj) {
  return JSON.stringify(obj) + '\n';
}
const SESSION = 'sess-tools-1';
const TOOL_ID = 'toolu_01abc';
const init = {
  type: 'system',
  subtype: 'init',
  session_id: SESSION,
  tools: ['Task', 'Bash', 'Read'],
};
// A tool_use block (index 0): start announces the name; input streams as raw
// JSON fragments via input_json_delta; then stop.
const uStart = {
  type: 'stream_event',
  session_id: SESSION,
  event: {
    type: 'content_block_start',
    index: 0,
    content_block: { type: 'tool_use', id: TOOL_ID, name: 'Read', input: {} },
  },
};
const uD1 = {
  type: 'stream_event',
  event: { type: 'content_block_delta', index: 0, delta: { type: 'input_json_delta', partial_json: '{"file_path":' } },
};
const uD2 = {
  type: 'stream_event',
  event: { type: 'content_block_delta', index: 0, delta: { type: 'input_json_delta', partial_json: '"a.txt"}' } },
};
const uStop = { type: 'stream_event', event: { type: 'content_block_stop', index: 0 } };
// The authoritative message events the partials previewed:
//   assistant turn carries the tool_use; the result rides back in a user turn;
//   the assistant then continues with prose.
const assistantToolUse = {
  type: 'assistant',
  session_id: SESSION,
  message: {
    role: 'assistant',
    content: [{ type: 'tool_use', id: TOOL_ID, name: 'Read', input: { file_path: 'a.txt' } }],
  },
};
const userToolResult = {
  type: 'user',
  session_id: SESSION,
  message: {
    role: 'user',
    content: [{ type: 'tool_result', tool_use_id: TOOL_ID, content: 'hello from a.txt', is_error: false }],
  },
};
const assistantText = {
  type: 'assistant',
  session_id: SESSION,
  message: { role: 'assistant', content: [{ type: 'text', text: 'The file says hello.' }] },
};
const result = {
  type: 'result',
  subtype: 'success',
  is_error: false,
  session_id: SESSION,
  total_cost_usd: 0.002,
  result: 'The file says hello.',
};
const EVENTS = [
  init, uStart, uD1, uD2, uStop,
  assistantToolUse, userToolResult, assistantText, result,
];
const STREAM = EVENTS.map(line);

// ---- a fake engine process (no real model call) -----------------------------
function makeFakeEngine(lines, opts) {
  const o = opts || {};
  const stdinChunks = [];
  const calls = [];
  function spawn(bin, args, options) {
    calls.push({ bin, args, options });
    const child = new EventEmitter();
    child.stdout = new EventEmitter();
    child.stderr = new EventEmitter();
    child.stdin = {
      write(chunk) {
        stdinChunks.push(chunk.toString('utf8'));
        return true;
      },
      end() {},
    };
    setImmediate(function () {
      const blob = lines.join('');
      if (o.split) {
        const mid = Math.floor(blob.length / 2);
        child.stdout.emit('data', Buffer.from(blob.slice(0, mid), 'utf8'));
        child.stdout.emit('data', Buffer.from(blob.slice(mid), 'utf8'));
      } else {
        child.stdout.emit('data', Buffer.from(blob, 'utf8'));
      }
      child.emit('close', typeof o.code === 'number' ? o.code : 0);
    });
    return child;
  }
  return { spawn, stdinChunks, calls };
}

// 1. foldReply — a tool-calling turn folds into ordered tool-use/result/text.
check('foldReply folds a tool-calling turn into [tool-use, tool-result, assistant-text]', () => {
  const reply = engine.foldReply(EVENTS);
  assert.deepStrictEqual(
    reply.entries.map((e) => e.kind),
    ['tool-use', 'tool-result', 'assistant-text'],
    'the call, its result, then the assistant prose — in order'
  );
  const call = reply.entries[0];
  assert.strictEqual(call.name, 'Read', 'the tool name is folded');
  assert.deepStrictEqual(call.input, { file_path: 'a.txt' }, 'the tool input is folded');
  const res = reply.entries[1];
  assert.strictEqual(res.toolUseId, TOOL_ID, 'the result links back to the call');
  assert.strictEqual(res.isError, false, 'a success result is not flagged an error');
  assert.strictEqual(res.text, 'hello from a.txt', 'the result text is folded');
  assert.strictEqual(reply.text, 'The file says hello.', 'final prose is the result string');
  assert.strictEqual(reply.isError, false);
});

// 2. renderTranscriptRow — paint a tool-use and a tool-result block.
check('renderTranscriptRow paints a tool-use block with its name + input', () => {
  const html = shell.renderTranscriptRow({ kind: 'tool-use', name: 'Read', toolId: TOOL_ID, input: { file_path: 'a.txt' } });
  assert.ok(/data-kind="tool-use"/.test(html), 'tagged data-kind="tool-use"');
  assert.ok(/Read/.test(html), 'the tool name shows');
  assert.ok(/file_path/.test(html) && /a\.txt/.test(html), 'the input JSON shows');
  assert.ok(/<pre/.test(html), 'input rendered in a pre block');
});
check('renderTranscriptRow paints a tool-result block, flagging errors', () => {
  const ok = shell.renderTranscriptRow({ kind: 'tool-result', toolUseId: TOOL_ID, isError: false, text: 'hello from a.txt' });
  assert.ok(/data-kind="tool-result"/.test(ok), 'tagged data-kind="tool-result"');
  assert.ok(!/data-error="true"/.test(ok), 'a success result is not flagged');
  assert.ok(/hello from a\.txt/.test(ok), 'the result text shows');
  const bad = shell.renderTranscriptRow({ kind: 'tool-result', toolUseId: TOOL_ID, isError: true, text: 'ENOENT' });
  assert.ok(/data-error="true"/.test(bad), 'an error result is flagged data-error');
  assert.ok(/error/.test(bad), 'the error label shows');
});
check('tool-use input is HTML-escaped (no markup injection)', () => {
  const html = shell.renderTranscriptRow({ kind: 'tool-use', name: 'Bash', input: { cmd: '<script>x</script>' } });
  assert.ok(!/<script>x<\/script>/.test(html), 'raw script tag does not survive');
  assert.ok(/&lt;script&gt;/.test(html), 'angle brackets are escaped');
});

// 3. partialDelta — stream a tool_use start (name) + input_json_delta + stop.
check('partialDelta streams a tool_use block start carrying the name', () => {
  assert.deepStrictEqual(engine.partialDelta(uStart), {
    phase: 'start', index: 0, kind: 'tool-use', name: 'Read',
  });
});
check('partialDelta streams the tool input as input_json_delta fragments', () => {
  assert.deepStrictEqual(engine.partialDelta(uD1), {
    phase: 'delta', index: 0, kind: 'tool-use', text: '{"file_path":',
  });
  assert.deepStrictEqual(engine.partialDelta(uD2), {
    phase: 'delta', index: 0, kind: 'tool-use', text: '"a.txt"}',
  });
  assert.deepStrictEqual(engine.partialDelta(uStop), { phase: 'stop', index: 0 });
});
check('partialDelta ignores the non-partial message + result events', () => {
  assert.strictEqual(engine.partialDelta(assistantToolUse), null);
  assert.strictEqual(engine.partialDelta(userToolResult), null);
  assert.strictEqual(engine.partialDelta(result), null);
});

// 4. assembleStream — the tool_use partials reconstruct the folded input.
check('assembleStream folds the tool_use partials into one named block', () => {
  const blocks = engine.assembleStream(EVENTS);
  assert.strictEqual(blocks.length, 1, 'one streamed block (the tool call)');
  assert.strictEqual(blocks[0].kind, 'tool-use');
  assert.strictEqual(blocks[0].name, 'Read', 'the block carries the tool name');
  assert.strictEqual(blocks[0].text, '{"file_path":"a.txt"}', 'the input JSON is reassembled');
});
check('the streamed tool input parses to the folded tool input (consistent)', () => {
  const blocks = engine.assembleStream(EVENTS);
  const reply = engine.foldReply(EVENTS);
  const streamedInput = JSON.parse(blocks[0].text);
  assert.deepStrictEqual(streamedInput, reply.entries[0].input,
    'the previewed input JSON equals the folded tool input');
});

// 5. driveTurn — fires onEvent for the tool-use partials; folds the reply.
(async function driveTurnToolCall() {
  const collected = [];
  const fake = makeFakeEngine(STREAM, { split: true });
  const reply = await engine.driveTurn({
    prompt: 'read a.txt',
    spawn: fake.spawn,
    onEvent: (ev) => collected.push(ev),
  });
  check('driveTurn fires onEvent for every event (across torn chunks) incl. the tool partials', () => {
    assert.strictEqual(collected.length, EVENTS.length, 'every line reached onEvent');
    const blocks = engine.assembleStream(collected);
    assert.strictEqual(blocks[0].name, 'Read');
    assert.strictEqual(blocks[0].text, '{"file_path":"a.txt"}');
  });
  check('driveTurn resolves the folded reply with the tool-use + tool-result entries', () => {
    assert.deepStrictEqual(
      reply.entries.map((e) => e.kind),
      ['tool-use', 'tool-result', 'assistant-text']
    );
    assert.strictEqual(reply.isError, false);
    assert.strictEqual(reply.text, 'The file says hello.');
  });

  // 6. Extension wiring — stream the tool call from the surface (host-free).
  await extensionWiring();

  // 7. Shell markup — the tool-use streaming preview label.
  check('the shell labels a tool-use streaming preview with the tool name', () => {
    const html = shell.renderShell({});
    assert.ok(/data-tool-name/.test(html), 'a tool-use preview carries the tool name');
    assert.ok(/kind === 'tool-use'/.test(html), 'the delta handler special-cases tool-use');
    assert.ok(/tool \u25b8 /.test(html), 'it labels the preview "tool \u25b8 <name>"');
  });

  console.log('\n' + passed + ' checks passed — row 7 evidence is green.');
  process.exit(0);
})().catch((err) => {
  console.error('\nFAILED:', err && err.stack ? err.stack : err);
  process.exit(1);
});

// Drive a tool-calling turn through the real extension module with a fake engine.
async function extensionWiring() {
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

  const fake = makeFakeEngine(STREAM);
  ext.activate({ subscriptions: [], extensionUri: { fsPath: __dirname } });
  registered[ext.OPEN_COMMAND]();
  ext.__setSpawnForTest(fake.spawn);

  const reply = await ext.sendPrompt('read a.txt');
  await new Promise((r) => setImmediate(() => setImmediate(r)));

  const deltas = posted.filter((m) => m && m.type === 'ontum:turn-delta');
  const replies = posted.filter((m) => m && m.type === 'ontum:turn-reply');

  check('sendPrompt streams the tool call: a tool-use turn-delta with its name', () => {
    // 4 tool partials: 1 start + 2 input deltas + 1 stop.
    assert.strictEqual(deltas.length, 4, 'one turn-delta per tool partial');
    assert.strictEqual(deltas[0].phase, 'start');
    assert.strictEqual(deltas[0].kind, 'tool-use');
    assert.strictEqual(deltas[0].name, 'Read', 'the tool name rides the start delta');
    const input = deltas.filter((d) => d.phase === 'delta').map((d) => d.text).join('');
    assert.strictEqual(input, '{"file_path":"a.txt"}', 'the streamed input reconstructs');
  });
  check('every tool-use turn-delta precedes the terminal turn-reply', () => {
    const firstReply = posted.findIndex((m) => m && m.type === 'ontum:turn-reply');
    const lastDelta = posted.map((m) => m && m.type).lastIndexOf('ontum:turn-delta');
    assert.ok(firstReply >= 0, 'a turn-reply was posted');
    assert.ok(lastDelta >= 0 && lastDelta < firstReply, 'all deltas precede the reply');
  });
  check('the turn-reply html carries the folded tool-use + tool-result blocks', () => {
    assert.strictEqual(replies.length, 1, 'exactly one turn-reply');
    const html = replies[0].html;
    assert.ok(/data-kind="tool-use"/.test(html), 'the tool call rendered');
    assert.ok(/data-kind="tool-result"/.test(html), 'the tool result rendered');
    assert.ok(/Read/.test(html) && /hello from a\.txt/.test(html), 'name + result text present');
    assert.strictEqual(replies[0].isError, false);
    assert.strictEqual(reply.text, 'The file says hello.', 'sendPrompt resolved the reply');
  });

  ext.__setSpawnForTest(null);
  ext.stopTail();
  ext.deactivate();
}

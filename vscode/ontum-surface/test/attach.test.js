// attach.test.js — proof for parity-checklist row 15.
//
// "Image / file attach."
//
// Normal Claude Code lets you attach an image (drag/paste/pick) or a file to a
// message; the attachment rides the turn as a content block in the SAME
// Messages-API user envelope row 5 drives — an image as a base64 `image` block,
// a PDF as a base64 `document` block, a text file inlined as a marked `text`
// block. The engine reads the attachment; the surface does not re-implement
// vision. So the ontum surface owns only the SURFACE of attachments: it
// CLASSIFIES a file by name, READS it off disk into a bounded record, ENCODES
// it into the content block(s) the engine accepts, and STAGES it on the turn.
// This test proves all of it host-free (no billed model call, no VS Code host):
//   - attach.classifyAttachment / isImageFile / mediaTypeForImage classify a
//     name into image / document / text + its media type;
//   - attach.readAttachment folds a real on-disk file (a 1×1 PNG + a text file)
//     into a bounded record (base64 for the image, utf8 for the text), and
//     refuses a missing / oversized file with an honest error (never throws);
//   - attach.attachmentBlock / attachmentBlocks encode the records into the
//     Messages-API blocks (image -> base64 image source, text -> marked text),
//     dropping an errored attachment;
//   - engine.encodeUserMessage folds the blocks AHEAD of the typed text, and
//     with NO attachments produces EXACTLY [{type:'text',text}] (backward-compat
//     — every earlier row's verbatim-stdin proof still holds);
//   - shell.renderAttachTray / renderShell paint the chips + carry the
//     attach-button + remove wiring;
//   - extension.addAttachment / removeAttachment / getAttachments stage + drop +
//     view (data-free) the attachments;
//   - the round-trip: a webview attach (injected picker) stages a PNG, the next
//     driven turn's stdin carries it as a base64 image block AHEAD of the typed
//     prompt (proven by a fake spawn — no model call), and the staged set CLEARS
//     after the send (the attachment rode exactly one turn).
// HONEST SCOPE: the engine remains authoritative on what an attachment means
// (vision/PDF reading); the surface classifies + reads + encodes + stages it.
// The LIVE file picker is the VS Code host dialog (window.showOpenDialog); the
// fold is proven host-free against a path via __setAttachPickerForTest. A real
// billed turn is a human's to run.
//
// Run: node vscode/ontum-surface/test/attach.test.js
// Exit 0 = all assertions passed; non-zero = a failure (the message says which).

'use strict';

const assert = require('assert');
const fs = require('fs');
const os = require('os');
const path = require('path');
const Module = require('module');
const { EventEmitter } = require('events');

let passed = 0;
let _lastHandler = null;
let _lastOpen = null;
function check(label, fn) {
  fn();
  passed++;
  console.log('  ok  ' + label);
}

const attach = require(path.join(__dirname, '..', 'attach.js'));
const shell = require(path.join(__dirname, '..', 'shell.js'));
const engine = require(path.join(__dirname, '..', 'engine.js'));

console.log('row 15 — image / file attach');

// ---- a fake workspace with a real image + a real text file -----------------
// A 1×1 transparent PNG (the canonical minimal PNG) written as real bytes, so
// readAttachment folds genuine on-disk bytes — not a stub.
const PNG_B64 =
  'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAC0lEQVR4' +
  '2mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==';
const WS = fs.mkdtempSync(path.join(os.tmpdir(), 'ontum-attach-'));
const PNG = path.join(WS, 'pixel.png');
const TXT = path.join(WS, 'notes.txt');
fs.writeFileSync(PNG, Buffer.from(PNG_B64, 'base64'));
fs.writeFileSync(TXT, 'hello from a file\n');

// ---- 1. classify by name ---------------------------------------------------
check('classifyAttachment maps image / document / text by extension', () => {
  assert.deepStrictEqual(attach.classifyAttachment('a.png'),
    { kind: 'image', mediaType: 'image/png' });
  assert.deepStrictEqual(attach.classifyAttachment('A.JPG'),
    { kind: 'image', mediaType: 'image/jpeg' }, 'extension match is case-insensitive');
  assert.deepStrictEqual(attach.classifyAttachment('doc.pdf'),
    { kind: 'document', mediaType: 'application/pdf' });
  assert.deepStrictEqual(attach.classifyAttachment('notes.txt'),
    { kind: 'text', mediaType: 'text/plain' });
  assert.deepStrictEqual(attach.classifyAttachment('weird.xyz'),
    { kind: 'text', mediaType: 'text/plain' }, 'unknown -> text, never guessed image');
});
check('isImageFile / mediaTypeForImage agree with the classifier', () => {
  assert.strictEqual(attach.isImageFile('p.gif'), true);
  assert.strictEqual(attach.isImageFile('p.txt'), false);
  assert.strictEqual(attach.mediaTypeForImage('p.webp'), 'image/webp');
  assert.strictEqual(attach.mediaTypeForImage('p.txt'), null);
});

// ---- 2. readAttachment folds real on-disk bytes ----------------------------
check('readAttachment folds a PNG into a base64 image record', () => {
  const rec = attach.readAttachment({ file: PNG });
  assert.strictEqual(rec.kind, 'image');
  assert.strictEqual(rec.mediaType, 'image/png');
  assert.strictEqual(rec.name, 'pixel.png');
  assert.ok(rec.bytes > 0, 'the byte count is honest');
  assert.strictEqual(rec.data, PNG_B64, 'the base64 round-trips the real bytes');
  assert.strictEqual(rec.text, undefined, 'an image carries no inlined text');
});
check('readAttachment folds a text file into an inlined utf8 record', () => {
  const rec = attach.readAttachment({ file: TXT });
  assert.strictEqual(rec.kind, 'text');
  assert.strictEqual(rec.text, 'hello from a file\n', 'the utf8 content is carried');
  assert.strictEqual(rec.data, undefined, 'a text file carries no base64');
});
check('readAttachment refuses a missing file with an honest error (no throw)', () => {
  const rec = attach.readAttachment({ file: path.join(WS, 'nope.png') });
  assert.strictEqual(rec.error, 'not found');
  assert.strictEqual(rec.data, undefined);
});
check('readAttachment refuses an oversized file with an honest error', () => {
  const rec = attach.readAttachment({ file: TXT, maxBytes: 1 });
  assert.strictEqual(rec.error, 'too large', 'the cap binds the read');
  assert.ok(rec.bytes >= 1, 'the actual size is reported');
});

// ---- 3. attachmentBlock / attachmentBlocks encode the Messages-API blocks ---
check('attachmentBlock encodes an image record as a base64 image block', () => {
  const block = attach.attachmentBlock(attach.readAttachment({ file: PNG }));
  assert.strictEqual(block.type, 'image');
  assert.strictEqual(block.source.type, 'base64');
  assert.strictEqual(block.source.media_type, 'image/png');
  assert.strictEqual(block.source.data, PNG_B64);
});
check('attachmentBlock encodes a text record as a marked text block', () => {
  const block = attach.attachmentBlock(attach.readAttachment({ file: TXT }));
  assert.strictEqual(block.type, 'text');
  assert.ok(block.text.indexOf('[file notes.txt]') === 0, 'the file marker leads');
  assert.ok(/hello from a file/.test(block.text), 'the content follows');
});
check('attachmentBlock drops an errored attachment (-> null)', () => {
  assert.strictEqual(attach.attachmentBlock({ name: 'x', error: 'not found' }), null);
  assert.strictEqual(attach.attachmentBlock(null), null);
});
check('attachmentBlocks encodes an array, dropping the errored ones', () => {
  const blocks = attach.attachmentBlocks([
    attach.readAttachment({ file: PNG }),
    { name: 'gone', error: 'not found' },
    attach.readAttachment({ file: TXT }),
  ]);
  assert.strictEqual(blocks.length, 2, 'two good blocks, the error dropped');
  assert.strictEqual(blocks[0].type, 'image');
  assert.strictEqual(blocks[1].type, 'text');
});
check('displayAttachment is a data-free view (no base64 payload)', () => {
  const view = attach.displayAttachment(attach.readAttachment({ file: PNG }));
  assert.deepStrictEqual(Object.keys(view).sort(), ['bytes', 'kind', 'name']);
  assert.strictEqual(view.data, undefined, 'the base64 never reaches the tray view');
});

// ---- 4. engine.encodeUserMessage folds blocks ahead of the text ------------
check('encodeUserMessage with NO attachments is EXACTLY [{type:text}] (backward-compat)', () => {
  const obj = JSON.parse(engine.encodeUserMessage('just text').trim());
  assert.strictEqual(obj.message.content.length, 1, 'one block');
  assert.deepStrictEqual(obj.message.content[0], { type: 'text', text: 'just text' });
});
check('encodeUserMessage folds attachment blocks AHEAD of the typed text', () => {
  const blocks = attach.attachmentBlocks([attach.readAttachment({ file: PNG })]);
  const obj = JSON.parse(engine.encodeUserMessage('look at this', blocks).trim());
  assert.strictEqual(obj.message.content.length, 2, 'image + text');
  assert.strictEqual(obj.message.content[0].type, 'image', 'the image leads');
  assert.deepStrictEqual(obj.message.content[1], { type: 'text', text: 'look at this' },
    'the typed text follows last');
});
check('encodeUserMessage admits only well-formed blocks (malformed dropped)', () => {
  const obj = JSON.parse(engine.encodeUserMessage('hi', [null, { no: 'type' }, 42]).trim());
  assert.strictEqual(obj.message.content.length, 1, 'only the text block survives');
  assert.strictEqual(obj.message.content[0].text, 'hi');
});

// ---- 5. shell.renderAttachTray + renderShell paint + wire the tray ---------
check('renderAttachTray paints a chip per attachment, escaped, with remove wiring', () => {
  const html = shell.renderAttachTray([
    { name: 'pixel.png', kind: 'image', bytes: 70 },
    { name: 'a<b>.txt', kind: 'text', bytes: 10 },
  ]);
  assert.ok(/data-attachment="pixel\.png"/.test(html), 'chip carries data-attachment');
  assert.ok(/data-count="2"/.test(html), 'the count is honest');
  assert.ok(/data-attach-name="pixel\.png"/.test(html), 'the remove button is wired by name');
  assert.ok(/&lt;b&gt;/.test(html), 'the name is HTML-escaped');
  assert.ok(/image · /.test(html), 'the kind + size meta is shown');
});
check('renderAttachTray marks an errored attachment honestly (no fake success)', () => {
  const html = shell.renderAttachTray([{ name: 'big.png', kind: 'image', bytes: 0, error: 'too large' }]);
  assert.ok(/data-error="true"/.test(html), 'the error flag is set');
  assert.ok(/error: too large/.test(html), 'the honest error is shown, not a size');
});
check('renderAttachTray on an empty list paints nothing (container still ships in shell)', () => {
  assert.strictEqual(shell.renderAttachTray([]), '', 'empty -> no chips');
});
check('renderShell carries the attach tray + button + remove wiring', () => {
  const html = shell.renderShell({ attachments: [{ name: 'pixel.png', kind: 'image', bytes: 70 }] });
  assert.ok(/class="ontum-attach"/.test(html), 'the tray container is in the composer');
  assert.ok(/data-attachment="pixel\.png"/.test(html), 'the passed attachment is rendered');
  assert.ok(/ontum-attach-add/.test(html), 'the attach button ships');
  assert.ok(/ontum:attach-file/.test(html), 'the attach-file wiring is present');
  assert.ok(/ontum:remove-attachment/.test(html), 'the remove wiring is present');
});
check('renderShell with no attachments still ships the tray container (no regression)', () => {
  const html = shell.renderShell({});
  assert.ok(/class="ontum-attach"/.test(html), 'the container ships even with no attachments');
  assert.ok(/ontum:attach-file/.test(html), 'the wiring ships too');
});

// ---- 6. extension staging API ---------------------------------------------
check('extension.addAttachment / getAttachments stage a data-free view', () => {
  const { ext } = loadExtension(WS);
  ext.addAttachment(PNG);
  const views = ext.getAttachments();
  assert.strictEqual(views.length, 1, 'one staged');
  assert.strictEqual(views[0].name, 'pixel.png');
  assert.strictEqual(views[0].kind, 'image');
  assert.strictEqual(views[0].data, undefined, 'the base64 never leaks into the view');
});
check('extension.addAttachment de-dups by name (re-attach refreshes, not stacks)', () => {
  const { ext } = loadExtension(WS);
  ext.addAttachment(PNG);
  ext.addAttachment(PNG);
  assert.strictEqual(ext.getAttachments().length, 1, 're-attaching the same file does not stack');
});
check('extension.removeAttachment drops a staged attachment by name', () => {
  const { ext } = loadExtension(WS);
  ext.addAttachment(PNG);
  ext.addAttachment(TXT);
  assert.strictEqual(ext.removeAttachment('pixel.png'), true, 'one removed');
  const names = ext.getAttachments().map((v) => v.name);
  assert.deepStrictEqual(names, ['notes.txt'], 'only the other remains');
  assert.strictEqual(ext.removeAttachment('ghost'), false, 'unknown name is a no-op');
});

// ---- 7. the round-trip: a driven turn carries the attachment block ---------
function emit(obj) {
  return JSON.stringify(obj) + '\n';
}
const SESSION = 'sess-attach-1';
const STREAM = [
  { type: 'system', subtype: 'init', session_id: SESSION, tools: ['Read'] },
  {
    type: 'assistant',
    session_id: SESSION,
    message: { role: 'assistant', content: [{ type: 'text', text: 'Saw it.' }] },
  },
  {
    type: 'result',
    subtype: 'success',
    is_error: false,
    session_id: SESSION,
    total_cost_usd: 0.0001,
    result: 'Saw it.',
  },
].map(emit);

(async function roundTrip() {
  const { ext } = loadExtension(WS);
  ext.activate({ subscriptions: [], extensionUri: { fsPath: __dirname } });
  lastOpen()();
  const onMessage = lastHandler();
  assert.ok(typeof onMessage === 'function', 'the webview message handler is wired');

  // (a) The webview asks to attach a file; the injected picker returns the PNG
  // path; it is staged + viewable.
  ext.__setAttachPickerForTest(function () {
    return Promise.resolve([PNG]);
  });
  onMessage({ type: 'ontum:attach-file' });
  await new Promise((r) => setImmediate(() => setImmediate(r)));

  check('a webview attach (injected picker) stages the chosen file', () => {
    const views = ext.getAttachments();
    assert.strictEqual(views.length, 1, 'the picked PNG is staged');
    assert.strictEqual(views[0].name, 'pixel.png');
  });

  // (b) The next driven turn's stdin carries the PNG as a base64 image block
  // AHEAD of the typed prompt (proven by a fake spawn — no model call).
  const fake = makeFakeEngine(STREAM);
  ext.__setSpawnForTest(fake.spawn);
  onMessage({ type: 'ontum:send-prompt', text: 'what is in this image?' });
  await new Promise((r) => setImmediate(() => setImmediate(r)));

  check('the turn carried the attachment as a base64 image block ahead of the text', () => {
    assert.strictEqual(fake.calls.length, 1, 'the engine was spawned once');
    const obj = JSON.parse(fake.stdin.join('').trim().split('\n')[0]);
    const content = obj.message.content;
    assert.strictEqual(content.length, 2, 'image block + text block');
    assert.strictEqual(content[0].type, 'image', 'the image leads');
    assert.strictEqual(content[0].source.media_type, 'image/png');
    assert.strictEqual(content[0].source.data, PNG_B64, 'the real bytes rode the turn');
    assert.deepStrictEqual(content[1], { type: 'text', text: 'what is in this image?' },
      'the typed prompt follows last');
  });

  check('the staged set CLEARS after the send (the attachment rode exactly one turn)', () => {
    assert.strictEqual(ext.getAttachments().length, 0, 'no chips remain after the turn');
  });

  // (c) A plain turn (no attachment) sends EXACTLY [{type:text}] — every earlier
  // row's verbatim-stdin proof is preserved.
  const fake2 = makeFakeEngine(STREAM);
  ext.__setSpawnForTest(fake2.spawn);
  onMessage({ type: 'ontum:send-prompt', text: 'plain question' });
  await new Promise((r) => setImmediate(() => setImmediate(r)));

  check('a plain turn (no attachment) sends exactly the text block (no regression)', () => {
    const obj = JSON.parse(fake2.stdin.join('').trim().split('\n')[0]);
    assert.strictEqual(obj.message.content.length, 1, 'one block only');
    assert.strictEqual(obj.message.content[0].text, 'plain question');
  });

  ext.__setSpawnForTest(null);
  ext.__setAttachPickerForTest(null);
  ext.stopTail();
  ext.deactivate();

  try {
    fs.rmSync(WS, { recursive: true, force: true });
  } catch (_) {
    /* best-effort cleanup */
  }

  console.log('\n' + passed + ' checks passed — row 15 evidence is green.');
  process.exit(0);
})().catch((err) => {
  console.error('\nFAILED:', err && err.stack ? err.stack : err);
  process.exit(1);
});

// ---- helpers ---------------------------------------------------------------

function lastHandler() {
  return _lastHandler;
}
function lastOpen() {
  return _lastOpen;
}

// loadExtension(cwd) -> require extension.js under a fake `vscode` whose
// workspace folder is `cwd`. The fake window's showOpenDialog is never reached —
// the row-15 picker comes from the injected __setAttachPickerForTest seam, not a
// host. Cache-busted each call so staged state does not leak between checks.
function loadExtension(cwd) {
  let messageHandler = null;
  const registered = {};
  const fakeVscode = {
    ViewColumn: { One: 1 },
    workspace: { workspaceFolders: [{ uri: { fsPath: cwd } }] },
    window: {
      createWebviewPanel() {
        return {
          viewType: 'ontum.surface',
          webview: {
            cspSource: 'vscode-resource://fake',
            html: '',
            onDidReceiveMessage(cb) {
              messageHandler = cb;
              _lastHandler = cb;
            },
            postMessage() {
              return true;
            },
          },
          reveal() {},
          onDidDispose() {},
          dispose() {},
        };
      },
      showOpenDialog() {
        // Never reached in this test (the picker is injected); present so a
        // production path would have a host to call.
        return Promise.resolve([]);
      },
    },
    commands: {
      registerCommand(id, cb) {
        registered[id] = cb;
        if (id === 'ontum.surface.open') _lastOpen = cb;
        return { dispose() {} };
      },
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
  return { ext, registered, getHandler: () => messageHandler };
}

// makeFakeEngine(lines) -> a spawn that replays captured NDJSON (no model call)
// AND records each spawn's argv + everything written to stdin, so the test can
// assert the attachment block reached the engine prompt channel.
function makeFakeEngine(lines) {
  const calls = [];
  const stdin = [];
  function spawn(bin, args) {
    calls.push({ bin, args });
    const child = new EventEmitter();
    child.stdout = new EventEmitter();
    child.stderr = new EventEmitter();
    child.stdin = {
      write(chunk) {
        stdin.push(chunk.toString());
        return true;
      },
      end() {},
    };
    setImmediate(function () {
      child.stdout.emit('data', Buffer.from(lines.join(''), 'utf8'));
      child.emit('close', 0);
    });
    return child;
  }
  return { spawn, calls, stdin };
}

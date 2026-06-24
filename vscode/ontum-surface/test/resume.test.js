// resume.test.js — proof for parity-checklist row 16.
//
// "Resume / continue an existing session."
//
// Normal Claude Code can RESUME a specific past conversation or CONTINUE the
// most recent one; --fork-session branches a new session id off either. The
// bridge spike resolved this row to `inherit`: the SAME `claude` CLI exposes
// exactly these levers, verified live on this machine —
//   -c, --continue                 Continue the most recent conversation
//   -r, --resume [sessionId]       Resume a conversation
//   --fork-session                 When resuming, create a new session id
// This test proves the ontum surface drives that inherited engine — host-free,
// no billed model call:
//   - engine.normalizeResumeTarget validates a target (unknown mode / id-less
//     resume -> 'new', so a turn never silently resumes the wrong session);
//   - engine.resumeArgsFromTarget maps the target to the engineArgs fragment,
//     and engine.engineArgs threads --continue / --resume <id> (+ --fork-session
//     ONLY alongside a resume/continue) into the drive channel's argv;
//   - shell.renderResumeControl + renderShell paint the composer's New /
//     Continue recent / Resume selected buttons (the in-force one aria-pressed,
//     the resume button carrying the selected session id) and carry the
//     `ontum:set-resume` change handler;
//   - extension.setResumeTarget records + normalizes the chosen target, and the
//     webview round-trip (a real onDidReceiveMessage `ontum:set-resume` message)
//     sets the session the NEXT turn joins;
//   - sendPrompt drives a turn whose spawned argv carries --resume <id> (or
//     --continue) — proven by a fake spawn that captures argv (no model call).
// HONEST SCOPE: this proves the resume/continue surface flows into the real
// engine argv, host-free. Driving a real billed turn that actually replays a
// past conversation is a human's to run at the surface.
//
// Run: node vscode/ontum-surface/test/resume.test.js
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

console.log('row 16 — resume / continue an existing session');

// ---- 1. the mode list ------------------------------------------------------
check('RESUME_MODES is exactly new / continue / resume', () => {
  assert.deepStrictEqual(engine.RESUME_MODES, ['new', 'continue', 'resume']);
});

// ---- 2. normalizeResumeTarget validates (conservative default) -------------
check('normalizeResumeTarget passes valid targets, defaults the rest', () => {
  assert.deepStrictEqual(engine.normalizeResumeTarget({ mode: 'new' }), {
    mode: 'new',
    sessionId: null,
    fork: false,
  });
  assert.deepStrictEqual(engine.normalizeResumeTarget({ mode: 'continue' }), {
    mode: 'continue',
    sessionId: null,
    fork: false,
  });
  assert.deepStrictEqual(
    engine.normalizeResumeTarget({ mode: 'resume', sessionId: 'sess-1' }),
    { mode: 'resume', sessionId: 'sess-1', fork: false }
  );
});
check('normalizeResumeTarget: a resume with no id falls back to new', () => {
  assert.strictEqual(
    engine.normalizeResumeTarget({ mode: 'resume' }).mode,
    'new',
    'nothing to resume -> new'
  );
  assert.strictEqual(
    engine.normalizeResumeTarget({ mode: 'resume', sessionId: '' }).mode,
    'new'
  );
});
check('normalizeResumeTarget: unknown / hostile mode -> new', () => {
  ['', 'bogus', 'RESUME', null, undefined, 7, {}].forEach((m) =>
    assert.strictEqual(
      engine.normalizeResumeTarget({ mode: m, sessionId: 'x' }).mode,
      'new',
      JSON.stringify(m) + ' -> new'
    )
  );
});
check('normalizeResumeTarget accepts a bare mode string + preserves fork', () => {
  assert.strictEqual(engine.normalizeResumeTarget('continue').mode, 'continue');
  assert.strictEqual(
    engine.normalizeResumeTarget({ mode: 'continue', fork: true }).fork,
    true
  );
});

// ---- 3. resumeArgsFromTarget maps target -> engineArgs fragment -------------
check('resumeArgsFromTarget: new -> {} (the default fresh-session drive)', () => {
  assert.deepStrictEqual(engine.resumeArgsFromTarget({ mode: 'new' }), {});
});
check('resumeArgsFromTarget: continue -> { continueSession }', () => {
  assert.deepStrictEqual(engine.resumeArgsFromTarget({ mode: 'continue' }), {
    continueSession: true,
  });
  assert.deepStrictEqual(
    engine.resumeArgsFromTarget({ mode: 'continue', fork: true }),
    { continueSession: true, forkSession: true }
  );
});
check('resumeArgsFromTarget: resume -> { resume } (+ fork)', () => {
  assert.deepStrictEqual(
    engine.resumeArgsFromTarget({ mode: 'resume', sessionId: 'sess-9' }),
    { resume: 'sess-9' }
  );
  assert.deepStrictEqual(
    engine.resumeArgsFromTarget({ mode: 'resume', sessionId: 'sess-9', fork: true }),
    { resume: 'sess-9', forkSession: true }
  );
});
check('resumeArgsFromTarget: id-less resume / lone fork are conservative', () => {
  assert.deepStrictEqual(
    engine.resumeArgsFromTarget({ mode: 'resume' }),
    {},
    'id-less resume -> {} (nothing to resume)'
  );
  assert.deepStrictEqual(
    engine.resumeArgsFromTarget({ mode: 'new', fork: true }),
    {},
    'a lone fork has nothing to fork from -> dropped'
  );
});

// ---- 4. engineArgs threads the resume/continue flags -----------------------
check('engineArgs carries --continue for a continue drive', () => {
  const args = engine.engineArgs({ continueSession: true });
  assert.ok(args.indexOf('--continue') >= 0, '--continue present');
  assert.ok(args.indexOf('--resume') < 0, 'no --resume on a continue');
});
check('engineArgs carries --resume <id> for a resume drive', () => {
  const args = engine.engineArgs({ resume: 'sess-77' });
  const i = args.indexOf('--resume');
  assert.ok(i >= 0, '--resume present');
  assert.strictEqual(args[i + 1], 'sess-77', 'the session id rides next');
  assert.ok(args.indexOf('--continue') < 0, 'no --continue on a resume');
});
check('engineArgs carries --fork-session only alongside resume/continue', () => {
  assert.ok(
    engine.engineArgs({ resume: 'a', forkSession: true }).indexOf('--fork-session') >= 0,
    'fork rides a resume'
  );
  assert.ok(
    engine.engineArgs({ continueSession: true, forkSession: true }).indexOf('--fork-session') >= 0,
    'fork rides a continue'
  );
  assert.ok(
    engine.engineArgs({ forkSession: true }).indexOf('--fork-session') < 0,
    'a lone fork (no resume/continue) is dropped — conservative'
  );
});
check('engineArgs with no opts carries no resume flags (no regression)', () => {
  const args = engine.engineArgs();
  assert.ok(args.indexOf('--continue') < 0, 'no --continue by default');
  assert.ok(args.indexOf('--resume') < 0, 'no --resume by default');
  assert.ok(args.indexOf('--fork-session') < 0, 'no --fork-session by default');
});

// ---- 5. shell.renderResumeControl paints the three-mode surface ------------
check('renderResumeControl renders New / Continue / Resume, in-force pressed', () => {
  const html = shell.renderResumeControl({ mode: 'continue' }, null);
  assert.ok(/data-region="resume"/.test(html), 'the resume region is present');
  ['new', 'continue', 'resume'].forEach((m) =>
    assert.ok(new RegExp('data-resume="' + m + '"').test(html), m + ' is a button')
  );
  assert.ok(/data-resume-mode="continue"/.test(html), 'the region reflects the mode');
  assert.ok(
    /data-resume="continue"[^>]*aria-pressed="true"/.test(html),
    'the in-force button is pressed'
  );
});
check('renderResumeControl: Resume carries the selected id; disabled without one', () => {
  const withSel = shell.renderResumeControl({ mode: 'new' }, 'sess-sel');
  assert.ok(
    /data-resume="resume"[^>]*data-session-id="sess-sel"/.test(withSel),
    'the resume button carries the selected session id'
  );
  assert.ok(!/data-resume="resume"[^>]*disabled/.test(withSel), 'enabled with a selection');
  const noSel = shell.renderResumeControl({ mode: 'new' }, null);
  assert.ok(/data-resume="resume"[^>]*disabled/.test(noSel), 'disabled without a selection');
});
check('renderResumeControl: an unknown target -> new (conservative)', () => {
  const html = shell.renderResumeControl({ mode: 'bogus' }, null);
  assert.ok(/data-resume-mode="new"/.test(html), 'unknown -> new');
  assert.ok(
    /data-resume="new"[^>]*aria-pressed="true"/.test(html),
    'new is the pressed default'
  );
});
check('renderResumeControl escapes a hostile selected id', () => {
  const html = shell.renderResumeControl(
    { mode: 'new' },
    '"><script>x</script>'
  );
  assert.ok(!/<script>x<\/script>/.test(html), 'the hostile id is escaped, not injected');
});

// ---- 6. renderShell carries the resume surface + its handler ----------------
check('renderShell carries the resume control + set-resume handler', () => {
  const html = shell.renderShell({
    resumeTarget: { mode: 'continue' },
    selectedSessionId: 'sess-x',
  });
  assert.ok(/data-region="resume"/.test(html), 'the resume region is in the composer');
  assert.ok(/data-resume-mode="continue"/.test(html), 'the host-passed target is reflected');
  assert.ok(/ontum:set-resume/.test(html), 'the shell posts ontum:set-resume');
  assert.ok(/function wireResume/.test(html), 'the resume handler is wired');
});
check('renderShell with no resumeTarget shows new (no regression)', () => {
  const html = shell.renderShell({});
  assert.ok(/data-resume-mode="new"/.test(html), 'new is the standing target');
});

// ---- 7. extension.setResumeTarget records + normalizes ---------------------
check('setResumeTarget records continue / resume and normalizes a bad one', () => {
  const ext = loadExtension().ext;
  assert.deepStrictEqual(
    ext.getResumeTarget(),
    { mode: 'new', sessionId: null, fork: false },
    'starts on a fresh session'
  );
  assert.strictEqual(
    ext.setResumeTarget({ type: 'ontum:set-resume', mode: 'continue' }).mode,
    'continue',
    'continue recorded'
  );
  const r = ext.setResumeTarget({ type: 'ontum:set-resume', mode: 'resume', id: 'sess-42' });
  assert.strictEqual(r.mode, 'resume');
  assert.strictEqual(r.sessionId, 'sess-42', 'the resume id is recorded');
  assert.strictEqual(
    ext.setResumeTarget({ mode: 'bogus' }).mode,
    'new',
    'a bad target normalizes to new'
  );
});

// ---- 8 + 9. the host-free wiring: webview round-trip + the driven argv ------
function line(obj) {
  return JSON.stringify(obj) + '\n';
}
const SESSION = 'sess-resume-1';
const EVENTS = [
  { type: 'system', subtype: 'init', session_id: SESSION, tools: ['Read'] },
  {
    type: 'assistant',
    session_id: SESSION,
    message: { role: 'assistant', content: [{ type: 'text', text: 'Resumed.' }] },
  },
  {
    type: 'result',
    subtype: 'success',
    is_error: false,
    session_id: SESSION,
    total_cost_usd: 0.0001,
    result: 'Resumed.',
  },
];
const STREAM = EVENTS.map(line);

(async function wiring() {
  const loaded = loadExtension();
  const ext = loaded.ext;
  const registered = loaded.registered;
  const getHandler = loaded.getHandler;

  ext.activate({ subscriptions: [], extensionUri: { fsPath: __dirname } });
  registered[ext.OPEN_COMMAND]();
  const onMessage = getHandler();
  assert.ok(typeof onMessage === 'function', 'the webview message handler is wired');

  check('a webview ontum:set-resume message sets the target', () => {
    onMessage({ type: 'ontum:set-resume', mode: 'continue' });
    assert.strictEqual(ext.getResumeTarget().mode, 'continue', 'continue round-tripped');
    onMessage({ type: 'ontum:set-resume', mode: 'bogus' });
    assert.strictEqual(ext.getResumeTarget().mode, 'new', 'a bad target falls back to new');
  });

  check('selecting a session then "resume" (no id) resumes the selected one', () => {
    onMessage({ type: 'ontum:select-session', id: SESSION });
    onMessage({ type: 'ontum:set-resume', mode: 'resume' });
    const t = ext.getResumeTarget();
    assert.strictEqual(t.mode, 'resume', 'resume mode');
    assert.strictEqual(t.sessionId, SESSION, 'defaults to the selected session');
  });

  // Drive a turn under the resume target; the spawned argv must carry --resume.
  let fake = makeFakeEngine(STREAM);
  ext.__setSpawnForTest(fake.spawn);
  let reply = await ext.sendPrompt('keep going');
  await new Promise((r) => setImmediate(() => setImmediate(r)));
  check('sendPrompt drives the turn with --resume <selected session id>', () => {
    assert.strictEqual(fake.calls.length, 1, 'the engine was spawned once');
    const args = fake.calls[0].args;
    const i = args.indexOf('--resume');
    assert.ok(i >= 0, 'the driven argv carries --resume');
    assert.strictEqual(args[i + 1], SESSION, 'and it is the selected session id');
    assert.strictEqual(reply.isError, false, 'the resumed turn folded a clean reply');
  });

  // Switch to continue; the next driven argv must carry --continue, not --resume.
  onMessage({ type: 'ontum:set-resume', mode: 'continue' });
  fake = makeFakeEngine(STREAM);
  ext.__setSpawnForTest(fake.spawn);
  reply = await ext.sendPrompt('and again');
  await new Promise((r) => setImmediate(() => setImmediate(r)));
  check('sendPrompt drives a continue turn with --continue (not --resume)', () => {
    const args = fake.calls[0].args;
    assert.ok(args.indexOf('--continue') >= 0, 'the driven argv carries --continue');
    assert.ok(args.indexOf('--resume') < 0, 'and not --resume');
  });

  // Switch back to a fresh session; the next driven argv carries neither.
  onMessage({ type: 'ontum:set-resume', mode: 'new' });
  fake = makeFakeEngine(STREAM);
  ext.__setSpawnForTest(fake.spawn);
  reply = await ext.sendPrompt('fresh start');
  await new Promise((r) => setImmediate(() => setImmediate(r)));
  check('sendPrompt drives a new-session turn with no resume flags', () => {
    const args = fake.calls[0].args;
    assert.ok(args.indexOf('--continue') < 0, 'no --continue on a fresh session');
    assert.ok(args.indexOf('--resume') < 0, 'no --resume on a fresh session');
  });

  ext.__setSpawnForTest(null);
  ext.stopTail();
  ext.deactivate();

  console.log('\n' + passed + ' checks passed — row 16 evidence is green.');
  process.exit(0);
})().catch((err) => {
  console.error('\nFAILED:', err && err.stack ? err.stack : err);
  process.exit(1);
});

// ---- helpers ---------------------------------------------------------------

// loadExtension() -> require extension.js under a fake `vscode`, returning the
// module plus the captured webview message handler. Mirrors permission.test.js.
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

// makeFakeEngine(lines) -> a spawn that replays captured NDJSON (no model call)
// AND records each spawn's argv, so a test can assert the driven argv carries
// the chosen --resume/--continue. Mirrors permission.test.js.
function makeFakeEngine(lines) {
  const calls = [];
  function spawn(bin, args) {
    calls.push({ bin, args });
    const child = new EventEmitter();
    child.stdout = new EventEmitter();
    child.stderr = new EventEmitter();
    child.stdin = {
      write() { return true; },
      end() {},
    };
    setImmediate(function () {
      child.stdout.emit('data', Buffer.from(lines.join(''), 'utf8'));
      child.emit('close', 0);
    });
    return child;
  }
  return { spawn, calls };
}

// permission.test.js — proof for parity-checklist row 9.
//
// "Permission prompts (canUseTool / permission-mode surface)."
//
// Normal Claude Code gates a tool behind a permission decision: the permission
// MODE (default / acceptEdits / plan / bypassPermissions) sets the standing
// policy and per-tool allow/deny lists pre-authorize or forbid specific tools —
// the canUseTool policy a host expresses. The bridge spike resolved this row to
// `inherit`: the SAME `claude` CLI exposes exactly these levers, verified live
// on this machine (`claude --help` advertises `--permission-mode` with the four
// choices, plus `--allowedTools`/`--disallowedTools`). This test proves the
// ontum surface drives that inherited engine — host-free, no billed model call:
//   - engine.normalizePermissionMode validates a mode (unknown -> 'default', so
//     a typo/hostile value can never escalate to bypassPermissions);
//   - engine.engineArgs threads the chosen mode + allow/deny lists into the
//     drive channel's argv (so a turn actually runs under the human's policy);
//   - shell.renderPermissionControl + renderShell paint the composer's
//     permission <select> (all four modes, the current one selected) and carry
//     the `ontum:set-permission-mode` change handler;
//   - extension.setPermissionMode records + normalizes the chosen mode, and the
//     webview round-trip (a real onDidReceiveMessage `ontum:set-permission-mode`
//     message) sets the mode the NEXT turn runs under;
//   - sendPrompt drives a turn whose spawned argv carries `--permission-mode
//     <chosen>` — proven by a fake spawn that captures argv (no model call).
// HONEST SCOPE: this proves the permission-MODE surface + allow/deny policy
// (the canUseTool levers the --print CLI exposes, verified live) flow into the
// real engine argv, host-free. An interactive mid-turn canUseTool control-
// request callback is an SDK/persistent-session feature whose live event shape
// this CLI version does not advertise in --help; the surface governs
// permissions via the mode + allow/deny policy the CLI DOES expose, and a real
// billed turn that exercises a live prompt is a human's to run.
//
// Run: node vscode/ontum-surface/test/permission.test.js
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

console.log('row 9 — permission prompts (canUseTool / permission-mode surface)');

// ---- 1. the mode list mirrors the CLI's advertised choices ------------------
check('PERMISSION_MODES is exactly the four modes claude --help advertises', () => {
  assert.deepStrictEqual(engine.PERMISSION_MODES, [
    'default',
    'acceptEdits',
    'plan',
    'bypassPermissions',
  ]);
});

// ---- 2. normalizePermissionMode validates (conservative default) -----------
check('normalizePermissionMode passes valid modes, defaults the rest', () => {
  ['default', 'acceptEdits', 'plan', 'bypassPermissions'].forEach((m) =>
    assert.strictEqual(engine.normalizePermissionMode(m), m, m + ' passes through')
  );
  ['', 'bogus', 'BYPASS', null, undefined, 42, {}].forEach((m) =>
    assert.strictEqual(
      engine.normalizePermissionMode(m),
      'default',
      JSON.stringify(m) + ' -> default (never escalates)'
    )
  );
});

// ---- 3. engineArgs threads the mode into the drive channel argv ------------
check('engineArgs carries --permission-mode for each valid mode', () => {
  ['default', 'acceptEdits', 'plan', 'bypassPermissions'].forEach((m) => {
    const args = engine.engineArgs({ permissionMode: m });
    const i = args.indexOf('--permission-mode');
    assert.ok(i >= 0, '--permission-mode present for ' + m);
    assert.strictEqual(args[i + 1], m, 'the mode value is ' + m);
  });
});
check('engineArgs normalizes an unknown mode to default in the argv', () => {
  const args = engine.engineArgs({ permissionMode: 'bogus' });
  const i = args.indexOf('--permission-mode');
  assert.strictEqual(args[i + 1], 'default', 'a bad mode lands on default');
});
check('engineArgs with no opts still defaults the mode (no regression)', () => {
  const args = engine.engineArgs();
  const i = args.indexOf('--permission-mode');
  assert.strictEqual(args[i + 1], 'default');
});

// ---- 4. engineArgs threads allow/deny tool policy --------------------------
check('engineArgs emits --allowedTools / --disallowedTools when given', () => {
  const args = engine.engineArgs({
    allowedTools: ['Bash(git:*)', 'Edit'],
    disallowedTools: ['Bash(rm:*)'],
  });
  const a = args.indexOf('--allowedTools');
  assert.ok(a >= 0, '--allowedTools present');
  assert.strictEqual(args[a + 1], 'Bash(git:*)');
  assert.strictEqual(args[a + 2], 'Edit');
  const d = args.indexOf('--disallowedTools');
  assert.ok(d >= 0, '--disallowedTools present');
  assert.strictEqual(args[d + 1], 'Bash(rm:*)');
});
check('engineArgs omits allow/deny flags when the lists are empty/absent', () => {
  const args = engine.engineArgs({ allowedTools: [], disallowedTools: [] });
  assert.ok(args.indexOf('--allowedTools') < 0, 'no empty --allowedTools');
  assert.ok(args.indexOf('--disallowedTools') < 0, 'no empty --disallowedTools');
});

// ---- 5. shell.renderPermissionControl paints the four-mode selector --------
check('renderPermissionControl renders all four modes, the current one selected', () => {
  const html = shell.renderPermissionControl('plan');
  assert.ok(/class="ontum-permission-mode"/.test(html), 'the select is present');
  ['default', 'acceptEdits', 'plan', 'bypassPermissions'].forEach((m) =>
    assert.ok(new RegExp('value="' + m + '"').test(html), m + ' is an option')
  );
  assert.ok(/value="plan"[^>]*selected/.test(html), 'plan is the selected option');
  assert.ok(/data-mode="plan"/.test(html), 'the control reflects the current mode');
});
check('renderPermissionControl defaults an unknown mode to default (conservative)', () => {
  const html = shell.renderPermissionControl('bogus');
  assert.ok(/value="default"[^>]*selected/.test(html), 'unknown -> default selected');
  assert.ok(!/value="bypassPermissions"[^>]*selected/.test(html), 'never auto-selects bypass');
});

// ---- 6. renderShell carries the permission surface + its change handler -----
check('renderShell carries the permission select + set-permission-mode handler', () => {
  const html = shell.renderShell({ permissionMode: 'acceptEdits' });
  assert.ok(/class="ontum-permission-mode"/.test(html), 'the select is in the composer');
  assert.ok(/value="acceptEdits"[^>]*selected/.test(html), 'the host-passed mode is selected');
  assert.ok(/ontum:set-permission-mode/.test(html), 'the shell posts ontum:set-permission-mode');
  assert.ok(/addEventListener\('change'/.test(html), 'a change handler is wired');
});
check('renderShell with no permissionMode shows default (no regression)', () => {
  const html = shell.renderShell({});
  assert.ok(/value="default"[^>]*selected/.test(html), 'default is the standing mode');
});

// ---- 7. extension.setPermissionMode records + normalizes -------------------
check('setPermissionMode records a valid mode and normalizes a bad one', () => {
  const ext = loadExtension().ext;
  assert.strictEqual(ext.getPermissionMode(), 'default', 'starts conservative');
  assert.strictEqual(ext.setPermissionMode('plan'), 'plan', 'raw string accepted');
  assert.strictEqual(ext.getPermissionMode(), 'plan');
  assert.strictEqual(
    ext.setPermissionMode({ type: 'ontum:set-permission-mode', mode: 'acceptEdits' }),
    'acceptEdits',
    'message form accepted'
  );
  assert.strictEqual(ext.getPermissionMode(), 'acceptEdits');
  assert.strictEqual(ext.setPermissionMode('bogus'), 'default', 'a bad mode normalizes');
  assert.strictEqual(ext.getPermissionMode(), 'default', 'never escalates');
});

// ---- 8 + 9. the host-free wiring: webview round-trip + the driven argv ------
function line(obj) {
  return JSON.stringify(obj) + '\n';
}
const SESSION = 'sess-perm-1';
const PLAN_EVENTS = [
  { type: 'system', subtype: 'init', session_id: SESSION, tools: ['Read', 'Bash'] },
  {
    type: 'assistant',
    session_id: SESSION,
    message: { role: 'assistant', content: [{ type: 'text', text: 'Here is a plan.' }] },
  },
  {
    type: 'result',
    subtype: 'success',
    is_error: false,
    session_id: SESSION,
    total_cost_usd: 0.0002,
    result: 'Here is a plan.',
  },
];
const PLAN_STREAM = PLAN_EVENTS.map(line);

(async function wiring() {
  const loaded = loadExtension();
  const ext = loaded.ext;
  const registered = loaded.registered;
  const getHandler = loaded.getHandler;

  ext.activate({ subscriptions: [], extensionUri: { fsPath: __dirname } });
  registered[ext.OPEN_COMMAND]();
  const onMessage = getHandler();
  assert.ok(typeof onMessage === 'function', 'the webview message handler is wired');

  check('a webview ontum:set-permission-mode message sets the mode', () => {
    onMessage({ type: 'ontum:set-permission-mode', mode: 'plan' });
    assert.strictEqual(ext.getPermissionMode(), 'plan', 'the round-trip set plan');
    onMessage({ type: 'ontum:set-permission-mode', mode: 'nope' });
    assert.strictEqual(ext.getPermissionMode(), 'default', 'a bad mode falls back to default');
  });

  // Set plan mode, then drive a turn; the spawned argv must carry the mode.
  onMessage({ type: 'ontum:set-permission-mode', mode: 'plan' });
  const fake = makeFakeEngine(PLAN_STREAM);
  ext.__setSpawnForTest(fake.spawn);
  const reply = await ext.sendPrompt('outline the work');
  await new Promise((r) => setImmediate(() => setImmediate(r)));

  check('sendPrompt drives the turn under the chosen mode (--permission-mode plan)', () => {
    assert.strictEqual(fake.calls.length, 1, 'the engine was spawned once');
    const args = fake.calls[0].args;
    const i = args.indexOf('--permission-mode');
    assert.ok(i >= 0, 'the driven argv carries --permission-mode');
    assert.strictEqual(args[i + 1], 'plan', 'and it is the human-chosen plan mode');
    assert.strictEqual(reply.isError, false, 'the plan turn folded a clean reply');
    assert.strictEqual(reply.text, 'Here is a plan.', 'the reply text folded');
  });

  ext.__setSpawnForTest(null);
  ext.stopTail();
  ext.deactivate();

  console.log('\n' + passed + ' checks passed — row 9 evidence is green.');
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

// makeFakeEngine(lines) -> a spawn that replays captured NDJSON (no model call)
// AND records each spawn's argv, so a test can assert the driven argv carries
// the chosen --permission-mode.
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

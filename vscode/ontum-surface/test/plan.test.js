// plan.test.js — proof for parity-checklist row 11.
//
// "Plan mode."
//
// The bridge spike resolved this row to `inherit` (SPIKE-FINDINGS.md): the SAME
// `claude` CLI exposes `--permission-mode plan`, already threaded into the drive
// channel's argv by engine.engineArgs (row 9). Plan mode runs the engine
// READ-ONLY — it researches and drafts a plan but makes no edits — and when the
// plan is ready the engine calls the `ExitPlanMode` tool, presenting the plan
// and asking the human to approve proceeding. Normal Claude Code intercepts that
// tool call, renders the plan, and offers Approve / Keep-planning; approving
// EXITS plan mode so the work can run. This test proves the ontum surface does
// the same — host-free, with no real billed model call — by:
//   - plan.isExitPlanTool recognising the ExitPlanMode tool (and the legacy
//     snake_case form), and plan.planFromToolUse folding its tool_use into the
//     proposed plan text; a non-plan tool folds to null (stays a diff/JSON dump);
//   - plan.nextModeOnPlanDecision exiting plan mode on approve (to 'default',
//     never escalating to acceptEdits/bypass) and staying in 'plan' on keep;
//   - engine.engineArgs carrying `--permission-mode plan` (the inherited lever);
//   - shell.renderTranscriptRow painting an ExitPlanMode tool_use as a plan card
//     (data-plan-tool, the proposed plan, Approve + Keep buttons carrying the
//     tool id) instead of a raw JSON dump, all HTML-escaped — while a non-plan
//     tool still renders its row-8 diff / row-7 JSON pre (no regression);
//   - engine.foldReply folding a plan-proposing turn into a tool-use entry whose
//     rendered row IS the plan card (one source of truth with rows 3/5/7/8);
//   - the shell carrying the delegated `ontum:plan-decision` click handler + the
//     read-only plan-mode banner when the in-force mode is 'plan';
//   - the extension recording the Approve/Keep round-trip AND exiting plan mode
//     on approve: a webview `ontum:plan-decision` message transitions
//     getPermissionMode plan→default (approve) / stays plan (keep), and a
//     malformed decision is ignored.
// HONEST SCOPE: this proves the plan-mode surface — the read-only banner, the
// ExitPlanMode plan card, the approve/keep AFFORDANCE, its decision round-trip,
// and the exit-plan-mode permission transition — host-free, against the captured
// ExitPlanMode tool shape and the live-verified `--permission-mode plan` lever
// (the tool name is the one this CLI version's tool registry exposes). Actually
// running the approved work is the engine's job under the exited mode, and a
// real billed plan turn is a human's to run.
//
// Run: node vscode/ontum-surface/test/plan.test.js
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

const plan = require(path.join(__dirname, '..', 'plan.js'));
const shell = require(path.join(__dirname, '..', 'shell.js'));
const engine = require(path.join(__dirname, '..', 'engine.js'));

console.log('row 11 — plan mode');

// ---- 1. plan.isExitPlanTool recognises the exit-plan tool ------------------
check('isExitPlanTool recognises ExitPlanMode (and legacy snake_case), rejects rest', () => {
  ['ExitPlanMode', 'exit_plan_mode'].forEach((n) =>
    assert.ok(plan.isExitPlanTool(n), n + ' is the exit-plan tool')
  );
  ['Edit', 'Read', 'Bash', 'Task', ''].forEach((n) =>
    assert.ok(!plan.isExitPlanTool(n), n + ' is not the exit-plan tool')
  );
});

// ---- 2. plan.isPlanMode (normalized) ---------------------------------------
check('isPlanMode is true only for the (normalized) plan mode', () => {
  assert.ok(plan.isPlanMode('plan'), 'plan -> true');
  ['default', 'acceptEdits', 'bypassPermissions', 'bogus', '', null].forEach((m) =>
    assert.ok(!plan.isPlanMode(m), JSON.stringify(m) + ' -> false')
  );
});

// ---- 3. plan.planFromToolUse folds the ExitPlanMode tool_use ---------------
const planEntry = {
  kind: 'tool-use',
  name: 'ExitPlanMode',
  toolId: 'toolu_plan_1',
  input: { plan: '1. Read the module\n2. Add the function\n3. Test it' },
};
check('planFromToolUse folds an ExitPlanMode tool_use into { name, toolId, plan }', () => {
  const p = plan.planFromToolUse(planEntry);
  assert.strictEqual(p.name, 'ExitPlanMode');
  assert.strictEqual(p.toolId, 'toolu_plan_1');
  assert.strictEqual(p.plan, '1. Read the module\n2. Add the function\n3. Test it');
});
check('planFromToolUse returns null for a non-plan tool / non-tool entry', () => {
  assert.strictEqual(
    plan.planFromToolUse({ kind: 'tool-use', name: 'Edit', input: { plan: 'x' } }),
    null,
    'an Edit tool is not a plan'
  );
  assert.strictEqual(plan.planFromToolUse({ kind: 'assistant-text', text: 'hi' }), null);
  assert.strictEqual(plan.planFromToolUse(null), null);
});
check('planFromToolUse tolerates a missing/odd plan input (empty plan, never faked)', () => {
  assert.strictEqual(plan.planFromToolUse({ kind: 'tool-use', name: 'ExitPlanMode' }).plan, '');
  assert.strictEqual(
    plan.planFromToolUse({ kind: 'tool-use', name: 'ExitPlanMode', input: { plan: 42 } }).plan,
    '',
    'a non-string plan folds to empty'
  );
});

// ---- 4. plan.nextModeOnPlanDecision (exit on approve, conservative) --------
check('nextModeOnPlanDecision exits plan on approve (to default, never bypass)', () => {
  assert.strictEqual(plan.nextModeOnPlanDecision('approve', 'plan'), 'default', 'approve exits to default');
  assert.notStrictEqual(plan.nextModeOnPlanDecision('approve', 'plan'), 'bypassPermissions', 'never escalates');
  assert.notStrictEqual(plan.nextModeOnPlanDecision('approve', 'plan'), 'acceptEdits', 'never silently auto-accepts');
});
check('nextModeOnPlanDecision stays in plan on keep, and on an unknown decision', () => {
  assert.strictEqual(plan.nextModeOnPlanDecision('keep', 'plan'), 'plan', 'keep stays in plan');
  assert.strictEqual(plan.nextModeOnPlanDecision('bogus', 'plan'), 'plan', 'unknown keeps current plan');
  assert.strictEqual(plan.nextModeOnPlanDecision('bogus', 'acceptEdits'), 'acceptEdits', 'unknown keeps current (normalized)');
});

// ---- 5. engine.engineArgs carries the inherited --permission-mode plan -----
check('engineArgs threads --permission-mode plan (the inherited lever)', () => {
  const args = engine.engineArgs({ permissionMode: 'plan' });
  const i = args.indexOf('--permission-mode');
  assert.ok(i >= 0, '--permission-mode present');
  assert.strictEqual(args[i + 1], 'plan', 'the mode value is plan');
});

// ---- 6. shell.renderTranscriptRow paints a plan card -----------------------
check('renderTranscriptRow paints an ExitPlanMode tool_use as a plan card with approve/keep', () => {
  const html = shell.renderTranscriptRow(planEntry);
  assert.ok(/data-plan-tool="true"/.test(html), 'flagged a plan tool');
  assert.ok(/data-kind="tool-use"/.test(html), 'still a tool-use block (row 7 structure)');
  assert.ok(/Add the function/.test(html), 'the proposed plan text shows');
  assert.ok(
    /data-plan-decision="approve"[^>]*data-tool-id="toolu_plan_1"/.test(html),
    'an Approve button carries the tool id'
  );
  assert.ok(
    /data-plan-decision="keep"[^>]*data-tool-id="toolu_plan_1"/.test(html),
    'a Keep button carries the tool id'
  );
  assert.ok(!/<pre class="ontum-tool-input">/.test(html), 'NOT the raw JSON dump (that is row 7)');
});
check('the plan text is HTML-escaped (no markup injection from the plan)', () => {
  const html = shell.renderTranscriptRow({
    kind: 'tool-use',
    name: 'ExitPlanMode',
    toolId: 't',
    input: { plan: '<script>boom()</script>' },
  });
  assert.ok(!/<script>boom\(\)<\/script>/.test(html), 'raw script tag does not survive');
  assert.ok(/&lt;script&gt;/.test(html), 'angle brackets are escaped');
});
check('a non-plan tool still renders its row-8 diff / row-7 pre (no regression)', () => {
  const editHtml = shell.renderTranscriptRow({
    kind: 'tool-use',
    name: 'Edit',
    toolId: 'tE',
    input: { file_path: 'a.js', old_string: 'x', new_string: 'y' },
  });
  assert.ok(/data-diff-tool="true"/.test(editHtml), 'Edit still renders as a diff');
  assert.ok(!/data-plan-tool/.test(editHtml), 'Edit is not a plan card');
  const readHtml = shell.renderTranscriptRow({ kind: 'tool-use', name: 'Read', input: { file_path: 'a' } });
  assert.ok(/<pre class="ontum-tool-input">/.test(readHtml), 'Read keeps the row-7 JSON pre');
  assert.ok(!/data-plan-tool/.test(readHtml), 'Read is not a plan card');
});

// ---- 7. shell markup carries the plan handler + the read-only banner -------
check('renderShell carries the delegated plan-decision handler + message type', () => {
  const html = shell.renderShell({});
  assert.ok(/ontum:plan-decision/.test(html), 'the shell posts ontum:plan-decision');
  assert.ok(/closest\('button\.ontum-plan-decision'\)/.test(html), 'delegation via closest (later-spliced plan cards work)');
});
check('renderShell shows the read-only plan-mode banner only in plan mode', () => {
  const inPlan = shell.renderShell({ permissionMode: 'plan' });
  assert.ok(/class="ontum-plan-badge"/.test(inPlan), 'the plan banner element shows in plan mode');
  assert.ok(/data-region="plan-mode"/.test(inPlan), 'and it is the plan-mode region');
  const notPlan = shell.renderShell({ permissionMode: 'default' });
  assert.ok(!/class="ontum-plan-badge"/.test(notPlan), 'no plan banner element outside plan mode');
});

// ---- 8. engine.foldReply: a plan turn folds into a plan-rendered entry ------
function line(obj) {
  return JSON.stringify(obj) + '\n';
}
const SESSION = 'sess-plan-1';
const PLAN_ID = 'toolu_plan_turn';
const initEv = { type: 'system', subtype: 'init', session_id: SESSION, tools: ['Read', 'ExitPlanMode'] };
const assistantPlan = {
  type: 'assistant',
  session_id: SESSION,
  message: {
    role: 'assistant',
    content: [
      {
        type: 'tool_use',
        id: PLAN_ID,
        name: 'ExitPlanMode',
        input: { plan: '1. Add plan.js\n2. Wire the surface\n3. Test it' },
      },
    ],
  },
};
const resultEv = {
  type: 'result',
  subtype: 'success',
  is_error: false,
  session_id: SESSION,
  total_cost_usd: 0.0003,
  result: 'Proposed a plan.',
};
const PLAN_EVENTS = [initEv, assistantPlan, resultEv];
const PLAN_STREAM = PLAN_EVENTS.map(line);

check('foldReply folds a plan-proposing turn into a tool-use entry rendered AS a plan card', () => {
  const reply = engine.foldReply(PLAN_EVENTS);
  const call = reply.entries.find((e) => e.kind === 'tool-use');
  assert.ok(call, 'the turn carries a tool-use entry');
  assert.strictEqual(call.name, 'ExitPlanMode', 'it is the ExitPlanMode call');
  const html = shell.renderTranscriptRows(reply.entries);
  assert.ok(/data-plan-tool="true"/.test(html), 'the ExitPlanMode entry renders as a plan card (one source of truth)');
  assert.ok(/Wire the surface/.test(html), 'the proposed plan text is in the render');
  assert.ok(/data-plan-decision="approve"/.test(html) && /data-plan-decision="keep"/.test(html), 'approve + keep affordance present');
});

// ---- 9. extension: record the Approve/Keep round-trip + exit plan mode ------
check('recordPlanDecision records approve/keep, exits plan on approve, ignores malformed', () => {
  const ext = loadExtension().ext;
  assert.strictEqual(ext.getLastPlanDecision(), null, 'no decision yet');
  // Enter plan mode (as the permission surface would), then approve the plan.
  ext.setPermissionMode('plan');
  assert.strictEqual(ext.getPermissionMode(), 'plan', 'in plan mode');
  const approved = ext.recordPlanDecision({ type: 'ontum:plan-decision', decision: 'approve', toolId: 'tP' });
  assert.deepStrictEqual(approved, { toolId: 'tP', decision: 'approve', mode: 'default' }, 'approve recorded + exited to default');
  assert.strictEqual(ext.getPermissionMode(), 'default', 'approve EXITED plan mode');
  // Keep-planning stays in plan.
  ext.setPermissionMode('plan');
  const kept = ext.recordPlanDecision({ decision: 'keep', toolId: 'tK' });
  assert.deepStrictEqual(kept, { toolId: 'tK', decision: 'keep', mode: 'plan' }, 'keep recorded + stayed in plan');
  assert.strictEqual(ext.getPermissionMode(), 'plan', 'keep stayed in plan mode');
  // Malformed decisions are ignored and do not clobber the last good one.
  assert.strictEqual(ext.recordPlanDecision({ decision: 'maybe' }), null, 'a bad decision is ignored');
  assert.strictEqual(ext.recordPlanDecision(null), null, 'a null message is ignored');
  assert.deepStrictEqual(ext.getLastPlanDecision(), { toolId: 'tK', decision: 'keep', mode: 'plan' }, 'last good decision intact');
  assert.strictEqual(ext.getPermissionMode(), 'plan', 'the ignored decisions did not change the mode');
});

// ---- 10 + 11. the full host-free wiring (message round-trip + turn-reply) ---
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

  check('a webview ontum:plan-decision message exits plan mode (approve) via the real handler', () => {
    onMessage({ type: 'ontum:set-permission-mode', mode: 'plan' });
    assert.strictEqual(ext.getPermissionMode(), 'plan', 'the surface set plan mode');
    onMessage({ type: 'ontum:plan-decision', decision: 'approve', toolId: PLAN_ID });
    assert.deepStrictEqual(ext.getLastPlanDecision(), { toolId: PLAN_ID, decision: 'approve', mode: 'default' });
    assert.strictEqual(ext.getPermissionMode(), 'default', 'the round-trip exited plan mode');
  });

  // Drive a plan-proposing turn under plan mode; the reply html must carry the card.
  onMessage({ type: 'ontum:set-permission-mode', mode: 'plan' });
  const fake = makeFakeEngine(PLAN_STREAM);
  ext.__setSpawnForTest(fake.spawn);
  const reply = await ext.sendPrompt('outline the work');
  await new Promise((r) => setImmediate(() => setImmediate(r)));

  check('sendPrompt drives a plan turn (--permission-mode plan) whose reply carries the plan card', () => {
    assert.strictEqual(fake.calls.length, 1, 'the engine was spawned once');
    const args = fake.calls[0].args;
    const i = args.indexOf('--permission-mode');
    assert.strictEqual(args[i + 1], 'plan', 'the driven argv carries --permission-mode plan');
    const replies = posted.filter((m) => m && m.type === 'ontum:turn-reply');
    assert.strictEqual(replies.length, 1, 'exactly one turn-reply');
    const html = replies[0].html;
    assert.ok(/data-plan-tool="true"/.test(html), 'the ExitPlanMode rendered as a plan card in the reply');
    assert.ok(/data-plan-decision="approve"/.test(html) && /data-plan-decision="keep"/.test(html), 'approve + keep in the reply');
    assert.strictEqual(reply.entries.find((e) => e.kind === 'tool-use').name, 'ExitPlanMode', 'sendPrompt resolved the plan reply');
  });

  ext.__setSpawnForTest(null);
  ext.stopTail();
  ext.deactivate();

  console.log('\n' + passed + ' checks passed — row 11 evidence is green.');
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
// --permission-mode plan.
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

// engine.js — drive ONE turn through the inherited Claude engine (pure data +
// process layer, no `vscode`).
//
// Row 5 of the parity checklist: "Drive a new turn through the engine (send a
// prompt, get a reply)." The bridge spike (SPIKE-FINDINGS.md) proved the channel
// is INHERITED, not invented: the same `claude` CLI this repo runs on exposes a
// bidirectional stream-json driver —
//   --print --input-format stream-json   (inject a user message on stdin)
//   --output-format stream-json --include-partial-messages  (events on stdout)
// — and because it is the same binary reading the same cwd config, the loaded
// environment (tools/MCP/hooks/skills/settings) rides along (the init event's
// `tools` list is the proof). This module owns only:
//   1. encoding a user prompt into the stream-json input envelope,
//   2. the argv that opens that channel,
//   3. folding the output event stream into ONE turn's reply, and
//   4. spawning the engine and resolving when the turn's `result` lands.
// It stores nothing of its own — the reply is a FOLD of the engine's own events
// (blueprint §The law), exactly as transcript.js folds the on-disk records.
//
// The `spawn` is injectable (defaulting to child_process.spawn) so a plain
// `node` test can feed a FAKE engine process canned stream-json and assert the
// send→reply round-trip WITHOUT a real model call (no key, no cost, no network)
// — host-free, deterministic, checkable evidence. The live channel itself is
// grounded separately by `claude --help` advertising these exact flags on this
// machine (recorded in the row-5 evidence); driving a real billed turn is left
// to a human at the surface, not spent in an unattended test.
//
// Scope note (honest under-claim): this module folds a turn to its REPLY (row
// 5) AND interprets the live partials into incremental render instructions (row
// 6 — `partialDelta`/`assembleStream` below). `driveTurn`'s `onEvent` hook feeds
// the partials to the surface as they arrive. A real billed turn is still left
// to a human at the surface; the partial-stream handling is proven host-free
// against the captured event shapes the spike observed.

'use strict';

const { foldTranscript } = require('./transcript');

// encodeUserMessage(text) -> the single stream-json input line the CLI reads on
// stdin: a user-message envelope, newline-terminated (the channel is the same
// newline-delimited JSON the rest of the loop folds). Content is sent as an
// array of text blocks — the canonical Messages-API shape the engine accepts.
function encodeUserMessage(text) {
  const msg = {
    type: 'user',
    message: {
      role: 'user',
      content: [{ type: 'text', text: String(text == null ? '' : text) }],
    },
  };
  return JSON.stringify(msg) + '\n';
}

// --- row 9: the permission surface ------------------------------------------
// Normal Claude Code gates a tool behind a permission decision: the permission
// MODE (default / acceptEdits / plan / bypassPermissions) sets the standing
// policy, and per-tool allow/deny lists pre-authorize or forbid specific tools
// (the canUseTool policy a host expresses). The bridge spike resolved this row
// to `inherit`: the SAME `claude` CLI exposes exactly these levers, verified
// live on this machine — `claude --help` advertises
//   --permission-mode <mode>  (choices: acceptEdits, bypassPermissions, default, plan)
//   --allowedTools <tools...> / --disallowedTools <tools...>
//   --dangerously-skip-permissions
// so the surface does not invent a permission engine; it drives the inherited
// one. engineArgs() below threads the chosen mode + allow/deny policy into the
// drive channel's argv (so a turn actually runs under the human's choice), and
// normalizePermissionMode() keeps the surface conservative — an unknown mode
// falls back to 'default' (never silently to bypass).

// The permission modes the engine accepts, in the order the surface offers
// them (most restrictive intent first). Mirrors `claude --help` exactly.
const PERMISSION_MODES = ['default', 'acceptEdits', 'plan', 'bypassPermissions'];

// normalizePermissionMode(m) -> a valid permission mode, defaulting to
// 'default' for anything unrecognised. Conservative by construction: a typo or
// a hostile value can never escalate to 'bypassPermissions'.
function normalizePermissionMode(m) {
  return PERMISSION_MODES.indexOf(m) >= 0 ? m : 'default';
}

// engineArgs(opts) -> the CLI argv that opens the stream-json drive channel.
//   opts.permissionMode  — one of default|acceptEdits|plan|bypassPermissions
//                          (normalized; unknown -> 'default'). The surface stays
//                          conservative — row 9's permission-mode lever.
//   opts.allowedTools     — array of tool specs to pre-authorize (row 9's
//                          allow-list, e.g. ['Bash(git:*)','Edit']); emitted as
//                          --allowedTools when non-empty.
//   opts.disallowedTools  — array of tool specs to forbid (row 9's deny-list);
//                          emitted as --disallowedTools when non-empty.
//   opts.resume          — a session id to continue (row 16 territory; passed
//                          through here so a resumed turn uses the same channel).
//   opts.model           — optional model override (passed as --model).
// The flags mirror exactly what `claude --help` advertises (verified live).
function engineArgs(opts) {
  const o = opts || {};
  const args = [
    '--print',
    '--input-format',
    'stream-json',
    '--output-format',
    'stream-json',
    '--include-partial-messages',
    '--verbose', // stream-json needs verbose to emit the full event stream
  ];
  args.push('--permission-mode', normalizePermissionMode(o.permissionMode));
  // Row 9 — per-tool allow/deny policy (the canUseTool levers the CLI exposes).
  if (Array.isArray(o.allowedTools) && o.allowedTools.length) {
    args.push('--allowedTools', ...o.allowedTools.map(String));
  }
  if (Array.isArray(o.disallowedTools) && o.disallowedTools.length) {
    args.push('--disallowedTools', ...o.disallowedTools.map(String));
  }
  if (o.resume) {
    args.push('--resume', String(o.resume));
    if (o.forkSession) args.push('--fork-session');
  }
  if (o.model) args.push('--model', String(o.model));
  return args;
}

// foldReply(events) -> the ONE turn's reply, folded from the output events.
//   { sessionId, tools, entries, text, isError, subtype, cost, usage,
//     durationMs, numTurns }
// - sessionId/tools come from the `system/init` event (tools proves the loaded
//   environment is inherited — the spike's central claim).
// - entries are folded from the `assistant` (and replayed `user`) message events
//   via the SAME foldTranscript used for on-disk transcripts, so a driven turn
//   renders identically to a read one (one source of truth).
// - text is the turn's final assistant prose: the terminal `result` event's
//   `result` string when present, else the concatenation of assistant-text
//   entries (an honest fallback, never a fabricated reply).
// - isError/subtype/cost/usage/durationMs/numTurns come from the `result` event
//   (row 18's usage/cost ride here too). No result event -> isError true with
//   subtype 'no-result' (the engine never closed the turn — absence is reported,
//   not papered over).
function foldReply(events) {
  const list = Array.isArray(events) ? events : [];
  let sessionId = null;
  let tools = null;
  let result = null;
  const messageRecords = [];
  for (const ev of list) {
    if (!ev || typeof ev !== 'object') continue;
    if (!sessionId && ev.session_id) sessionId = ev.session_id;
    if (ev.type === 'system' && ev.subtype === 'init') {
      if (Array.isArray(ev.tools)) tools = ev.tools;
      continue;
    }
    if (ev.type === 'assistant' || ev.type === 'user') {
      // A full turn message event carries { message:{ role, content } } — the
      // exact record shape foldTranscript already knows how to fold.
      if (ev.message) messageRecords.push({ type: ev.type, message: ev.message });
      continue;
    }
    if (ev.type === 'result') {
      result = ev; // the terminal event — last one wins
      continue;
    }
    // stream_event partials and anything else are ignored here (row 6 will
    // consume partials for incremental rendering).
  }

  const entries = foldTranscript(messageRecords);
  const assistantText = entries
    .filter((e) => e.kind === 'assistant-text')
    .map((e) => e.text)
    .join('\n');

  let text;
  let isError;
  let subtype;
  let cost = null;
  let usage = null;
  let durationMs = null;
  let numTurns = null;
  if (result) {
    subtype = result.subtype || (result.is_error ? 'error' : 'success');
    isError = result.is_error === true || subtype !== 'success';
    text =
      typeof result.result === 'string' && result.result !== ''
        ? result.result
        : assistantText;
    if (typeof result.total_cost_usd === 'number') cost = result.total_cost_usd;
    if (result.usage && typeof result.usage === 'object') usage = result.usage;
    if (typeof result.duration_ms === 'number') durationMs = result.duration_ms;
    if (typeof result.num_turns === 'number') numTurns = result.num_turns;
  } else {
    subtype = 'no-result';
    isError = true;
    text = assistantText;
  }

  return {
    sessionId,
    tools,
    entries,
    text,
    isError,
    subtype,
    cost,
    usage,
    durationMs,
    numTurns,
  };
}

// --- row 6: incremental streaming of the live turn --------------------------
// With --include-partial-messages the engine emits `stream_event` partials that
// wrap the Anthropic streaming events (content_block_start / _delta / _stop).
// They let the surface paint the assistant's text + thinking AS IT ARRIVES,
// before the turn's terminal `result` lands. The partials are a LIVE PREVIEW,
// not a second source of truth: the authoritative final render is still
// foldReply's folded entries (the surface replaces the preview with them when
// the turn closes), so a streamed block and a folded one never disagree.

// blockKind(t) -> the render kind for a streamed content-block type, or null
// for kinds we do not stream. The kinds are the SAME ones
// transcript.foldTranscript emits, so a streamed block wears the same data-kind
// as its eventual folded twin. `tool_use` is streamed as of row 7 (the live
// "calling tool X…" preview); its accumulating input arrives as
// `input_json_delta` partials (see partialDelta below).
function blockKind(t) {
  if (t === 'text') return 'assistant-text';
  if (t === 'thinking') return 'assistant-thinking';
  if (t === 'tool_use') return 'tool-use';
  return null;
}

// partialDelta(event) -> ONE incremental render instruction, or null when the
// event is not a renderable partial. The instruction is intentionally tiny so
// the surface can apply it directly to a per-index block:
//   { phase:'start', index, kind }        — a new assistant block opened
//   { phase:'start', index, kind:'tool-use', name } — a tool call opened
//   { phase:'delta', index, kind, text }  — text/thinking/input appended to it
//   { phase:'stop',  index }              — the block closed
// kind is 'assistant-text', 'assistant-thinking', or 'tool-use' (row 7). The
// instruction is tolerant of both the wrapped (`{type:'stream_event',
// event:{...}}`) and the bare (`{type:'content_block_*', ...}`) forms. The kind
// on a delta is derived from the delta itself (text_delta / thinking_delta /
// input_json_delta), so a delta still renders correctly even if its
// content_block_start was torn or dropped. A tool_use start carries the tool
// `name` (so the surface can paint "calling tool X…" immediately); its
// accumulating input arrives as `input_json_delta` partials (the raw streaming
// JSON, replaced by the folded, pretty-printed input when the turn closes).
function partialDelta(event) {
  if (!event || typeof event !== 'object') return null;
  const inner =
    event.type === 'stream_event' && event.event ? event.event : event;
  if (!inner || typeof inner !== 'object') return null;
  const index = typeof inner.index === 'number' ? inner.index : 0;
  if (inner.type === 'content_block_start') {
    const cb = inner.content_block || {};
    const kind = blockKind(cb.type);
    if (!kind) return null;
    const out = { phase: 'start', index, kind };
    // A tool call announces its name at the start — carry it so the live
    // preview can label the block before any input has streamed.
    if (kind === 'tool-use' && typeof cb.name === 'string') out.name = cb.name;
    return out;
  }
  if (inner.type === 'content_block_delta') {
    const d = inner.delta || {};
    if (d.type === 'text_delta' && typeof d.text === 'string') {
      return { phase: 'delta', index, kind: 'assistant-text', text: d.text };
    }
    if (d.type === 'thinking_delta' && typeof d.thinking === 'string') {
      return {
        phase: 'delta',
        index,
        kind: 'assistant-thinking',
        text: d.thinking,
      };
    }
    // A tool call's input streams as raw JSON fragments (row 7).
    if (d.type === 'input_json_delta' && typeof d.partial_json === 'string') {
      return { phase: 'delta', index, kind: 'tool-use', text: d.partial_json };
    }
    return null;
  }
  if (inner.type === 'content_block_stop') {
    return { phase: 'stop', index };
  }
  return null;
}

// assembleStream(events) -> fold a list of events into the ordered live blocks
// the partials describe: [{ index, kind, text }] in first-seen order, each
// block's text the concatenation of its deltas. A tool-use block also carries
// `name` (row 7); text/thinking blocks keep the bare { index, kind, text }
// shape (no `name` key) so the row-6 preview==fold equality holds. Pure (no
// process), so a test can prove the partials reconstruct the same prose/input
// the final fold yields.
function assembleStream(events) {
  const list = Array.isArray(events) ? events : [];
  const byIndex = new Map();
  const order = [];
  for (const ev of list) {
    const d = partialDelta(ev);
    if (!d) continue;
    let block = byIndex.get(d.index);
    if (!block) {
      block = { index: d.index, kind: d.kind || 'assistant-text', text: '' };
      byIndex.set(d.index, block);
      order.push(block);
    }
    if (d.kind) block.kind = d.kind;
    if (typeof d.name === 'string') block.name = d.name;
    if (d.phase === 'delta') block.text += d.text;
  }
  return order;
}

// driveTurn(opts) -> Promise<reply>. Spawns the engine on the stream-json
// channel, writes the encoded prompt to stdin, collects the newline-delimited
// output events (torn-tail tolerant, the same fold law as the store), and
// resolves with foldReply(events) once the process closes.
//   opts.prompt          — the user text to send (required).
//   opts.cwd             — working dir for the engine (defaults to process.cwd).
//   opts.bin             — the engine binary (default 'claude').
//   opts.spawn           — injectable spawn (default child_process.spawn) so a
//                          test can feed a fake process — no real model call.
//   opts.onEvent(ev)     — optional per-event hook (row 6 will stream on it).
//   opts.permissionMode/resume/forkSession/model — forwarded to engineArgs.
// Rejects only on a spawn/process error; a turn that ends in an engine error
// resolves with isError:true so the surface can render the failure honestly.
function driveTurn(opts) {
  const o = opts || {};
  const spawnFn = o.spawn || require('child_process').spawn;
  const bin = o.bin || 'claude';
  const args = engineArgs(o);

  return new Promise((resolve, reject) => {
    let child;
    try {
      child = spawnFn(bin, args, {
        cwd: o.cwd || process.cwd(),
        stdio: ['pipe', 'pipe', 'pipe'],
      });
    } catch (err) {
      reject(err);
      return;
    }

    const events = [];
    let stdoutBuf = '';
    let stderr = '';
    let settled = false;

    function consumeLine(line) {
      const s = line.trim();
      if (!s) return;
      let ev;
      try {
        ev = JSON.parse(s);
      } catch (_) {
        return; // a torn line — never fatal (same tolerance as the store fold)
      }
      events.push(ev);
      if (typeof o.onEvent === 'function') {
        try {
          o.onEvent(ev);
        } catch (_) {
          /* a bad hook must not break the drive */
        }
      }
    }

    if (child.stdout && typeof child.stdout.on === 'function') {
      child.stdout.on('data', (chunk) => {
        stdoutBuf += chunk.toString('utf8');
        let nl;
        while ((nl = stdoutBuf.indexOf('\n')) >= 0) {
          const line = stdoutBuf.slice(0, nl);
          stdoutBuf = stdoutBuf.slice(nl + 1);
          consumeLine(line);
        }
      });
    }
    if (child.stderr && typeof child.stderr.on === 'function') {
      child.stderr.on('data', (chunk) => {
        stderr += chunk.toString('utf8');
      });
    }

    child.on('error', (err) => {
      if (settled) return;
      settled = true;
      reject(err);
    });

    child.on('close', (code) => {
      if (settled) return;
      settled = true;
      // Flush a trailing complete line with no closing newline (best-effort).
      consumeLine(stdoutBuf);
      const reply = foldReply(events);
      reply.exitCode = typeof code === 'number' ? code : null;
      reply.stderr = stderr;
      resolve(reply);
    });

    // Send the prompt down the channel and close stdin so the engine runs the
    // single turn and exits (the --print one-shot contract).
    try {
      if (child.stdin && typeof child.stdin.write === 'function') {
        child.stdin.write(encodeUserMessage(o.prompt));
        if (typeof child.stdin.end === 'function') child.stdin.end();
      }
    } catch (err) {
      if (!settled) {
        settled = true;
        reject(err);
      }
    }
  });
}

module.exports = {
  encodeUserMessage,
  engineArgs,
  foldReply,
  partialDelta,
  assembleStream,
  driveTurn,
  // Row 9 — the permission surface (mode normalization + the mode list).
  PERMISSION_MODES,
  normalizePermissionMode,
};

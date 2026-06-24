// transcript.js — read ONE session's transcript and fold it into ordered,
// render-ready entries (pure data layer, no `vscode`).
//
// Row 3 of the parity checklist: "Read + render a transcript (user / assistant
// / tool-use / tool-result)." This module owns only the *reading + folding* of a
// single `~/.claude/projects/<encoded-cwd>/<session-id>.jsonl` file into the
// ordered list of things a viewer paints. It is a FOLD (blueprint §The law): it
// derives entries from the engine's own records and stores nothing of its own.
//
// No `vscode` dependency, so a plain `node` test can point it at a fake file and
// assert exactly what it returns — host-free, checkable evidence.
//
// The record/block shapes (observed in the live store + the Messages-API shape
// the engine writes through, see SPIKE-FINDINGS.md):
//   - a turn record is `{ type:'user'|'assistant', timestamp, message:{ role,
//     content } }` where `content` is a string OR an array of blocks;
//   - assistant blocks: `{type:'text',text}`, `{type:'thinking',thinking}`,
//     `{type:'tool_use',id,name,input}`;
//   - a tool result rides in a USER turn as `{type:'tool_result',tool_use_id,
//     content,is_error}`, content a string or an array of `{type:'text',text}`.
// A torn final line (live-tail caught mid-append) is tolerated by the shared
// parseTranscript (sessions.js) — bad lines are counted, not thrown.

'use strict';

const fs = require('fs');
const path = require('path');
const { parseTranscript } = require('./sessions');

// fileForSession(dir, id) -> the transcript file path for a session id.
function fileForSession(dir, id) {
  return path.join(dir, String(id) + '.jsonl');
}

// toolResultText(content) -> a flat string from a tool_result's content, which
// may be a plain string or an array of content blocks.
function toolResultText(content) {
  if (typeof content === 'string') return content;
  if (Array.isArray(content)) {
    return content
      .map((b) => (b && typeof b.text === 'string' ? b.text : ''))
      .filter((s) => s !== '')
      .join('\n');
  }
  return '';
}

// entriesFromMessage(role, content) -> zero or more ordered render entries.
// Each entry: { role, kind, ... } where kind is one of
//   'user-text' | 'assistant-text' | 'assistant-thinking' | 'tool-use' |
//   'tool-result'. Empty/whitespace-only text blocks are dropped (no fake rows).
function entriesFromMessage(role, content) {
  const out = [];
  if (typeof content === 'string') {
    const t = content.trim();
    if (t) {
      out.push({
        role,
        kind: role === 'user' ? 'user-text' : 'assistant-text',
        text: content,
      });
    }
    return out;
  }
  if (!Array.isArray(content)) return out;
  for (const b of content) {
    if (!b || typeof b !== 'object') continue;
    switch (b.type) {
      case 'text':
        if (typeof b.text === 'string' && b.text.trim()) {
          out.push({
            role,
            kind: role === 'user' ? 'user-text' : 'assistant-text',
            text: b.text,
          });
        }
        break;
      case 'thinking':
        if (typeof b.thinking === 'string' && b.thinking.trim()) {
          out.push({ role, kind: 'assistant-thinking', text: b.thinking });
        }
        break;
      case 'tool_use':
        out.push({
          role,
          kind: 'tool-use',
          name: typeof b.name === 'string' ? b.name : '',
          toolId: typeof b.id === 'string' ? b.id : '',
          input: b.input,
        });
        break;
      case 'tool_result':
        out.push({
          role,
          kind: 'tool-result',
          toolUseId: typeof b.tool_use_id === 'string' ? b.tool_use_id : '',
          isError: b.is_error === true,
          text: toolResultText(b.content),
        });
        break;
      default:
        // Unknown block types are skipped, not faked — absence is information.
        break;
    }
  }
  return out;
}

// foldTranscript(records) -> ordered entries across all user/assistant turns.
// Non-turn records (system, summary, …) carry no rendered message and are
// skipped. Order is preserved (the file order = the conversation order).
function foldTranscript(records) {
  const out = [];
  for (const r of records) {
    if (!r || typeof r !== 'object') continue;
    if (r.type !== 'user' && r.type !== 'assistant') continue;
    if (!r.message) continue;
    const role = r.message.role || r.type;
    const entries = entriesFromMessage(role, r.message.content);
    for (const e of entries) {
      e.ts = r.timestamp || null;
      out.push(e);
    }
  }
  return out;
}

// readTranscript({ file }) -> { entries, torn }. A missing/unreadable file
// yields an honest empty transcript (no throw); a torn tail is counted.
function readTranscript(opts) {
  const o = opts || {};
  if (!o.file) return { entries: [], torn: 0 };
  let text;
  try {
    text = fs.readFileSync(o.file, 'utf8');
  } catch (_) {
    return { entries: [], torn: 0 };
  }
  const parsed = parseTranscript(text);
  return { entries: foldTranscript(parsed.records), torn: parsed.torn };
}

module.exports = {
  readTranscript,
  foldTranscript,
  entriesFromMessage,
  toolResultText,
  fileForSession,
};

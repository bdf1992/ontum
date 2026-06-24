// sessions.js — the transcript-store reader (pure data layer, no `vscode`).
//
// Row 2 of the parity checklist: "List local sessions from the transcript
// store; select one." This module owns only the *reading* of that store — the
// `~/.claude/projects/<encoded-cwd>/<session-id>.jsonl` files the engine writes.
// It is a FOLD (blueprint §The law): it derives session metadata from the
// engine's own files and stores nothing of its own.
//
// It has no `vscode` dependency so a plain `node` test can point it at a fake
// store directory and assert what it returns — honest, host-free evidence.
//
// The store shape (observed, see SPIKE-FINDINGS.md): each file is one session,
// newline-delimited JSON, one record per line. A record carries `sessionId`,
// `cwd`, `gitBranch`, `timestamp`, a `type` (system/user/assistant/…) and, for
// turns, a `message` with `{ role, content }` where content is a string OR an
// array of blocks ({ type, text, … }). A half-written final line (a live tail
// caught mid-append) is tolerated, not fatal.

'use strict';

const fs = require('fs');
const os = require('os');
const path = require('path');

// encodeProjectDir(cwd) -> the projects/ subdir name the engine uses for a cwd.
// The engine maps every non-alphanumeric char in the absolute path to '-'
// (observed: `C:\Users\bdf19\ontum-overnight` -> `C--Users-bdf19-ontum-overnight`).
function encodeProjectDir(cwd) {
  return String(cwd).replace(/[^a-zA-Z0-9]/g, '-');
}

// storeDirFor(cwd, home) -> absolute path to the transcript store for a cwd.
function storeDirFor(cwd, home) {
  const h = home || os.homedir();
  return path.join(h, '.claude', 'projects', encodeProjectDir(cwd));
}

// textOf(content) -> a flat preview string from a message.content value, which
// may be a plain string or an array of content blocks.
function textOf(content) {
  if (typeof content === 'string') return content.trim();
  if (Array.isArray(content)) {
    return content
      .map((b) => (b && typeof b.text === 'string' ? b.text : ''))
      .join(' ')
      .replace(/\s+/g, ' ')
      .trim();
  }
  return '';
}

// parseTranscript(text) -> { records, torn }. Newline-delimited JSON, tolerant
// of a torn final line (the live-tail case): bad lines are counted, not thrown.
function parseTranscript(text) {
  const lines = String(text).split('\n');
  const records = [];
  let torn = 0;
  for (const line of lines) {
    const s = line.trim();
    if (!s) continue;
    try {
      records.push(JSON.parse(s));
    } catch (_) {
      torn++;
    }
  }
  return { records, torn };
}

// summarize(records) -> session metadata derived purely from the records.
function summarize(records) {
  let id = null;
  let cwd = null;
  let gitBranch = null;
  let firstUserText = '';
  let messageCount = 0;
  let firstTs = null;
  let lastTs = null;
  for (const r of records) {
    if (!r || typeof r !== 'object') continue;
    if (!id && r.sessionId) id = r.sessionId;
    if (!cwd && r.cwd) cwd = r.cwd;
    if (!gitBranch && r.gitBranch) gitBranch = r.gitBranch;
    if (r.timestamp) {
      if (!firstTs) firstTs = r.timestamp;
      lastTs = r.timestamp;
    }
    if (r.type === 'user' || r.type === 'assistant') {
      messageCount++;
      if (!firstUserText && r.type === 'user' && r.message) {
        const t = textOf(r.message.content);
        // Skip tool-result-only or empty user turns when naming the session.
        if (t) firstUserText = t;
      }
    }
  }
  return { id, cwd, gitBranch, firstUserText, messageCount, firstTs, lastTs };
}

// listSessions({ dir, limit }) -> [session], newest-first by file mtime.
// Each session: { id, file, mtimeMs, sizeBytes, messageCount, title, cwd,
// gitBranch, firstTs, lastTs, torn }. A missing/empty store yields [].
function listSessions(opts) {
  const o = opts || {};
  const dir = o.dir;
  if (!dir) return [];
  let names;
  try {
    names = fs.readdirSync(dir);
  } catch (_) {
    return []; // no store yet for this cwd — an honest empty list, not an error
  }
  const out = [];
  for (const name of names) {
    if (!name.endsWith('.jsonl')) continue;
    const file = path.join(dir, name);
    let stat;
    try {
      stat = fs.statSync(file);
    } catch (_) {
      continue;
    }
    if (!stat.isFile()) continue;
    let text;
    try {
      text = fs.readFileSync(file, 'utf8');
    } catch (_) {
      continue;
    }
    const parsed = parseTranscript(text);
    const meta = summarize(parsed.records);
    out.push({
      id: meta.id || name.replace(/\.jsonl$/, ''),
      file,
      mtimeMs: stat.mtimeMs,
      sizeBytes: stat.size,
      messageCount: meta.messageCount,
      title: (meta.firstUserText || '(no prompt yet)').slice(0, 120),
      cwd: meta.cwd,
      gitBranch: meta.gitBranch,
      firstTs: meta.firstTs,
      lastTs: meta.lastTs,
      torn: parsed.torn,
    });
  }
  out.sort((a, b) => b.mtimeMs - a.mtimeMs);
  if (o.limit && o.limit > 0) return out.slice(0, o.limit);
  return out;
}

module.exports = {
  listSessions,
  parseTranscript,
  summarize,
  textOf,
  encodeProjectDir,
  storeDirFor,
};

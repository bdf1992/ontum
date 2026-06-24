// livetail.js — incrementally tail ONE session's transcript as the engine
// appends to it (pure data layer, no `vscode`).
//
// Row 4 of the parity checklist: "Live-tail the active session as it appends."
// Rows 2–3 read a whole transcript once; this module owns the *delta*: given a
// byte offset already consumed, it reads only the bytes written since and folds
// the newly-completed lines into the same render-ready entries transcript.js
// produces. It is a FOLD (blueprint §The law): it derives the new entries from
// the engine's own appended bytes and stores nothing of its own — the offset is
// the caller's to hold.
//
// No `vscode` dependency, so a plain `node` test can append to a fake file and
// assert exactly which new entries (and which advanced offset) come back —
// host-free, checkable evidence.
//
// The tail law (why byte offsets, why "complete lines only"):
//   - The engine appends newline-delimited JSON. A read can catch the file
//     mid-append, so the FINAL line may be torn (half-written). We consume only
//     up to the last '\n' — everything after it is an incomplete line left for
//     a later tick, when its closing newline has arrived. This is the classic
//     safe-tail invariant and it makes the torn-tail case a non-event, not an
//     error.
//   - Offsets are BYTES (the file is UTF-8 and multibyte chars must not split a
//     line boundary count), so we work on a Buffer, not a decoded string.
//   - If the file shrank below the held offset (truncation / rotation), we
//     reset to the top and flag `reset` so the caller can repaint rather than
//     append into a stale list.

'use strict';

const fs = require('fs');
const { parseTranscript, listSessions } = require('./sessions');
const { foldTranscript } = require('./transcript');

const NEWLINE = 0x0a; // '\n'

// tailTranscript({ file, fromOffset }) -> { entries, nextOffset, torn, reset }.
//   entries    — the folded render entries from lines completed since fromOffset
//                (empty when nothing new, or only a torn line, has arrived).
//   nextOffset — the byte offset the caller should hold for the next tail; it
//                advances only past COMPLETE lines, so a torn tail is re-read,
//                never skipped.
//   torn       — count of malformed complete lines in the consumed slice (0 in
//                the normal append case; a torn FINAL line is not counted here
//                because it is not consumed).
//   reset      — true when the file was shorter than fromOffset (truncated /
//                rotated) and we re-read from the top; the caller should repaint.
// A missing/unreadable file yields no entries and holds the offset (no throw).
function tailTranscript(opts) {
  const o = opts || {};
  if (!o.file) return { entries: [], nextOffset: 0, torn: 0, reset: false };
  const from =
    typeof o.fromOffset === 'number' && o.fromOffset > 0 ? o.fromOffset : 0;

  let buf;
  try {
    buf = fs.readFileSync(o.file); // Buffer (no encoding) — byte-accurate
  } catch (_) {
    return { entries: [], nextOffset: from, torn: 0, reset: false };
  }

  let start = from;
  let reset = false;
  if (from > buf.length) {
    // The file is shorter than what we already consumed: it was truncated or
    // rotated. Re-read from the top and tell the caller to repaint.
    start = 0;
    reset = true;
  }
  if (start >= buf.length) {
    // Nothing new since last tail.
    return { entries: [], nextOffset: buf.length, torn: 0, reset };
  }

  const slice = buf.slice(start);
  const lastNl = slice.lastIndexOf(NEWLINE);
  if (lastNl < 0) {
    // A partial line with no closing newline yet — consume nothing, hold the
    // offset so the line is re-read once it is complete.
    return { entries: [], nextOffset: start, torn: 0, reset };
  }

  const completeBuf = slice.slice(0, lastNl + 1);
  const text = completeBuf.toString('utf8');
  const parsed = parseTranscript(text);
  const entries = foldTranscript(parsed.records);
  return {
    entries,
    nextOffset: start + completeBuf.length,
    torn: parsed.torn,
    reset,
  };
}

// activeSession({ dir }) -> the newest session in the store (the one being
// written right now), or null when the store is empty/unreadable. "Active" =
// most-recently-modified file, which is what listSessions already sorts on.
function activeSession(opts) {
  const o = opts || {};
  if (!o.dir) return null;
  const list = listSessions({ dir: o.dir, limit: 1 });
  return list.length ? list[0] : null;
}

module.exports = {
  tailTranscript,
  activeSession,
};

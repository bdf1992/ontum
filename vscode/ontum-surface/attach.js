// attach.js — recognise, read, and encode image / file attachments into the
// turn's user message (pure data + fs layer, no `vscode`).
//
// Row 15 of the parity checklist: "Image / file attach." Normal Claude Code
// lets you attach an image (drag/paste/pick) or a file to a message; the
// attachment rides the turn as a content block in the SAME Messages-API user
// envelope row 5 drives — an image as a base64 `image` block, a PDF as a
// base64 `document` block, a text file inlined as a marked `text` block. The
// engine reads the attachment; the surface does not re-implement vision. So
// this module owns only the SURFACE of attachments:
//   1. CLASSIFY an attachment by name → image / document / text + its media
//      type (classifyAttachment / mediaTypeForImage / isImageFile);
//   2. READ it off disk into a bounded record (readAttachment), base64 for an
//      image/document and utf8 for a text file, refusing an oversized/missing
//      file with an honest error (never throws, never silently truncates);
//   3. ENCODE it into the Messages-API content block(s) the engine accepts
//      (attachmentBlock / attachmentBlocks), which engine.encodeUserMessage
//      folds ahead of the typed text.
//
// Reading is a FOLD of the on-disk bytes (blueprint §The law: paint what is
// there, invent nothing), so it is proven host-free against real temp files —
// exactly as sessions.js folds the transcript store and mentions.js the
// workspace tree. The LIVE file picker (a drag/paste/open dialog) comes from
// the VS Code host (window.showOpenDialog); this module is proven against a
// path, not a host. The engine remains the authority on what an attachment
// means; the surface classifies + reads + encodes it onto the turn.

'use strict';

const fs = require('fs');
const path = require('path');

// The image extensions Claude accepts as vision input, mapped to the media
// type the base64 `image` block declares. (The Anthropic image input set:
// png / jpeg / gif / webp.)
const IMAGE_MEDIA_TYPES = {
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif': 'image/gif',
  '.webp': 'image/webp',
};

// Non-image binaries the API accepts as a `document` block (base64 source).
const DOC_MEDIA_TYPES = {
  '.pdf': 'application/pdf',
};

// The per-attachment read cap. The Anthropic image input limit is ~5 MB per
// image; cap every read at that so a huge file never bloats the stdin envelope
// (or hangs the host). An oversized file is REFUSED with an honest error, not
// silently truncated (a truncated image/file is worse than an absent one).
const MAX_ATTACH_BYTES = 5 * 1024 * 1024;

// extOf(name) -> the lower-cased extension (incl. the dot), or '' when none.
function extOf(name) {
  return path.extname(String(name == null ? '' : name)).toLowerCase();
}

// mediaTypeForImage(name) -> the image media type for a file name, or null when
// the extension is not a supported image type.
function mediaTypeForImage(name) {
  return IMAGE_MEDIA_TYPES[extOf(name)] || null;
}

// isImageFile(name) -> true when the name has a supported image extension.
function isImageFile(name) {
  return mediaTypeForImage(name) != null;
}

// classifyAttachment(name) -> { kind, mediaType } for a file name:
//   - an image extension          -> { kind:'image',    mediaType:'image/png' … }
//   - a document extension (.pdf)  -> { kind:'document', mediaType:'application/pdf' }
//   - anything else                -> { kind:'text',     mediaType:'text/plain' }
// Conservative by construction: an unknown type is treated as text (inlined as
// a marked text block), never guessed to be an image the engine would reject.
function classifyAttachment(name) {
  const img = mediaTypeForImage(name);
  if (img) return { kind: 'image', mediaType: img };
  const doc = DOC_MEDIA_TYPES[extOf(name)];
  if (doc) return { kind: 'document', mediaType: doc };
  return { kind: 'text', mediaType: 'text/plain' };
}

// readAttachment(opts) -> a bounded attachment record read off disk, or an
// honest error record. Never throws.
//   opts.file     — the absolute/relative path to read (or opts.dir+opts.name).
//   opts.dir/name — joined to a path when opts.file is absent.
//   opts.maxBytes — the read cap (default MAX_ATTACH_BYTES); an oversized file
//                   yields { name, error:'too large', bytes }.
//   opts.fs       — injectable fs (default the real fs) so a test can fold a
//                   fake store; production reads the real bytes.
// Returns on success:
//   image/document -> { name, kind, mediaType, bytes, data }   (data = base64)
//   text           -> { name, kind, mediaType, bytes, text }   (text = utf8)
// Returns on failure: { name, error } (missing / oversized / unreadable) — the
// surface renders the error honestly; an errored attachment encodes to no block.
function readAttachment(opts) {
  const o = opts || {};
  const fsi = o.fs || fs;
  const file =
    o.file || (o.dir && o.name ? path.join(o.dir, o.name) : o.name) || '';
  const name = o.name || (file ? path.basename(file) : '');
  const maxBytes =
    typeof o.maxBytes === 'number' && o.maxBytes > 0
      ? o.maxBytes
      : MAX_ATTACH_BYTES;
  if (!file) return { name, error: 'no file' };
  let stat;
  try {
    stat = fsi.statSync(file);
  } catch (_) {
    return { name, error: 'not found' };
  }
  if (stat && typeof stat.size === 'number' && stat.size > maxBytes) {
    return { name, error: 'too large', bytes: stat.size };
  }
  let buf;
  try {
    buf = fsi.readFileSync(file);
  } catch (_) {
    return { name, error: 'unreadable' };
  }
  if (!Buffer.isBuffer(buf)) buf = Buffer.from(String(buf), 'utf8');
  // A read whose actual length exceeds the cap (a fake stat, a race) is still
  // refused — the cap binds the bytes that reach the envelope, not just the stat.
  if (buf.length > maxBytes) {
    return { name, error: 'too large', bytes: buf.length };
  }
  const cls = classifyAttachment(name);
  const rec = { name, kind: cls.kind, mediaType: cls.mediaType, bytes: buf.length };
  if (cls.kind === 'text') {
    rec.text = buf.toString('utf8');
  } else {
    rec.data = buf.toString('base64');
  }
  return rec;
}

// attachmentBlock(att) -> the Messages-API content block for ONE attachment
// record, or null when it errored / is empty (so it contributes no block):
//   image    -> { type:'image',    source:{ type:'base64', media_type, data } }
//   document -> { type:'document', source:{ type:'base64', media_type, data } }
//   text     -> { type:'text', text:'[file <name>]\n<content>' }  (inlined,
//               marked so the engine reads it as the attached file)
// The shapes mirror exactly what the Anthropic Messages API / the stream-json
// stdin envelope accept; the surface builds the block, the engine reads it.
function attachmentBlock(att) {
  if (!att || typeof att !== 'object' || att.error) return null;
  if (att.kind === 'image' && typeof att.data === 'string' && att.data) {
    return {
      type: 'image',
      source: {
        type: 'base64',
        media_type: att.mediaType || 'image/png',
        data: att.data,
      },
    };
  }
  if (att.kind === 'document' && typeof att.data === 'string' && att.data) {
    return {
      type: 'document',
      source: {
        type: 'base64',
        media_type: att.mediaType || 'application/pdf',
        data: att.data,
      },
    };
  }
  if (att.kind === 'text' && typeof att.text === 'string') {
    const head = '[file ' + (att.name || 'attachment') + ']';
    return { type: 'text', text: head + '\n' + att.text };
  }
  return null;
}

// attachmentBlocks(atts) -> the content blocks for an array of attachment
// records, dropping any that errored / folded to null. [] for a non-array. The
// order is preserved (the surface attaches them in pick order, ahead of the
// typed text — engine.encodeUserMessage folds them in).
function attachmentBlocks(atts) {
  if (!Array.isArray(atts)) return [];
  const out = [];
  for (const a of atts) {
    const b = attachmentBlock(a);
    if (b) out.push(b);
  }
  return out;
}

// displayAttachment(att) -> a small, data-free view of an attachment record for
// the surface tray (the base64 payload never needs to reach the DOM): the name,
// kind, byte count, and any error. A test asserts the tray renders this, not the
// raw bytes.
function displayAttachment(att) {
  if (!att || typeof att !== 'object') return { name: '', kind: 'text', bytes: 0 };
  const view = {
    name: att.name || '',
    kind: att.kind || 'text',
    bytes: typeof att.bytes === 'number' ? att.bytes : 0,
  };
  if (att.error) view.error = att.error;
  return view;
}

module.exports = {
  IMAGE_MEDIA_TYPES,
  DOC_MEDIA_TYPES,
  MAX_ATTACH_BYTES,
  mediaTypeForImage,
  isImageFile,
  classifyAttachment,
  readAttachment,
  attachmentBlock,
  attachmentBlocks,
  displayAttachment,
};

'use strict';
/* tier.js — the PURE classifier for the forest mask (no `vscode`, no I/O).
 *
 * Given the file-touch records (the SAME log loop/coverage.py folds — one
 * source of truth, not a second), it answers one question per path: what tier
 * of agent attention has this file received? One of four, in a deterministic
 * precedence:
 *
 *   undiscovered  no agent has ever read or edited this path (it is not in the
 *                 records at all) — the masked / dimmed default.
 *   read          some agent read it, but none has edited it.
 *   written       some agent edited it (an `edit` record). written OUTRANKS
 *                 read: an edit is the stronger, more consequential touch.
 *   in-context    it was touched (read OR edited) within `recencyMs` of now.
 *                 This is an OVERLAY tier that wins over read/written for very
 *                 recent touches.
 *
 * IMPORTANT — `in-context` is a PROXY, not a measurement. True context-window
 * membership (what tokens a model currently holds, and what was evicted) is
 * UNOBSERVABLE from outside the model: the harness records that a file tool
 * touched a path, never whether those bytes still sit in the live context.
 * Recency of the last touch is the best available signal that a file is
 * "in context right now", so this tier reads it that way and says so. A file
 * read an hour ago and long since evicted will correctly fall back to `read`;
 * a file touched seconds ago reads `in-context`. The window is the dial.
 *
 * The §10 tooth lives in this file: the precedence is real and discriminating
 * (a constant classifier is caught by tier.test.js). Pure: no Date.now(), no
 * fs — `nowMs` and `recencyMs` are passed in so the test is deterministic.
 */

/** Milliseconds for a record's `ts` (ISO 8601), or null if it will not parse.
 *  A torn / malformed ts never throws — it just does not count toward recency
 *  (the torn-tail tolerance the rest of the loop lives by). */
function recordMs(rec) {
  if (!rec || typeof rec.ts !== 'string') return null;
  const ms = Date.parse(rec.ts);
  return Number.isFinite(ms) ? ms : null;
}

/**
 * Classify one path's agent-attention tier.
 *
 * @param {Array<{ts?:string, session?:string, action?:string, path?:string}>} touchRecords
 *        every file-touch record (the whole log; this fn filters by path).
 * @param {string} repoRelPath  the repo-relative, forward-slash path to classify.
 * @param {number} nowMs        "now" in epoch milliseconds (injected for testability).
 * @param {number} recencyMs    the in-context window in ms; a touch within this
 *                              of `nowMs` reads `in-context`. <= 0 disables the
 *                              overlay (nothing is ever `in-context`).
 * @returns {"undiscovered"|"read"|"written"|"in-context"}
 */
function classify(touchRecords, repoRelPath, nowMs, recencyMs) {
  if (!Array.isArray(touchRecords) || !repoRelPath) return 'undiscovered';

  let seen = false;       // any record for this path at all
  let edited = false;     // any `edit` record
  let recent = false;     // any touch within the recency window

  const windowOpen = typeof recencyMs === 'number' && recencyMs > 0
    && typeof nowMs === 'number' && Number.isFinite(nowMs);

  for (const rec of touchRecords) {
    if (!rec || rec.path !== repoRelPath) continue;
    seen = true;
    if (rec.action === 'edit') edited = true;
    if (windowOpen) {
      const ms = recordMs(rec);
      // a touch in [nowMs - recencyMs, nowMs] is "recent". A future ts (clock
      // skew) is not counted as recent — only the closed window behind now.
      if (ms !== null && ms <= nowMs && (nowMs - ms) <= recencyMs) recent = true;
    }
  }

  if (!seen) return 'undiscovered';   // never touched — the masked default
  if (recent) return 'in-context';    // overlay: very recently touched
  if (edited) return 'written';       // edit outranks read
  return 'read';                      // read, not recently, never edited
}

/** The fixed tier vocabulary, in precedence order (for consumers/labels). */
const TIERS = ['undiscovered', 'read', 'written', 'in-context'];

module.exports = { classify, recordMs, TIERS };

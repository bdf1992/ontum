// usage.js — fold + format the cost / usage a driven turn reports (pure data,
// no `vscode`).
//
// Row 18 of the parity checklist: "Cost / usage display." Normal Claude Code
// shows what a turn cost — the dollars spent, the tokens in/out (incl. the
// prompt-cache reads/writes), how long it took, how many model turns it ran.
// The bridge spike (SPIKE-FINDINGS.md) resolved the DATA to `inherit`: the
// engine's terminal `result` event already carries `total_cost_usd`, a `usage`
// object ({input_tokens, output_tokens, cache_creation_input_tokens,
// cache_read_input_tokens}), `duration_ms`, and `num_turns`, and engine.foldReply
// already folds those onto the reply ({cost, usage, durationMs, numTurns}). So
// this module owns only the DISPLAY of cost/usage: it does NOT meter, estimate,
// or invent a number — every value here is a FOLD of the engine's own reported
// usage (the §The law grain), with an honest em-dash when a field is absent
// (a turn that errored before a result reports no usage — that absence is shown,
// never papered over with a fabricated 0).
//
// It is pure (no process, no `vscode`), so a plain `node` test proves the fold +
// the formatting + the running-total accumulation host-free, exactly as the rest
// of the surface is proven without a billed model call.

'use strict';

// num(n) -> n when it is a finite number, else null. The single gate every fold
// passes through, so a missing/NaN/Infinity/string field becomes an honest
// "no data" (rendered as an em-dash), never a misleading 0.
function num(n) {
  return typeof n === 'number' && isFinite(n) ? n : null;
}

// addable(a, b) -> a + b treating null as "no contribution" but preserving null
// when BOTH are null (so a running total over turns that all lacked a field
// stays honestly null, not a fabricated 0).
function addable(a, b) {
  const x = num(a);
  const y = num(b);
  if (x === null && y === null) return null;
  return (x || 0) + (y || 0);
}

// tokenTotals(usage) -> the token counts folded from the engine result's `usage`
// object into a stable shape: { input, output, cacheRead, cacheCreation, total }.
// `total` is the sum of the four (the real billed footprint — cache reads/writes
// are tokens too), or null when NONE of the four was reported (an honest "no
// token data", not 0). Tolerant of a missing/odd usage object. The field names
// mirror the Messages-API usage shape the CLI reports.
function tokenTotals(usage) {
  const u = usage && typeof usage === 'object' ? usage : {};
  const input = num(u.input_tokens);
  const output = num(u.output_tokens);
  const cacheCreation = num(u.cache_creation_input_tokens);
  const cacheRead = num(u.cache_read_input_tokens);
  let total = null;
  for (const v of [input, output, cacheCreation, cacheRead]) {
    if (v !== null) total = (total || 0) + v;
  }
  return { input, output, cacheRead, cacheCreation, total };
}

// foldUsage(reply) -> the display model for ONE turn's cost/usage, folded from
// the reply engine.foldReply produced:
//   { cost, durationMs, numTurns, tokens:{input,output,cacheRead,cacheCreation,total}, hasData }
// Every field is the engine's own reported value or null (no estimation). `hasData`
// is true when at least one usage signal was reported (so the surface can show an
// honest "no usage reported" state for a turn that errored before its result,
// rather than a row of em-dashes pretending to be a $0 turn).
function foldUsage(reply) {
  const r = reply && typeof reply === 'object' ? reply : {};
  const cost = num(r.cost);
  const durationMs = num(r.durationMs);
  const numTurns = num(r.numTurns);
  const tokens = tokenTotals(r.usage);
  const hasData =
    cost !== null ||
    durationMs !== null ||
    numTurns !== null ||
    tokens.total !== null;
  return { cost, durationMs, numTurns, tokens, hasData };
}

// accumulateUsage(prev, reply) -> a running SESSION total folded by adding this
// turn's usage onto the prior total. Normal Claude Code shows a session's
// cumulative spend, not just the last turn; this is that meter. `turns` counts
// the turns that actually reported usage (so it reflects billed turns, not Stop
// clicks / spawn errors that reported nothing). Pure — prev is never mutated.
// A first call passes prev = null/undefined.
function accumulateUsage(prev, reply) {
  const p =
    prev && typeof prev === 'object'
      ? prev
      : { cost: null, durationMs: null, tokens: {}, turns: 0 };
  const cur = foldUsage(reply);
  const pt = p.tokens && typeof p.tokens === 'object' ? p.tokens : {};
  return {
    cost: addable(p.cost, cur.cost),
    durationMs: addable(p.durationMs, cur.durationMs),
    tokens: {
      input: addable(pt.input, cur.tokens.input),
      output: addable(pt.output, cur.tokens.output),
      cacheRead: addable(pt.cacheRead, cur.tokens.cacheRead),
      cacheCreation: addable(pt.cacheCreation, cur.tokens.cacheCreation),
      total: addable(pt.total, cur.tokens.total),
    },
    // Count this turn only if it reported real usage (an honest billed-turn count).
    turns: (num(p.turns) || 0) + (cur.hasData ? 1 : 0),
  };
}

// --- human formatting --------------------------------------------------------
// Each formatter returns an em-dash for a null/absent value (the honest "no
// data"), never a fabricated 0, so a cold reader can tell "this turn cost $0.00"
// (a real, reported near-zero) from "this turn reported no cost" (—).

const DASH = '\u2014'; // em-dash

// formatUsd(n) -> a dollar string. Sub-cent turns are common, so small amounts
// keep 4 decimals ($0.0021); a dollar or more rounds to cents ($1.23).
function formatUsd(n) {
  const v = num(n);
  if (v === null) return DASH;
  const digits = Math.abs(v) < 1 ? 4 : 2;
  return '$' + v.toFixed(digits);
}

// formatTokens(n) -> a grouped integer ("1,234"), or "—" when absent. Rounds a
// fractional value defensively (token counts are integers, but be tolerant).
function formatTokens(n) {
  const v = num(n);
  if (v === null) return DASH;
  return Math.round(v).toLocaleString('en-US');
}

// formatDuration(ms) -> a compact human duration:
//   < 1s        -> "840ms"
//   < 60s       -> "2.3s"
//   >= 60s      -> "1m 5s"
// or "—" when absent. Pure string math (no Date), so it is deterministic.
function formatDuration(ms) {
  const v = num(ms);
  if (v === null) return DASH;
  if (v < 1000) return Math.round(v) + 'ms';
  const totalSec = v / 1000;
  if (totalSec < 60) return totalSec.toFixed(1) + 's';
  const m = Math.floor(totalSec / 60);
  const s = Math.round(totalSec - m * 60);
  return m + 'm ' + s + 's';
}

// usageSummary(reply) -> a single honest line summarising ONE turn's cost/usage,
// e.g. "$0.0021 · 15 tokens (10 in · 5 out) · 2.3s · 1 turn". A turn that
// reported no usage folds to "no usage reported" (not a fake row of zeros).
// Cache tokens are appended only when present (most turns have none).
function usageSummary(reply) {
  const u = foldUsage(reply);
  if (!u.hasData) return 'no usage reported';
  const parts = [];
  parts.push(formatUsd(u.cost));
  const t = u.tokens;
  if (t.total !== null) {
    const io = [];
    if (t.input !== null) io.push(formatTokens(t.input) + ' in');
    if (t.output !== null) io.push(formatTokens(t.output) + ' out');
    if (t.cacheRead !== null) io.push(formatTokens(t.cacheRead) + ' cache-read');
    if (t.cacheCreation !== null) {
      io.push(formatTokens(t.cacheCreation) + ' cache-write');
    }
    const detail = io.length ? ' (' + io.join(' · ') + ')' : '';
    parts.push(formatTokens(t.total) + ' tokens' + detail);
  }
  if (u.durationMs !== null) parts.push(formatDuration(u.durationMs));
  if (u.numTurns !== null) {
    parts.push(u.numTurns + (u.numTurns === 1 ? ' turn' : ' turns'));
  }
  return parts.join(' \u00b7 ');
}

module.exports = {
  tokenTotals,
  foldUsage,
  accumulateUsage,
  formatUsd,
  formatTokens,
  formatDuration,
  usageSummary,
};

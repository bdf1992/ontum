// plan.js — the plan-mode surface (pure data layer, no `vscode`, no `shell`).
//
// Row 11 of the parity checklist: "Plan mode." The bridge spike resolved this
// row to `inherit` (SPIKE-FINDINGS.md): the SAME `claude` CLI exposes
// `--permission-mode plan`, already threaded into the drive channel's argv by
// engine.engineArgs (row 9). Plan mode runs the engine READ-ONLY — it researches
// and drafts a plan but makes no edits — and when the plan is ready the engine
// calls the `ExitPlanMode` tool, presenting the plan and asking the human to
// approve proceeding. Normal Claude Code intercepts that tool call, renders the
// plan, and offers Approve / Keep-planning; approving EXITS plan mode so the
// work can run.
//
// This module owns only the *folding* of that flow — it is a FOLD (blueprint
// §The law): it recognises the engine's own ExitPlanMode tool_use record and
// derives what the surface renders + which mode a decision leaves in force. It
// stores nothing. No `vscode`/`shell` dependency, so a plain `node` test can
// hand it a captured tool_use and assert exactly what it returns — host-free,
// checkable evidence. The rendering (the plan card, the approve/keep buttons)
// lives in shell.js; the decision round-trip (and the mode transition) lives in
// extension.js.

'use strict';

const { normalizePermissionMode } = require('./engine');

// The tool the engine calls to leave plan mode: it presents the plan it has
// drafted and asks the human to approve proceeding. This CLI version (2.0.19)
// exposes it as `ExitPlanMode` (the name in the CLI's own tool registry);
// tolerate the legacy snake_case form too so a record from either never falls
// through to the row-7 JSON dump.
const EXIT_PLAN_TOOLS = ['ExitPlanMode', 'exit_plan_mode'];

// isExitPlanTool(name) -> true when a tool_use's name is the plan-exit tool.
function isExitPlanTool(name) {
  return EXIT_PLAN_TOOLS.indexOf(String(name)) !== -1;
}

// isPlanMode(mode) -> true when the (normalized) permission mode is 'plan'. The
// surface uses this to show the read-only plan-mode banner; normalization keeps
// it honest (an unknown value is not plan).
function isPlanMode(mode) {
  return normalizePermissionMode(mode) === 'plan';
}

// planFromToolUse(entry) -> { name, toolId, plan } for an ExitPlanMode tool_use
// entry, or null when the entry is not the plan-exit tool (so the caller renders
// it as an ordinary tool call / diff). The entry is a transcript.foldTranscript
// tool-use entry: { kind:'tool-use', name, toolId, input }. The plan text is the
// tool input's `plan` string (the markdown the engine drafted); a missing/odd
// input folds to an empty plan, never a fabricated one.
function planFromToolUse(entry) {
  if (!entry || entry.kind !== 'tool-use') return null;
  const name = entry.name || '';
  if (!isExitPlanTool(name)) return null;
  const input = entry.input && typeof entry.input === 'object' ? entry.input : {};
  const plan = typeof input.plan === 'string' ? input.plan : '';
  return { name, toolId: entry.toolId || '', plan };
}

// The two decisions the plan surface offers the human.
const PLAN_DECISIONS = ['approve', 'keep'];

// isPlanDecision(d) -> true when d is a recognised plan decision.
function isPlanDecision(d) {
  return PLAN_DECISIONS.indexOf(String(d)) !== -1;
}

// nextModeOnPlanDecision(decision, current) -> the permission mode in force
// after the human's plan decision.
//   'approve' -> EXIT plan mode so the work can proceed — conservatively to
//                'default' (ask before risky tools), NEVER silently to
//                acceptEdits/bypassPermissions (the surface never escalates the
//                permission posture on the human's behalf).
//   'keep'    -> stay in 'plan' (keep researching; no edits yet).
//   anything else -> stay in whatever mode is currently in force (normalized),
//                falling back to 'plan' if the current mode is itself plan, so an
//                unrecognised decision can never accidentally exit plan mode.
function nextModeOnPlanDecision(decision, current) {
  if (String(decision) === 'approve') return 'default';
  if (String(decision) === 'keep') return 'plan';
  return normalizePermissionMode(current);
}

module.exports = {
  EXIT_PLAN_TOOLS,
  isExitPlanTool,
  isPlanMode,
  planFromToolUse,
  PLAN_DECISIONS,
  isPlanDecision,
  nextModeOnPlanDecision,
};

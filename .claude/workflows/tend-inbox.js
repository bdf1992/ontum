export const meta = {
  name: 'tend-inbox',
  description: 'Tick-tender: investigate each owner-ask parked on bdo against CURRENT repo reality, close what the repo has already resolved (cited), and shape the genuine residue — a closed report, not a draft pile',
  whenToUse: 'When owner-ask mirror issues are open, or on demand, to stop stale parked items from sitting on bdo. It checks each item against what is true NOW (old reports go stale), closes the resolved ones through the issue pen, does/plans the session-doable ones, and hands bdo only the decisions that are genuinely his.',
  phases: [
    { title: 'Scout', detail: 'list the open owner-ask mirrors and their parked items' },
    { title: 'Investigate', detail: 'one grounded inference per item: resolved | session-doable | owner-decision' },
    { title: 'Close', detail: 'close fully-resolved mirrors through the issue pen (recorded, reversible)' },
  ],
}

// The point of the whole package, made concrete: REDUCE what bdo has to do.
// Owner-asks parked in old reports go stale — the repo moves on and the item is
// quietly already-resolved, but it still sits on his surface as open work. This
// tender does to owner-asks what tend-heal did to heal findings: CHECK each one
// against current reality, with cited evidence. Three honest outcomes:
//
//   resolved        — the repo already did this; the mirror is closeable NOW.
//   session-doable  — real work, but a session's, not bdo's; produce the plan.
//   owner-decision  — genuinely his (a name, an authority dial, a security call);
//                     shape it so the decision is one gesture, never a research task.
//
// It CLOSES the resolved mirrors itself (issue pen — recorded, provenance,
// reversible by reopen), because leaving bdo to hand-close issues a session
// verified done is offloading janitorial work (a rule that forces offloading is
// a bug in the rule). It never closes an item it could not verify resolved, and
// it never decides an owner-decision. `args.close` (default true) gates the
// actual close; set false for a dry report.

// args may arrive as a JSON string (a stringified payload) instead of an
// object — parse defensively so `close: false` actually disables the close
// (a string has no `.close`, which silently flipped the guard ON once).
const A = (typeof args === 'string' ? (() => { try { return JSON.parse(args) } catch { return {} } })() : args) || {}
const DO_CLOSE = A.close !== false

const ASKS = {
  type: 'object', additionalProperties: false, required: ['mirrors'],
  properties: {
    mirrors: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        required: ['issue', 'title', 'items'],
        properties: {
          issue: { type: 'number', description: 'the GitHub issue number of the owner-ask mirror' },
          title: { type: 'string' },
          items: {
            type: 'array',
            items: {
              type: 'object', additionalProperties: false,
              required: ['n', 'summary'],
              properties: {
                n: { type: 'number', description: 'the item number within the mirror' },
                summary: { type: 'string', description: 'the parked item, one line' },
              },
            },
          },
        },
      },
    },
  },
}

const VERDICT = {
  type: 'object', additionalProperties: false,
  required: ['issue', 'item', 'outcome', 'evidence', 'next'],
  properties: {
    issue: { type: 'number' },
    item: { type: 'number' },
    outcome: {
      type: 'string',
      enum: ['resolved', 'session-doable', 'owner-decision', 'inconclusive'],
      description: 'resolved = the repo already did this (cite the file/done-line/receipt); session-doable = real work but not bdo\'s; owner-decision = genuinely his (name/dial/security); inconclusive = could not determine',
    },
    evidence: { type: 'string', description: 'the citation that proves the outcome — a file:line, a done-line id, a receipt, or a log fact actually checked. Never prose-only.' },
    next: { type: 'string', description: 'for resolved: why the mirror item is moot. for session-doable: the concrete plan (the pen/steps). for owner-decision: the decision shaped as one gesture, with the recommended option named.' },
  },
}

phase('Scout')
const scout = await agent(
  'List the open owner-ask mirror issues: run `gh issue list --state open --search "[owner-ask] in:title" --json number,title` ' +
  'from the repo root. For each, run `gh issue view <n> --json body -q .body` and extract its numbered parked items (the "1.", "2." list). ' +
  'Return the mirrors with their items, one line each. If none are open, return an empty array.',
  { label: 'scout:owner-asks', phase: 'Scout', schema: ASKS }
)

const mirrors = (scout && scout.mirrors) || []
const flat = mirrors.flatMap((m) => m.items.map((it) => ({ ...it, issue: m.issue, mtitle: m.title })))
if (!flat.length) {
  log('tend-inbox: no open owner-asks — nothing parked on bdo. No-op.')
  return { investigated: 0, resolved: 0, mirrors: [] }
}
log(`tend-inbox: ${flat.length} parked item(s) across ${mirrors.length} mirror(s) — investigating against current reality`)

phase('Investigate')
const verdicts = await parallel(flat.map((it) => () =>
  agent(
    `An owner-ask parked on bdo (issue #${it.issue}, item ${it.n}):\n"${it.summary}"\n\n` +
    'Reports go stale — the repo may already have resolved this. INVESTIGATE against the current tree: ' +
    'use Read/Grep/Bash (e.g. `python -m loop.reconcile --status`, grep the done/ lines, read the cited code) to find out what is TRUE NOW. ' +
    'Decide one outcome, backed by a real citation (a file:line, a done-line id, a receipt id, a log fact) — never prose alone:\n' +
    '  resolved        — the repo already did this; the item is moot. Cite the proof.\n' +
    '  session-doable  — real work, but a session\'s (engineering/cleanup); give the concrete plan.\n' +
    '  owner-decision  — genuinely bdo\'s (a name to pick, an authority dial to set, a security call); ' +
    'shape it as ONE gesture and name the recommended option.\n' +
    '  inconclusive    — you could not determine it; say what is missing.\n' +
    'Do NOT do the engineering and do NOT make the owner decision here — investigate and classify only.',
    { label: `ask:#${it.issue}.${it.n}`, phase: 'Investigate', schema: VERDICT }
  ).catch(() => null)
))

const kept = verdicts.filter(Boolean)
// a mirror is closeable only when EVERY one of its items is resolved
const byIssue = {}
for (const v of kept) (byIssue[v.issue] = byIssue[v.issue] || []).push(v)
// A mirror is closeable only when it HAS items, every item was investigated,
// and every verdict is `resolved`. The `length > 0` guard is load-bearing:
// without it a mirror whose body has no numbered items folds to an empty set,
// and `[].every(...)` is vacuously true — which once closed a standing
// owner-directive (#348) with zero investigation. No items investigated is
// never "all resolved"; it is "nothing checked" → leave it for bdo.
const closeable = mirrors
  .filter((m) => m.items.length > 0 &&
                 (byIssue[m.issue] || []).length === m.items.length &&
                 (byIssue[m.issue] || []).every((v) => v.outcome === 'resolved'))
  .map((m) => m.issue)

const resolved = kept.filter((v) => v.outcome === 'resolved').length
const ownerCalls = kept.filter((v) => v.outcome === 'owner-decision')
log(`tend-inbox: ${resolved}/${kept.length} already resolved · ${closeable.length} mirror(s) fully closeable · ${ownerCalls.length} genuine owner-decision(s)`)

phase('Close')
const closed = []
if (DO_CLOSE && closeable.length) {
  for (const issue of closeable) {
    const proof = (byIssue[issue] || []).map((v) => `item ${v.item}: ${v.evidence}`).join('; ')
    const r = await agent(
      `Close owner-ask mirror #${issue} through the governed issue pen (a recorded act, reversible by reopen). ` +
      `Every item was verified already-resolved by the repo. Run from the repo root:\n` +
      `python .claude/skills/issue/issue.py close ${issue} --reason "tend-inbox verified every parked item already resolved by the current repo; closing the stale mirror (reopen if any item is still live). Evidence — ${proof.replace(/"/g, "'")}" --by tend-inbox.v0\n` +
      'If the issue pen rejects the verb/flags, report the exact error verbatim instead of forcing a raw gh close. Report what happened.',
      { label: `close:#${issue}`, phase: 'Close' }
    ).catch((e) => String(e))
    closed.push({ issue, result: r })
  }
} else if (!DO_CLOSE) {
  log('tend-inbox: close disabled (args.close=false) — reporting only')
}

return {
  investigated: kept.length,
  resolved,
  closeable,
  closed,
  ownerDecisions: ownerCalls.map((v) => ({ issue: v.issue, item: v.item, gesture: v.next, evidence: v.evidence })),
  sessionDoable: kept.filter((v) => v.outcome === 'session-doable').map((v) => ({ issue: v.issue, item: v.item, plan: v.next })),
  verdicts: kept,
}

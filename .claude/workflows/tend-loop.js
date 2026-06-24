export const meta = {
  name: 'tend-loop',
  description: 'The tick-conductor: one bounded cycle that drains the value-confirm clog (the real rail) and fans out the inference tenders over the incomplete-flow surfaces, journalled so the drafts survive a mortal session',
  whenToUse: 'The unit a ~5-minute external scheduler runs (bdo\'s activation gesture). One call = one tick: optional bounded value-confirm drain + the heal/gaps tenders + a journalled tick-report. Safe-by-default (drainLimit 0); the drain is a dial.',
  phases: [
    { title: 'Drain', detail: 'fire ≤ drainLimit real value-confirm reviews through the existing heartbeat rail' },
    { title: 'Tend', detail: 'run the inference tenders over heal + gaps' },
    { title: 'Journal', detail: 'append the compiled tick-report to the gitignored tender journal' },
  ],
}

// One tick of the incomplete flow. Two layers, by design:
//
//   (1) the LOAD-BEARING burn — the value-confirm clog (atoms stuck at
//       value_accepted → value_confirmed). This already has a real, sanctioned
//       rail: `loop.heartbeat --drain-limit N` fires at most N INDEPENDENT
//       value-confirm reviews through the gate pen (done-0150/0178). We REUSE
//       it — no second truth. It is gated behind `args.drainLimit` and DEFAULTS
//       TO 0, because each real review is headless inference + a trust-rail
//       GitHub issue; turning it up is a deliberate dial, not the safe default.
//
//   (2) the COMPOUNDING assist — the inference tenders (tend-heal, tend-gaps)
//       turn standing findings into checked, ready-to-act drafts. Propose-grain:
//       they write no verdict and clear no park (D-4). Safe to run every tick.
//
// The drafts are journalled to a gitignored sink so they outlive this session —
// the next session (or bdo's digest) reads ready work instead of re-deriving it.

// args may arrive as a JSON string (a stringified payload) — parse it the way
// the sibling tenders do (tend.js / tend-inbox.js), so a dialed-up drain isn't
// silently dropped to its default (a string has no `.drainLimit`).
const A = (typeof args === 'string' ? (() => { try { return JSON.parse(args) } catch { return {} } })() : args) || {}
const DRAIN_LIMIT = Number(A.drainLimit) || 0
const GAP_LIMIT = Number(A.gapLimit) || 5
const BY = A.by || 'tend-loop.v0'

// ---- (1) Drain: the real value-confirm rail, only when explicitly dialed up.
phase('Drain')
let drained = { fired: 0, line: 'drain off (drainLimit 0)' }
if (DRAIN_LIMIT > 0) {
  const out = await agent(
    `Run exactly: \`python -m loop.heartbeat --drain-limit ${DRAIN_LIMIT} --by ${BY}\` from the repo root. ` +
    'This fires real, independent value-confirm reviews through the existing gate rail — do not reimplement it, ' +
    'just run it and report its result line. Return how many reviews it reports firing (drained=N) and its final result line.',
    {
      label: `drain:${DRAIN_LIMIT}`,
      phase: 'Drain',
      schema: {
        type: 'object', additionalProperties: false, required: ['fired', 'line'],
        properties: {
          fired: { type: 'number', description: 'the drained=N count from the heartbeat result' },
          line: { type: 'string', description: 'the heartbeat result line verbatim' },
        },
      },
    }
  ).catch(() => null)
  if (out) drained = out
  log(`tend-loop: value-confirm drain fired ${drained.fired} real review(s)`)
} else {
  log('tend-loop: drain off (drainLimit 0) — running the inference tenders only')
}

// ---- (2) Tend: the inference tenders, as composed sub-workflows.
phase('Tend')
const [heal, gaps] = await parallel([
  () => workflow('tend-heal').catch((e) => ({ error: String(e), tended: 0, drafts: [] })),
  () => workflow('tend-gaps', { limit: GAP_LIMIT }).catch((e) => ({ error: String(e), tended: 0, drafts: [] })),
])

const report = {
  by: BY,
  drain: drained,
  heal: { tended: heal.tended || 0, actionable: heal.actionable || 0, drafts: heal.drafts || [] },
  gaps: { tended: gaps.tended || 0, ready: gaps.ready || 0, drafts: gaps.drafts || [] },
}

// ---- (3) Journal: append the tick-report so the drafts survive this session.
// The journal is a gitignored sensor trace (sibling of tool-use.jsonl), not
// truth — the truth is the log the drain advanced. One JSON line per tick.
phase('Journal')
const payload = JSON.stringify(report).replace(/'/g, "'\\''")
await agent(
  'Append exactly one timestamped JSON line to the gitignored tender journal `.ai-native/log/tenders.jsonl` ' +
  '(create the file if absent), then report the file\'s total line count. Run this from the repo root, ' +
  'which stamps an ISO `ts` field onto the report and appends it as one line:\n' +
  `python -c "import json,sys,datetime; r=json.loads(sys.argv[1]); r['ts']=datetime.datetime.now(datetime.timezone.utc).isoformat(); open('.ai-native/log/tenders.jsonl','a',encoding='utf-8').write(json.dumps(r,ensure_ascii=False)+chr(10))" '${payload}'`,
  { label: 'journal', phase: 'Journal' }
).catch(() => null)

const actionable = (report.heal.actionable || 0) + (report.gaps.ready || 0)
log(`tend-loop tick: drained ${report.drain.fired} · ${actionable} ready draft(s) journalled`)
return report

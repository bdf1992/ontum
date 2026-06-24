export const meta = {
  name: 'tend',
  description: 'The generic work-consuming process: granted a NAMED section of the ledger (loop.section), it works a bounded batch of that section\'s open items and surfaces work-to-close — one consumer, any queue',
  whenToUse: 'The general form bdo asked for ("free to work over a named section of the log/ledger ... a process which consumes work"). Point it at any section — value-confirm, stale-park, gaps, owner-asks — with args.section, and it folds that section\'s open items and surfaces each as ready-to-close work. Propose-grain: it surfaces and drafts the close, it does not actuate (the specialized tenders own actuation where the close is known and safe).',
  phases: [
    { title: 'Pull', detail: 'fold loop.section items --name <section> into the work batch' },
    { title: 'Work', detail: 'one bounded inference per item, per the section\'s closes_via contract' },
  ],
}

// The consumer half of the producer/consumer pair: loop/section.py NAMES and
// folds the work (the producer); this WORKS it (the consumer). It is generic by
// construction — it knows nothing about the section beyond what `loop.section`
// hands it (the items + the section's `closes_via` contract), so a new section
// is consumable the day it joins the registry, no new workflow. It surfaces
// work-to-close; it does not actuate the close (actuation reaches pens/network
// and is section-specific — the specialized tenders, e.g. tend-inbox, own it
// where the close is known reversible-safe). Bounded: `args.limit` items/tick.

const A = (typeof args === 'string' ? (() => { try { return JSON.parse(args) } catch { return {} } })() : args) || {}
const SECTION = A.section
const LIMIT = Number(A.limit) || 5

if (!SECTION) {
  log('tend: no section named — pass args.section (one of: value-confirm, stale-park, gaps, owner-asks)')
  return { error: 'no section', worked: 0 }
}

const QUEUE = {
  type: 'object', additionalProperties: false, required: ['closesVia', 'items'],
  properties: {
    closesVia: { type: 'string', description: 'the section\'s closes_via line — how work in it is ended' },
    items: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false, required: ['id', 'summary'],
        properties: {
          id: { type: 'string' },
          summary: { type: 'string' },
        },
      },
    },
  },
}

const DISPOSITION = {
  type: 'object', additionalProperties: false,
  required: ['id', 'outcome', 'action', 'evidence'],
  properties: {
    id: { type: 'string' },
    outcome: {
      type: 'string',
      enum: ['ready-to-close', 'drafted', 'owner', 'blocked'],
      description: 'ready-to-close = verified done/safe, the exact close action is ready to run; drafted = a concrete next move readied; owner = genuinely bdo\'s call (shaped); blocked = could not proceed, say why',
    },
    action: { type: 'string', description: 'the one ready move — the exact close command (per closes_via), the drafted next step, or the shaped owner gesture' },
    evidence: { type: 'string', description: 'the citation backing the outcome — a file:line, receipt id, log fact, or surface actually read; never prose alone' },
  },
}

phase('Pull')
const pulled = await agent(
  `Run \`python -m loop.section items --name ${SECTION} --json\` from the repo root. ` +
  'Return its `items` array (each id + summary) and the section\'s `closes_via` line ' +
  `(from \`python -m loop.section list --json\`, the row named "${SECTION}"). ` +
  `Return at most the first ${LIMIT} items, in order. If the section is unknown or empty, return an empty items array.`,
  { label: `pull:${SECTION}`, phase: 'Pull', schema: QUEUE }
)

const items = (pulled && pulled.items) || []
const closesVia = (pulled && pulled.closesVia) || '(unknown — read loop.section)'
if (!items.length) {
  log(`tend[${SECTION}]: queue empty — nothing to consume. No-op.`)
  return { section: SECTION, worked: 0, dispositions: [] }
}
log(`tend[${SECTION}]: consuming ${items.length} item(s) · closes via: ${closesVia}`)

phase('Work')
const dispositions = await parallel(items.map((it) => () =>
  agent(
    `Section "${SECTION}" — an open work item:\n  id: ${it.id}\n  ${it.summary}\n\n` +
    `How work in this section is closed: ${closesVia}\n\n` +
    'Work this one item: investigate it against the live repo (Read/Grep/Bash — fold status, read the cited code/receipts) ' +
    'and surface it as ready-to-act. Decide one outcome backed by a real citation (never prose alone):\n' +
    '  ready-to-close — verified done or safe to close; give the EXACT close command per the closes_via above.\n' +
    '  drafted        — real work remains; give the one concrete next move (the pen/steps).\n' +
    '  owner          — genuinely bdo\'s call; shape it as one gesture and name the recommended option.\n' +
    '  blocked        — could not proceed; say exactly what is missing.\n' +
    'Propose-grain: do NOT actuate — do not fire the review, close the issue, or run the pen here. Surface the ready move only.',
    { label: `work:${it.id}`, phase: 'Work', schema: DISPOSITION }
  ).catch(() => null)
))

const kept = dispositions.filter(Boolean)
const ready = kept.filter((d) => d.outcome === 'ready-to-close')
const owner = kept.filter((d) => d.outcome === 'owner')
log(`tend[${SECTION}]: ${kept.length} worked · ${ready.length} ready-to-close · ${owner.length} for bdo`)
return { section: SECTION, worked: kept.length, readyToClose: ready.length, ownerCalls: owner.length, dispositions: kept }

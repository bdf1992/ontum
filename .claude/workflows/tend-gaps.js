export const meta = {
  name: 'tend-gaps',
  description: 'Tick-tender: take the pressure-top gaps and draft the one concrete next move for each (propose-grain; the cut stays bdo\'s, D-4)',
  whenToUse: 'Every few minutes, or on demand, to turn loop.gaps\' standing pressure-ordered backlog into drafted, ready-to-pick-up moves — the idle default is "work the backlog the harness generated", and this readies that work.',
  phases: [
    { title: 'Scout', detail: 'parse loop.gaps into the pressure-ordered small-item list' },
    { title: 'Tend', detail: 'one bounded inference per gap → a drafted next move' },
  ],
}

// loop.gaps folds the loop's own gaps into one fixed pressure order and hands
// each a kind/subject/why and the one concrete move (always an existing pen's).
// It writes nothing — the next session is meant to pick the top one up. This
// tender reads that backlog and, per gap, drafts the move into something ready
// to act on: for an idle-part, either a minimal way to exercise it through the
// working system, or the honest case that its silence is by design (absence is
// information). It proposes; it never runs the move (the cut stays bdo's/a
// session's, D-4). `args.limit` bounds how many top gaps to tend (default 5).

// args may arrive as a JSON string (a stringified payload) — parse it the way
// the sibling tenders do (tend.js / tend-inbox.js) so `limit` is actually read,
// not silently dropped to its default (a string has no `.limit`).
const A = (typeof args === 'string' ? (() => { try { return JSON.parse(args) } catch { return {} } })() : args) || {}
const LIMIT = Number(A.limit) || 5

const GAPS = {
  type: 'object',
  additionalProperties: false,
  required: ['gaps'],
  properties: {
    gaps: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['kind', 'subject', 'why', 'move'],
        properties: {
          kind: { type: 'string', description: 'e.g. idle-part, mock-stage, parked-piece, surface-drift, dormant-part' },
          subject: { type: 'string', description: 'the part/atom/surface the gap is about' },
          why: { type: 'string' },
          move: { type: 'string', description: 'the one concrete move loop.gaps names' },
        },
      },
    },
  },
}

const DRAFT = {
  type: 'object',
  additionalProperties: false,
  required: ['subject', 'route', 'draft', 'confidence'],
  properties: {
    subject: { type: 'string' },
    route: {
      type: 'string',
      enum: ['exercise', 'silence-by-design', 'build', 'needs-owner', 'inconclusive'],
      description: 'exercise = a minimal real exercise of the part through the working system; silence-by-design = an honest case the part should stay idle (absence is information); build = the gap names a thing to build; needs-owner = the move is bdo\'s cut (D-4); inconclusive = could not tell',
    },
    draft: { type: 'string', description: 'the ready-to-act move: the exact pen invocation / exercise steps, OR the silence-by-design justification. Never run it here — only draft it.' },
    confidence: { type: 'string', enum: ['high', 'medium', 'low'] },
  },
}

phase('Scout')
const scout = await agent(
  'Run `python -m loop.gaps` from the repo root (it has no --json flag — parse its text). ' +
  `Return the first ${LIMIT} gaps in the order printed (they are already pressure-ordered, top = the work). ` +
  'For each, capture kind, subject, why, and the one move it names. Do not invent gaps; return fewer if fewer exist.',
  { label: 'scout:gaps', phase: 'Scout', schema: GAPS }
)

const gaps = (scout && scout.gaps) || []
if (!gaps.length) {
  log('tend-gaps: no open gaps — the backlog is clear. No-op.')
  return { tended: 0, drafts: [] }
}
log(`tend-gaps: drafting moves for the top ${gaps.length} gap(s)`)

phase('Tend')
const drafts = await parallel(gaps.map((g) => () =>
  agent(
    `A loop gap (kind: ${g.kind}) on "${g.subject}". Why it is a gap: ${g.why}\n` +
    `The move loop.gaps names: "${g.move}"\n\n` +
    'Draft this move into something a session can act on in one pass. Read the subject if it is a file ' +
    '(use Read/Grep) so your draft is grounded, not generic. ' +
    'For an idle-part, decide between: (a) "exercise" — the smallest real path that runs the part through the ' +
    'working system so a word of its lands on the record; or (b) "silence-by-design" — the honest, cited case that ' +
    'this part is correctly idle right now (absence is information). ' +
    'Rules: propose-grain. Do NOT run the move, do not exercise the part, do not write any record — only draft. ' +
    'If the move is bdo\'s cut (e.g. pruning a dormant part), route it "needs-owner".',
    { label: `tend:${g.subject}`, phase: 'Tend', schema: DRAFT }
  ).catch(() => null)
))

const kept = drafts.filter(Boolean)
const ready = kept.filter((d) => d.route === 'exercise' || d.route === 'build')
log(`tend-gaps: ${kept.length} drafted · ${ready.length} ready to pick up`)
return { tended: kept.length, ready: ready.length, drafts: kept }

export const meta = {
  name: 'tend-heal',
  description: 'Tick-tender: infer over each heal finding and draft the one reconcile move (propose-grain, the heal stays bdo\'s, D-4)',
  whenToUse: 'Every few minutes, or on demand, to turn loop.heal\'s standing stale-park/flapping/override findings into checked, ready-to-act reconcile drafts instead of findings that just sit.',
  phases: [
    { title: 'Scout', detail: 'fold loop.heal --json into the small-item list' },
    { title: 'Tend', detail: 'one bounded inference per finding → a drafted reconcile move' },
  ],
}

// loop.heal is a read-only fold: it NAMES where a tooth bit stale/wrong and the
// one heal move, but it never acts (D-4 — the heal stays bdo's/a session's). The
// gap this tender fills: those findings stand on the summon surface every session
// and nothing checks them. Here each finding is one small item — we verify the
// claim against the live owner surfaces and hand back a checked draft, never a
// disposition. Propose-grain by construction: we write no verdict and clear no park.

const FINDINGS = {
  type: 'object',
  additionalProperties: false,
  required: ['findings'],
  properties: {
    findings: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['subject', 'kind', 'move'],
        properties: {
          subject: { type: 'string', description: 'the atom/gate the finding is about, e.g. atom.gates-enumerated.v2' },
          kind: { type: 'string', description: 'stale-park | flapping-gate | owner-override' },
          move: { type: 'string', description: 'the heal move loop.heal proposes' },
        },
      },
    },
  },
}

const DRAFT = {
  type: 'object',
  additionalProperties: false,
  required: ['subject', 'verdict', 'reason', 'draft'],
  properties: {
    subject: { type: 'string' },
    verdict: {
      type: 'string',
      enum: ['stale-surface-confirmed', 'already-reconciled', 'needs-owner', 'inconclusive'],
      description: 'stale-surface-confirmed = the healed bite STILL shows as an open park on an owner surface (the reconcile is real and safe); already-reconciled = no owner surface shows it (nothing to do); needs-owner = the move touches truth only bdo may move (D-4); inconclusive = could not tell from the surfaces',
    },
    reason: { type: 'string', description: 'one sentence, citing the surface (inbox/digest) actually read' },
    draft: { type: 'string', description: 'the one concrete next move, ready to act on (a pen invocation, or "none — already reconciled"); never an actuation here, only the draft' },
  },
}

phase('Scout')
const scout = await agent(
  'Run `python -m loop.heal --json` from the repo root and return its findings array verbatim ' +
  '(each finding\'s subject, kind, and move). Do not invent findings; if the array is empty, return an empty array.',
  { label: 'scout:heal', phase: 'Scout', schema: FINDINGS }
)

const findings = (scout && scout.findings) || []
if (!findings.length) {
  log('tend-heal: no heal findings — the teeth are clean. No-op.')
  return { tended: 0, drafts: [] }
}
log(`tend-heal: ${findings.length} finding(s) to check against the owner surfaces`)

phase('Tend')
const drafts = await parallel(findings.map((f) => () =>
  agent(
    `A heal finding (kind: ${f.kind}) names "${f.subject}". The proposed heal move is:\n"${f.move}"\n\n` +
    'Your job is to CHECK this claim against the live owner surfaces, not to act on it. ' +
    'Read what bdo actually sees: run `python -m loop.node inbox` and `python -m loop.digest --today` from the repo root. ' +
    `Decide whether ${f.subject}'s refusal still shows as an OPEN park/owner item on either surface.\n\n` +
    'Rules: this tender is propose-grain. You NEVER write a verdict, clear a park, or run any pen that mutates state — ' +
    'the heal stays bdo\'s (D-4). You only return a checked draft of the one move. ' +
    'If the move would touch the truth log or settle a verdict, your verdict is "needs-owner". ' +
    'Cite the surface you actually read in your reason.',
    { label: `tend:${f.subject}`, phase: 'Tend', schema: DRAFT }
  ).catch(() => null)
))

const kept = drafts.filter(Boolean)
const actionable = kept.filter((d) => d.verdict === 'stale-surface-confirmed')
log(`tend-heal: ${kept.length} checked · ${actionable.length} with a real, safe reconcile draft`)
return { tended: kept.length, actionable: actionable.length, drafts: kept }

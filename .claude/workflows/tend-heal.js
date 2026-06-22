export const meta = {
  name: 'tend-heal',
  description: 'Tick-tender: infer over each heal finding and draft the one reconcile move — now ON THE RAIL: pinned to a governed, versioned node prompt (prompt-as-code) with its hash recorded (propose-grain, the heal stays bdo\'s, D-4)',
  whenToUse: 'Every few minutes, or on demand, to turn loop.heal\'s standing stale-park findings into checked, ready-to-act reconcile drafts. The agents run a GOVERNED prompt (.ai-native/nodes/tend-heal.claude.v1.md), not an inline string — pinned by hash, halted if the prompt fails the requirements door.',
  phases: [
    { title: 'Pin', detail: 'load the governed node prompt + hash (loop.prompt_req); halt if it fails the door' },
    { title: 'Scout', detail: 'fold loop.heal --json into the small-item list' },
    { title: 'Tend', detail: 'one branded, prompt-pinned agent per finding → a drafted reconcile move' },
  ],
}

// Re-founded on the written rail (agent-summoning-requirements C1+C3): the
// agents are no longer prompted by an inline string. Their instructions ARE the
// versioned node prompt `.ai-native/nodes/tend-heal.claude.v1.md` (prompt-as-
// code, §7), delivered with its sha256 and recorded on the result so every
// disposition is attributable to the exact prompt. The PROMPT-REQUIREMENTS DOOR
// (loop.prompt_req) gates the run: a prompt missing an edge HALTS the tender
// rather than running ungoverned. Still propose-grain: it writes no verdict and
// clears no park (D-4).

const NODE = 'tend-heal.claude.v1'

const PIN = {
  type: 'object', additionalProperties: false,
  required: ['found', 'valid', 'prompt_hash', 'prompt', 'problems'],
  properties: {
    found: { type: 'boolean' },
    valid: { type: 'boolean' },
    prompt_hash: { type: ['string', 'null'] },
    prompt: { type: ['string', 'null'] },
    problems: { type: 'array', items: { type: 'string' } },
  },
}

const FINDINGS = {
  type: 'object', additionalProperties: false, required: ['findings'],
  properties: {
    findings: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        required: ['subject', 'kind', 'move'],
        properties: {
          subject: { type: 'string' },
          kind: { type: 'string' },
          move: { type: 'string' },
        },
      },
    },
  },
}

const DRAFT = {
  type: 'object', additionalProperties: false,
  required: ['subject', 'verdict', 'reason', 'draft'],
  properties: {
    subject: { type: 'string' },
    verdict: {
      type: 'string',
      enum: ['stale-surface-confirmed', 'already-reconciled', 'needs-owner', 'inconclusive'],
      description: 'the disposition vocabulary the governed prompt defines',
    },
    reason: { type: 'string', description: 'one sentence, citing the surface (inbox/digest) actually read' },
    draft: { type: 'string', description: 'the one concrete next move, ready to act on, or "none"' },
  },
}

// ---- Pin: load the governed prompt; halt if it fails the requirements door.
phase('Pin')
const pin = await agent(
  `Run \`python -m loop.prompt_req deliver --node ${NODE} --json\` from the repo root and return its JSON exactly ` +
  '(found, valid, prompt_hash, prompt, problems).',
  { label: `pin:${NODE}`, phase: 'Pin', schema: PIN }
)
if (!pin || !pin.found || !pin.valid || !pin.prompt) {
  const why = (pin && pin.problems && pin.problems.join('; ')) || 'deliver failed'
  log(`tend-heal: governed prompt ${NODE} failed the door — HALT (no ungoverned run): ${why}`)
  return { halted: true, node: NODE, problems: (pin && pin.problems) || ['deliver failed'] }
}
const GOVERNED = pin.prompt
const PROMPT_HASH = pin.prompt_hash
log(`tend-heal: pinned to ${NODE} @ ${PROMPT_HASH}`)

// ---- Scout: the small-item list from loop.heal.
phase('Scout')
const scout = await agent(
  'Run `python -m loop.heal --json` from the repo root and return its findings array verbatim ' +
  '(each finding\'s subject, kind, and move). Do not invent findings; if empty, return an empty array.',
  { label: 'scout:heal', phase: 'Scout', schema: FINDINGS }
)
const findings = (scout && scout.findings) || []
if (!findings.length) {
  log('tend-heal: no heal findings — the teeth are clean. No-op.')
  return { node: NODE, promptHash: PROMPT_HASH, tended: 0, drafts: [] }
}
log(`tend-heal: ${findings.length} finding(s) to check, pinned to ${PROMPT_HASH}`)

// ---- Tend: each agent RUNS THE GOVERNED PROMPT, branded ontum-node:<id>.
phase('Tend')
const drafts = await parallel(findings.map((f) => () =>
  agent(
    GOVERNED +
    `\n\n---\nYour summons — the one finding to check:\n` +
    `  subject: ${f.subject}\n  kind: ${f.kind}\n  move: ${f.move}`,
    { label: `ontum-node:${NODE}:${f.subject}`, phase: 'Tend', schema: DRAFT }
  ).catch(() => null)
))

const kept = drafts.filter(Boolean)
const actionable = kept.filter((d) => d.verdict === 'stale-surface-confirmed')
log(`tend-heal: ${kept.length} checked · ${actionable.length} with a real reconcile draft · prompt ${PROMPT_HASH}`)
return { node: NODE, promptHash: PROMPT_HASH, tended: kept.length, actionable: actionable.length, drafts: kept }

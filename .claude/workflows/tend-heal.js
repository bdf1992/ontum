export const meta = {
  name: 'tend-heal',
  description: 'Tick-tender: infer over each heal finding and draft the one reconcile move — ON THE RAIL (governed prompt-as-code, hash recorded) and ON THE BOOKS (every agent run receipted under a training-run posture, monitorable — propose-grain, the heal stays bdo\'s, D-4)',
  whenToUse: 'Every few minutes, or on demand, to turn loop.heal\'s standing stale-park findings into checked, ready-to-act reconcile drafts. The agents run a GOVERNED prompt (.ai-native/nodes/tend-heal.claude.v1.md), not an inline string — pinned by hash, halted if the prompt fails the requirements door — and each run is booked on the books (loop.agent_run) so it is witnessed, never vanishing.',
  phases: [
    { title: 'Open', detail: 'open a training-run posture on the books (loop.agent_run open) — nothing auto-trusted as done' },
    { title: 'Pin', detail: 'load the governed node prompt + hash (loop.prompt_req); halt if it fails the door' },
    { title: 'Scout', detail: 'fold loop.heal --json into the small-item list' },
    { title: 'Tend', detail: 'one branded, prompt-pinned agent per finding → a drafted reconcile move' },
    { title: 'Book', detail: 'book each disposition on the books under the training run (loop.agent_run receipt) — the monitor reads it back' },
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

const RUN = {
  type: 'object', additionalProperties: false, required: ['run'],
  properties: { run: { type: 'string', description: 'the atr.* training-run id printed by `loop.agent_run open`' } },
}

const BOOKED = {
  type: 'object', additionalProperties: false, required: ['booked', 'result'],
  properties: {
    booked: { type: 'boolean', description: 'true if the receipt landed on the books' },
    result: { type: 'string', description: 'the stdout result line (done | needs-you)' },
  },
}

// ---- Open: open the training-run posture on the books. Every run below is
// booked under it (loop.agent_run) — witnessed, never vanishing; nothing here is
// auto-trusted as done (training, not production).
phase('Open')
const opened = await agent(
  'Run `python -m loop.agent_run open --by tend-heal --note "heal-tender tick"` from the repo root ' +
  'and return the atr.* run id it prints (the token after "on the books:").',
  { label: 'open:training-run', phase: 'Open', schema: RUN }
)
const RUN_ID = opened && opened.run
if (!RUN_ID) {
  log('tend-heal: could not open a training run — HALT (a run that cannot be booked is not run on the books)')
  return { halted: true, why: 'agent_run open did not return a run id' }
}
log(`tend-heal: training run open on the books: ${RUN_ID}`)

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

// ---- Book: each disposition lands on the books under the training run. The
// booking is itself governed — `loop.agent_run receipt` refuses a prompt_hash
// that is not this node's, so a run cannot be booked against an ungoverned
// prompt. The monitor reads it back with `python -m loop.agent_run --run <id>`.
phase('Book')
const booked = await parallel(kept.map((d) => () => {
  const reason = (d.reason || '').replace(/"/g, "'").slice(0, 400)
  return agent(
    `Run this from the repo root and return its result line:\n` +
    `python -m loop.agent_run receipt --run ${RUN_ID} --node ${NODE} ` +
    `--prompt-hash ${PROMPT_HASH} --subject "${d.subject}" --verdict "${d.verdict}" ` +
    `--reason "${reason}"\n` +
    `Set booked=true only if the line begins "result: done".`,
    { label: `book:${d.subject}`, phase: 'Book', schema: BOOKED }
  ).catch(() => ({ booked: false, result: 'spawn failed' }))
}))
const onBooks = booked.filter((b) => b && b.booked).length
log(`tend-heal: ${onBooks}/${kept.length} disposition(s) on the books under ${RUN_ID} — monitor: python -m loop.agent_run --run ${RUN_ID}`)
return { node: NODE, run: RUN_ID, promptHash: PROMPT_HASH, tended: kept.length, actionable: actionable.length, onBooks, drafts: kept }

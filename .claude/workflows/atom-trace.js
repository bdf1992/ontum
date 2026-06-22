export const meta = {
  name: 'atom-trace',
  description:
    'Read-only. Trace one atom across the append-only log: fan out a reader per log surface (events by id, receipts by artifact_hash, admissions, and the merge receipts landed_atoms), then synthesize the atom true folded pipeline state — parked stage, each verdict with its judging node and prompt_hash, landed-on-main yes/no, and the one concrete next action. No mutation. args: an atom id (e.g. atom.heal-override-hash-aware.v0) OR its sha256 content hash (string).',
  phases: [
    {
      title: 'Resolve',
      detail:
        'Turn the single args string into the atom identity — its id and its artifact_hash (sha256 of the file bytes in .ai-native/atoms/). Accept either form and resolve the missing half. If neither resolves to a real atom, return an honest no-such-atom rather than a fabricated state.',
    },
    {
      title: 'Gather',
      detail:
        'Fan out one reader per log surface in parallel: events by id, receipts by artifact_hash (every verdict, node, prompt_hash), admissions naming the atom, and merge receipts landed_atoms for did-it-reach-main. Each reader returns only the records it found — raw facts, no inference.',
    },
    {
      title: 'Fold',
      detail:
        'Synthesize one folded pipeline state: the parked stage, the ordered verdicts each with node and prompt_hash, a landed-on-main yes/no with the merge receipt cited, and the single concrete next action (an existing pen verb). This is the return value — the atom true state read from the log alone.',
    },
  ],
}

// An authored workflow for the workflow-authoring wrapper (A2). Read-only:
// every agent reads the append-only log and reports raw records; the fold is a
// synthesis, and nothing here changes the tree. Parameterized over `args` — the
// single atom id or content hash to trace.
//
// NOTE (graded-speed arc, 2026-06-21): the draft-capability run produced this
// file's meta as '...' + '...' concatenation, which lint.py PASSED but the
// Workflow runtime REJECTS ("meta must be a pure literal"). The meta above was
// collapsed to pure literals by hand. The root fix is making lint.py faithful to
// the runtime — graded-speed.proposal.md, the unfaithful-gate finding.

const target = (typeof args === 'string' && args.trim()) || ''
if (!target) {
  return { target, error: 'no atom id or content hash given in args', state: null }
}

const IDENTITY_SCHEMA = {
  type: 'object',
  properties: {
    found: { type: 'boolean' },
    id: { type: 'string' },
    artifact_hash: { type: 'string' },
    file: { type: 'string' },
    note: { type: 'string' },
  },
  required: ['found'],
}

// --- Resolve: the single string -> {id, artifact_hash}. Load-bearing so the
// receipt reader keys on artifact_hash, never id (the standing lesson). ---
phase('Resolve')
const identity = await agent(
  `Resolve the atom identity for the lookup string: "${target}".\n` +
    `It is EITHER an atom id (looks like atom.<slug>.vN) OR a sha256 content hash ` +
    `(64 hex chars). The atom files live in .ai-native/atoms/ and an atom's pipeline ` +
    `identity is the sha256 of its file BYTES.\n` +
    `- If it is an id: find the atom file, compute its artifact_hash (sha256 of the ` +
    `file bytes), and return both id and artifact_hash.\n` +
    `- If it is a hash: find which atom file's sha256 equals it, and return that file's ` +
    `id and the artifact_hash.\n` +
    `Resolve the missing half yourself so either lookup form works. If NEITHER form ` +
    `resolves to a real atom on disk, return found:false with an honest note — never ` +
    `fabricate an id or hash. Return the identity.`,
  { label: 'resolve', phase: 'Resolve', schema: IDENTITY_SCHEMA },
)

if (!identity || !identity.found) {
  return {
    target,
    error: 'no such atom',
    note: identity?.note || 'neither an atom id nor a content hash resolved',
    state: null,
  }
}

const atomId = identity.id || target
const artifactHash = identity.artifact_hash || ''

// --- Gather: one reader per log surface, in parallel. Each returns only the
// records it found — raw facts, no inference. Bounded fan-out. ---
phase('Gather')
const SURFACES = [
  {
    surface: 'events',
    ask:
      `Read .ai-native/log/events.jsonl and report every line whose subject/atom is ` +
      `the id "${atomId}". For each: the event type, ts, and any next_suggested_event. ` +
      `Raw records only — do not interpret.`,
  },
  {
    surface: 'receipts',
    ask:
      `Read .ai-native/log/receipts.jsonl and report every receipt whose ` +
      `artifact_hash equals "${artifactHash}" (key on artifact_hash, NEVER id). For ` +
      `each verdict: the stage/node, the verdict, the judging node, prompt_hash, and ` +
      `ts, in log order. Raw records only.`,
  },
  {
    surface: 'admissions',
    ask:
      `Read .ai-native/log/admissions.jsonl and report every admission that names the ` +
      `atom id "${atomId}" or the hash "${artifactHash}" (e.g. node_real, confirm-arc, ` +
      `value-gate). For each: kind, by, ts. Raw records only.`,
  },
  {
    surface: 'landed',
    ask:
      `Read the merge receipts in .ai-native/log/receipts.jsonl (the rcp.merge.* / ` +
      `landed_atoms records, the atoms_on_main set). Report whether artifact id ` +
      `"${atomId}" or hash "${artifactHash}" appears in any merge receipt's ` +
      `landed_atoms, and if so cite that merge receipt id. Raw fact only — yes/no plus ` +
      `the citation.`,
  },
]

const readers = SURFACES.slice(0, 8).map((s) => () =>
  agent(s.ask, { label: `gather:${s.surface}`, phase: 'Gather' }).then((text) =>
    text ? { surface: s.surface, records: text } : null,
  ),
)
const gathered = (await parallel(readers)).filter(Boolean).slice(0, 8)

if (!gathered.length) {
  return { target, atom: atomId, artifact_hash: artifactHash, error: 'no records gathered', state: null }
}

// --- Fold: synthesize one folded pipeline state from the gathered records. ---
phase('Fold')
const state = await agent(
  `Synthesize the TRUE folded pipeline state of atom ${atomId} ` +
    `(artifact_hash ${artifactHash}) from these independent, raw reads of each log ` +
    `surface:\n\n` +
    gathered
      .filter(Boolean)
      .map((g) => `## ${g.surface}\n${g.records}`)
      .join('\n\n') +
    `\n\nFold them into ONE state, read from the log alone (never inferred):\n` +
    `- the stage the atom is currently parked at;\n` +
    `- the ordered list of verdicts, each with its judging node and prompt_hash;\n` +
    `- landed-on-main: yes or no, citing the merge receipt id if yes;\n` +
    `- the single concrete next action, named as an existing pen's verb ` +
    `(e.g. loop.node judge / loop.node confirm-arc / pr.py land).\n` +
    `This is the return value.`,
  { label: 'fold', phase: 'Fold' },
)

return { target, atom: atomId, artifact_hash: artifactHash, surfaces: gathered.length, state }

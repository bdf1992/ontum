export const meta = {
  name: 'subsystem-map',
  description:
    'Read-only. Map a subsystem: fan out readers over its parts, then synthesize one ' +
    'structured map (entry points, responsibilities, seams, risks). No mutation. ' +
    'args: a path or a short description of the subsystem to map (string).',
  phases: [
    { title: 'Survey', detail: 'list the parts of the subsystem' },
    { title: 'Read', detail: 'one reader per part, in parallel' },
    { title: 'Synthesize', detail: 'fold the reads into one map' },
  ],
}

// The worked example for the workflow-authoring wrapper (A1). It demonstrates the
// shape every authored workflow shares: a pure-literal meta, phased fan-out,
// and a synthesis stage — all read-only, parameterized over `args`.

const target = (typeof args === 'string' && args.trim()) || 'the loop/ package'

const PART_SCHEMA = {
  type: 'object',
  properties: {
    parts: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          name: { type: 'string' },
          path: { type: 'string' },
          why: { type: 'string' },
        },
        required: ['name', 'path'],
      },
    },
  },
  required: ['parts'],
}

phase('Survey')
const survey = await agent(
  `Survey ${target}. List its distinct parts (files, modules, or components) worth ` +
    `reading separately to understand it. For each: a name, a path, and one line on why ` +
    `it matters. Do not read deeply yet — just enumerate. Return the parts.`,
  { label: 'survey', phase: 'Survey', schema: PART_SCHEMA },
)

const parts = (survey?.parts || []).slice(0, 12) // bound the fan-out
if (!parts.length) {
  return { target, error: 'survey found no parts', map: null }
}

phase('Read')
const reads = await parallel(
  parts.map((p) => () =>
    agent(
      `Read ${p.path} (${p.name}) as part of ${target}. Report, tersely: its ` +
        `responsibility, its entry points / public surface, what it depends on, what ` +
        `depends on it, and any risk or smell. Be concrete; cite symbols.`,
      { label: `read:${p.name}`, phase: 'Read' },
    ).then((text) => ({ part: p, read: text })),
  ),
)

phase('Synthesize')
const map = await agent(
  `You are mapping ${target}. Here are independent reads of its parts:\n\n` +
    reads
      .filter(Boolean)
      .map((r) => `## ${r.part.name} (${r.part.path})\n${r.read}`)
      .join('\n\n') +
    `\n\nSynthesize ONE structured map: the subsystem's purpose in a sentence, its ` +
    `entry points, the responsibility of each part, the seams between parts, and the ` +
    `top risks. Prose + a short bullet structure. This is the return value.`,
  { label: 'synthesize', phase: 'Synthesize' },
)

return { target, parts: parts.length, map }

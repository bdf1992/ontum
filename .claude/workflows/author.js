export const meta = {
  name: 'author',
  description: 'The generative top: reads the volume scoreboard + the section census, finds the most under-served quota, and AUTHORS a tuned tender workflow that would fill it (propose-grain — writes a draft- script, schedules nothing; the activation gesture stays bdo\'s, D-4)',
  whenToUse: 'When the package needs to extend itself: a volume dimension is under target with no tender working it, or a named section has open work but no tuned consumer. One call = one authored draft tender. The cut between draft and scheduled is bdo\'s 5-minute gesture — this only writes the first draft.',
  phases: [
    { title: 'Sense', detail: 'fold the live field — under-filled volume dimensions, sections with open work, the top gap' },
    { title: 'Author', detail: 'compose one tuned tender workflow for the most under-served target, against the existing tenders as the pattern commons' },
    { title: 'Stage', detail: 'write the authored script to .claude/workflows/draft-<slug>.js — PROPOSED, never scheduled' },
  ],
}

// THE GENERATIVE LOOP (bdo, 2026-06-22): "an agent that authors workflows as
// generative loops that launch agents that launch managers over work ... to fill
// volumes and quotas based on setpoints and pattern commons."
//
// The package already CONSUMES work: tend*.js drain named sections (loop/section.py),
// loop/volume.py scores the quota body, loop/fleet.py watches the conductors. The one
// thing missing is the GENERATIVITY — nothing AUTHORS a new tender when a quota goes
// unfilled. This workflow is that top: it closes the loop so the package extends itself.
//
//   volume under-target  ─►  author a tuned tender  ─►  (bdo activates)  ─►  tender
//        ▲                                                                    fills it
//        └──────────────────  volume re-measures  ◄───────────────────────────┘
//
// It is PROPOSE-GRAIN by construction (the law of this directory): it writes ONE
// draft- workflow file (a new, reversible file) and NOTHING else — no schedule, no
// wiring, no spend beyond its own few sensing/authoring agents. A draft- script is
// invocable by name for a human to try, but the 5-minute scheduler never auto-runs
// it; promotion (rename draft-<slug>.js -> <slug>.js after review) is bdo's gesture,
// the same activation cut the tick already lives behind. The author writes the first
// draft; it never decides the tender is real (D-4).
//
// The PATTERN COMMONS is the existing tenders themselves: the author reads tend.js
// and tend-gaps.js as the shape every tender shares (export const meta; sense a
// section; one bounded inference per small item; propose-grain return) and composes
// the new one in that grammar — not from a blank page.

const FIELD = {
  type: 'object',
  additionalProperties: false,
  required: ['targets', 'covered', 'note'],
  properties: {
    // the under-served targets, most-pressing first: a section with open work
    // and no tuned tender, and/or a volume dimension under its target.
    targets: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['kind', 'name', 'why', 'closes_via'],
        properties: {
          kind: { type: 'string', enum: ['section', 'dimension'], description: 'section = a named ledger queue with open work; dimension = a volume target under its fill' },
          name: { type: 'string', description: 'the section name or volume dimension name' },
          why: { type: 'string', description: 'the pressure: open count / fill vs target, and that no tuned tender works it today' },
          closes_via: { type: 'string', description: 'for a section, its closes_via line from loop.section; for a dimension, the measure it counts and the pen that raises it' },
        },
      },
    },
    // the sections/dimensions that ALREADY have a tuned tender (tend-heal=stale-park,
    // tend-gaps=gaps, tend-inbox=owner-asks) — so the author never double-builds one.
    covered: { type: 'array', items: { type: 'string' } },
    note: { type: 'string', description: 'one honest line on the field — e.g. "no volume declared yet, sensing sections only"' },
  },
}

const TENDER = {
  type: 'object',
  additionalProperties: false,
  required: ['slug', 'name', 'description', 'serves', 'cadence', 'script', 'rationale'],
  properties: {
    slug: { type: 'string', description: 'kebab-case, no "tend-"/"draft-" prefix — e.g. "value-confirm" for a value-confirm tender' },
    name: { type: 'string', description: 'the workflow meta.name — MUST equal "draft-" + slug (the staged filename), so it is invocable but never mistaken for a scheduled tender' },
    description: { type: 'string' },
    serves: { type: 'string', description: 'the exact section/dimension name this tender consumes' },
    cadence: { type: 'string', enum: ['tick', 'on-demand', 'slow'], description: 'tick = safe to run every 5-min beat (propose-grain only); on-demand = a human runs it; slow = an hourly/daily fold. The speed band (graded-speed): a quota-filling consumer is "tick", a heavier authoring/migration pass is "slow".' },
    script: { type: 'string', description: 'the COMPLETE .js workflow script: export const meta literal (pure, no interpolation) + body using agent()/parallel(). It must (1) sense its section via the loop fold named in serves, (2) run one bounded inference per open item, (3) be propose-grain — write no verdict, clear no park, return drafts. Model it on tend-gaps.js.' },
    rationale: { type: 'string', description: 'why this tender, why this cadence, and the one thing a reviewer should check before promoting it' },
  },
}

// ---- Sense: fold the live field into under-served targets ----------------------
phase('Sense')
const field = await agent(
  'Sense the loop\'s self-extension field from the repo root. Run, and read the output of:\n' +
  '  - `python -m loop.section list --json`  (the named work queues + open counts + closes_via)\n' +
  '  - `python -m loop.volume` then `python -m loop.volume rates`  (the quota scoreboard; if no volume is declared yet, rates shows what is measurable)\n' +
  '  - `python -m loop.gaps`  (the pressure-ordered gap backlog, for context)\n\n' +
  'The tuned tenders that ALREADY exist (do not propose a duplicate): ' +
  'tend-heal serves "stale-park", tend-gaps serves "gaps", tend-inbox serves "owner-asks", ' +
  'and tend.js is the GENERIC consumer of any section but actuates nothing. ' +
  'Return the under-served targets — a section with open work and no TUNED tender (note: "value-confirm" has the ' +
  'heartbeat drain but no inference tender), and/or a volume dimension under its target — most-pressing first. ' +
  'List the covered ones too so the author cannot double-build. Be honest in `note` about what the field actually shows.',
  { label: 'sense:field', phase: 'Sense', schema: FIELD }
)

const targets = (field && field.targets) || []
if (!targets.length) {
  log('author: no under-served target — every section with open work has a tuned tender, and no volume dimension is under fill. The package is fully manned. No-op.')
  return { authored: null, note: (field && field.note) || 'fully manned' }
}
const target = targets[0]
log(`author: the most under-served target is ${target.kind} "${target.name}" — ${target.why}`)

// ---- Author: compose one tuned tender, in the pattern commons grammar ----------
phase('Author')
const authored = await agent(
  `Author a tuned tender workflow for this under-served ${target.kind}: "${target.name}".\n` +
  `Why it needs one: ${target.why}\n` +
  `How its work is closed: ${target.closes_via}\n\n` +
  'The PATTERN COMMONS is the existing tenders — read them so the new one shares their grammar, not a blank page:\n' +
  '  - `.claude/workflows/tend-gaps.js`  (the cleanest template: sense a section via its loop fold, one bounded inference per small item, propose-grain return)\n' +
  '  - `.claude/workflows/tend.js`        (the generic consumer — shows the section-agnostic shape)\n' +
  '  - `.claude/workflows/CLAUDE.md`      (the law: consumer of a named section, propose-grain by construction, never actuates blind)\n' +
  'and the producer it must read: `loop/section.py` (the section fold) — open the relevant section with ' +
  `\`python -m loop.section items --name ${target.kind === 'section' ? target.name : '<section>'} --json\` shape in your script.\n\n` +
  'HARD CONSTRAINTS on the script you return:\n' +
  '  - `export const meta = {...}` is a PURE LITERAL (no variables, no interpolation) and meta.name === "draft-" + your slug.\n' +
  '  - It SENSES its section/dimension from the live fold (loop.section / loop.volume), never a hardcoded list.\n' +
  '  - One bounded inference per open item (parallel()/pipeline over the items), each returning a checked draft.\n' +
  '  - PROPOSE-GRAIN: it writes NO verdict, clears NO park, schedules nothing, and returns its drafts. ' +
  'If the section\'s close reaches a pen (e.g. the issue pen), the tender DRAFTS the close — it does not actuate ' +
  '(only tend-inbox actuates, behind a non-empty guard, because closing is reversible there; default to draft-only).\n' +
  '  - Stdlib python in the agent prompts; no new dependency.\n' +
  'Pick the cadence honestly: a quota-filling consumer that only drafts is "tick"; anything that would spend or ' +
  'actuate is "on-demand". Return the complete script — it must parse and run as written.',
  { label: `author:${target.name}`, phase: 'Author', schema: TENDER }
)

if (!authored || !authored.script) {
  log('author: could not compose a tender for the target. Reporting the target so a session can author it by hand.')
  return { authored: null, target, note: 'authoring failed — target surfaced for a session' }
}

// guard the staged name: a draft- prefix is the propose-grain marker — the
// scheduler never auto-runs a draft-, and meta.name must match the filename.
const slug = String(authored.slug).replace(/^(tend-|draft-)/, '')
const filename = `draft-${slug}.js`

// ---- Stage: write the authored script as a PROPOSED draft ----------------------
phase('Stage')
const header =
  `// PROPOSED — machine-authored by the \`author\` workflow (the generative top), ${target.kind} "${target.name}".\n` +
  `// This is a DRAFT tender: invocable by name (\`${authored.name}\`) for a human to try, but the 5-minute\n` +
  `// scheduler never auto-runs a draft-. Review it, run it once by hand, then promote it (rename to\n` +
  `// ${slug}.js) — that rename is the activation gesture (D-4). Rationale: ${authored.rationale.replace(/\n/g, ' ')}\n\n`
const scriptText = header + authored.script

// Write the draft through the Stage agent's own Write tool — verbatim, no
// encoding dance (an earlier base64-via-Buffer version assumed a Node global the
// workflow runtime does not expose; the dogfood run caught it). The file content
// is delimited so the agent writes exactly the bytes between the markers.
await agent(
  `Create the file \`.claude/workflows/${filename}\` (a NEW file under the workflows CLAUDE.md) using the Write tool, ` +
  'with EXACTLY the content between the markers below — verbatim, no edits, no added or trimmed lines:\n\n' +
  `----- BEGIN ${filename} -----\n${scriptText}\n----- END ${filename} -----\n\n` +
  `Then run \`node --check .claude/workflows/${filename}\` from the repo root and report the byte count and whether it parses.`,
  { label: `stage:${filename}`, phase: 'Stage' }
).catch(() => null)

log(`author: staged ${filename} — a draft tender for ${target.kind} "${target.name}". Review → run once → rename to promote.`)
return {
  authored: { file: `.claude/workflows/${filename}`, name: authored.name, serves: authored.serves, cadence: authored.cadence },
  target,
  rationale: authored.rationale,
  promote: `rename .claude/workflows/${filename} -> .claude/workflows/${slug}.js after review (bdo's activation gesture)`,
}

export const meta = {
  name: 'draft-capability',
  description:
    'Read-only on the repo tree. A slow-band workflow whose subagents DRAFT fast-band machinery: from a plain-language description of a capability you want a fast agent to have, it frames the shape, fans out to draft a launchable workflow (.js) and its companion skill (SKILL.md), then routes the workflow draft through the EXISTING author-workflow check (lint.py) on a throwaway temp file — it does not re-invent validation. One bounded repair pass if the check refuses. It PROPOSES drafts as its return value; it never writes them into the repo, never arms them, never runs them (arming is A3 / review-workflow, running is A4 — neither is built). args: a plain-language description (string), or { description, slug } (object).',
  phases: [
    { title: 'Frame', detail: 'read the description + the wrapper convention; choose slug, shape, blast radius' },
    { title: 'Draft', detail: 'fan out: draft the workflow .js and the companion skill, in parallel' },
    { title: 'Check', detail: 'reuse author-workflow/lint.py on a temp copy; one bounded repair pass if refused' },
    { title: 'Compile', detail: 'fold the drafts + the verdict into one shaped read for review (A3)' },
  ],
}

// The SLOW band of bdo's speed gradient, made concrete: a workflow that authors
// machinery FOR fast agents (a skill + a launchable workflow), driven by a
// plain-language description. It composes the wrapper rather than re-inventing it:
//  - the home + contract is .claude/workflows/CLAUDE.md (A1),
//  - the soundness check is .claude/skills/author-workflow/lint.py (A2),
//  - the review/arm gate is .claude/skills/review-workflow (A3) — downstream of here.
// Safety posture: it produces DRAFTS as return values and validates them against a
// throwaway temp file OUTSIDE the repo. The repo tree is untouched; nothing is armed
// or run. (lint.py's `mutates` flag is conservative — it sees the verb "write" in the
// check step's temp-file prompt — so a draft may render `mutates`; that is the temp
// file, not the repo. A3 still gets to see and weigh the produced draft.)

const LINT = '.claude/skills/author-workflow/lint.py'

const input =
  typeof args === 'string'
    ? { description: args }
    : args && typeof args === 'object'
      ? args
      : {}
const description = (input.description || '').trim()
if (!description) {
  return {
    error: 'no capability description given',
    hint: 'pass a plain-language description of the fast-agent capability to draft, ' +
      'e.g. "find tests that import a deprecated module and report each call site"',
  }
}
const slugHint = (input.slug || '').trim()

const FRAME_SCHEMA = {
  type: 'object',
  properties: {
    slug: { type: 'string' },
    shape: { type: 'string' },
    blastRadius: { type: 'string', enum: ['read-only', 'mutates'] },
    argsContract: { type: 'string' },
    purpose: { type: 'string' },
    phases: {
      type: 'array',
      items: {
        type: 'object',
        properties: { title: { type: 'string' }, detail: { type: 'string' } },
        required: ['title'],
      },
    },
  },
  required: ['slug', 'shape', 'blastRadius', 'purpose'],
}

phase('Frame')
const frame = await agent(
  `You are framing a NEW native AI workflow + a companion skill for a "fast agent" — an ` +
    `agent that USES the loop and responds to pressure. Do NOT draft yet; just decide the shape.\n\n` +
    `The capability the fast agent should gain, in bdo's words:\n"""${description}"""\n\n` +
    `First READ the two convention files so your shape obeys them:\n` +
    `  - .claude/workflows/CLAUDE.md   (the home + the meta/body contract, A1)\n` +
    `  - .claude/skills/author-workflow/SKILL.md   (the ritual + the four legal shapes, A2)\n\n` +
    `Then decide and return:\n` +
    `  - slug: short kebab-case verb-or-noun (the launch handle)${slugHint ? ` — bdo suggested "${slugHint}"; honor it unless it is clearly wrong` : ''}\n` +
    `  - shape: ONE of "fan-out+synthesize" | "pipeline" | "find->verify" | "loop-until" — the right one, not the biggest\n` +
    `  - blastRadius: "read-only" if the fast workflow only reads/searches/audits, else "mutates"\n` +
    `  - argsContract: what the fast workflow should accept via \`args\` (a path, a question, a config)\n` +
    `  - purpose: one sentence on what the fast workflow does\n` +
    `  - phases: 2-4 phases, each {title, detail}\n` +
    `Prefer read-only. If it must mutate, say so plainly — A3 will need to see it.`,
  { label: 'frame', phase: 'Frame', schema: FRAME_SCHEMA },
)

const slug = (frame?.slug || slugHint || 'fast-capability').trim()
const blastRadius = frame?.blastRadius === 'mutates' ? 'mutates' : 'read-only'
const phaseList = (frame?.phases || []).slice(0, 6)

phase('Draft')
const [workflowDraft, skillDraft] = await parallel([
  () =>
    agent(
      `Draft the FULL text of a launchable native Workflow script for the fast agent, ` +
        `to live at .claude/workflows/${slug}.js. It must SATISFY the author-workflow check:\n` +
        `  1. begin with a PURE-LITERAL \`export const meta = { name, description, phases }\` — ` +
        `no \${} interpolation and no function calls inside meta;\n` +
        `  2. meta.name MUST equal "${slug}" exactly;\n` +
        `  3. phases is an array of { title, detail } objects;\n` +
        `  4. the body uses at least one orchestration primitive: agent() / parallel() / pipeline() / phase();\n` +
        `  5. parameterize over \`args\` (never hard-code the target); bound every fan-out with .slice(0, N) ` +
        `and .filter(Boolean) on agent results.\n\n` +
        `Shape: ${frame?.shape || 'fan-out+synthesize'}. Blast radius: ${blastRadius}` +
        `${blastRadius === 'mutates' ? " — say so in meta.description AND use isolation: 'worktree' on each mutating agent()" : ' — keep it read-only'}.\n` +
        `Purpose: ${frame?.purpose || description}\n` +
        `Args contract: ${frame?.argsContract || description}\n` +
        `Phases to realize: ${JSON.stringify(phaseList)}\n\n` +
        `Model it on the worked reference .claude/workflows/subsystem-map.js (read it). ` +
        `Return ONLY the JavaScript file text — no markdown fences, no commentary.`,
      { label: 'draft:workflow', phase: 'Draft' },
    ),
  () =>
    agent(
      `Draft the FULL text of a companion skill so a fast agent can invoke this capability ` +
        `by name, to live at .claude/skills/${slug}/SKILL.md. Match the house style of an ` +
        `existing skill — read .claude/skills/author-workflow/SKILL.md for the frontmatter shape ` +
        `(--- name / description --- then a short ritual). The skill's job is to LAUNCH the ` +
        `"${slug}" workflow (Workflow({ name: "${slug}" })) with the right args, and to state ` +
        `its blast radius (${blastRadius}) and that arming/running is gated downstream (A3/A4). ` +
        `Capability, in bdo's words: """${description}""". ` +
        `Return ONLY the SKILL.md text — no extra commentary.`,
      { label: 'draft:skill', phase: 'Draft' },
    ),
])

const CHECK_SCHEMA = {
  type: 'object',
  properties: {
    ok: { type: 'boolean' },
    problems: { type: 'array', items: { type: 'string' } },
    mutates: { type: 'boolean' },
    fitOk: { type: 'boolean' },
    dangling: { type: 'array', items: { type: 'string' } },
  },
  required: ['ok', 'problems'],
}

const checkPrompt = (jsText) =>
  `Validate a DRAFT workflow against the existing author-workflow check — do NOT touch the repo. ` +
  `Make a throwaway temp dir (\`mktemp -d\`), write the draft below into it as "${slug}.js", ` +
  `then run, from the repo root:\n` +
  `  python ${LINT} "$TMPDIR/${slug}.js" --json\n` +
  `(where $TMPDIR is the dir you made). Parse the JSON it prints and return: ok (top-level "ok"), ` +
  `problems (the "problems" array), mutates ("flags".mutates), fitOk ("fit".ok), dangling ("fit".dangling). ` +
  `Delete the temp dir when done. Report the verdict faithfully; do not fix anything here.\n\n` +
  `----- DRAFT ${slug}.js -----\n${jsText}\n----- END DRAFT -----`

phase('Check')
let check = await agent(checkPrompt(workflowDraft), {
  label: 'check',
  phase: 'Check',
  schema: CHECK_SCHEMA,
})

let finalWorkflow = workflowDraft
let repaired = false
if (check && check.ok === false) {
  repaired = true
  finalWorkflow = await agent(
    `The author-workflow check REFUSED this draft workflow. Fix ONLY the named problems and ` +
      `return the corrected FULL file text (no fences, no commentary).\n\n` +
      `Problems: ${JSON.stringify(check.problems || [])}\n` +
      `Dangling references: ${JSON.stringify(check.dangling || [])}\n\n` +
      `----- DRAFT ${slug}.js -----\n${workflowDraft}\n----- END DRAFT -----`,
    { label: 'repair', phase: 'Check' },
  )
  check = await agent(checkPrompt(finalWorkflow), {
    label: 'recheck',
    phase: 'Check',
    schema: CHECK_SCHEMA,
  })
}

phase('Compile')
const shapedRead = await agent(
  `Produce a SHAPED READ (the Taster's Clause: organized, reasoned, riskiest step flagged — ` +
    `not a script dump) of a freshly-drafted fast-agent capability, for bdo / a reviewer to weigh. ` +
    `Lead with what it does, then its phases, then its blast radius, then the single riskiest step, ` +
    `then the check verdict. Be terse and honest. Do not recommend running it — arming is A3.\n\n` +
    `slug: ${slug}\n` +
    `shape: ${frame?.shape}\n` +
    `purpose: ${frame?.purpose}\n` +
    `blastRadius: ${blastRadius}\n` +
    `phases: ${JSON.stringify(phaseList)}\n` +
    `lint verdict: ${JSON.stringify(check)}\n` +
    `repaired once: ${repaired}`,
  { label: 'shaped-read', phase: 'Compile' },
)

return {
  slug,
  shape: frame?.shape || null,
  blastRadius,
  draft: {
    workflowPath: `.claude/workflows/${slug}.js`,
    workflow: finalWorkflow,
    skillPath: `.claude/skills/${slug}/SKILL.md`,
    skill: skillDraft,
  },
  lint: check || null,
  repaired,
  shapedRead,
  next:
    'This workflow PROPOSED a draft only — it did not write into the repo, arm, or run anything. ' +
    'To place and arm it, use the author-workflow skill (A2) then review-workflow (A3); the run rail (A4) launches only what is armed.',
}

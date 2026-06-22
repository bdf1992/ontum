# .claude/workflows/ — the workflow-authoring wrapper's home

Authored AI workflows live here. This is the **native** home: the
Workflow tool resolves a named workflow (`Workflow({name: "<slug>"})`)
from this directory, so a script that lands here is launchable by name
with no extra wiring. The branded wrapper over the native workflow
surface
([`workflow-authoring-wrapper.proposal.md`](../../.ai-native/proposals/workflow-authoring-wrapper.proposal.md))
rides this convention instead of inventing one.

## What a workflow file is

One JavaScript file per workflow, `<slug>.js`. It is a script against the
native Workflow orchestration: it **must** begin with a pure-literal
`export const meta = { name, description, phases }` block, then a body
using `agent()` / `parallel()` / `pipeline()` / `phase()`. The `meta.name`
is the launch handle and should equal the file's `<slug>`.

## The naming + safety convention (A1)

- **Name** = a short kebab-case verb-or-noun that says what it does
  (`subsystem-map`, `review-diff`, `find-flaky-tests`). The file is
  `<name>.js`; `meta.name` matches.
- **Read-only by default.** A workflow that only reads (search, map,
  audit, synthesize) is safe to author and run freely. A workflow whose
  agents **mutate** files declares it in its `meta.description` and uses
  `isolation: 'worktree'` per mutating agent — and, per the wrapper, does
  not run unattended until the review gate (A3) and the authority dial
  exist. Until then: review before run.
- **Args, not hard-coding.** Parameterize over `args` (a path, a
  question, a config object) so one authored workflow serves many runs.
- **Authored here, reviewed before armed.** A2 (the authoring agent)
  drafts into this directory; A3 (the review interface) renders a draft
  as *what it does · phases · blast radius · riskiest step* and arms it.

## Rule of this directory

A workflow is **config-as-code** (§7): versioned, reviewed, landed as a
stamped increment — never a throwaway. When the bespoke live portal
arrives, these files and their review surface carry straight over.

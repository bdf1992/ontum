---
name: review-workflow
description: Review a drafted AI workflow before it is allowed to run — render it as a shaped read (what it does · its phases · its blast radius · the riskiest step) and, on approval, arm it (a recorded act on the log). Use when bdo wants to review a workflow, decide whether to approve/arm one, see what an authored workflow would do, or runs "/review-workflow". This is A3 of the workflow-authoring wrapper (.ai-native/proposals/workflow-authoring-wrapper.proposal.md): the author skill drafts, this skill reviews and arms, the run rail (A4) launches only what is armed. The pen is review.py beside this file.
---

# review-workflow — see what it does, then arm it

The review half of the branded wrapper (mirrors the PR pen). It does not run a
workflow; it makes a draft **legible** before anyone runs it, and records the
approval as a fact on the log.

## The shaped read (the Taster's Clause, not a script dump)

```sh
python .claude/skills/review-workflow/review.py render .claude/workflows/<slug>.js
```

renders the draft as: **what it does**, its **phases**, its **blast radius**
(`read-only` or `mutates`), and the **riskiest step** — plus whether it is
currently armed. A draft that fails the authoring check is shown as REFUSED with
the reason; you cannot arm it. `--json` emits the dataset (for a future page).

## Arming (the recorded approval)

```sh
python .claude/skills/review-workflow/review.py arm .claude/workflows/<slug>.js --by bdo
```

writes one `workflow_armed` admission to the log: who approved, which workflow,
its path, and its **bytes** (`version_hash`). Arming binds to the bytes — the
repo's content-hash identity invariant — so **editing a workflow un-arms it** and
it must be reviewed again. The run rail (A4) refuses any workflow not armed at its
current bytes.

Arming **refuses** a workflow that fails the authoring check *or* the §10 fit
check — a `workflow('slug')` reference to a missing or malformed sibling (two
locally-fine workflows that refuse to fit). To withdraw approval without editing
the file (a workflow found dangerous), **disarm** it — a superseding record, on
the log, never an erase:

```sh
python .claude/skills/review-workflow/review.py disarm .claude/workflows/<slug>.js --by bdo
```

## The discipline

- **Render before arm.** Always look at the shaped read first. A `mutates`
  workflow's riskiest step (it writes files; must run worktree-isolated) is the
  thing to actually check before approving.
- **Arming is an act, not a label.** It is recorded with provenance; it is not a
  comment or a flag. Only arm what you would run.
- **The wrapper requires an arm before every run** until the risk-tiered
  authority dial exists (see the proposal) — there is no unattended path yet.
- **No second write path.** Arming goes through this pen (the same `append_line`
  seam every pen uses); there is deliberately no other way to mark a workflow
  runnable.

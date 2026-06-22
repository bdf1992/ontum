---
name: author-workflow
description: Help bdo author a native AI workflow from a plain-language description — draft the Workflow script into .claude/workflows/, validate it against the wrapper convention before showing it, and never arm a draft that fails the check. Use when bdo says "author a workflow", "make me a workflow that…", "write an agent/workflow to…", describes a multi-agent job he wants to launch by name, or runs "/author-workflow". This is A2 of the workflow-authoring wrapper (.ai-native/proposals/workflow-authoring-wrapper.proposal.md): agents help author workflows; a separate review interface (A3) arms them. The draft check is lint.py beside this file. It PROPOSES a draft; it never runs it.
---

# author-workflow — describe it, I draft it, the check proves it sound

The authoring half of the interim bench. bdo describes a job in plain language;
this skill turns it into a launchable native Workflow script in
`.claude/workflows/`, **validated before it is shown**. It does not run the
workflow — running is A4, and arming is the review interface (A3).

## The home and the contract

Authored workflows live in `.claude/workflows/<slug>.js` and are launched by
name (`Workflow({name: "<slug>"})`). The structural contract is in
[`.claude/workflows/CLAUDE.md`](../../workflows/CLAUDE.md). The deterministic
check of that contract is [`lint.py`](lint.py) beside this file.

## The ritual

1. **Read the gesture.** What is the job? What does it read or change? Is it
   read-only (safe) or does it mutate the tree (needs worktree isolation + a
   review before any run)? If the description is too thin to draft a sound
   workflow, ask one shaping question — do not invent scope.

2. **Pick the shape** from the native Workflow patterns — the right one, not the
   biggest:
   - **fan-out + synthesize** (`parallel` then one `agent`) — survey/map/audit.
   - **pipeline** (`pipeline(items, stageA, stageB)`) — per-item multi-stage work
     with no barrier; the default for multi-stage.
   - **find → verify** — fan out finders, then adversarially verify each finding.
   - **loop-until** (count / dry / budget) — unknown-size discovery.
   `subsystem-map.js` is the worked reference for the fan-out+synthesize shape.

3. **Draft the file.** Write `.claude/workflows/<slug>.js`:
   - begin with a **pure-literal** `export const meta = { name, description,
     phases }` — `meta.name` MUST equal `<slug>`;
   - parameterize over `args` (a path, a question, a config), never hard-code;
   - read-only by default; if it mutates, say so in `description` and use
     `isolation: 'worktree'` on each mutating `agent()`;
   - bound every fan-out (`.slice(0, N)`), and `.filter(Boolean)` agent results.

4. **Run the check — this is the gate, not a formality:**
   ```sh
   python .claude/skills/author-workflow/lint.py .claude/workflows/<slug>.js
   ```
   If it REFUSES, fix the named problem and re-check. **Never show or hand off a
   draft that fails.** A `mutates — needs review` flag is not a failure; it is
   the signal the review interface (A3) must see before the workflow is armed.

5. **Hand off, don't launch.** Present the sound draft as *what it does · its
   phases · its blast radius (read-only or mutates) · the riskiest step* — the
   shape A3 will render. Authoring proposes; arming and running are downstream.

## Rules

- **The check is law.** A draft that fails `lint.py` is not authored — it is a
  refused attempt with a named reason. No exceptions.
- **Read-only is the default; mutation is declared, isolated, and reviewed.**
- **One workflow, one job.** Don't bundle unrelated jobs into one script; author
  two.
- **Propose, never run.** This skill writes a draft. It does not call the
  Workflow tool. (D-4: the run is gated downstream.)

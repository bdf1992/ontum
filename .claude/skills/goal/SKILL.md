---
name: goal
description: >-
  Define the next pressure-bearing unit of work in Ontum without collapsing
  durable outcomes into single-session done-lines. Use when bdo runs /goal,
  asks to set the next goal, define what Claude should cook on, or convert
  live pressure into executable work. This ritual first distinguishes outcome
  pressure from session work, then derives candidates from the live field,
  owner intent, and any outcome-pressure probes. It may create either:
  (1) an outcome proposal / probe-set when the desired reality is multi-session,
  or (2) a frozen done-line when the work is truly session-scoped. It never
  treats a done-line as completion of an outcome, never invents a missing epic,
  never stamps for bdo, and never writes without explicit confirmation.
version: 0.2.0
owner: bdo
changelog:
  - version: 0.2.0
    note: >-
      Corrects the Goal->Session collapse. A goal may be an outcome-pressure
      object spanning sessions, while a done-line is a single-session stop
      condition. Desired reality must be evidence-bearing through probes.
      The ritual now chooses the correct artifact instead of always minting
      a done-line.
---

# /goal — carrying outcome pressure into executable work

A goal here is **not automatically a done-line**.

A done-line is single-session: frozen, bounded, and shaped by "when met, stop."

A goal may be larger: a durable desired reality that spans many sessions. In
that case, the goal is not completed by writing audits, contracts, or plans.
Those may be instruments, probes, or session progress toward the goal.

This ritual exists to prevent that collapse.

`/goal` asks first:

> Are we defining an outcome, or are we defining the next session-sized move
> that reduces pressure toward an outcome?

## Core distinction

| Thing | Meaning | Artifact |
| --- | --- | --- |
| **Outcome** | A desired reality that persists across sessions | Probe-set / proposal / epic horizon pressure |
| **Probe** | Evidence-bearing predicate that can resolve met / partial / unmet | Outcome-pressure input |
| **Session work** | One bounded unit of focused execution | Done-line |
| **Task** | A thinner implementation step | Atom / story / task, not this ritual's output |

A done-line may serve a goal.
A done-line is not the goal unless the goal is truly session-sized.

## Step 0 — Read pressure before naming work

Read the existing field and any outcome-pressure artifacts.

```sh
python -m loop.gaps
python -m loop.digest
ls .ai-native/epics/
```

If available, also read:

```sh
python -m loop.pressure
```

If no outcome-pressure fold exists yet, infer carefully from committed
evidence, open reports, audits, PRs, and bdo's current intent. Mark that
inference as provisional.

Summarize:

- current work-pressure,
- current outcome-pressure,
- owner-pressure,
- what is janitorial pressure versus outcome pressure,
- what is blocked by missing evidence.

## Step 1 — Classify bdo's intent

Before proposing work, classify the request:

1. **Outcome definition** — bdo is naming a desired reality that spans sessions.
2. **Probe definition** — bdo is making desired reality measurable.
3. **Session execution** — bdo wants the next focused unit of work.
4. **Clarification / audit** — bdo wants to understand current reality before building.

Say which one it is.

If it is multi-session, do **not** force it into a done-line.

## Step 2 — If outcome-sized, define evidence-bearing probes

For outcome-sized goals, draft a probe-set instead of a done-line.

Each probe must include:

- desired condition,
- evidence source,
- check method,
- met / partial / unmet resolution,
- non-example,
- owner-blessing status.

Refuse any probe that cannot be checked.

Aspirational prose is allowed as horizon, but it is not allowed as a probe.

Example:

```text
Outcome:
Causality is the operational knowledge surface for Ontum.

Probe:
A graph persists across reload.

Check:
Create graph -> save -> reload -> graph survives with node config and edges.

Evidence:
browser test, saved graph file, test receipt.

Non-example:
A demo template reloads successfully but user-authored graph state is lost.
```

## Step 3 — If session-sized, draft a done-line

Only create a done-line when the chosen work is actually a bounded unit of
execution.

A valid done-line must:

- reduce a named pressure,
- ladder to an existing epic or outcome,
- name the evidence it will produce,
- include a non-example,
- stop when met.

It must not pretend to complete the whole outcome.

Bad:

```text
Done when Causality is an operational knowledge surface.
```

Good:

```text
Done when Causality has a saved-graph schema and a failing/passing
persistence test proving a user-created node survives reload.
```

## Step 4 — Surface candidates

Offer 2–3 candidates, clearly labeled by type:

```text
Outcome candidate
Probe candidate
Session done-line candidate
```

Each candidate must name:

- pressure source,
- epic / outcome home,
- evidence produced,
- why now,
- what it does not complete.

Let bdo choose or redirect.

## Step 5 — Pressure-test the chosen candidate

Run the chosen candidate through:

- Is this outcome-sized or session-sized?
- What evidence proves it?
- What would falsely look done?
- What pressure does it reduce?
- What remains after it completes?
- Does it require owner blessing?
- Does it belong to an existing epic/outcome?
- If it fails, how will the system notice?

If these cannot be answered, do not write. Return to candidate shaping.

## Step 6 — Write only the correct artifact

### If outcome/probe-sized

Write a proposal or probe-set. Do not mint a frozen done-line unless the
session also has a bounded implementation move.

Possible locations:

```text
outcomes/
pressure/
proposals/
.ai-native/reports/
```

Use the repo's existing conventions if a canonical location exists.

### If session-sized

Mint the done-line through the records pen only:

```sh
python -m loop.pen new done --slug <kebab-slug> --title "<single-session stop condition>" --body -
```

The body must include:

```text
> **Done when:**
> **Non-example:**
> **Pressure reduced:**
> **Does not complete:**
> **Evidence expected:**
```

Then stop. `/goal` does not execute the workhorse session.

## Hard refusals

- Do not collapse a multi-session outcome into a done-line.
- Do not call a goal done because a document, audit, or plan exists.
- Do not write probes that cannot be checked.
- Do not invent a missing epic.
- Do not stamp for bdo.
- Do not create a second write path around the records pen.
- Do not treat janitorial work-pressure as outcome-pressure unless it directly
  blocks the desired reality.
- Do not say "done" when the artifact is unlanded, unmerged, or only local.

## Output format before writing

Before any write, present:

```text
Classification:
Outcome / Probe / Session done-line / Audit

Pressure:
What pressure this responds to.

Chosen artifact:
What will be written and where.

Done does not mean:
What this will not complete.

Confirmation needed:
Yes / no, and from whom.
```

## References

- `ai-native-loop-substrate.md`
- `.ai-native/epics/`
- `.ai-native/done/`
- `loop/gaps.py`
- `loop/digest.py`
- `loop/pen.py`
- outcome-pressure proposal, if present

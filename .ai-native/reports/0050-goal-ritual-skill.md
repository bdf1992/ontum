# Report 0050 — The /goal skill — a multi-step goal-definition ritual

## What landed

**Done-line 0059** (`goal-ritual`) and **`.claude/skills/goal/SKILL.md`**
(v0.1.0): a no-code, multi-step `/goal` ritual that defines and creates
*one* ontum goal worth an hour+ of attention, derived over the live field
and a conversation with bdo. It thinks, then it writes.

- **Two sources.** Step 0 derives over the field through folds that
  already exist (`loop.gaps`, `.ai-native/epics/`, `loop.digest`) — the
  skill adds no Python. Steps 1–3 derive over dialogue with bdo.
- **Goal best-practices × ontum, as one gate.** Every candidate is held
  to a five-row checklist: specific/outcome-stated (→ one epic piece),
  measurable/falsifiable (→ a receipt could prove it + a required
  non-example + the §10 refusal test), right-sized (→ an hour+ unit,
  thicker than a ticket, thinner than an epic), relevant (→ ladders to an
  existing epic's horizon, else `needs-you`), time-bound (→ "when met,
  stop").
- **Thinks then writes.** Step 4 mints the goal as the next numbered
  done-line through the existing records pen (`loop.pen new done`) — never
  a second write path, never editing a frozen line, never inventing a
  missing epic, never stamping for bdo.

### The §10 pair (the receipt the done-line demanded)

- **Positive — derivation runs, with teeth.** Step 0's folds executed
  live against this repo with no new code. They yielded real orientation,
  including a genuine hour+ candidate the field already carries:
  `loop/digest` flags `epic.the-field`'s divergence — `loop/field.py` was
  promised by `atom.field-topology.v0` and reached `ready_for_spec`, but
  the file does not exist and done-line 0050 is already waiting. That is a
  locally-fine candidate that *does* fit (specific, measurable against
  0050, right-sized, ladders to `epic.the-field`'s horizon).
- **Negative — the gate refuses a misfit.** A plausible-but-bad candidate
  is refused, not softened: a ticket-thin item ("add a docstring to
  `census.py`") fails *right-sized* and *outcome-stated* — no changed
  system state, below the hour+ floor `epic.owner-harness` rejects; and a
  homeless item ("wire a Slack standup bot") fails *relevant* — no epic's
  horizon it ladders to, so the ritual surfaces `needs-you` rather than
  authoring an epic. Two locally-plausible asks refuse to fit, and the
  checklist notices.

## needs-you

Nothing blocking. One standing item surfaced for awareness, not action:
the field-derivation already points at a live, well-formed goal —
**build `loop/field.py` against done-line 0050** (the `epic.the-field`
divergence in the digest). That is exactly the kind of goal `/goal` is
built to crystallize; it is offered as the natural first real invocation,
bdo's to take or redirect.

## End-state

`report` — `/goal` is built, frozen-done-line and skill landed, §10 pair
proven; the next move is the first *real* `/goal` pass to define bdo's
own hour+ goal.

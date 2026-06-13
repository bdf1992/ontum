---
name: goal
description: >-
  Define and create one ontum goal worth an hour+ of focused attention,
  derived over the live field and a conversation with bdo. Use when bdo
  runs /goal, asks to "set a goal", "define the next goal", "give me
  something to work on", or wants a bounded, well-formed unit of work
  before a workhorse session. A multi-step ritual, not a one-shot: it
  orients over the field (existing read-only folds — loop.gaps, the
  epics, loop.digest; it adds no code of its own), surfaces candidates
  tied to real epics, pressure-tests the pick against a goal
  best-practices checklist mapped onto ontum's own gates, sharpens the
  definition of done in dialogue, and — only on confirmation — writes the
  goal as the next numbered done-line through the records pen
  (loop.pen new done). It thinks, then it writes. There is no second
  write path; it never invents a missing epic and never stamps for bdo.
version: 0.1.0
owner: bdo
changelog:
  - version: 0.1.0
    note: >-
      First form (done-line 0059). A no-code, multi-step /goal ritual:
      derive over field + dialogue, hold every candidate to the goal
      best-practices x ontum checklist, culminate by minting the goal as
      a frozen done-line through loop.pen. Survey/dashboard mode and
      auto-starting the workhorse session are named out of scope.
---

# /goal — defining the next goal worth an hour

A goal here is not a task and not a wish. It is **one bounded unit of
work worth an hour or more of focused attention**, named *before* the
work, with a clear signal that says *stop* when it is met. In ontum that
artifact already exists: it is a **done-line** (`.ai-native/done/`,
§9.4) — written before code, and **frozen the instant it is written**
(done-line 0033). You cannot edit it later, and only bdo can move it. So
this ritual earns its length: it is the careful front door to writing a
done-line you will have to live with.

`/goal` derives the goal over **two sources at once**:

1. **The field** — the live state of the repo, read through folds that
   already exist. This skill writes no code and adds no Python; it
   *reads* `loop.gaps`, `.ai-native/epics/`, and `loop.digest`.
2. **The conversation with bdo** — what he actually wants to move next.
   A goal pulled only from the field is mechanical; a goal pulled only
   from talk floats free of what is real. The good one is the
   intersection.

It **thinks, then it writes.** Steps 0–3 are thinking. Step 4 is the
write. Do not skip to the write.

## The checklist every candidate must pass

Good goal-setting and ontum doctrine agree; this ritual enforces both as
one gate. Hold every candidate against all five — and surface, out loud,
any it fails. A candidate that fails is *refused*, not softened.

| Best practice | The ontum-native gate |
|---|---|
| **Specific / outcome-stated** | Names a *changed state of the system* tied to one existing epic piece — not a list of tasks, not "work on X". |
| **Measurable / falsifiable** | A receipt could prove it (*no receipt, no version bump*). It carries a required **non-example** and the **§10 refusal test**: could two locally-fine atoms refuse to fit, and would a gate notice? If everything would pass on the first try, the bar isn't doing its job. |
| **Right-sized** | An **hour+** unit — *thicker than a ticket* (the scale `epic.owner-harness` explicitly rejects) and *thinner than a whole epic*. Out of room means shrink the scope and ship the smaller thing (§9). |
| **Relevant / connected to a why** | It ladders up to an existing epic's `horizon`. If **no epic fits**, surface it as `needs-you` — do **not** author a new epic. Absence is information. |
| **Time-bound** | "When met, **stop**" is the envelope. The hour+ of attention is the budget, not an open tab. |

## The program

### Step 0 — Derive over the field (read-only)

Run the existing folds and read the arcs. Add no code.

```sh
python -m loop.gaps          # the pressure-ordered backlog — the top one is the work
ls .ai-native/epics/         # the nine arcs; read the relevant epic.*.json (arc, horizon, pieces)
python -m loop.digest        # what landed / refused / awaits, arc-first — the recent weather
```

Lay out, briefly: where pressure sits, which epic is climbing, and the
top open rungs. This is the field half of the derivation — orient before
proposing.

### Step 1 — Surface candidates

From the field plus bdo's opening intent, put **2–3 candidate goals** on
the table. Each must be tied to a **real epic piece** — name the epic and
the piece. Do not invent candidates the field doesn't support; if bdo's
intent points somewhere no epic covers, say so plainly. Let him pick or
redirect.

### Step 2 — Pressure-test the pick

Run the chosen candidate through the checklist above, out loud, one row
at a time. Name every gate it fails. Specifically interrogate:

- **Size:** is this genuinely an hour+, or is it ticket-thin (refuse) or
  a whole epic in disguise (split or narrow)?
- **Home:** which epic's horizon does it ladder to? If none fits, this is
  a `needs-you` — surface it, don't manufacture a home.
- **Teeth (§10):** how could this goal's atoms *refuse to fit*, and would
  a gate notice the misfit? If you can't name a way it could fail, the
  bar is too soft — sharpen it until you can.

A candidate that can't clear the checklist does not get written. Say why,
and return to Step 1.

### Step 3 — Draft the definition of done

In dialogue, write the **"when this is true, stop"** line in bdo's terms
first, plus the required **non-example** (what would look done but isn't).
Iterate until it is sharp — this is the step the freeze makes matter,
because the next step makes it permanent. Read the draft back and get his
explicit confirmation.

### Step 4 — Commit the goal (the write)

On confirmation only, mint the goal as the next numbered done-line
through the **existing records pen** — never a hand-written file, never a
second write path:

```sh
python -m loop.pen new done --slug <kebab-slug> --title "<the goal, one line>"
# or, one-move with the full body (Done-when + non-example + out-of-scope):
python -m loop.pen new done --slug <kebab-slug> --title "<...>" --body -
```

The pen scaffolds the heading and enforces the form (`> **Done when:**`).
Fill the bar you sharpened in Step 3. The written line **is** the created
goal: a frozen contract the workhorse session then executes against.

Then stop. `/goal` ends at a defined, written goal — it does not start
the hour+ of work itself (that is a separate session against this
done-line).

## Hard refusals (the ritual will not)

- **Edit or soften a frozen done-line.** Once written, a goal is a
  contract. If a landed goal's bar is wrong, name it in the report's
  `needs-you` and keep working — moving it is bdo's alone (`loop.pen
  supersede-done --by bdo`).
- **Invent a missing epic or a missing why.** No epic fits → `needs-you`,
  not authorship. Absence is information (hard rule).
- **Stamp for bdo or open a second write path.** Goals land only through
  `loop.pen`; verdicts and confirmations are bdo's gestures, never this
  ritual's.
- **Write a goal that hasn't cleared the checklist**, or skip the
  thinking to get to the write.

## Not this ritual's job (named, for later)

- **A survey / dashboard of all nine epics' progress** — the full-ladder
  progression map is a distinct read-only view; this ritual defines *one*
  goal and stops.
- **Running the workhorse session** — executing the goal is separate work
  against the frozen done-line.

## References (cite, don't copy — single source of truth)

The ritual derives over these; it never duplicates them. Read the live
file, not a paraphrase.

- **The doctrine** — `ai-native-loop-substrate.md`: §9 (working method —
  the definition of done is written *before* the work; out of room means
  ship the smaller thing), §10 (the refusal test — two locally-fine atoms
  that refuse to fit, and the gate that notices), §12 (the tripwire —
  polishing instead of building is the signal to go build), D-4 (the owner
  is the last stop).
- **The done-line discipline** — `.ai-native/done/` and its `.pen.json`;
  done-line 0033 freezes a written line (the bar is a contract, not a
  draft). The records pen is `loop/pen.py` (`python -m loop.pen new done`).
- **The arcs** — `.ai-native/epics/epic.*.json`: each carries `arc`,
  `horizon`, and `pieces` (atom + glue). A goal ladders to one epic's
  horizon or it is `needs-you`. Why ticket-scale is refused:
  `epic.owner-harness` (the owner steers arcs, not tickets).
- **The field folds** — `loop/gaps.py` (the pressure-ordered backlog, the
  top one is the work), `loop/digest.py` (what landed / refused / awaits,
  arc-first, with divergences).

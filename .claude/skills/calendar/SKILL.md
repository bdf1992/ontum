---
name: calendar
description: The ontum↔calendar bridge — prepare the daily owner-meeting, publish it as a record to the private calendar repo (bdf1992/calendar), and consume the owner's decisions back into ontum. Use to publish a meeting (so bdo can open it from any device), to land a finished meeting's decisions, or to understand the meeting lifecycle. The pen is calendar.py beside this file; the prepared agenda comes from loop/meeting.py; the model is decoupled pub/sub — the calendar repo is standalone and ontum is one subscriber.
---

# calendar — the ontum ↔ calendar bridge

bdo, 2026-06-22: a private **`calendar` repo** (`bdf1992/calendar`) is the central
pub/sub substrate where every meeting lands, reachable from any device — git is
the cross-device layer. ontum is the **first producer**. This skill is the
outward seam: `loop/meeting.py` (a pure fold) prepares the agenda; this pen
*reaches* the calendar repo (the no-network rule keeps reach out of `loop/`,
exactly as `reflect.py` does).

**Decoupled pub/sub** (bdo's call): the calendar repo never needs ontum present.
ontum *publishes* a record; the runner (the agent bdo opens the meeting with)
*writes decisions* into that record; ontum *subscribes* and lands them.

## The lifecycle

```
PREPARE   loop/meeting.py        rank + 30-min-cap the owner-asks -> the agenda
PUBLISH   calendar.py publish    write the meeting record to bdf1992/calendar + log it
OPEN      bdo, any device        opens meetings/<date>-owner-asks/ in Claude Code
RUN       the folder's CLAUDE.md  the agent walks the agenda, takes confirm/defer/discharge
TRANSCRIBE the runner            writes decisions[] + TRANSCRIPT.md, commits them back
LAND-BACK calendar.py consume    ontum records each decision (closing evidence) + actuates it
```

## Verbs (the pen is `calendar.py`)

```sh
# the prepared meeting record, to stdout — dry, no reach
python .claude/skills/calendar/calendar.py build [--date YYYY-MM-DD]

# publish it to the calendar repo and record the publish on ontum's log
python .claude/skills/calendar/calendar.py publish --by <who> [--date YYYY-MM-DD] [--repo bdf1992/calendar]

# land a finished meeting's decisions back into ontum (decoupled subscribe)
python .claude/skills/calendar/calendar.py consume --meeting meeting.<date>-owner-asks --by <who>
```

## How a decision lands (the return leg)

The runner records each decision in the repo as
`{"id": "<agenda-item-id>", "verdict": "confirm|defer|discharge", "note": "...", "by": "bdo"}`.
`consume` reads them and, for each not-yet-seen decision:

1. **records** it as a first-class `meeting_decision` event on ontum's log — the
   closing evidence;
2. **actuates** it through the existing pen — a `discharge` of an owner-ask calls
   `reflect.discharge_owner_ask` *citing that event*; `confirm`/`defer` are
   recorded-only until their handlers land (named, honest).

It is **idempotent**: a decision already on the log is never re-applied (the
re-run law). The cut stays bdo's — the runner serves, the owner decides (D-4).

## Rules

- **No second source of truth.** ontum's log stays the record of fact; the
  calendar record is the delivery surface, and decisions become real ontum
  records only through `consume`.
- **Reach lives in the pen.** `loop/meeting.py` is network-free; every gh call is
  here, behind injectable `put_file`/`get_json` (tested without a network).
- **The owner meeting is one meeting type.** The substrate is general — new
  meeting types are new `type` values with the same record shape.

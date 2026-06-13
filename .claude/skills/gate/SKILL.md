---
name: gate
description: Launch a real gate — a mortal judging process for an atom parked at an admitted-real node. The gate composes its context from the ambient log state (node prompt, atom, arc, prior receipts), launches a headless claude that runs real inference and returns one verdict, lands that verdict through the one pen (loop.node judge), and opens a GitHub issue for the run at its birth (bdo's trust rail — every headless run is watched until the gate earns trust). Use when an atom is parked awaiting a real node (summon/inbox shows "awaiting <node>"), when asked to make a gate judge for real instead of mock, or to demonstrate a gate saying yes/no/amend on real content. The pen is gate.py beside this file.
---

# gate — a real gate is a launcher of mortal minds

The hollowness this repo carried: the gates never *launched* anything. A
mock gate returns a constant; nothing is born, nothing runs inference,
nothing can refuse. This skill makes a gate real.

## The pen

```sh
python .claude/skills/gate/gate.py launch \
    --atom <atom-id> --node <node-id> --by <who>
```

It does five things, in order:

1. **Reads the registered surface** (`github-issues`) from the log — no
   surface, no launch (the trust rail has nowhere to write).
2. **Composes the judging context** from the ambient state of the log: the
   node's versioned prompt (the criteria, hashed), the atom (the claim),
   the epic it serves and its glue, and the receipts already on this exact
   atom version (the hesitations it inherits). This composition *is* the
   gate's intelligence — not a fixed verdict, a prompt assembled from
   everything the log knows right now.
3. **Opens a GitHub issue at the process's birth, before it runs** — bdo's
   trust rail. The issue closes with the verdict; it stays open if the
   process hangs or crashes (an unfinished run stays visible).
4. **Launches a mortal `claude -p`** that runs real inference, reasons in
   the open, and returns exactly one verdict from the seam's terminal set.
5. **Lands the verdict through the one pen** (`loop.node judge`, D-4 — the
   pen never writes a verdict itself) and **records the run** on the ledger
   (`loop.runs record`).

## Before launching

The launch asks the **trust ladder** first (done-line 0054): a mortal
`claude -p` blinks in as the `summoned-session` class, and the pen refuses
to birth it while that class holds no `judge` rung — the pen half of
"pens and the spawn rail enforce the rung at act time"
(atom.trust-ladder.v0). The refusal names the fix: bdo grants the rung by
gesture (the rung-intake skill); `python -m loop.trust ladder` shows what
each class holds.

The atom must be **announced and parked** at the gate (the seam must be
open), and the gate's stage must be **admitted-real**:

```sh
python -m loop.summon              # shows what is parked, awaiting which node
python -m loop.orchestrate         # seeds/announces a new atom, parks it at a real gate
python -m loop.node admit-real --stage <mock-node> --node <real-node> --by bdo
```

If `judge` reports "no announced event awaits judgement", the atom is not
yet in the pipeline — announce it (orchestrate) first. If it reports
"stage … is not admitted-real", the loop is still judging its own mock —
admit the real node (bdo's call, `--by bdo`).

## Hard rules this pen keeps

- Outward reach (gh) and process launch (claude) live **here, in the pen**,
  never in `loop/` (no network, no subprocess — local-first holds even
  though the dependency ban lifted). The pen *reads* the log; it *writes* the
  verdict only through `loop.node judge` and the run only through
  `loop.runs record` — the seams stay the seams.
- A node never judges an event it announced (D-2) — `loop.node judge`
  refuses it; the pen does not try.
- The verdict's receipt carries the `prompt_hash` of the exact node prompt
  that judged (§7) — every verdict attributable.

## §10

The proof a gate is real is that its verdict *could have been its opposite*.
The composed prompt binds the launched mind to name the one check that could
have failed and didn't. First exercised by `atom.rename-vars.v0` — a hollow,
agent-serving atom the value gate refused `reject_no_value`, the first
non-accept verdict on the log (done-line: first light; GitHub issue #47).

# Contributing

This is not a conventional open-contribution repo. It runs as a two-party
loop — **bdo** (PM, owner) and **Claude** (engineering) — under the doctrine in
[`ai-native-loop-substrate.md`](ai-native-loop-substrate.md). The doctrine is
the contract: it is a doc we work from, not a rulebook we answer to, and if
something in it is wrong or in the way, the move is to say so and change it —
not to quietly work around it.

These guidelines exist mostly so that *future sessions* (human or model) pick
up the discipline without re-deriving it.

## The working agreements (doctrine §9)

1. A version means a real capability landed, not "I added more structure."
2. **No receipt, no version bump.**
3. Skeleton first, then one real node at a time — no second one until the
   first has a passing receipt.
4. **Write the one-line "done" before starting.** When it's met, stop.
   Done-lines live in `.ai-native/done/`.
5. Timebox the work, not the result — out of room means shrink the scope and
   ship the smaller thing.
6. Every version leaves behind something useful on its own, so stopping
   anywhere still leaves working pieces.

## Hard rules

- **Read-only zones stay read-only.** `docs/phase-2/` and `docs/sources/` are
  context, not material. The loop must not import, integrate, refactor, or
  "improve" anything in them. If a build seems to need them, that is a scope
  error — report it, don't code around it.
- **Don't invent missing context; absence is information.** If the doctrine or
  a briefing references something that isn't on disk, stop and surface it
  (`needs-you`) rather than authoring it yourself. Anything that *must* be
  authored provisionally gets flagged as provisional in the file itself.
- **The log is truth (D-5).** `.ai-native/log/` is append-only;
  `queues/`/`offsets/` are a cache and must remain a pure fold over the log.
  Appends are line-atomic with torn-tail tolerance.
- **No one signs their own line (D-2).** A node never judges its own writer's
  work; every gate reads someone else's output.
- **bdo merges (D-4).** Sessions develop on their assigned `claude/*` branch
  and push there; merging to main is the owner's act, not the session's. The
  full lifecycle is the
  [branch-ritual skill](.claude/skills/branch-ritual/SKILL.md) — run it at
  hand-off, and when the Branches page needs gardening.
- **Stdlib only** in `loop/` for now. No broker, no daemon, no network. Every
  invocation ends with a clear stdout result: `done` | `report` | `needs-you`.

## Before you push

```sh
python -m unittest discover -s tests -v
```

The test that matters (doctrine §10) is not "atoms validate" — it's whether
two locally-fine atoms can *refuse to fit* and the seam notices. If everything
passes on the first try, the check isn't doing its job yet.

## Session hygiene

- Each session ends with a numbered report in `.ai-native/reports/`, including
  its end-state and anything surfaced as `needs-you`.
- Commits are small and step-shaped, with messages that say what landed.
- Conflicts between instructions get *named in the report*, not silently
  resolved (see report 0000 for the pattern).

## The tripwire (doctrine §12)

If we catch ourselves editing the doctrine — or polishing repo structure —
instead of building the next §11 step, that's the signal to close the file and
go build.

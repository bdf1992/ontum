---
name: reflect
description: >-
  Reflect the owner's stamp queue onto registered external surfaces:
  an atom arriving at bdo's stamp opens a GitHub issue carrying the
  arc-first briefing; the stamp landing closes it with the verdict and
  receipt id. Use when the summon hook reports surface drift, at the
  end of any session that judged or stamped atoms, or when bdo looks
  at an external surface and sees nothing while the hook says work
  waits (the exact incident behind done-line 0018). The pen is
  reflect.py beside this file; the drift fold is loop/reflect.py;
  surfaces are admitted records and every applied act is receipted on
  the log.
version: 0.1.0
owner: bdo
changelog:
  - version: 0.1.0
    note: >-
      First form (done-line 0018). bdo's directive, on the record
      (chat, 2026-06-10): "these need surfaced within a UI so make
      sure your priritzing the intent" — given minutes after GitHub
      Issues showed him nothing while the queue held work.
---

# Reflect

The owner's queue lives in the log; the owner lives on his surfaces.
This skill closes that gap in one direction only: **log → surface,
never back**. The issue is a mirror — judging it does nothing; the
verdict still lands through `loop.node judge` (D-4, one pen).

## The ritual

1. **Read the drift** (pure fold, writes nothing):

   ```sh
   python -m loop.reflect           # every registered surface + its drift
   ```

   `done` means every surface mirrors the log — stop. `report` names
   the acts (open / close) that would close the gap.

2. **Apply it** (the pen — the only writer):

   ```sh
   python .claude/skills/reflect/reflect.py apply --surface github-issues --by <who>
   ```

   Opens one issue per atom newly at the stamp (briefed arc-first, with
   the verdict set and the clear line); closes the issue with verdict +
   receipt id when the stamp has landed. Each applied act is recorded on
   the log before the next is attempted — a half-applied run resumes, a
   re-run with no drift is a no-op.

3. **Verify**: re-run step 1 and expect `done`.

## Registering a surface

Surfaces are admitted records (I-8), signed, latest-wins — never code:

```sh
python -m loop.reflect register --surface github-issues \
    --address bdf1992/ontum --by bdo
```

Omit `--address` to deregister. Reflecting to an unregistered surface
refuses (§10: it must not fit).

## Boundaries

- The drift fold (`loop/reflect.py`) is stdlib-pure: no network, no
  subprocess. All outward reach lives in this pen, like the PR pen.
- The hook (`loop.summon --hook`) names drift ambiently so a stale
  surface is surfaced, not silently wrong — but the hook never writes;
  applying stays a deliberate act through this pen.
- Next-not-now, each its own stamped increment: more surface kinds,
  ambient auto-apply (today's hooks never write — changing that is a
  contract change), and the served web inbox (auth still named-not-built).

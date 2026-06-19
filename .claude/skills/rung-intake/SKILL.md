---
name: rung-intake
description: >
  Read bdo's trust-rung grants from GitHub and act on them. The trust ladder
  (loop/trust.py) denies every class everything until a rung is admitted, and
  a rung is bdo's to grant the way every decision of his is made: from GitHub,
  wherever he is, by closing the class's rung-confirm issue with a plain-language
  comment. This skill reads that comment, judges his intent (grant / decline /
  unclear), and on a clear grant runs the rung admission on his authorization
  (loop.node admit-rung --by bdo) — always replying with how it read him,
  never granting on a guess. Use when there are closed rung-confirm issues to
  read, when the spawn rail refuses a branded node-spawn for want of a rung,
  or when asked to "read bdo's rung grants" or "process the rung inbox".
version: 0.1.0
---

# rung-intake — bdo's GitHub trust grants, read and acted on

bdo will not run a CLI and will not open a custom UI. His surface is GitHub,
which he can reach from any device. Third sibling of arc-intake (done-line
0038) and realness-intake (done-line 0042): that pair lets him confirm an
*arc* and make a *gate real*; this one lets him grant a *capability rung* —
what a whole class of summoned agent may do from then on (read < judge <
author; ontum-touch is LOCKED and never asked). A rung is a real authority
act — the spawn rail (`spawn_guard.py`) enforces it at every branded
node-spawn — and it stays bdo's (D-4: nothing grants itself a rung). This
skill does not take that decision from him; it carries it from GitHub to the
log.

## The one invariant — read before anything

**Never grant on a guess about what bdo meant.** You are reading natural
language. If his comment clearly grants, run the admission. If it clearly
declines, leave the ladder unchanged. If it is ambiguous, empty, or you are
not sure — you **reopen the issue and ask**, and grant nothing. A misread
rung widens what every agent of a class may do, silently, everywhere the
ladder is checked — the worst outcome here; an extra question is cheap.

And **always echo your reading back** in the reply, so bdo sees exactly how
he was understood and what happened — a wrong read is then visible and his to
correct, never silent.

## Before opening an issue: the rung must have a waiting act

Only open a rung-confirm issue when something concrete is refused for want of
that exact rung — a branded spawn the rail denied, a pen act the ladder
blocks — and name that act in the issue body. Asking for trust with nothing
waiting to use it would be rung-farming; the ladder grows because work needs
it, not because trust is nice to have. The pen itself refuses to open an
issue for the LOCKED rung (ontum-touch) or for any class/capability the
admission pen could not grant — this skill never works around that refusal.

```sh
python .claude/skills/rung-intake/rung.py open \
  --class <agent-class> --capability <rung> --repo <owner/repo>
```

## The ritual

1. **Get the worklist** (deterministic, read-only):
   ```sh
   python .claude/skills/rung-intake/rung.py pending --repo <owner/repo> --json
   ```
   Each item is `{number, agent_class, capability, title, comment}` — an issue
   bdo closed and the comment he closed it with. (Empty list → nothing to do;
   stop.)

2. **Read each comment and judge his intent** — this is yours, not a pen's:
   - **grant** — he clearly wants the rung admitted ("grant it", "yes", "let
     them judge", "go ahead", "trusted", in any phrasing).
   - **decline** — he clearly does not ("no", "hold off", "not yet", "too
     soon", "needs more receipts").
   - **unclear** — anything else: a question, a caveat, mixed signals, empty.

3. **Act on the verdict:**
   - **grant:** run the rung admission on his authorization — his closed
     issue is the stamp, you are its executor (D-4, never `--by` yourself):
     ```sh
     python -m loop.node admit-rung --class <agent-class> --capability <rung> --by bdo
     ```
     Then reply with the admission id and close out:
     ```sh
     python .claude/skills/rung-intake/rung.py reply --issue <n> --repo <owner/repo> \
       --body "Read your intent as: GRANT — <agent-class> now holds the '<rung>' rung (admission adm.<...>). The spawn rail enforces it from the next branded spawn; trust accrues as receipts against it." --done
     ```
   - **decline:** admit nothing. Reply with your reading and mark it done:
     ```sh
     python .claude/skills/rung-intake/rung.py reply --issue <n> --repo <owner/repo> \
       --body "Read your intent as: DECLINE — the ladder is unchanged; <agent-class> still holds no '<rung>' rung and the acts waiting on it stay refused." --done
     ```
   - **unclear:** admit nothing. Reply with what you were unsure about and
     **reopen** so it returns:
     ```sh
     python .claude/skills/rung-intake/rung.py reply --issue <n> --repo <owner/repo> \
       --body "I wasn't sure how to read this — did you mean grant <agent-class> the '<rung>' rung, or hold? Reopening so you can say." --reopen
     ```

4. **Stop when the worklist is empty.** Do not escalate to bdo by any channel
   but his reply comment — the issue is the conversation.

## Where the pieces live

- The gh I/O: `rung.py` beside this file (open / pending / reply) — deterministic.
- The admission: `loop.node admit-rung` (the one write path for the ladder) —
  run only on a clear grant, `--by bdo`. It refuses ontum-touch absolutely.
- The enforcement: `.claude/hooks/spawn_guard.py` (branded spawns) and any pen
  that asks `loop.trust.permits()`.
- The ladder, read-only: `python -m loop.trust ladder`.
- The wake-up: `.claude/hooks/gesture_surface.py` (done-line 0044) surfaces
  his closed rung issues at session start.

## When the ritual is wrong

This is ours to sharpen. If reading bdo fights the work, change this file and
`rung.py` in the same PR, bump the version, and land it the way everything
lands now: bdo confirms its arc from GitHub, the merge-node lands it.

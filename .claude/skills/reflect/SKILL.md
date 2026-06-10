---
name: reflect
description: >-
  The reflection service as application: the owner's stamp queue
  mirrored onto registered external surfaces (GitHub Issues today) —
  an atom arriving at bdo's stamp opens an issue with the arc-first
  briefing; the stamp landing closes it with the verdict and receipt
  id. Reflection rules (kind x surface, admitted records) make it
  automatic: the Stop-hook beat applies enabled rules after every
  turn. Use when the summon hook reports surface drift, when bdo looks
  at an external surface and sees nothing while the hook says work
  waits, to register surfaces or admit rules, or to extend the service
  with a new kind or surface translator. The pen is reflect.py beside
  this file; the drift fold is loop/reflect.py; every applied act is
  receipted on the log.
version: 0.2.0
owner: bdo
changelog:
  - version: 0.2.0
    note: >-
      The pattern commons (done-line 0020). bdo's pub/sub directive
      and stamp ("Lets do it then", chat 2026-06-10): rules as the
      translation matrix, the Stop-hook beat as the subscriber, the
      skill as the application manual. First writing hook — contract
      change stamped on the done-line.
  - version: 0.1.0
    note: >-
      First form (done-line 0018). bdo's directive, on the record
      (chat, 2026-06-10): "these need surfaced within a UI so make
      sure your priritzing the intent" — given minutes after GitHub
      Issues showed him nothing while the queue held work.
---

# Reflect — the pattern commons

The owner's queue lives in the log; the owner lives on his surfaces.
This service closes that gap in one direction only: **log → surface,
never back**. The issue is a mirror — judging it does nothing; the
verdict still lands through `loop.node judge` (D-4, one pen).

The pub/sub reading (bdo's frame, level-triggered form): **the log is
the topic, rules are the subscriptions, reflection records are the
acks, drift is the unconsumed backlog.** No broker, no daemon — a
missed beat costs nothing because the next beat re-derives the whole
diff from the log.

## Using

```sh
python -m loop.reflect                    # surfaces, rules, drift — read-only
python -m loop.reflect register --surface github-issues \
    --address bdf1992/ontum --by bdo      # admit a surface (omit --address: deregister)
python -m loop.reflect rule --kind owner-stamp-queue \
    --surface github-issues --on --by bdo # admit a rule (--off: disable)

python .claude/skills/reflect/reflect.py apply --surface github-issues --by <who>
                                          # the deliberate hand: any registered surface
python .claude/skills/reflect/reflect.py auto --by reflect-auto
                                          # the beat's verb: only what enabled rules name
```

The beat itself is wired in `.claude/settings.json`: a `Stop` hook runs
`auto` after every turn. With a rule on, drift clears itself; with no
rule, nothing leaves the machine and the summon hook surfaces the drift
for a deliberate `apply`. Both paths receipt every act on the log,
signed.

## Extending

- **A new kind** (something else worth reflecting — open summons, epic
  progress, parked atoms) is a new drift fold: add the fold to
  `loop/reflect.py`, list the kind in `RULE_KINDS`, and admit rules for
  it. Its own done-line: a kind defines what the system says out loud.
- **A new surface kind** (PR comments, email, the phone inbox) is a new
  translator in the pen: a branch in `_apply_acts` (or a sibling
  function) that knows the surface's verbs. The fold never changes —
  desired view and drift are surface-shape-agnostic.
- The refusals stay load-bearing (§10): unknown kinds refuse at the
  CLI, unregistered surfaces refuse in the fold, configured-off drift
  never reflects.

## Managing

- **Audit**: every reflected act is a log record with provenance —
  `surface.reflected` events carry surface, atom, act, external ref,
  and signature. The fold *is* the audit; there is no second ledger.
- **Pause**: `rule ... --off --by <who>` — a superseding admission,
  never an erasure. The drift then accumulates visibly (summon hook,
  `loop.reflect` status) instead of applying.
- **Remove a surface**: `register --surface <id> --by <who>` with no
  `--address`. Its reflection history stands.
- A failed act stops the run, keeps what landed receipted, and the
  next beat (or re-run) resumes from the rest — never double-acting.

## Boundaries

- The drift fold (`loop/reflect.py`) is stdlib-pure: no network, no
  subprocess (pinned by test over its imports). All outward reach
  lives in this pen, like the PR pen.
- The Stop-hook beat is the repo's **first writing hook** — stamped by
  bdo on done-line 0020. It writes only through the pen, only what
  enabled rules name, fail-open, exit 0 always, never gating the owner.
- Next-not-now, each its own stamped increment: more kinds, more
  surface translators, the served web inbox (auth still named-not-built).

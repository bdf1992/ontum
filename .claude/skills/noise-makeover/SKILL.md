---
name: noise-makeover
description: The noise make-over — read the open owner-ask mirror issues and gate-run trackers against the log, silence only what the record PROVES resolved, and escalate the rest to a named conclusion (#628). Use when bdo's GitHub inbox is accreting stale owner-ask or gate-tracker issues, when asked to "make over the noise", reconcile the inbox, or clean up stranded trackers. Dry-run by default; it silences nothing until bdo has drawn the noise-silence fence (the standing permission is his). The pure fold is loop/reconcile_noise.py; this pen is the only network-reaching half, and it closes only through the issue pen and reflect.discharge_owner_ask, never raw gh.
---

# noise-makeover — the inbox made over into signal

bdo's GitHub inbox accretes because two surfaces have an automated OPEN path and
a manual / in-process-only CLOSE path (owner-ask mirror issues; gate-run
trackers). This skill is the reconciler: it **makes the noise over into one
synthesized, useful read** and **silences the raw noise the record proves
resolved** — bounded, with teeth.

## The two halves

- **The fold** — `loop/reconcile_noise.py` (pure, read-only, no network). Per open
  noise subject it computes a *resolution reading*: an owner-ask is resolved when
  an arc it asks bdo to confirm now carries an `arc_confirmed` admission; a
  gate-tracker is resolved when its atom's *current bytes* carry a settled
  value-gate / value-confirm verdict. It synthesizes the **useful sound** (one
  digest line) and the **§10 teeth**: a close with no provable resolution is
  REFUSED — it stays open and escalates (#628).
- **The pen** — `makeover.py` beside this file (the only outward reach). It lists
  the open issues, hands them to the fold, and silences what the fence authorizes
  — discharging owner-asks through `reflect.discharge_owner_ask` (re-verifying the
  cite teeth) and closing mirror/tracker issues through the **issue pen**, never
  raw `gh`.

## How to run it

```sh
# the read-only fold (what would be silenced, what still needs you):
python -m loop.reconcile_noise

# the dry-run plan, matched against the live open issues (reaches nothing):
python .claude/skills/noise-makeover/makeover.py

# apply — silences ONLY what the fence authorizes (cooling; default-inert):
python .claude/skills/noise-makeover/makeover.py --apply --by claude
```

## The standing permission is bdo's (do not stamp it for him)

The make-over silences nothing until bdo draws the fence — a bounded standing
authorization, default-INERT:

```sh
python -m loop.reconcile_noise admit-fence --max-closes 10 --by bdo
```

Cooling (silencing proven-resolved noise) is the allowed direction; anything
unproven escalates, never auto-closes. To let the transformer (wave 2) reach a
mind for free-text asks, bdo admits one gateway policy:

```sh
python -m loop.inference policy --caller noise-makeover --surface noise-makeover --mind <mind-id> --by bdo
```

The bundle is `.ai-native/proposals/noise-makeover.proposal.md`.

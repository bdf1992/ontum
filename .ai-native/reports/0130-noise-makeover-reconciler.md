# Report 0130 — the noise make-over reconciler

## What landed

The noise make-over (`atom.noise-makeover.v0`, PR #668), blueprint-first under
`epic.owner-harness`, serving #628. The owner's GitHub inbox accretes because two
surfaces have an automated OPEN path and a manual / in-process-only CLOSE path:
owner-ask mirror issues (open-only) and gate-run trackers (closed only from inside
the producing process).

- **The bundle** — `.ai-native/proposals/noise-makeover.proposal.md`: full shape,
  categorized concept-list (N1…N6), CTAs, the two bdo-stamp gestures named and not
  taken.
- **Wave 1 (fold + useful sound)** — `loop/reconcile_noise.py`: per open noise
  subject, a resolution reading from the log alone (owner-ask → `arc_confirmed`
  cite; gate-tracker → settled value verdict on *current bytes*, idempotent
  regardless of producing process); one synthesized digest line, wired into
  `loop/digest.py`.
- **Wave 2 (transformer)** — `transform_unresolved`: a free-text ask + log span
  through the inference gateway (`loop/inference.py`), gated (default-deny) and
  degrading; the teeth hold over inference output.
- **Actuator pen** — `.claude/skills/noise-makeover/{makeover.py,SKILL.md}`:
  silences only what the fence authorizes, through the issue pen and
  `reflect.discharge_owner_ask`, never raw `gh`; dry-run default.
- **§10 teeth** — `tests/test_reconcile_noise.py` (15 cases): a close with no
  provable cite is refused and escalates; a hallucinated cite is refused like a
  fabricated one. Suite green (1512).

No live issue was closed; auto-silence is inert until bdo stamps the fence.

## needs-you

1. **Draw the standing auto-silence fence** (default-inert; cooling-only; a
   session cannot draw it): `python -m loop.reconcile_noise admit-fence
   --max-closes 10 --by bdo`.
2. **Admit a gateway policy** so the wave-2 transformer can reach a mind (today it
   degrades by escalating free-text asks by name): `python -m loop.inference
   policy --caller noise-makeover --surface noise-makeover --mind <mind-id> --by
   bdo`.
3. **Confirm `epic.owner-harness`** if you want PR #668 landed — the merge-node
   lands it; you confirm.

## End-state

`report` — committed on `claude/noise-makeover-reconciler`; PR #668 opened for
independent review (not merged); suite green (1512); auto-silence inert pending
bdo's fence.

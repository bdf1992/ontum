# Report 0037 — the merge surface: aggregate divergence issues

## What landed

By done-line 0037 — the post-merge issue surface bdo asked for, as a new
reflection kind (not a new system):

- **`merge-divergences`** in [loop/reflect.py](../../loop/reflect.py): a kind
  whose drift folds the digest's *divergences* into **aggregate** issues —
  `_divergence_groups` groups refusals by their confirmed arc (one issue per
  arc, listing every refused piece) and cap-breaches into one, each carrying
  its data points and judgement pattern. `divergence_drift` returns acts in
  `drift()`'s shape keyed by group id, so the existing gh translator and
  reflection records open/close it unchanged. `DRIFT_BY_KIND` dispatches the
  beat (`auto_plan`) and `status` by kind. **Explicitly not** the
  one-issue-per-atom echo of the owner-stamp mirror.
- Idempotent: one open per group, one close when the group reconciles (its
  divergences clear); re-running with no change writes nothing.
- [tests/test_divergence_surface.py](../../tests/test_divergence_surface.py):
  11 tests; §10 centre — two refusals under one confirmed arc fold to **one**
  aggregate issue, not two. Full suite green (400).

## needs-you

- **The switch is a rule, not a merge.** It stays silent until a rule is
  admitted: `python -m loop.reflect rule --kind merge-divergences --surface
  github-issues --on --by bdo`. Until then it never opens an issue (§10:
  configured-off drift never leaves the machine). Not built into the beat
  on its own — your stamp turns it on.
- **Daily arc-digest delivery** — the other half of "I only want daily ARC
  digests" — is a scheduling piece (a recurring run of `loop.digest`),
  separate from this; named, not yet built, since a scheduled cloud routine
  is yours to authorize.

## End-state

`report` — the aggregate divergence surface is built and green; it speaks the
moment a rule enables it, and stays a mirror (verdicts still land through the
one pen, D-4).

# Done-line 0037 — the merge surface: aggregate divergence issues, not a per-PR echo

Written before code, per §9.4. When this line is met, stop.

> **Done when:** a new reflection kind `merge-divergences` folds the digest's
> divergences (done-line 0032) into **aggregate** issues — one per *group*
> (refusals grouped by their confirmed arc; cap-breaches grouped as one),
> each carrying its data points and the judgement pattern — **not** one issue
> per PR or atom (the reflect mirror's shape, which bdo rejects for the
> post-merge surface). It rides the existing reflect rails: the kind is an
> entry in `RULE_KINDS` with a drift fold keyed by *group identity*; the
> existing gh translator opens/closes it unchanged; open is idempotent (once
> per group) and close fires when the group reconciles (zero divergences),
> through the same reflection records. Enabling it is a rule admission
> (`merge-divergences × github-issues --on`) — bdo's or a stamped one; with no
> rule it is silent (§10: configured-off drift never leaves the machine).
> §10 teeth: a confirmed arc with a refused piece opens exactly one aggregate
> issue; when that refusal reconciles, exactly one close; re-running with no
> change writes nothing. Recorded in loop/CLAUDE.md.

## Why (bdo, 2026-06-11)

"The issues the loop opens after a merge must be **aggregate — bulk
data-point surfacing + judgement patterns, NOT a one-issue-per-PR echo.**"
Today's reflect mirror is the echo (one issue per atom at his stamp); this is
the post-merge surface he wants instead — keyed to *divergences* (where a
confirmed arc and a gate refusal refuse to fit), low-volume and high-signal.

## Out of scope, named

- **Span-bounding.** v1 folds all-time; daily/since-last-merge windowing
  rides `loop.digest`'s `--since/--until` later.
- **Live body updates as data accrues.** The issue opens once per pattern and
  points to `loop.digest` for live detail; it does not rewrite its body as
  more data points land — it closes when the pattern reconciles.
- **Scheduled daily digest delivery.** The other half of bdo's ask
  (a daily arc digest to him) is a scheduling piece, named separately.

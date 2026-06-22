# Done-line 0184 — The owner-ask mirror is idempotent against the shared surface — one open issue per ask group, no duplicates

Written before code, per §9.4. When this line is met, stop.

The reflector's owner-ask mirror double-fires (#547): within hours #525–#544
duplicate #511–#530, each report's ask group surfacing 2–3× and burying bdo's
real asks. The fold-level idempotence (`(g["id"],"open") not in seen`) is real
but insufficient under the parallel-worktree fleet: the reflection 'open' ack
lives on the LOCAL log, a sibling session forks from main before it exists,
each opens an issue and appends a `surface.reflected` event with the same
content-derived id but a different external_ref; the union-merged log keeps one
ack while GitHub keeps both issues. The fix dedupes each open against the
SHARED surface truth (open issues carrying a stable mirror-key) in the pen,
where outward reach already lives — keyed by the group's stable id (report_id
for owner-ask), level-triggered, no second engine.

> **Done when:** the owner-ask mirror mints at most ONE open issue per ask
> group — a second reflect/auto pass over a group already mirrored to an open
> issue on the surface plans/performs ZERO new opens (it records the ack
> against the existing issue and skips the create); a §10 test proves the
> idempotence is non-vacuous (with the surface-dedup removed, the same setup
> mints a duplicate and the test FAILS); and the existing duplicate pile is
> reconciled to one-open-issue-per-group (or confirmed already reconciled).

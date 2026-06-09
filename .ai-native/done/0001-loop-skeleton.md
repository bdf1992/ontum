# Done-line 0001 — phase-1 loop skeleton

Written before code, per §9.4. When this line is met, stop.

> **Done when:** one fake atom (`atom.loop-skeleton.v0`) reaches its
> `desired_state` (`value_confirmed`) through reconcile passes over
> `.ai-native/log/`; killing the process midway (SIGKILL) loses nothing —
> the next pass resumes from the files with no lost and no doubled receipts;
> and deleting `queues/` + `offsets/` then replaying from `log/` rebuilds
> them byte-identical.

Source: doctrine §11 works-when + the briefing's firm constraints (log is
truth / cache is a fold; level-triggered; idempotent by content hash;
line-atomic appends with torn-tail tolerance).

Next, not now: make exactly one node real, starting with L0 — needs bdo's
input and a fresh stamp.

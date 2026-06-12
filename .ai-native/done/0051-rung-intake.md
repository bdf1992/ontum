# Done-line 0051 — Rung intake: bdo grants trust rungs by gesture

﻿Written before code, per §9.4. When this line is met, stop.

> **Done when:** bdo can grant a trust-ladder rung the way he confirms an arc
> or a realness: from GitHub, by closing one issue with a comment in his own
> words. A deterministic pen (rung.py, sibling of realness.py) opens the
> rung-confirm issue — marked `ontum:rung-confirm class=... capability=...`,
> labelled — and refuses to open one for the LOCKED rung (ontum-touch is never
> a question bdo gets asked; unlocking it is a pen change, never a gesture);
> `pending` lists the rung issues he closed and no session answered; the
> SessionStart gesture heartbeat (done-line 0044) gains the rung subscriber so
> his act wakes the next session; and the rung-intake SKILL reads his words —
> a clear confirm runs `loop.node admit-rung --class <c> --capability <p>
> --by bdo` (his closed issue is the authorization the session executes, D-4),
> a decline leaves the ladder unchanged, unclear reopens and asks. Proven by
> tests: the marker round-trips and a half-marker refuses to parse; the locked
> rung is refused at open; the heartbeat formats a rung line and stays silent
> on an empty inbox; and the join to the rail is pinned — an admission written
> through `loop.node.admit_rung` is exactly what flips
> `spawn_guard.node_spawn_refusal` from refusal to pass on a prompt-pinned
> node (the gesture this surface carries is the one the rail obeys).

## Out of scope, named

- **Granting any rung.** The admission stays bdo's (`--by bdo` on his clear
  confirm read by the SKILL); nothing here grants, only carries.
- **The live branded spawn of value-gate.claude.v1** (wave 2's proof case) —
  it needs the real admission this surface exists to carry; it runs the
  session after bdo's tap, not this one.
- **New rungs, classes, or any unlock of ontum-touch.** The ladder's
  vocabulary stays loop/trust.py's; this is I/O for what exists.

# Done-line 0166 — The digest goes through the one gateway, consumed by listeners

Written before code, per §9.4. When this line is met, stop.

bdo, 2026-06-21: *"it should use the gateway, only go through one, an be
consumed/digested by those listening."* The daily arc digest reached his
GitHub surface through **two** cloud routines that each ran `loop.digest`
and wrote via **raw `gh issue`** — two outward couriers bypassing the one
governed reflector pen. The digest belongs in the gateway it already half
uses (its *divergences* flow through `loop.reflect` as `merge-divergences`);
the whole digest should be one published topic that listeners consume.

> **Done when:** the full arc digest reaches a registered surface as ONE
> live, self-updating issue **only** through the reflector pen (a new
> `daily-digest` reflect topic + an `edit` act on the pen), an unchanged
> digest produces no act (the level-triggered beat never spams), and a test
> proves the open-once / edit-on-change / never-twice shape — so the two
> raw-`gh` cloud couriers are redundant and retire.

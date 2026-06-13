# Report 0056 — The spawn rail denies an unbranded node-fill

## What landed

A prevention, born from a mistake I made this session. After building the
inference plane I spawned an independent agent to land my own PR #115 as the
merge-node — but I used a **plain, unbranded** `Agent`. The land was authorized
(bdo's confirmed arc; the `land` pen's guards; `by: merge-node.claude.v1` on the
receipt), but the *spawn* skipped the branded rail: no prompt pinned, no rung
checked at spawn time. The rail only **shamed** it after the fact. bdo: "If the
branded path is possible, lets create hook which prevents your accident?"

It is possible and was wide open (`branded-subagent` holds the `judge` rung,
`merge-node.claude.v1.md` exists to pin) — so there was no reason to go
unbranded. This closes the door:

- `.claude/hooks/spawn_guard.py` — the PreToolUse rail now reads an *unbranded*
  spawn for what it **does**. A node-only act — `pr.py land`, `loop.node judge`,
  `gate.py launch`, or a claimed node identity (`--by …claude.v1` / `--node
  …claude.v1`) — means a node-fill that forgot its brand, and it is **denied at
  the door** (exit 2) with the brand it needs. A plain helper or research spawn,
  which never claims a node identity, passes untouched (watched, as before). The
  discriminator is surgical because a node-fill *must* claim an identity to reach
  those pens and a helper never does.
- `tests/test_spawn_rail.py` — 20/20 green (7 new): the exact accident refused
  (unbranded `pr.py land --by merge-node.claude.v1`), an unbranded gate-judge
  refused, a plain helper passes, `--by bdo` does **not** trip it (owner stamping
  a pen ≠ a node-fill), a branded node-act stands down to the rung/prompt check,
  and the live hook denies end-to-end with exit 2.

This tightens `atom.branded-spawn-rail.v0` (done-line 0026): shame became
prevention. The bar was stated before the work (a direct, scoped bdo request,
not a new arc, so no separate frozen done-line).

## needs-you

Nothing new. (The inference plane's bootstrap gesture #116 still waits on your
one stamp — separate from this.)

## End-state

`report` — the spawn rail now refuses an unbranded node-fill at the door, so the
accident that filled the merge-node seat anonymously cannot recur; plain helpers
are untouched; landed as its own PR for the merge-node (branded, this time).

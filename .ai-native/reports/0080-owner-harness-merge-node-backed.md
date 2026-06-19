# Report 0080 — Owner-harness carried: the merge-node gets its own line; the 88-refusals lie

## What landed

**The lesson from the refusals (bdo's prompt).** The digest's "88 refusals in
span" is almost entirely an artifact: folding `receipts.jsonl` directly, **79
of the 88 are `landed` events** — merge-node successes miscounted because
[digest.py:109](../../loop/digest.py#L109) flags any receipt with no
`next_suggested_event` as a refusal. The genuine refusals are **~7**, and they
teach three things:

- **Counterfeit-done (the recurring one):** `value-confirm` returned `missed`
  on `atom.gates-enumerated.v1` and `atom.field-topology.v0` — both claimed
  delivered artifacts (`loop/field.py`, "mock temp 0/5") that were false on
  trunk. The gate measured reality and caught both.
- **Agent-serving busywork refused:** `value-gate` rejected `atom.rename-vars.v0`
  ("I personally find it cleaner") — no owner value on record.
- **bdo's own voice points at one arc:** both bdo `amend` refusals
  (`owner-inbox.v0`, `github-verdict-mirror.v0`) ask for the same thing — a
  surface he operates remotely, with richer intent, where external surfaces
  become local. That is **epic.owner-harness**. (The fix for the counter
  itself is already written and mergeable in PR #180, retro-fold.)

**The carry (bdo picked owner-harness).** The arc read 3/5 with two pieces
"unbuilt" — but both were real-in-fact: `github-verdict-mirror.v0` was
amended-forward by bdo into the landed `surface-registry.v0` (settled history),
and `atom.merge-node.v0` named an organ that was **built, admitted real
(`adm.852e04202b05`, bdo 2026-06-12), and has landed 79 PRs** — yet never put
on the log. The lander never landed itself: the one organ whose law is *no one
signs their own line* was the one writer with no atom of its own (the
self-asserted identity mock-shame caught in the 22 unadmitted landings).

I authored `atom.merge-node.v0` as a retrospective backing and carried it the
full pipeline, D-2 clean:

- value-gate `value-gate.claude.v1` → **accept** `rcp.9bbebc5479a7` (independent branded judge)
- owner-stamp → satisfied by the confirmed arc `adm.728a87a9ca48`
- placement `placement-gate.det.v1` → **sound** `rcp.ca5cbd11126f`
- handoff `handoff-gate.det.v1` → **ready_for_spec** `rcp.fca33938226f`
- value-confirm `value-confirm.claude.v1` → **confirmed** `rcp.41e01e992ca0` (a second, distinct independent judge)

Both real gates were judged by independent branded subagents that did not
author the atom. **PR #192** is the unit the merge-node lands; owner-harness
now reads **4/5** (the 5th piece superseded-forward into surface-registry — the
arc is effectively complete).

## needs-you

- **Stale epic glue (your call, not silently edited).** The merge-node piece's
  glue in `epic.owner-harness.json` still says *"Until bdo admits the node real
  (--by bdo)… it merges nothing and he still merges."* Your 2026-06-11/06-12
  stamps already overtook that. Re-steer the glue or leave it — yours.
- **The digest miscounts landings as refusals.** PR #180 (retro-fold) fixes it
  and is mergeable; until it lands, every "N refusals" headline overcounts by
  the landing count. Not an owner gesture — just the reason the board reads
  scary.

## End-state

`report` — owner-harness carried to effectively-complete: `atom.merge-node.v0`
`value_confirmed` and opened as PR #192 for the merge-node to land; the "88
refusals" explained (79 are landings); two needs-you surfaced (stale glue, the
digest counter fixed by PR #180).

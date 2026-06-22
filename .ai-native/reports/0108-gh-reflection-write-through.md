# Report 0087 — GitHub as a deterministic reflection of local — D-13 and the merge-receipt join (Phase A)

## What landed

Continuation of report 0107 (the terminal-pull gateway). The gateway's
namespace-gap finding opened a design conversation with bdo, which
produced his directive and **Phase A** of the fix.

**bdo's directive (2026-06-18):** *"GitHub should only be a deterministic
reflection of what we have locally, and the pens should confirm this by
being a write-through carbon copy."* He thought it was already required.
It was, in spirit (the records pen's carbon-copy, done-line 0070; D-5) —
but never extended to the GitHub-boundary pens.

**Done-line 0124 — Phase A (PR #230, branch `claude/gh-reflection-write-through`),
built in an isolated worktree off origin/main, homed under the confirmed
`epic.owner-harness` so the merge-node can land it.**

- **Doctrine D-13** — external surfaces are deterministic reflections of
  the log; the pen that writes to one is a write-through carbon copy
  carrying enough to re-derive the local truth it reflects; a write that
  drops the local identity is a lossy reflection and a pen bug.
- **`_merge_receipt` / `cmd_land`** (`pr.py`) carry **`landed_atoms`** —
  the artifact_ids the PR's range adds, computed by **reusing
  `_range_atom_facts`** (the off-log gate's own reach — no second
  derivation), before the merge while the head branch still exists. The
  land raises rather than record a merge it cannot describe.
- **`loop/digest.py atoms_on_main`** — the pure join fold reading
  `landed_atoms`, so *"did atom X reach main?"* is answerable from the log
  alone; surfaced as a confirmed-on-main count. The 90 pre-D-13 receipts
  stand as lossy history (the gap closes forward, never by back-edit).
- §10 teeth (tests): a `landed` receipt with `landed_atoms` joins; the
  old shape without them does not, though both say `landed`. Suite green
  (935). Dogfood: atom + independent value-gate (D-2) accept
  `rcp.2b3c25086d66`.

## needs-you

- **The merge-node can land PR #230 now** — `epic.owner-harness` is
  confirmed and the suite is green; no gesture from you is required (an
  independent merge-node lands it; I authored it, so I do not).
- **Phase B is the next arc, not done:** updating the pipeline seams with
  the gateway implementations of the proposal's §13.10 (gate→gateway→
  patrol→actuator). It depends on this join (the patrol's
  *passed-but-unpulled* signal is now computable). Your call when to open
  it.

## needs-you — a frozen-bar note (surfaced, not edited)

Done-line 0124's prose names the new clause **"D-12"**, but D-12 was
already taken ("every site is a transducer"). The doctrine and all code
correctly use **D-13**; the bar's intent (add the write-through-reflection
axiom) is met. Per the freeze rule I did not edit the frozen line — the
stale number is recorded here. The independent value-gate flagged it too.

## End-state

`report` — Phase A of bdo's GitHub-as-deterministic-reflection directive
landed as PR #230 (D-13 + the merge receipt's `landed_atoms` join);
Phase B (seams → gateways) named and deferred; one frozen-bar label
discrepancy surfaced.

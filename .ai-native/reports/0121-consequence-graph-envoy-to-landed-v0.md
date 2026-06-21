# Report 0121 — Consequence graph: envoy round-trip to a landed, independently-gated v0 keystone

## What landed

The full chain from a design proposal to a keystone on main, in one session:

- **Envoy out, review home.** Sealed the `consequence-graph` envoy package (9
  files) for a foreign peer-architect; the review returned GO for one small
  read-only piece and a NO-GO list (no tier-2 inference, no value/money, no
  volume, no actuation). Landed the 8 corrections as proposed atoms under
  **epic.consequence-graph-response** (PR #388); bdo confirmed the arc via
  `pr.py confirm --from-ref` (adm.6a176eb59681).
- **The v0 keystone (done-line 0167) — LANDED, rcp.merge.400.**
  `loop/consequence_graph.py`: a read-only stdlib fold that materializes the
  tier-1 consequence-graph **plane** from the log — one node shape + a `kind`,
  tier-1 edges that are literal log facts (no inferred causal edges), `failure`/
  `repair` marks and cited `consequence` nodes, one bounded typed decaying
  propagation pass (radius 2, per-edge-kind decay; authorship/arc edges render
  but never propagate; channels never net). A mark whose citation does not
  resolve is **refused** (the term-economy ghost tooth, on marks). On the live
  log: 579 nodes, 805 edges, 12 cited marks, 0 ghosts.
- **`tests/test_consequence_graph.py`** — 11 tests, proven **non-vacuous**
  (authorship propagation flipped on makes the actor receive drag 1.8 and the
  no-superspreader test fails; the ghost is refused while the resolved citation
  lands). Full suite green.
- **Independent value-gate did its job.** `value-gate.claude.v1` refused
  **twice** (amend) with fair, specific reasons — the atom's story over-claimed
  owner-blessing the log did not carry, the exact vacuous move the fold's own
  tooth forbids — and **accepted** on the third (rcp.6ac22e915d77) once the
  prose matched the record. The §10 principle in action: the check that refuses
  is the check that works.
- **Landed by an independent merge-node** (non-author attestation), through the
  pen, no direct push; GitHub's spurious CONFLICTING was confirmed clean via
  `git merge-tree`.

## needs-you

- **#388 disposition (arc/epic call, yours).** The 8 review-finding atoms are
  realized by the landed v0 (#400). #388 is still open and confirmed, but its
  epic file is not yet on main (only the confirmation admission is — a dangling
  confirmation). Land #388 to put the epic + findings on the record, or close it
  as realized — that is an arc-scale call (D-4).
- **The next pieces, when you want them** (all deferred by the reviewer's NO-GO
  and named in done-line 0167): tier-2 inferred edges (gated), `value`/money
  marks split into loved/adopted/reused/pattern-setting, the consequence volume,
  and — much later, behind the disposer fence — actuation.

## End-state

\`report\` — the consequence-graph v0 keystone is on main, independently gated;
#388 awaits your disposition; the viewport is behind origin/main and a few
session worktrees are stranded-merged debris for the gardener (nothing lost).

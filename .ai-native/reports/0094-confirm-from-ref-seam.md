# Report 0094 — confirm --from-ref: path A of the three-marks handoff

## What landed

The confirm-seam fix from PR #244 / issue #245's handoff, path A (done-line 0130, PR #246):

- `pr.py confirm --from-ref <branch>` — when an arc's epic record lives only on
  an unlanded PR (not yet on the trunk), the epic is read from that ref for
  validation while the confirmation admission still lands on the trunk. Resolves
  issue #245's triggering deadlock (to confirm you needed the epic on main; to
  land the PR you needed the arc confirmed).
- Teeth (`epic_id_in_blob`, §10 in `tests/test_merge_land.py`): a ref that does
  not declare the epic is refused — `--from-ref` relocates where the epic is
  read, it is never a bypass. Full suite green (994).
- `atom.confirm-from-ref.v0` authored and **announced/parked at the value gate**;
  the PR was opened via the GitHub MCP (no `gh` here), like #244.

## needs-you

Three items, all bdo's alone (a session cannot do them), surfaced on PR #246:

1. **Confirm `epic.owner-harness`** (`--by bdo`) so the merge-node can land #246
   (the confirm-seam fix itself).
2. **Confirm `epic.three-marks`** for real, now possible with the new seam:
   `pr.py confirm --epic epic.three-marks --by bdo --from-ref claude/pen-architecture-analogy-72boq5`
   — then the merge-node lands #244. (Note: #244 also needs atom-backing; its CI
   is red. Its wave-1 code added no atom file. That is a separate piece on a
   branch this session does not own — surfaced, not fixed.)
3. **The #245 parity decision** (gh-in-env vs MCP-backed pens) stays bdo's.

## Conflict / finding surfaced

Issue #245 demonstrated a **third** time this session: the real gate
(`.claude/skills/gate/gate.py`) shells out to `gh` for its trust-rail issue and
dies with `FileNotFoundError` in the web/mobile environment. So **atom-backing a
PR cannot complete here** — the value-gate receipt that would back
`atom.confirm-from-ref.v0` never lands, and the atom-invariant CI check stays red
until a local session (or fixed parity) runs the gate. The same gap blocks #244.
This is not coded around: the atom is honestly parked awaiting the value gate.

## End-state

`report` — path A built, tested (994 green), committed, pushed, and PR #246
opened under epic.owner-harness; landing waits on bdo's two arc confirmations
and the #245-blocked value-gate receipt (atom parked, not skipped).

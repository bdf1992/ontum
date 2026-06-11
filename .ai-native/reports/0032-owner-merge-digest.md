# Report 0032 — the merge digest — eyes before the hand-off

## What landed

By done-line 0032 (the merge digest):

- **[loop/digest.py](../../loop/digest.py)** — the owner's merge digest:
  a pure, read-only fold over a span of the log, grouped arc-first
  (done-line 0006). It surfaces what landed, refused, awaits; the dial in
  play; the field's heat/cool behaviour; and — the teeth — *divergences*
  where two locally-fine records refuse to fit. It writes nothing (a read
  surface, like summon/census); `--json` emits the raw dataset, `--today`
  / `--since` / `--until` bound the span. Verdicts are read generically
  (`next_suggested_event` is the advance/refuse signal), so the digest
  already speaks the merge-node's `{land, refuse, send_back}` the day
  those receipts appear — "landed" becomes merged-to-main for free.
- **[tests/test_digest.py](../../tests/test_digest.py)** — 14 tests; the
  §10 case is the centre: a *confirmed* arc harbouring a *refused* piece
  is a contradiction the digest surfaces as a named divergence, not
  smooths over. Full suite green (295).
- **[loop/CLAUDE.md](../../loop/CLAUDE.md)** — the digest recorded as the
  read surface it is (commands, module layering, the `-m` gotcha).
- **[epic.owner-harness](../epics/epic.owner-harness.json)** — gains the
  `atom.merge-node.v0` piece: the hand that lets bdo step out of the merge
  seat. The digest is named there as its eyes, already built.

This is the move done-line 0028 explicitly named and deferred — draining
the *PR* queue (bdo's manual merge), not just the atom queue.

## needs-you

bdo asked to stop being in charge of merging. That is the **merge-node**,
the next piece — and it turns on two stamps that are his alone (D-4),
neither this session's to make:

1. **Amend the `bdo merges` hard rule** (CLAUDE.md + the doctrine). The
   owner is the last stop *at arc scale* (done-line 0028); the merge-node
   moves the mechanical land off his hand while he keeps the arc stamp.
   This is a doctrine change — surfaced, not worked around.
2. **`admit-real` the merge-node `--by bdo`** once it is built. Until both,
   nothing changes operationally: he still merges; the digest only watches.
3. *(optional)* **Confirm the owner-harness arc** (`loop.node confirm-arc
   --epic epic.owner-harness --by bdo`) if he wants the loop to carry its
   remaining pieces under one stamp.

Also surfaced (judgment call, not acted on): the command_guard watcher
reports raw `git` at 82 uses with no branded wrapper — the recurring tool
the least-permissions direction would mint next. Left to bdo.

## End-state

`report` — the digest ships read-only and green; the merge-node (bdo
stepping out of the merge seat) is the next piece, built only up to where
his two stamps activate it.

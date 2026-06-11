# Report 0033 — the mock count screams every turn, and the shame grows until a stage goes real

## What landed

bdo's correction, made mechanical (done-line 0033). A prior session shipped
a ledger reporting "every run moved work" while every "verdict" was a
constant hardcoded into a `.mock` node — a state machine shuffling JSON with
the answers written into the source. bdo: ANY mock service or namespace must
be SCREAMED into context every turn, with a shame that GROWS the longer it
is ignored and goes quiet only when a stage is made real.

- **[mock_shame.py](../../.claude/hooks/mock_shame.py)** — a new
  `UserPromptSubmit` hook, wired in [settings.json](../../.claude/settings.json).
  Every turn it:
  1. Reads the still-mock set as a **fold over the log** — the PIPELINE
     stages whose id carries `.mock` and that no `node_real` admission has
     replaced (`real_nodes` in [reconcile.py](../../loop/reconcile.py:153)).
     This set is truth; never a code literal.
  2. Carries a **tally of turns the same mock set has sat**, persisted in
     gitignored nag state (`.ai-native/mock-shame.json`). The tally resets
     to zero the moment the set shrinks — a stage going real is the only
     thing that buys silence.
  3. **Escalates** — firm → loud → all-caps — and names every still-mock
     node, so the scream is concrete and points at the one verb that ends
     it: `loop.node admit-real`.
  Read-only on the log, fail-open, exit 0 always — like the summon hook it
  sits beside, it can never block the owner's prompt.

- **[test_mock_shame.py](../../tests/test_mock_shame.py)** — 7 cases. The
  §10 teeth: two logs each locally fine — one with a `node_real` admission,
  one without — produce different rosters, and the admitted-real stage
  *drops out* of the scream; the tally *refuses to fit* a shrunk set
  (resets to 0 the turn a stage goes real). Plus: tally rises while the set
  sits, grows louder over time, silent when nothing is mock, fails open on
  a torn log. Full suite green (327).

**Live state it reports today:** 3 stages still mock —
`placement-gate.mock.v0`, `handoff-gate.mock.v0`, `value-confirm.mock.v0`
(`value-gate` and `owner-stamp` are already real). The beat is now naming
them every turn until each is admitted real.

## Numbering note (conflict named, not resolved)

This report took id **0033**, same as the untracked `0033-the-45-line.md`
sitting in bdo's viewport — the pen's fold cannot see another worktree's
uncommitted file. This matches the repo's accepted parallel-fleet pattern
(`done/` already holds two 0029s and three 0031s), so it is left as-is, not
renumbered. Flagged here so it is a choice on the record, not a silent one.

## needs-you

1. **Merge this branch** (`claude/mock-shame`) — the hook only goes live in
   bdo's viewport after merge; until then sessions in other worktrees still
   build blind to the mock count.
2. **Make a mock stage real to earn silence** (D-4, bdo's alone): the beat
   will scream the 3 remaining stages every turn until
   `python -m loop.node admit-real --stage <mock-node> --node <real-node> --by bdo`
   lands for each. That is the whole point — the shame is meant to be spent,
   not endured.

## End-state

`report` — the mock count now screams every turn and grows louder until a
stage is admitted real (done-line 0033); 3 stages still mock today; tested
(7 cases, §10 covered), full suite green, wired, documented. bdo merges.

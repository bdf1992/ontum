# Report 0037 — close the free stop-working card: supersede is bdo's alone

## What landed

A follow-up tightening on top of merged done-line 0033 (PR #44). bdo's correction: the supersede ritual as first shipped let a session author a new, weaker done-line — returned `needs-you` and marked it "pending bdo's stamp," but it still WROTE the new bar and the admission. That is a free "stop working" card: a session could redefine done, cease work, and hand off. bdo: "I don't want that."

The fix makes `loop.pen supersede-done` bdo's alone, mirroring `confirm-arc`'s `--by must be bdo` gate:

- A non-bdo signer is refused at the top of the verb, BEFORE anything is written — no new line, no `done_superseded` admission, no pending state. The refusal tells the session its only move: name the bad bar in the report's needs-you and KEEP WORKING; bdo supersedes it himself if he agrees.
- Only bdo's own signature reaches the write; the admission is therefore always `authorized: true, authorized_by: bdo` (the `authorized=false` branch is gone entirely).
- The freeze guard itself is unchanged — it already denied all in-place edits. This closes the *additive* escape hatch the supersede verb had opened.
- `.pen.json`'s change_request story, the three composition surfaces (.ai-native/, .claude/, loop/ CLAUDE.md), and the pen docstring/help all restated: a session does not get to change what done meant at all.
- Receipt: `tests/test_freeze_guard.py` — `test_a_session_cannot_supersede_at_all` loops four session signers (claude, codex, overnight-codex, empty) and asserts code 2 with nothing written; `test_only_bdo_supersede_writes_and_it_is_his_own` asserts bdo's writes the additive line and records the authorized admission. Full suite green.

## needs-you

- **Codex parity still not built** (carried from report 0033). This is a Claude-harness hook; Codex writes via `apply_patch`, which does not pass these hooks. A Codex done-line edit — the exact incident that started this — is still unguarded until the `apply_patch` write-guard lands in `fence/`, designed from `probe_codex.py` readings. This is the highest-value next step: the freeze means little against the engineer it was provoked by until the fence enforces it too.
- **`done_superseded` recorded but not folded** (carried from 0033): no digest/summon surface reads it yet. Lower priority now that the verb is bdo-only — a supersede on the record is always bdo's deliberate act, not a session escape to watch for.

## End-state

`report` — supersede-done is bdo-only; a session has no path, additive or in-place, pending or otherwise, to change what done meant; tests green. Codex-side fence parity remains the open gap.

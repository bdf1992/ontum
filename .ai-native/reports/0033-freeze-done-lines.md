# Report 0033 — the frozen done-line and the painful supersede

## What landed

Done-line 0033. A written done-line is now frozen, and the only way to change what "done" meant is additive and deliberately painful — the response to Codex editing its own overnight done-line to add an exhaustion clause (moving the bar instead of meeting it).

- **The freeze guard** (`.claude/hooks/freeze_guard.py`, wired `PreToolUse` on Write|Edit|MultiEdit|NotebookEdit): an *existing* file in a records directory whose `.pen.json` declares `"frozen": true` cannot be edited or overwritten in place — absolutely, no owner exception. Creation is untouched (write_guard's land). Fails open loudly; denials hit the watch log. Live-verified: editing 0033 itself is denied with the supersede story on stderr.
- **The done directory's access pattern**, configured where the place declares its form: `.ai-native/done/.pen.json` gains `"frozen": true` and a `change_request` story — the loud, painful path a cold reader sees in the refusal.
- **The supersede ritual** (`loop.pen supersede-done`): the one way to move the bar. It refuses a bar never set and a glib reason (< 40 chars of honest reflection), writes a NEW line carrying the abandonment reflection as permanent history (the original's bytes are never touched), records a loud `done_superseded` admission, and never self-authorizes a session's own change — a session's supersede returns `needs-you` and sits pending bdo's stamp (no one signs their own line); bdo's own authorizes itself (he steers the bar, D-4).
- Receipt: `tests/test_freeze_guard.py` (8 tests) pins the edit/overwrite refusal, the still-passing creation, the unfrozen directory's freedom, the dotfile carve-out, fail-open, and the ritual's painfulness. Full suite: 328 pass.

## needs-you

- **Codex parity is NOT yet built.** This guard is a Claude-harness hook; Codex writes through `apply_patch`, which does not pass these hooks. The freeze is enforced for Claude sessions today; for Codex it must land in the fence layer (`fence/`) as the `apply_patch` write-guard that `fence/CLAUDE.md` says is to be designed from `probe_codex.py` readings, never against the undocumented contract. Until then, a Codex done-line edit is unguarded. Surfaced, not coded around.
- **The supersession is recorded, not yet folded.** The `done_superseded` admission lands loudly on the log, but no surface (digest/summon) yet reads it as a pending divergence or computes an "effective done" text. The act is on the record and bdo-gated; wiring it into the digest's divergences (a confirmed arc harbouring an abandoned bar) and the owner inbox is the natural next done-line.
- **Frozen is done-only for now.** `reports/` is also written-once history but is left editable deliberately (a report is a narrative a session may still be drafting). Whether to freeze it too is bdo's call.

## End-state

`report` — done-line 0033 met: a written done-line cannot be edited in place by a Claude session, and changing what done meant is a loud, owner-gated, reflection-bearing supersede; 328 tests green; Codex-side parity and digest-folding surfaced as needs-you.

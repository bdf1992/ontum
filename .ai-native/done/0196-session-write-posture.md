# Done-line 0196 — The session write-posture witness

Written before code, per §9.4. When this line is met, stop.

> **Done when:** `loop/session.py` exists: the `write-on` pen appends one
> `session_write_on` to events.jsonl (session_id from CLAUDE_CODE_SESSION_ID,
> required non-empty narration, emergency flag, write-once idempotent), and the
> read-only fold reports per-session write_posture (reader|writer) by crossing
> the local session registry against those records. Witness-only — stops
> nothing. Adversarial tests in tests/test_session.py prove: a session with no
> write-on reads `reader`; one with a write-on reads `writer`; a second write-on
> is a no-op; an unset session id / empty narration is refused; the fold is
> read-only. Full suite green.

## Why

bdo, 2026-06-23: *"We should start every single session in READ only mode, and
turning write on is a named event that happens alongside the first actual
write."* A session's most basic posture — was it a reader or a writer, and when
did it cross? — leaves no trace today. This is the **witness** increment of
`session-read-write-mode.proposal.md`: the one new log shape, the one pen, and
the read-only fold. Witness before actuator — it stops nothing and breaks
nothing.

## In scope (increment 1 — the witness)

- `loop/session.py` — the `write-on` pen (one write path via
  `reconcile.append_line`, write-once idempotent per session) + the read-only
  per-session `write_posture` fold (reusing `watcher.load_registry`, no second
  registry reader).
- The record kind `session_write_on` in `events.jsonl`.
- `tests/test_session.py` — the adversarial §10 teeth.
- A `loop/CLAUDE.md` module-layering line.

## Not in scope (increment 2 — named, not invented away)

- **The fence** — the L1 `append_line` chokepoint + the L2 consequence-fence
  under policy, with the full bypass red-team suite. This increment installs no
  gate, no guard, no fence.
- **The proxy-write hole** (a parent that only spawns writers) — increment 2.
- **The summon/hook briefing** that tells a session its posture ambiently.

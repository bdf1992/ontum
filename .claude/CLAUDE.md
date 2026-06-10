# .claude/ — the harness config (config-as-code)

Everything in this directory changes what sessions will admit, reject,
route, or ignore — that is code (§7): versioned, tested where it can
be, landed as stamped increments, never hand-tuned silently.

- `settings.json` — the hook wiring. Current hooks:
  - `PreToolUse` Bash|PowerShell → `hooks/command_guard.py`: denies raw
    `gh pr` mutations and pushes to trunk (the PR pen is the paved
    path); watches every other external tool into
    `.ai-native/log/tool-use.jsonl` (`--report` says which wrapper is
    worth building next).
  - `PreToolUse` Write → `hooks/write_guard.py`: a new file lands only
    under a governing `CLAUDE.md` (root governs root level only), and
    records directories with a `.pen.json` enforce form — next id,
    pattern, required sections (the records pen `loop/pen.py` is the
    paved path).
  - `SessionStart` + `UserPromptSubmit` → `loop.summon --hook`: open
    summons and the owner-backlog count, injected ambiently.
- `hooks/` — the guards. Deny = exit 2 + reason on stderr; guards fail
  open on their own errors and never gate the owner.
- `skills/` — versioned rituals (prompt-as-code): `branch-ritual` (with
  `pr.py`, the PR pen), `glyph-knolling`.

Direction, on the record (bdo, 2026-06-10): least permissions from now
on — wrappers and denials are how the hand is forced; the watcher's
report decides which wrapper gets built next.

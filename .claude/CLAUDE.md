# .claude/ — the harness config (config-as-code)

Everything in this directory changes what sessions will admit, reject,
route, or ignore — that is code (§7): versioned, tested where it can
be, landed as stamped increments, never hand-tuned silently.

- `settings.json` — the hook wiring. Current hooks:
  - `PreToolUse` Bash|PowerShell → `hooks/command_guard.py`: denies raw
    `gh pr` mutations and all raw `git push` (the PR pen — create /
    edit / push — is the paved path); watches every other external
    tool into `.ai-native/log/tool-use.jsonl` (`--report` says which
    wrapper is worth building next).
  - `PreToolUse` Write → `hooks/write_guard.py`: a new file lands only
    under a governing `CLAUDE.md` (root governs root level only), and
    records directories with a `.pen.json` enforce form — next id,
    pattern, required sections (the records pen `loop/pen.py` is the
    paved path).
  - `SessionStart` + `UserPromptSubmit` → `loop.summon --hook`: open
    summons, the owner-backlog count, and unreflected surface drift,
    injected ambiently.
  - `Stop` → `hooks/reflect_auto.py`: the auto beat (done-line 0020),
    the repo's first *writing* hook — contract change stamped by bdo.
    After each turn it runs the reflector pen's `auto` verb: only what
    admitted, enabled reflection rules name leaves the machine; every
    act receipted on the log; fail-open, exit 0 always.
- `hooks/` — the guards. Deny = exit 2 + reason on stderr; guards fail
  open on their own errors and never gate the owner.
- `skills/` — versioned rituals (prompt-as-code): `branch-ritual` (with
  `pr.py`, the PR pen), `glyph-knolling`, `envoy` (with `envoy.py`, the
  export pen — the repo leaves as a sealed ≤10-file package, receipted
  on `exports/log.jsonl`), `reflect` (with `reflect.py`, the reflector
  pen — the owner's stamp queue mirrored onto registered external
  surfaces, every applied act receipted on the log; done-line 0018).

Direction, on the record (bdo, 2026-06-10): least permissions from now
on — wrappers and denials are how the hand is forced; the watcher's
report decides which wrapper gets built next.

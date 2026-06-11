# .claude/ — the harness config (config-as-code)

Everything in this directory changes what sessions will admit, reject,
route, or ignore — that is code (§7): versioned, tested where it can
be, landed as stamped increments, never hand-tuned silently.

- `settings.json` — the hook wiring. Current hooks:
  - `PreToolUse` Bash|PowerShell → `hooks/command_guard.py`: denies raw
    `gh pr` mutations and raw `git add`/`git commit`/`git push` (the PR
    pen and the git pen are the paved paths) — the deny-list is derived
    at runtime from the fence registry `fence/policy.py` (done-line
    0029), so this guard and the rendered `.codex/` layer move
    together; watches every other external tool — *including standalone local mutating git*
    (checkout, branch, merge, …) — into
    `.ai-native/log/tool-use.jsonl` (`--report` says which wrapper is
    worth building next; read-only git stays raw-and-watched).
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
  `pr.py`, the PR pen, and `git.py`, the git pen — branded `add`/`commit`,
  named paths only, no sweep; done-line 0020), `glyph-knolling`, `envoy`
  (with `envoy.py`, the
  export pen — the repo leaves as a sealed ≤10-file package, receipted
  on `exports/log.jsonl`), `reflect` (with `reflect.py`, the reflector
  pen — the owner's stamp queue mirrored onto registered external
  surfaces, every applied act receipted on the log; done-line 0018),
  `overnight-loop` (with `overnight.py`, the read-only brief pen — a
  long autonomous run starts only from a named arc, a session branch,
  explicit stop conditions, tests, and a report handoff; done-line 0031).

Direction, on the record (bdo, 2026-06-10): least permissions from now
on — wrappers and denials are how the hand is forced; the watcher's
report decides which wrapper gets built next.

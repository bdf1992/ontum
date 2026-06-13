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
    under a governing `CLAUDE.md` (root governs root level only), and a
    records directory with a `.pen.json` is the records pen's land —
    a raw `Write` there is allowed only as a faithful **carbon copy** of
    what `loop/pen.py` would have produced (done-line 0070, bdo's
    write-through model, 2026-06-11): fleet-safe id, the pen's heading,
    required sections, LF/UTF-8 newline-terminated bytes. The single
    definition is `loop.pen.carbon_divergences`, imported by the guard so
    the pen and the guard never disagree (I-4); a divergent write is
    refused with the divergences named — the refusal *is* the fail
    notification — never silently let through. The pen self-checks its
    own output against the same definition, so it can only ever emit a
    carbon copy.
  - `PreToolUse` Write|Edit|MultiEdit|NotebookEdit →
    `hooks/freeze_guard.py` (done-line 0033): a written done-line is a
    contract, not a draft — an *existing* file in a records directory
    whose `.pen.json` declares `"frozen": true` cannot be edited or
    overwritten in place, absolutely, with no owner exception (Codex
    editing its own done-line to add an exhaustion clause is exactly
    what this refuses). No session gets to change what done meant at all
    — not even by superseding, which is bdo's alone (`loop.pen
    supersede-done --by bdo` refuses every session signer and writes
    nothing); a session's only move is to surface a bad bar and keep
    working. The original stands as history. Creation is untouched —
    that is write_guard's land. Fails open, loudly.
  - `SessionStart` + `UserPromptSubmit` → `loop.summon --hook`: open
    summons, the owner-backlog count, and unreflected surface drift,
    injected ambiently.
  - `UserPromptSubmit` → `hooks/mock_shame.py` (done-line 0033; widened
    by 0049): the shame beat — every turn it screams every *effective*
    mock (the `loop.gaps.effective_mocks` fold, never a code literal):
    still-mock pipeline stages, `.mock` actors on the record outside the
    stage lifecycle, and record-writers no `node_real` admission ever
    named (self-asserted identity — the merge-node's 22 unadmitted
    landings are how this was caught). It grows louder the longer the
    set sits, resetting to silence only when an admission names a seat. The tally is gitignored nag
    state (`.ai-native/mock-shame.json`); the still-mock set it points
    at is the truth. bdo's correction made mechanical: a mock that moves
    fake work cannot hide behind a clean ledger. Read-only on the log,
    fail-open, exit 0 always.
  - `SessionStart` → `skills/branch-ritual/git.py sync --hook`
    (done-line 0031; amended 2026-06-11): the merge's return leg —
    fast-forwards the viewport (the primary worktree, bdo's reading
    surface) to origin/main, and **restores a stranded off-trunk
    viewport to main when its branch work is safe** (clean, pushed) —
    the session does the cleanup, it is never surfaced to bdo as a
    chore. It surfaces only to preserve work a restore would lose
    (uncommitted/unpushed, or local commits on main), naming the
    session's own fix. A writing hook like the Stop beat, stamped by bdo
    the same way; fail-open, exit 0 always.
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

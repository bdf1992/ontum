# Done-line 0013 — the write pen: records take their form from the place

Written before code, per §9.4 — by hand, for the last time in a
records directory: this is the bootstrap entry for the tool that makes
hand-creation here deniable. When this line is met, stop.

bdo's directive, on the record (chat, 2026-06-10 ~01:50, with the live
exhibit of two `0011-*.md` files eleven minutes apart): "a hook or
wrapper tool for write file which requires a CLAUDE.md file to be in
directory, with a hook ensuring a file can't be improperly created…
deterministic creation like ID incrementing and required fields like a
form… every directory has a control config for its tool wrappers…
we generally work on least permissions from now on, to force our hand."

> **Done when:** a session's Write is gated by a PreToolUse hook
> (`.claude/hooks/write_guard.py`): creating a file requires a
> governing `CLAUDE.md` at or above the target directory *within* the
> repo — the root file governs only the root level, so every subtree
> earns its own environment (D-9; `tests/` and `.claude/` get theirs
> tonight, `docs/` deliberately has none, which mechanizes its
> read-only hard rule for sessions); a records directory carrying a
> control config (`.pen.json`: filename pattern, id discipline,
> required sections, the pen command) additionally refuses wrong-next
> ids, malformed names, and missing required sections — with the
> refusal naming the paved path; the records pen (`loop/pen.py`)
> *is* that path: it allocates the next id deterministically from the
> directory fold, scaffolds the required sections, writes LF bytes,
> and reports what it made; edits to existing files and dotfiles pass
> untouched; the hook fails open on its own errors and never blocks
> the owner; the 0011 collision is resolved on disk (this branch:
> `0011-pr-pen` stands, the backlog entry is renumbered 0012); and
> tests pin the refusals and the pen's determinism (§10: a
> locally-fine but wrongly-numbered record must not fit).

Named limits, honest: the shell side (`echo > file`) stays watched by
`command_guard.py`, not gated, tonight — the watcher's `--report`
decides whether that wrapper is worth building (we only build what we
use). Broader least-permission allowlists in `settings.json` are
proposed in the PR, not imposed at 2am: the dial is bdo's (I-8).

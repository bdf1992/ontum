# Done-line 0057 — A frozen records directory refuses the fill-later stub

Written before code, per §9.4. When this line is met, stop.

> **Done when:** `loop.pen.new` no longer scaffolds a dead-path stub into a
> frozen records directory. Concretely, `python -m loop.pen new done --slug X
> --title Y` WITHOUT `--body` refuses — it prints a `result: needs-you —` line
> that says the directory is frozen and write-once, that the complete content
> must arrive via `--body`, and names the directory's required sections — and
> it writes NO file and returns non-zero. The two working paths are untouched:
> the same frozen `done` dir WITH a valid `--body` still mints the line
> (regression), and an UNFROZEN records dir (`reports`) WITHOUT `--body` still
> scaffolds the fill-later stub exactly as today (regression). The fix lives
> only in `loop/pen.py`; `.claude/hooks/freeze_guard.py` is not touched. The
> §10 bar fires the refusal for real: a test scaffolds-then-fails against a
> frozen dir and asserts the filesystem is unchanged (no file, non-zero), and
> the same call against an unfrozen dir still writes — two locally-fine inputs
> the one branch must tell apart.

## Why this is the bug, not a feature

The pen advertises a scaffold-then-fill path ("fill the placeholders before
committing"), but `.ai-native/done/` is frozen: `freeze_guard` denies any Edit
to an existing file there, so the placeholder can never be filled. On a frozen
dir the stub is a trap, and `--body` is the only real path. The pen, not the
guard, must refuse the trap at the source.

## Out of scope, named

- **The freeze guard** — `freeze_guard.py` stays the pure hard-rule guard; the
  fix does not weaken or touch it.
- **The supersede ritual and the `--body` form/section checks** — unchanged.
- **Non-frozen records dirs** — scaffold-then-fill stays valid there; this only
  closes the path that was always a dead end.

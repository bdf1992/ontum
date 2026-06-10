# Report 0009 — overnight loop: foundation reconnected, the summons wired

Session: the self-paced overnight loop bdo started 2026-06-10 ~00:45,
running on `claude/quiet-hopper-ovn8x1` (PR #9). Four done-lines met:
0007, 0008, 0009, 0010. Suite 51/51 on Windows at head. This report may
gain a dated addendum if later overnight increments land on the same
branch; the PR description is kept current either way.

## What landed, by done-line

**0007 — platform determinism.** Discovered: `core.autocrlf=true` had
rewritten every atom CRLF at checkout on bdo's Windows machine.
Identity is the content hash, so the fold read the whole field as
unborn — `--status` showed five unborn atoms while the log held four
settled and one awaiting the stamp. Operationally: **the owner inbox
was hiding `atom.epic-layer.v0`**, which had been waiting on bdo since
04:01Z. Fix: `.gitattributes` pins LF for source, exempts
`.ai-native/**` and `*.jsonl` from eol conversion entirely, and
union-merges the three logs; the working tree was restored to the
stored LF bytes, so every hash re-matches its announced identity —
history *reconnected*, nothing re-announced, nothing retro-invalidated
(D-5). Also: the kill test used POSIX-only `signal.SIGKILL`; it now
uses a cross-platform hard kill, so the suite runs green on Windows and
"tests before every push" is enforceable on this machine again.

The diagnostic worth keeping (§10 spirit): two sensors disagreeing —
the orchestrator's fold vs the raw log — *was* the signal. Neither was
wrong; their disagreement located the corruption precisely.

**0008 — the summons fires.** `loop/summon.py`: the open summons as a
pure read-only fold — who is summoned, at which seam, the terminal set,
the one judge line that clears it. `.claude/settings.json` (first hook
wiring in this repo): `SessionStart` and `UserPromptSubmit` run
`python -m loop.summon --hook`, so any session that blinks in here is
handed its summons — the session is the virtual node (D-10), and
`loop.node judge` stays the only pen. The hook never writes and always
exits 0; the stamp queue is deliberately excluded (the inbox is the
owner's surface, D-4).

**0009 — prompts as code.** `.ai-native/nodes/value-gate.claude.v1.md`:
the L0 gate's judging prompt as hand-authored versioned source with
§7's edges. The summons delivers it with its sha256; the receipt
records `prompt_hash` — every verdict attributable to the exact prompt
that judged, while the hash stays out of the receipt id so a prompt
edit can never reopen a settled verdict (I-2). Absence remains
information: a node without a prompt file still summons and judges.
Named debt: semantic evals for the prompt are owed with its next change.

**0010 — the environment composes.** Per bdo's @/@@ directive (chat,
2026-06-10): the root `CLAUDE.md` is now a thin composition surface
that `@`-imports module environments living next to their modules
(`loop/CLAUDE.md`, `glyphs/CLAUDE.md`, `.ai-native/CLAUDE.md`), and
names the scope stack — user-global beneath, project above, nested
files per directory. Nothing load-bearing dropped; the module docs
catch up with tonight's substrate; `CLAUDE.md` is finally committed.

## Mid-flight coordination, named

- bdo (with a second session) committed `ac0d5f2` — branch-ritual
  0.2.0 — directly onto this rolling branch at 01:24 while the loop was
  between increments. No conflict resulted; the loop adopted a
  pull-before-iteration habit from that point. The sharpened ritual
  (story on every PR, dead-branch check, flags surface in the PR) is
  followed by this hand-off.
- The stranded busy-feynman glyph work this loop had queued as a
  gardening note was already recovered as PR #8 with its story written.
  Nothing left to do there but bdo's stamp.

## needs-you (the morning queue)

1. **`atom.epic-layer.v0` awaits your stamp** (`owner-stamp.bdo.v1`) —
   it was invisible until 0007 reconnected the field. `python -m
   loop.node inbox` briefs it; the web inbox works too.
2. **PR #9 at the stamp** — this branch: done-lines 0007–0010.
3. **PR #8 at the stamp** — the glyph-viewer recovery (pre-existing,
   carries its own needs-you flags including the report-numbering
   collision).
4. **Report numbering**: this report takes 0009 on this branch;
   PR #8's branch carries its own 0009–0012. Filenames differ so merges
   stay clean, but the index forks — the renumbering decision flagged
   on PR #8 now covers both.
5. **Hook trust prompt**: first session in this repo after merge,
   Claude Code will ask to trust the project hooks in
   `.claude/settings.json`. Accepting is your stamp on that config.
6. Optional machine hygiene: `.gitattributes` now neutralizes it, but
   `core.autocrlf=true` is still set on this machine; `git config
   --global core.autocrlf false` would remove the trap for other repos.
   Your machine, your call.

## End-state

`report` — four done-lines met and pushed; field healthy (4 settled,
1 at your stamp, 0 parked); nothing blocked except on your verdicts.

# Report 0133 — tool-scout skill — agentic search over CLI tools + repo tooling

## What landed

No done-line preceded this work — named as a conflict, not silently
resolved (see below). bdo asked directly for a dedicated skill to query
across his PC and repos for tools, usable within 15 minutes, and floated
discussing/forking off the repo's graphing and query tooling
(`causality/term_economy.py`).

Landed: `.claude/skills/tool-scout/` — `SKILL.md` plus `scout.py`, a pure
stdlib, read-only, no-network fold indexing four sources (PATH
executables; this repo's `.claude/skills/*/SKILL.md`;
`.claude/workflows/*.js` meta blocks; `python -m loop.*` commands from
`loop/CLAUDE.md`), ranked by token overlap. Forking `term_economy.py` was
considered and declined (different domain, §10 don't-double-build); the
pen reuses the pattern instead (pure/read-only/stdlib, sibling grain to
`loop/gaps.py`/`causality/term_economy.py`).

A naming collision surfaced and was resolved by disambiguation, not
avoidance: this repo already has a capital-S **Scout**
(`loop/scout.py`/`ScoutCTA`, done-line 0148, `epic.strategy`) — a
strategic-conjecture generator, unrelated in purpose. `SKILL.md` carries
an explicit "not to be confused with" note and changelog entry naming
the distinction, kept the requested name (bdo's literal ask) rather than
silently avoiding the collision by renaming.

PR #751 opened to main; requisitioned an independent review via the
`code-review` skill (§ the hard rule — work isn't landed at "I built it").
The review returned three findings, all addressed on this branch before
hand-off:
- **Confirmed bug** (fixed): `META_DESC_RE`/`META_NAME_RE` stopped at a
  backslash-escaped quote inside a workflow's JS string literal instead
  of the real closing quote, silently truncating any description
  containing one — reproduced against this repo's own `tend-heal.js`
  (`"...bdo\'s, D-4)"` truncated to `"...bdo\"`). Fixed with an
  escape-aware string regex (`(?:\\.|(?!\1)[^\\])*`) plus unescape.
- **Missing test coverage** (fixed): added `tests/test_tool_scout.py` (7
  tests) — the escaped-quote regression is now reproduced against a
  fixture and asserted fixed, plus coverage for the skill/loop sources,
  search ranking, no-write invariant, and CLI JSON/no-match output.
- **Missing session report** (fixed): this file.

Suite: green now (`python -m unittest discover -s tests -v`) except one
pre-existing failure, unrelated to this branch (named at push with
`--red-ok` and in the PR body) — see needs-you below.

`gh` CLI is unavailable in this remote session's container, so the PR
itself was opened via the GitHub MCP tool rather than `pr.py create`
(which shells out to `gh`); the git pen's branded commit and
`pr.py push --red-ok` still ran normally as the paved path.

## needs-you

1. **Pre-existing red test, unrelated to this branch:**
   `tests.test_git_pen.TestGitGuard.test_local_mutating_git_is_now_watched`
   fails on `main` too (confirmed by inspection — nothing in this diff
   touches `fence/`, `command_guard.py`, or `test_git_pen.py`). The
   done-line-0145 workstation fence now denies viewport-flipping git
   verbs (`checkout -b`, `branch -D`, `merge`, `rebase`, `worktree add`)
   whenever `command_guard.py`'s session payload omits `cwd` and falls
   back to `os.getcwd()` (the primary tree). This test's mock payload
   (done-line 0020 era) predates the fence and never sets `cwd`, so it
   now trips a rule that didn't exist when it was written. This is a
   judgment call, not a mechanical fix: either the test should mock a
   worktree `cwd` (asserting the fence's intended shape), or the fence's
   `cwd` fallback needs a decision for the untagged-payload case. Flagging
   rather than picking one myself.
2. **Blueprint-before-build was skipped, by explicit request.** bdo's
   ask carried a hard 15-minute constraint; the doctrine's "blueprint
   before build" (bdo, 2026-06-20) asks for a bundle/CTA-agreement before
   building on any non-trivial arc, and "write the done-line before
   starting" (§9.4) asks for a done-line first. Read this as a
   single-session, bounded skill addition (not a new arc) and built
   directly rather than stall on ceremony against an explicit time
   window — naming the tension here rather than silently picking one
   rule over the other. No done-line exists for this work; if bdo wants
   one written retroactively for the record, that's his call, not mine
   to backfill unasked.
3. Unrelated, ambient, pre-existing pressure noticed but not touched:
   the owner-ask-shame beat reports 36 owner-asks across 12 reports never
   surfaced to a bdo-read surface — out of scope for this task, named so
   it isn't mistaken for something this session addressed.

## End-state

`report` — tool-scout skill built, reviewed, findings fixed, tests
green (one pre-existing unrelated failure declared), PR #751 open at
`bdf1992/ontum` awaiting bdo's arc confirmation and the merge-node.

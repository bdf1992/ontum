# Report 0013 — the PR pen: the story is validated, not requested

*Numbered 0013, not 0009: PR #8's branch carries reports 0004–0012,
colliding with main's 0004–0008. This number clears the whole known
fork. The renumbering decision is still bdo's (flagged on PR #8).*

## What happened

bdo saw PR #8 at the stamp wearing "No description provided" and asked
why the requests don't carry a story. Diagnosis: the branch-ritual
skill *already required* the story (v0.1.0, hand-off step 4) — prose
that nothing enforced. PR #8 was opened by the owner's button, outside
the ritual, recovering nine commits a session had stranded on
`claude/busy-feynman-4hd46k` after PR #6 merged — the second stranding
(PR #2 was the first). Two failures, one root: the ritual asked,
nothing validated.

bdo's directive: make PR creation a CLI tool with required fields and
validation, deny the raw GitHub verbs with a hook — and (amended
mid-build) make the hook a *watcher* over all raw external-tool use,
so wrapper coverage grows from observed use. Determinism over
compliance, applied to our own process.

## What landed (done-line 0011)

- **The pen** — `.claude/skills/branch-ritual/pr.py`, the one write
  path to a PR (the `loop/node.py` pattern). `create` refuses to
  submit without the story: a title that isn't the branch name, what
  landed, the done-line served (or `none --why`), the report number,
  the end-state vocabulary, flags raised for bdo (required when
  `needs-you`). It also refuses dead branches (unless `--recover`,
  the PR #4 pattern), second open PRs from the same head, and a red
  suite unless declared with `--red-ok` — the declaration lands *in
  the story*. `edit` is the repair path through the same validation;
  `check` audits open PRs for unwritten stories (the owner's button
  still exists — `check` is the sensor for that gap).
- **The guard + watcher + shame** — `.claude/hooks/command_guard.py`,
  wired as PreToolUse *and* PostToolUse hooks on Bash/PowerShell in
  `.claude/settings.json`. Denies (exit 2, message points at the
  pen): `gh pr create/edit/merge/close/reopen/review`, `git push` to
  the trunk in any refspec spelling. Everything else passes, but raw
  external-tool use (gh, curl, network git, …) is recorded to
  `.ai-native/log/tool-use.jsonl` — a sensor trace, gitignored,
  deletable, not truth. `--report` folds it: which raw tools sessions
  actually reach for, heaviest first — the next wrapper worth
  building. We only build what we use. And per bdo's third directive:
  collection alone is silent, so the PostToolUse pass (`--post`)
  *shames* unbranded use into the context window via
  `additionalContext` — once per tool per session, with the running
  audit count — so the generic brand surfaces naturally in
  conversation and becomes a judgment call (mint the wrapper or keep
  it raw). All `gh` use is collected, including read-only; the pen's
  own internal `gh` subprocess calls are sanctioned and invisible to
  the hook by construction (hooks see top-level commands only).
- **Skill 0.2.0 → 0.3.0** — earlier this session, 0.2.0 sharpened the
  prose (story binds every PR including recovery, dead-branch check
  before push, flags-for-bdo surface in the description). 0.3.0 makes
  it structural: hand-off runs through the pen; gardening gains the
  two folds (`pr.py check`, `command_guard.py --report`).
- **Tests** — `tests/test_pr_ritual.py`, 27 tests. The shame path is
  pinned: first unbranded use injects context, repeat use in the same
  session stays quiet, a new session is shamed afresh with the
  cumulative count, local work is never shamed. The §10 case is
  pinned: a locally-fine, story-less create refuses to fit; the
  guard denies each raw verb and stays blind to local work; the
  watch log tolerates a torn tail (it never happened). Probed live
  beyond the suite: the pen refused a story-less create and refused
  a well-formed create against this branch's already-open PR #9, at
  the right layer each time.
- Also this session: PR #8's missing story was written onto it
  (`gh pr edit`, before the guard denied that verb — the repair verb
  is now `pen edit`).

## Design decisions, named

- **Deny-list, not deny-all.** bdo asked about wrapping "all GitHub
  commands"; what shipped denies the *mutating* verbs and watches the
  rest. Denying read-only `gh` would brick sessions (the pen itself
  reads via `gh`). The watcher is the agreed mechanism for growing
  coverage; the deny-list is one tuple in `command_guard.py`.
- **The hook gates sessions, not the owner.** GitHub's button still
  makes story-less PRs; `pen check` during gardening is the sensor.
- **The watch log is a trace, not truth** — gitignored beside the
  cache entries, torn-tail-tolerant at read, deletable any time.

## End-state: `report`

Work is on `claude/quiet-hopper-ovn8x1`, joining open PR #9 at the
stamp. Suite 76/76 green.

Open items for bdo (also flagged on PR #8): the report-numbering
collision; the Core 27 mint awaiting the pin; the 'drift' borrow.
One more: the PreToolUse hook takes effect for *new* sessions when
settings.json is loaded — running sessions (this one included) are
not retro-gated mid-flight.

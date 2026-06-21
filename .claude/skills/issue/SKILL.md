---
name: issue
description: >-
  The governed door for GitHub issue mutations (#412): the issue-side
  sibling of the PR pen. A session does not type raw `gh issue close`
  or `gh issue comment` — those are forbidden by the fence and, worse,
  used to slip through the Claude surface silently (the prompt-parity
  hole: a `prompt`-decision fence rule is a no-op on Claude). This pen
  is the paved path: it closes or comments through the `gh` CLI AND
  records the act on the append-only log with provenance — who, why,
  when — so a governed issue mutation is a fact the loop can fold, never
  a side effect that vanished into GitHub. Use when you need to close an
  issue with a reason or comment on one as a recorded act. The pen is
  issue.py beside this file. Note: the reflector pen (reflect.py) still
  owns the owner-stamp-queue mirror and the gate pen (gate.py) still
  owns its run-issues — this pen is for deliberate, recorded issue acts
  a session takes by hand.
version: 0.1.0
owner: bdo
changelog:
  - version: 0.1.0
    note: >-
      First form (#412). GitHub issue creation/closing/commenting was
      ungoverned and the fence rule that should have caught it was
      decision `prompt` — a silent no-op on Claude (only `forbidden`
      rules compile into command_guard.DENY_RULES). This pen + the
      flip of `gh-issue-mutate` to `forbidden` close the hole: raw
      `gh issue` mutations are denied, reads stay raw-and-witnessed,
      and every governed mutation lands a provenance record.
---

# Issue — the governed issue door

Raw `gh issue close` / `gh issue comment` / `gh issue create` are
**forbidden** by the fence registry (`fence/policy.py`,
`gh-issue-mutate`). A mutation goes through this one writer, which does
two things the raw command never did: it makes the act, and it
**records the act on the log** with provenance. Reads (`gh issue view`,
`gh issue list`, `gh issue status`) stay raw — they are witnessed, not
gated (the repo's read/write asymmetry).

Forbidding the raw command does **not** block this pen: the
command_guard watches the *Bash* tool, and this pen shells out to `gh`
from inside Python where no Bash hook sees it — exactly as raw `gh pr`
is forbidden while `pr.py` works.

## Using

```sh
# close an issue with a reason (the reason is posted as a closing comment)
python .claude/skills/issue/issue.py close <number> --reason "<why>" --by <who>

# comment on an issue as a recorded act
python .claude/skills/issue/issue.py comment <number> --body "<text>" --by <who>
```

`--repo <owner/repo>` is optional; without it `gh` infers the repo from
the working directory's git remote.

Every invocation ends with a `result: done | report | needs-you` line:

- **done** — the gh act succeeded and the provenance record is on the log.
- **report — refused: …** — the door refused the input (an empty reason,
  an empty body, or a missing `--by`): a governed mutation must carry
  accountability. Nothing reached `gh`; nothing was recorded.
- **needs-you — …** — `gh` itself refused (no such issue, auth, network);
  surface it.

## The teeth

- A governed close carries a **reason** and a **signer** (`--by`),
  refused at the door otherwise — an unattributed close is exactly what
  this pen exists to prevent.
- The provenance record lands **only after** the gh call succeeds: a
  close GitHub refused is never written as if it happened.
- The record is one append-only event
  (`{"type":"issue.closed"|"issue.commented","number":…,"reason"/"body":…,
  "by":…,"kind":"issue-governance","id":"evt.…","ts":…}`), written
  through `loop.reconcile.append_line` — the same line-atomic, torn-tail
  tolerant writer as the rest of the log.

## Boundaries

- Outward reach (`gh`) lives here, in the pen, never in `loop/` (which
  is network-free) — like `reflect.py` and `gate.py`.
- This pen is for **deliberate, recorded** issue acts a session takes by
  hand. The owner-stamp-queue mirror stays the reflector pen's
  (`reflect.py`); a gate's run-issue stays the gate pen's (`gate.py`).
- Reads are not in scope — a session may always look (`gh issue view`,
  `gh issue list`).
- The §10 proof is `tests/test_issue_pen.py`: the pen records a
  well-formed event and refuses an empty reason / missing signer (no
  reach, no record), and the live command_guard denies `gh issue close`
  while passing `gh issue view`/`list` — the hole, closed and proven
  non-vacuous.

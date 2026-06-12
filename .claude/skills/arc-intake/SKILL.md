---
name: arc-intake
description: >
  Read bdo's arc confirmations from GitHub and act on them. bdo steers from
  GitHub on his phone — he closes an arc's confirm issue with a plain-language
  comment, and the comment carries his intent. This skill reads that comment,
  judges his intent (confirm / decline / unclear), and on a clear confirm runs
  the confirm pen and lets the merge-node land the arc's PRs — always replying
  with how it read him, never landing on a guess. Use when there are closed
  arc-confirm issues to read, when the summon/digest reports them, or when
  asked to "read bdo's confirmations" or "process the arc inbox".
version: 0.1.1
---

<!-- changelog 0.1.1 (done-line 0052): the land example says the v1 seat
     (merge-node.claude.v1) — the id issue #82 admits and the land pen's
     unadmitted-signer refusal names; v0 is the superseded stage side. -->

# arc-intake — bdo's GitHub confirmations, read and acted on

bdo will not run a CLI and will not open a custom UI. His surface is GitHub,
which he already carries on his phone. An arc with PRs waiting becomes one
issue; he **closes it with a comment in his own words**, and the comment is
the intent. This skill is the session that reads him — because meaning is the
model's to recover, not a keyword's.

## The one invariant — read before anything

**Never land on a guess about what bdo meant.** You are reading natural
language. If his comment clearly confirms, act. If it clearly declines, leave
the arc unconfirmed. If it is ambiguous, empty, or you are not sure — you
**reopen the issue and ask**, and land nothing. A misread that lands work to
main is the worst outcome here; an extra question is cheap.

And **always echo your reading back** in the reply, so bdo sees exactly how
he was understood and what happened — a wrong read is then visible and his to
correct, never silent.

## The ritual

1. **Get the worklist** (deterministic, read-only):
   ```sh
   python .claude/skills/arc-intake/intake.py pending --repo <owner/repo> --json
   ```
   Each item is `{number, epic, title, comment}` — an issue bdo closed and the
   comment he closed it with. (Empty list → nothing to do; stop.)

2. **Read each comment and judge his intent** — this is yours, not a pen's:
   - **confirm** — he clearly wants the arc's work landed ("yes", "ship it",
     "go ahead", "looks good, land it", and the like, in any phrasing).
   - **decline** — he clearly does not ("no", "hold off", "not yet", "revert").
   - **unclear** — anything else: a question, a caveat, mixed signals, empty.

3. **Act on the verdict:**
   - **confirm:** stamp the arc to the trunk, then land its PRs as the
     merge-node (you did not author them; bdo's confirmation is the authority):
     ```sh
     python .claude/skills/branch-ritual/pr.py confirm --epic <epic> --by bdo
     # then, per open PR under this arc:
     python .claude/skills/branch-ritual/pr.py land <n> --epic <epic> --by merge-node.claude.v1
     ```
     Then reply and close out:
     ```sh
     python .claude/skills/arc-intake/intake.py reply --issue <n> --repo <owner/repo> \
       --body "Read your intent as: CONFIRM <epic>. Landed #<a>, #<b> (rcp.merge.<a>, ...). " --done
     ```
   - **decline:** land nothing. Reply with your reading and mark it done:
     ```sh
     python .claude/skills/arc-intake/intake.py reply --issue <n> --repo <owner/repo> \
       --body "Read your intent as: DECLINE <epic>. Left it unconfirmed; its PRs stay open." --done
     ```
   - **unclear:** land nothing. Reply with what you were unsure about and
     **reopen** so it returns:
     ```sh
     python .claude/skills/arc-intake/intake.py reply --issue <n> --repo <owner/repo> \
       --body "I wasn't sure how to read this — did you mean confirm <epic> and land its PRs, or hold? Reopening so you can say." --reopen
     ```

4. **Stop when the worklist is empty.** Do not escalate to bdo by any channel
   but his reply comment — the issue is the conversation.

## Where the pieces live

- The gh I/O: `intake.py` beside this file (open / pending / reply) — deterministic.
- The stamp to the trunk: `pr.py confirm` (the owner seam, done-line 0033).
- The land: `pr.py land` / the `merge-node` skill — never your own authored PR.
- The eyes bdo reads instead: `python -m loop.digest`.

## When the ritual is wrong

This is ours to sharpen. If reading bdo fights the work, change this file and
`intake.py` in the same PR, bump the version, and land it the way everything
lands now: bdo confirms its arc from GitHub, the merge-node lands it.

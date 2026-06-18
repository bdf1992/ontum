---
name: realness-intake
description: >
  Read bdo's realness confirmations from GitHub and act on them. A mock pipeline
  stage with a built, tested real backing waits on one decision — bdo trusting it
  to judge for real — and bdo makes that decision the way he makes every
  decision: from GitHub, wherever he is, by closing the stage's realness-confirm
  issue with a plain-language comment. This skill reads that comment, judges his
  intent (confirm / decline / unclear), and on a clear confirm runs the realness
  admission on his authorization (loop.node admit-real --by bdo) — always
  replying with how it read him, never admitting on a guess. Use when there are
  closed realness-confirm issues to read, when the summon/digest/mock-shame
  surfaces a stage waiting on its stamp, or when asked to "read bdo's realness
  confirmations" or "process the realness inbox".
version: 0.1.0
---

# realness-intake — bdo's GitHub realness stamps, read and acted on

bdo will not run a CLI and will not open a custom UI. His surface is GitHub,
which he can reach from any device. Sibling to arc-intake (done-line 0038):
that skill lets him confirm an *arc*; this one lets him make a *gate real*.
Making a stage real is a real authority act — it changes what the loop trusts
to judge — and it stays bdo's (done-line 0028 scopes arc-confirmation to the
owner-stamp stage, **not** `node_real`; both prior real gates were admitted by
his direct stamp). This skill does not take that decision from him; it carries
it from GitHub to the log.

## The one invariant — read before anything

**Never admit on a guess about what bdo meant.** You are reading natural
language. If his comment clearly confirms, run the admission. If it clearly
declines, leave the stage mock. If it is ambiguous, empty, or you are not sure
— you **reopen the issue and ask**, and admit nothing. A misread that makes a
gate real wires the loop to trust a judge bdo did not bless — the worst outcome
here; an extra question is cheap.

And **always echo your reading back** in the reply, so bdo sees exactly how he
was understood and what happened — a wrong read is then visible and his to
correct, never silent.

## Before opening an issue: the backing must be real-able

Only open a realness-confirm issue for a stage whose real node is **built and
tested** — the prompt/law spec exists in `.ai-native/nodes/<node>.md` and a test
proves the node can refuse (§10). Opening the gesture for a backing that cannot
yet say no would be asking bdo to bless a turnstile. The honest signal that a
backing is ready is its passing §10 test on the trunk.

```sh
python .claude/skills/realness-intake/realness.py open \
  --stage <mock-node> --node <real-node> --repo <owner/repo>
```

## The ritual

1. **Get the worklist** (deterministic, read-only):
   ```sh
   python .claude/skills/realness-intake/realness.py pending --repo <owner/repo> --json
   ```
   Each item is `{number, stage, node, title, comment}` — an issue bdo closed
   and the comment he closed it with. (Empty list → nothing to do; stop.)

2. **Read each comment and judge his intent** — this is yours, not a pen's:
   - **confirm** — he clearly wants the gate made real ("make it real", "yes",
     "wire it up", "go live", "looks good, ship it", in any phrasing).
   - **decline** — he clearly does not ("no", "hold off", "not yet", "keep it
     mock", "needs more proof").
   - **unclear** — anything else: a question, a caveat, mixed signals, empty.

3. **Act on the verdict:**
   - **confirm:** run the realness admission on his authorization — his closed
     issue is the stamp, you are its executor (D-4, never `--by` yourself):
     ```sh
     python -m loop.node admit-real --stage <stage> --node <node> --by bdo
     ```
     Then reply with the admission id and close out:
     ```sh
     python .claude/skills/realness-intake/realness.py reply --issue <n> --repo <owner/repo> \
       --body "Read your intent as: CONFIRM — made <stage> real, backed by <node> (admission adm.<...>). The loop now parks atoms here for it to judge; the mock temperature drops by one." --done
     ```
   - **decline:** admit nothing. Reply with your reading and mark it done:
     ```sh
     python .claude/skills/realness-intake/realness.py reply --issue <n> --repo <owner/repo> \
       --body "Read your intent as: DECLINE — left <stage> mock; its real backing <node> stays built and tested, waiting for your stamp." --done
     ```
   - **unclear:** admit nothing. Reply with what you were unsure about and
     **reopen** so it returns:
     ```sh
     python .claude/skills/realness-intake/realness.py reply --issue <n> --repo <owner/repo> \
       --body "I wasn't sure how to read this — did you mean make <stage> real (back it with <node>), or hold? Reopening so you can say." --reopen
     ```

4. **Stop when the worklist is empty.** Do not escalate to bdo by any channel
   but his reply comment — the issue is the conversation.

## Where the pieces live

- The gh I/O: `realness.py` beside this file (open / pending / reply) — deterministic.
- The admission: `loop.node admit-real` (the realness seam) — run only on a clear confirm, `--by bdo`.
- What goes mock→real, and the mock temperature: `hooks/mock_shame.py` and
  `python -m loop.placement_gate --atom <id>` (a backing's read-only preview).
- The eyes bdo reads: `python -m loop.digest`.

## When the ritual is wrong

This is ours to sharpen. If reading bdo fights the work, change this file and
`realness.py` in the same PR, bump the version, and land it the way everything
lands now: bdo confirms its arc from GitHub, the merge-node lands it.

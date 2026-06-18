---
name: policy-intake
description: >
  Read bdo's gateway-policy authorizations from GitHub and act on them. The
  inference gateway (loop/inference.py) denies every (caller, surface, mind)
  by default — RBAC admits no thought without a rule — and a policy is bdo's to
  set the way every decision of his is made: from GitHub on his phone, by
  closing the policy's policy-confirm issue with a plain-language comment. This
  skill reads that comment, judges his intent (permit / decline / unclear), and
  on a clear permit runs the admission on his authorization (loop.inference
  policy --by bdo) — always replying with how it read him, never admitting on a
  guess. Use when there are closed policy-confirm issues to read, when a gateway
  caller (e.g. the gardener's cut-verifier) is held for want of a policy, or
  when asked to "read bdo's policy authorizations" or "process the policy inbox".
version: 0.1.0
---

# policy-intake — bdo's GitHub gateway-policy stamps, read and acted on

bdo will not run a CLI and will not open a custom UI. His surface is GitHub,
which he already carries on his phone. Fourth sibling of arc-intake (done-line
0038), realness-intake (0042), and rung-intake (0051): that family lets him
confirm an *arc*, make a *gate real*, and grant a *trust rung*; this one lets
him set a *gateway policy* — the default-deny RBAC (loop/inference.py) that
authorizes which caller may consult which mind at which surface. A policy is a
real authority act: the gateway enforces it at every inference call, and it
stays bdo's (D-4: nothing grants itself a policy).

It is how bdo sets the **bound** of the inference-as-composition layer (his
framing, 2026-06-17): the settled, owner-stamped edge inside which just-in-time
inference composes behavior. The first caller it gates is the inference-verified
cut (done-line 0100): the gardener's branch deletion is held by default-deny
until a policy here permits `(branch-ritual.garden, branch-cut, a mind)`.

## The one invariant — read before anything

**Never admit on a guess about what bdo meant.** You are reading natural
language. If his comment clearly permits, run the admission. If it clearly
declines, leave the gateway at default-deny (which is already safe — nothing is
un-guarded by inaction). If it is ambiguous, empty, or you are not sure — you
**reopen the issue and ask**, and admit nothing. A misread policy widens what an
agent class may make the gateway think, silently — the worst outcome here; an
extra question is cheap. Default-deny is the safe failure: a policy never set is
a caller still held, never a caller wrongly let through.

And **always echo your reading back** in the reply, so bdo sees exactly how he
was understood and what happened — a wrong read is then visible and his to
correct, never silent.

## Before opening an issue: the policy must have a waiting act

Only open a policy-confirm issue when something concrete is held for want of
that exact policy — a gateway caller the default-deny refused, a cut the
gardener is holding because inference was unavailable — and name that held act
in the issue body. Asking for an authorization with nothing waiting to use it
would be policy-farming; the gateway opens because work needs it, not because a
rule is nice to have. The pen refuses to open a malformed policy (it imports
`loop.inference.policy_refusal`, the same check the admission pen makes), so the
question asked and the act admittable never drift; this skill never works around
that refusal.

```sh
python .claude/skills/policy-intake/policy.py open \
  --caller branch-ritual.garden --surface branch-cut --mind '*' --repo <owner/repo>
```

## The ritual

1. **Get the worklist** (deterministic, read-only):

   ```sh
   python .claude/skills/policy-intake/policy.py pending --repo <owner/repo>
   ```

   Each row is a policy-confirm issue bdo CLOSED and not yet acted on, carrying
   the `(caller, surface, mind, permit)` it asks for and his closing comment.

2. **Read his intent from the comment** — permit / decline / unclear. Judge the
   plain language, not keywords. "yes, let the gardener think", "go ahead",
   "authorize it" is a permit. "no", "not yet", "hold off" is a decline.
   Anything you cannot be sure of is **unclear** — do not admit.

3. **Act only on a clear permit**, on his authorization (D-4):

   ```sh
   python -m loop.inference policy \
     --caller <c> --surface <s> --mind <m> [--deny] --by bdo
   ```

   (`--deny` only if the marker's `permit=false`.) The receipt cites bdo as the
   grantor; the gateway reads the policy from the log at call time.

4. **Reply with what was done — always:**

   ```sh
   # on a clear permit, after the admission:
   python .claude/skills/policy-intake/policy.py reply --issue <n> --repo <owner/repo> \
     --body "Read you as: permit. Set the gateway policy (caller, surface, mind) --by bdo. The cut-verifier can now consult its mind; the gardener resumes verified cuts." --done

   # on a clear decline:
   python .claude/skills/policy-intake/policy.py reply --issue <n> --repo <owner/repo> \
     --body "Read you as: decline. Left the gateway at default-deny — the caller stays held (safe). Reopen with a permit when you want it live." --done

   # on unclear — reopen and ask, admit nothing:
   python .claude/skills/policy-intake/policy.py reply --issue <n> --repo <owner/repo> \
     --body "I couldn't be sure whether you meant permit or decline. Reopening — a one-word 'permit' or 'decline' is enough." --reopen
   ```

   `--done` marks the issue `intake-done` so a re-run never honours the same
   gesture twice (I-2 at the surface).

## What this skill never does

- Never admits a policy bdo did not clearly authorize (the one invariant).
- Never opens an issue for a policy with no waiting act, or one the admission
  pen would refuse (the pen enforces both).
- Never reaches the gateway itself — it only sets the *authorization*; the
  inference call stays the gateway pen's, gated by the policy this admits.

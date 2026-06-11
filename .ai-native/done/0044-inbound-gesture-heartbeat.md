# Done-line 0044 — bdo's GitHub gestures reach a session on the heartbeat, not a poll

Written before code, per §9.4. When this line is met, stop.

> **Done when:** bdo's inbound GitHub gestures reach a session on a **known
> event, never a poll**. A SessionStart hook (the harness layer, where `gh`
> lives) asks the intake pens which arc-confirm and realness-confirm issues bdo
> has **closed** and not yet been answered on, and surfaces the count + which
> skill reads each into the session's context — the missing *inbound* subscriber
> on the summon hook's existing heartbeat (SessionStart + UserPromptSubmit). It
> judges nothing and acts on nothing: reading bdo's words is the model's job (the
> intake SKILLs), which a deterministic hook cannot do — it only wakes the
> session to the fact that he acted. Pub/sub, level-triggered: the closed issue
> is the topic, the session is the subscriber, the heartbeat is the known event —
> no daemon, no busy-poll (`loop/` stays stdlib-only; the `gh` reach lives in the
> hook). **Fail-open and bounded:** no gh, no auth, or a slow call and the hook
> stays silent and exits 0, never delaying or gating a session. Wired into
> `settings.json` SessionStart. Proven by a test pinning the pure surfacing:
> pending gestures format a clear wake line naming the skill, an empty inbox
> stays silent, and a broken sensor yields silence rather than a crash.

## Out of scope, named

- **Zero-session wake (GH Actions on issue-close).** bdo chose heartbeat-only
  (2026-06-11); the webhook layer — which still needs a model trigger to judge
  intent — is its own done-line *if* the session-start cadence proves too slow.
- **Acting on the gesture.** `admit-real` / `confirm-arc` stay the intake SKILLs
  the session runs; this hook only wakes it. A hook that judged intent would be
  the keyword-guessing the intake doctrine forbids.
- **UserPromptSubmit cadence.** SessionStart only for now (one gh call per
  session). Hanging it on every prompt — or a throttled version — is a tuning
  knob for later, not this line.

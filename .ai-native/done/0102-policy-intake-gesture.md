# Done-line 0102 — bdo authorizes a gateway policy from GitHub, never a CLI

Written before code, per §9.4. When this line is met, stop.

bdo, 2026-06-17: the inference-verified cut (done-line 0100) is inert until a
gateway policy authorizes the garden to consult a mind — and a policy is
config-as-code AuthZ, which today is only settable by CLI (`loop.inference
policy --by bdo`). bdo does not run a CLI; his surface is GitHub. This builds
the fourth sibling of arc-intake / realness-intake / rung-intake: the inbound
half of his GitHub surface for **gateway policies**, so he authorizes the cut
(and any future policy) by closing one issue with a plain-language comment.
This is how he sets the **bound** of the inference-as-composition layer (his
2026-06-17 framing) — the settled, owner-stamped edge inside which JIT
inference composes behavior. The pen moves bytes to and from GitHub only; the
intent-judgment is the SKILLs, and the privileged act stays bdos (D-4).

> **Done when:** a `policy.py` pen beside a `policy-intake` SKILL.md gives the
> three deterministic gh verbs the rung-intake pen gives — **open** (one
> `policy-confirm` issue carrying a hidden `caller/surface/mind/permit` marker,
> refusing any policy `loop.inference.policy_refusal` would reject, so it opens
> no question the admission pen could not answer), **pending** (the closed,
> not-yet-acted policy-confirm issues, each parsed back to its policy and
> carrying bdos closing comment — the worklist), and **reply** (echo what was
> done, reopen-to-ask on unclear, or mark intake-done so a re-run never
> double-acts) — the pen importing loop.inference for one vocabulary so what is
> asked and what can be admitted never drift; the SKILL states the one
> invariant (never admit on a guess about his intent: a clear confirm runs
> `loop.inference policy ... --by bdo`, a decline leaves default-deny, an
> unclear comment reopens-and-asks) and the waiting-act discipline (open only
> when a gateway caller is actually held for want of that policy); and
> `tests/test_policy_intake.py` pins the teeth: a half-marker is not a marker,
> open_refusal is exactly inference.policy_refusal (a malformed policy is
> refused at the door), and the worklist drops an already-acted (intake-done)
> issue so no gesture is honoured twice (I-2 at the surface).

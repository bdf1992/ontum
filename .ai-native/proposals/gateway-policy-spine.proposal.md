# gateway-policy-spine.proposal.md

**Status: PROPOSED** (study-first, per bdo, 2026-06-18). Author: a session
(Claude), on bdo's direction, derived with a `last30days` pass. Nothing here
is minted; the adopt-vs-native decision (and the naming) stay bdo's (D-4).

## The thesis

The repo's hard guards — `command_guard`, `write_guard`, `freeze_guard`, and
now `ask_guard` — are scattered bespoke hooks. bdo's frame (2026-06-18):
turn them into **policies installed into gateways**, so that *what's guarded*
is **derived from policy**, and *policy* is **derived from context** (surface,
user, location, configuration, bounded inference). This is the
Policy-Decision-Point / Policy-Enforcement-Point (PDP/PEP) architecture — and
the striking finding is that **the repo has already half-built it** and **the
field is standardizing exactly this split**.

## bdo's derivation chain (formalized)

```
location + configuration + inference      ->  gateway operation
surface  + user-information + gateway-op   ->  policy
policy                                     ->  what is guarded
```

Read bottom-up: where you are + the config + bounded inference decide how a
gateway *operates*; the surface (which harness) + who you are + that operation
decide the *policy* in force; the policy decides what is *guarded*.

## Prior art (the last30days derive, 2026-06-18)

External signal confirms the frame is where the field is heading — ontum is
not greenfielding a private idea:

- **apparitor** (open-sourced 2026-06-16, Apache-2.0): a *vendor-neutral
  authorization for AI agents* that "checks every agent action — an MCP tool
  call, an agent-to-agent invoke, a tool call inside a guardrail — against a
  policy engine before it runs and blocks the ones that aren't allowed.
  Fail-closed, works with OPA/Cedar/OpenFGA." That is this proposal's spine
  shipped as a library.
- **AuthZEN**: the emerging standard **PDP API** — the wire format between the
  enforcement point (PEP) and the decision engine (PDP). It is literally
  bdo's "gateway operation talks to policy" interface, standardized.
- **Policy engines named**: OPA/Rego, Cedar, OpenFGA — all usable as the PDP.
- **Consensus default is fail-CLOSED** for agent authz.

*Honest caveat (grounding, not census):* the research window was thin — X and
Hacker News returned nothing, public Reddit 403'd (keyless RSS carried it), and
one self-promoting OSS post (apparitor) is the central artifact. Treat this as
strong corroboration of the *pattern*, not a market survey.

## What ontum already has (the pieces, currently unmapped)

| Role | What it is | Where it lives today |
|------|-----------|----------------------|
| **PEP** — enforce at the tool seam | intercept a tool call, apply the verdict | `command_guard.py`, `write_guard.py`, `freeze_guard.py`, `ask_guard.py`; the rendered `.codex/` layer |
| **PDP** — decide | given an action + context, allow/deny | `fence/policy.py` (the static rule registry), `loop/inference.py` (runtime RBAC gateway: **default-deny** on `(caller, surface, mind)`), `disposer.py`'s fence |
| **PIP** — supply context | who/where/what-config | `loop/trust.py` (user authority = rungs), surface (Claude vs Codex render), location (worktree/dir), config (`.pen.json` / `settings.json` / fence registry), bounded inference (the inference-as-composition layer) |

**Honest state:** the pieces exist but are **not unified into one spine**.
`command_guard` already derives its deny-list from `fence/policy.py` at runtime
(done-line 0029) — it is the **one proven PEP→PDP link**. `write_guard`,
`freeze_guard`, and `ask_guard` are still bespoke hooks with their decision
logic inlined.

## The central decision: the fail-mode tier

This is the whole ballgame, and the research sharpens it: the field defaults
**fail-closed**; ontum's guards **fail-open** (a broken guard never blocks
work). These do not reconcile by hand-waving. The proposed resolution is a
**two-tier** model:

- **Bright-line rules** — e.g. `freeze_guard` ("a frozen done-line cannot be
  edited, *no owner exception*", bdo's own design). These fail **CLOSED**,
  deterministic, no inference, like the field.
- **Contextual / graduated policy** — where surface + user + location +
  bounded inference legitimately derive the decision. These fail **OPEN** so a
  broken sensor never blocks the worker.
- **Inference may only NARROW within deterministic bounds, never widen** (the
  `disposer.py` fence shape; the *bounded* in inference-as-composition).
  Inference never derives a bright-line decision.

Conflating the two tiers — routing a bright line through inference-derived
policy — is how an absolute stops being absolute. The tier is non-negotiable.

## ontum's differentiator over apparitor / AuthZEN

The field's PEP/PDP is **RBAC/ABAC** — who-can-do-what. ontum adds the layer
they do not have: **governance = authority + attribution** (the session-gateway
insight). Every decision is an **append-only record with provenance**, and
**no one signs their own line**. So ontum's PDP does not just *decide* — it
*decides-and-records-with-attribution*. The spine is auditable by construction,
not as a bolt-on. That is the thing worth keeping native even if the PEP/PDP
shape is borrowed.

## The work-queue dimension (bdo's 5th, 2026-06-18)

The spine is not only a gatekeeper. Agents also **surface a queue of work to be
processed based on policy** — `loop/gaps.py` already surfaces pressure-ordered
work; the spine governs *which agent-class may take which work*. This connects
to the **design-conversation skill** (the session-gateway for talk): a bounded
conversation **compiles into a policy-governed work queue** — talk becomes
governed work, not alignment theater. It also lines up with the gateway-economy
(gate → gateway → patrol → actuator, the contribution economy). The governance
of *who may take what* overlaps `loop/trust.py` rungs and `loop/gaps.py`; the
spine should **spec that seam, not double-build it** (§10).

## ask_guard as the worked first-migration (bdo's pick)

`ask_guard.py`'s `shape_problems()` is already a **pure function** (input: the
questions; output: the violations). That *is* a PDP policy, embedded in a hook.
The migration:

1. The hook becomes a **thin PEP**: intercept the `AskUserQuestion`, gather
   context, call the PDP, enforce the verdict.
2. `shape_problems()` becomes a **policy record** the PDP evaluates; the rules
   (R1/R2/R7 in `policy.md`) become policy data citing the registry.
3. Result: the **first guard born policy-native** instead of bespoke-hook #5.

It is the safe first-mover: **low blast radius** (it gates *my* asks — not bdo,
not landing), pure logic, already written. Note the honest split discovered
while building it: **R7 (the comprehension-checklist rule) is a judgment rule,
not a deterministic deny** — the guard cannot tell a design ask from a simple
one without false-denying, so R7 lives in policy + the audit fold, the guard's
hard teeth stay on the floor. That split is itself an instance of this tier.

## The open decision (left for bdo — the "study-first" output)

| | Adopt the AuthZEN PEP/PDP split | Native ontum spine |
|--|--|--|
| Interop | OPA/Cedar/OpenFGA/AuthZEN PDPs usable | none |
| Standard | rides where the field is standardizing | diverges |
| Cost | a wire format + mapping to learn | reinvent what is standardizing |
| Provenance | must wrap AuthZEN to add append-only/attribution | native |

**Recommendation (not a decision):** adopt the **PEP/PDP/PIP shape** and the
AuthZEN wire for the *contextual tier*; keep ontum's **two-tier failure** and
**provenance** layer on top. But this is bdo's to settle — that is what
"study-first" reserves.

## §10 — teeth, non-examples, open holes

**Teeth:** a bright-line rule routed through the spine must still fail CLOSED
and refuse with no exception — test: freeze a done-line, attempt an edit *via
the spine*, expect denial (exactly as `freeze_guard` does today).

**Non-examples:** inference deriving a bright-line decision (softening
`freeze_guard`); a unified spine that makes every guard fail the *same* way
(loses the tier); a PDP with no attribution (loses ontum's edge); double-building
`fence` / `inference` / `trust` instead of composing them.

**Open holes:**
- **OH1** — Does AuthZEN's model carry attribution/append-only, or must ontum
  wrap it? (the provenance differentiator's feasibility)
- **OH2** — The **PIP contract**: exactly what context every decision receives
  (surface, rung, location, config, inference budget).
- **OH3** — Migration order after `ask_guard`: `command_guard` is already
  half-there; `write_guard`/`freeze_guard` follow; the bright-line `freeze_guard`
  proves the closed tier.
- **OH4** — The work-queue governance seam vs `loop/trust.py` + `loop/gaps.py`
  (spec, don't double-build).

## What this proposal does NOT do

It does not rush the safety layer into inference (the worst place for
nondeterminism); it does not double-build the existing fence/inference/trust
organs; and it does not decide adopt-vs-native — that stays bdo's.

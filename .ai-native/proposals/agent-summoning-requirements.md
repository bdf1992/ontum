# Agent summoning & environment — requirements capture

**Status:** captured, not built (bdo, 2026-06-22: *"at least capture the
requirements and refinements needed to meet the explicit and implied
requirements and to add features on top"*). A requirements ledger in the shape
of [`administrator-requirements.md`](administrator-requirements.md); its home is
[`authoring-platform.proposal.md`](authoring-platform.proposal.md) (the single
surface that ties the agent/environment story together).

## The frame (one line)

An agent must be summoned **not with a flat text string but as a governed,
composed working environment** — *prompt-as-code + the prompt's requirements +
the code path that delivers it + infra-as-code for its environment +
observability + auth* — and the loop spends these agents as utensils to **fill a
volume** (the setpoint, widened). We define the volume, the expectations, and the
rewards and consequences; we do **not** define the model.

## The triggering gap (why this is captured now)

The tend workflows (`.claude/workflows/tend*.js`, this session) summon a subagent
with **one hand-typed paragraph + an output schema and nothing else** — no
versioned prompt, no fingerprint, no requirements check, no composed environment,
no receipt, no auth. The spawn guard flagged it verbatim: *"an unbranded spawn …
if it fills a node, brand it `ontum-node:<id>` so the rail pins the prompt and
checks the rung."* The infrastructure to summon an agent **right** is already
written down and partly built — the workers went around it with strings. This
ledger is the delta between what is written and what is real, plus what to add.

Legend: **status** = `met` (real on the trunk) · `partial` (specified/partly
built, with a named hole) · `missing` (named, not built).

---

## A. Explicit requirements — already written down

| id | requirement | written where | status | the hole |
|---|---|---|---|---|
| **R1** | **Prompt-as-code.** A prompt is versioned source (`.ai-native/nodes/<id>.md`), delivered with its `sha256`, and that hash is recorded on the receipt (`prompt_hash`) — every verdict attributable to the exact prompt. | doctrine §7; done-line 0009; `loop/summon.py`, `loop/node.py` | partial | only the **node/gate** path uses it; **workflow/subagent** prompts are ungoverned inline strings. |
| **R2** | **Prompt requirements (the edges).** A prompt MUST declare its role · what it reads · what it returns (one verdict from the seam's terminal set) · what it won't do (D-2) · the evals that back it. | doctrine §5, §7:340; the `nodes/*.md` instances; `tests/test_prompts.py` | partial | no **validator** enforces the edges at summon; a prompt missing an edge is not refused. |
| **R3** | **The code path (the spawn rail).** `summon` hands prompt+hash → `node` writes the receipt (idempotent I-2, terminal-set checked, no self-judge D-2, admitted-real I-8) → `gate` launches the real mortal mind → `trust` checks the rung first. | `loop/summon.py`, `loop/node.py`, `.claude/skills/gate/gate.py`, `loop/trust.py`; doctrine §16 | partial | the rail is **node-shaped only**; the **Workflow-tool** spawn path does not enter it. |
| **R4** | **Infra-as-code (the composed environment).** A node's briefing is assembled *on arrival* from the stack of environment files along its path (`CLAUDE.md` `@`-imports, glob-scoped, nested) — *"move it and it's a different program."* | doctrine §8, §16; done-line 0010; `environments.proposal.md`; the `CLAUDE.md` surfaces | partial | composition is for **human/session** context; a **spawned subagent** gets no composed environment, only the string. |
| **R5** | **Observability.** Receipts carry `prompt_hash`; `activity.py` accounts every wired hook (collects/uses/where/witnessed); digest · census · heal · gaps are the eyes; pressure is visible field-state on the log. | doctrine §14, §15; `loop/activity.py`, `loop/digest.py`, `loop/census.py`, `loop/heal.py` | partial | **workflow agent runs leave no receipt** — they vanish; their work is unwitnessed and uncounted. |
| **R6** | **Auth (the three A's).** A trust ladder (`permits(class, capability)`, cumulative, `ontum-touch` locked) + a default-deny inference gateway (`(caller, surface, mind) → permit/refuse`) gate what an agent class may read/judge/author; a session is born authenticated · authorized · attributed. | `loop/trust.py`, `loop/inference.py`; `gateway-policy-spine.proposal.md`; `session-gateway.proposal.md` §5 | partial | the **rung check is on the gate launch only**; workflow subagents are spawned with **no class, no rung check, no policy**. |

---

## B. Implied requirements — needed, not yet spelled out

| id | requirement | implied by | status |
|---|---|---|---|
| **R7** | **The summon is multi-channel, not text-only.** A prompt should compose its environment across every channel — **code examples** (behavior guidance), **diagrams** (workflow understanding), **documentation**, **named utilities** — not one prose blob (bdo, 2026-06-22). | §16 "the place is the program"; bdo's correction | missing |
| **R8** | **One rail for every agent.** The Workflow-tool subagent path and the §7 node path must be the **same** governed rail — branding, prompt+hash, rung check, receipt — so no agent runs off-record. | R1+R3+R5+R6; the spawn-guard nudge | missing |
| **R9** | **Prompts are generated from the frame, not hand-authored.** An agent's prompt+environment should be **composed** from its role + the section it works + the targets it fills — honoring *"we don't define the model."* | the volume frame; "generative relationships, not the model" | missing |
| **R10** | **The prompt's requirements are checked before it runs** (a prompt-requirements gate: edges declared, eval owed) — the §10 teeth applied to prompts themselves. | R2; §10 (the gate must be able to refuse) | missing |
| **R11** | **An agent's environment is reproducible** — snapshot-able and attributable, so a run can be replayed and audited (the environment is an acceptance unit, like a deploy snapshot). | `environments.proposal.md` (snapshot = acceptance unit) | partial |

---

## C. Refinements — to meet the explicit + implied requirements

These close the delta above. Each is a buildable piece, propose-grain; the cut stays bdo's (D-4).

- **C1 — Re-found the tenders on the rail (R1·R3·R8).** Lift each tend agent's inline prompt into a versioned `.ai-native/nodes/<id>.md` with its declared edges; summon it branded `ontum-node:<id>`, delivered with its hash, rung-checked; record a receipt carrying `prompt_hash`. The proof piece: do this for **one** tender first.
- **C2 — An environment composer (R4·R7).** A utility that, given a role + section + targets, assembles the agent's working environment — the prompt, the relevant `CLAUDE.md` surfaces, code examples, the workflow diagram, the named utilities/pens — into the summon. The summon becomes a *workshop*, not a sticky note.
- **C3 — A prompt-requirements validator (R2·R10).** A checker (sibling of `loop/phrasing.py`'s door) that refuses a node prompt missing role/reads/returns/won't-do, and flags an eval owed — non-vacuous (a fabricated edge-less prompt is caught).
- **C4 — Bridge the Workflow spawn to the rail (R8).** The `agent()` call routes through the summon/brand/rung path instead of a bare string; an off-rail spawn is surfaced, not silent.
- **C5 — Auth the workflow agents (R6).** A spawned subagent carries a class and is rung-checked through `trust.permits` / `inference.authorize`; default-deny.
- **C6 — Receipt every agent run (R5).** A workflow agent's run leaves a witnessed receipt (sibling of `tool-use.jsonl` / the gate run-trace) — so its work counts on the record and toward the volume.
- **C7 — Environment composer = `envoy.py`, re-pointed (R7·C2).** Reuse the envoy pen's existing ≤10-file bundle composer (arc + Mermaid/ASCII visuals + code + tests + docs + history) to assemble an agent's working environment instead of authoring it — composition, not invention. Re-point it at a node, not an external reviewer.
- **C8 — Agent registry = `herald.py` (R8·C5).** Register every spawned agent through the herald's `introduce` (it mints a content-hash credential at the trust-ladder floor); `roster`/`reputation` then make every agent known and its standing a fold over its acts — one rail, every agent branded.

---

## D. Features on top — new capabilities to add

- **D1 — Prompt-with-environment (R7·C2).** The multi-channel summon as a first-class capability: code examples + diagrams + docs + utilities travel with the prompt.
- **D2 — The volume scoreboard + the loop that fills it.** `loop/volume.py` (built this session, §10-tested) declares the volume as admitted dimensions (no baked numbers/items), measures actual-vs-target, and signals under/at/over. **Next:** the slow loop infers a resting target per dimension and the fast loop heats/cools each by the environment state — the thermostat widened from one dial to the whole body.
- **D3 — The one open-ended loop (the Administrator / conductor).** One standing loop with access to everything, an open-ended goal (*"keep the loop moving — finish what's safe, hand bdo only what's truly his"*), that picks work across all sections and spends workflows/subagents — **on the rail** — as its hands. (`/administer`, `loop/fleet.py` exist as the by-hand form + the eyes.)
- **D4 — Generative composition (R9).** The loop composes each agent's prompt+environment from the frame rather than a human authoring it — the "we don't define the model" principle, realized.
- **D5 — The regimen.** A declared cadence/rhythm the loop follows (the daily volume targets, the owner-report beat) — the expectations side of the setpoint.

---

## E. The composition map — nothing imagined, only repo parts wired

Every requirement above is reachable by **composing parts that already exist on
the trunk** (verified 2026-06-22). This is the composer's inventory — each line a
real module/pen/skill, none invented:

**The rail (R1·R2·R3 — prompt-as-code + edges + code path)**
- `.ai-native/nodes/*.md` — the versioned prompt files (the form to copy).
- `loop/reconcile.node_prompt()` — loads a prompt with its `sha256` (the hash channel).
- `loop/summon.py` — delivers prompt+hash to the summoned agent.
- `loop/node.py judge` — the one pen that writes the receipt with `prompt_hash`; idempotent (I-2), terminal-set + no-self-judge (D-2) + admitted-real (I-8) checked.
- `.claude/skills/gate/gate.py` — **already composes** (node prompt + atom + epic + prior receipts) and launches a real mortal mind on the rail, refusing via `trust.permits` (`launch_refusal`). To re-found a tender (C1/C4): a tend agent runs **gate-shaped**, not as a bare `agent()` string.
- `tests/test_prompts.py` — the eval home for R2.

**The environment (R4·R7·C2 — composed, multi-channel)**
- `CLAUDE.md` `@`-imports + nested `CLAUDE.md` — the text/doc surface that already assembles a per-place briefing.
- `.claude/skills/envoy/envoy.py` — **already composes a ≤10-file bundle: arc + Mermaid/ASCII visuals + code + tests + documentation + history.** This *is* the multi-channel environment composer (R7).
- `glyphs/viewer.html`, `causality/canvas.html`, the `diagrams/` work — the diagram channel.
- `docs/` + the `*/CLAUDE.md` files — the documentation channel.
- `.claude/skills/*` — the named-utility channel (the tools on the bench).

**Auth (R6·C5·C8 — who may, and who is this agent)**
- `loop/trust.py permits()` + `loop/node.py admit-rung` — the rung check (gate.py already calls it).
- `loop/inference.py authorize()` — the default-deny `(caller, surface, mind)` gateway.
- `loop/herald.py` — **already registers agents** (`introduce` mints a content-hash credential at the trust floor; `roster`/`reputation` fold standing from acts) — the registry for "one rail, every agent known."

**Observability (R5·C6 — every run on the record)**
- receipts carry `prompt_hash` — a node run is already witnessed.
- `loop/activity.py` + `.claude/activity-register.json` — the form for "declare what a collector does."
- `loop/fleet.py` — **already folds every Conductor/Workflow across sessions** (the runtime witness for workflow agents; the D3 eyes).
- `digest` · `census` · `heal` · `gaps` · `retro` — the sensor folds that read the record.
- `loop/volume.py` (built) — counts agent acts toward the volume (`owner_acts`, `verdicts_written`, `merges_landed` are live; add an `agent_runs` measure once C6 receipts exist).

**The validator (C3 — teeth on prompts)**
- `loop/phrasing.py` + `tests/test_phrasing.py` — the door pattern to copy: prove a property, refuse otherwise, non-vacuous test. A prompt-requirements door is the same shape over the §5/§7 edges.

**The frame the prompts generate from (R9·D4)**
- `loop/section.py` (built) — the role/queue an agent is summoned to.
- `loop/volume.py` (built) — the targets it fills.
- `loop/orchestrate.py` + `slowloop.py` + `disposer.py` — the thermostat (heat/cool; propose/dispose within an admitted fence). Generalize its one dial to the volume's dimensions (D2).

**The conductor (D3 — already by-hand)**
- `/administer` skill + `loop/fleet.py` — run many workflows, watch the agent-network by their work, bounded by the admitted concurrency dial.

**The honest read:** no requirement here needs a part that does not exist. The
delta is **wiring** (C1–C8) — routing the off-rail `agent()` string through the
rail (`gate`-shaped), the environment through `envoy`, the identity through
`herald`, the teeth through a `phrasing`-shaped door — not new infrastructure.

## Where it stands

- **Built this session:** `loop/section.py` (the work queues), `loop/volume.py` (the scoreboard, D2 half), the tend workflows (off-rail — the gap C1–C6 closes).
- **Already real (to build on):** the node/gate spawn rail (R1·R3), the trust ladder + inference gateway (R6), the composition surfaces (R4), the sensor folds (R5), `loop/fleet.py` + `/administer` (D3 by-hand).
- **The recommended first cut:** **C1 + C3** — re-found one tender as a real node (versioned prompt, summoned on the rail, receipted) and stand up the prompt-requirements validator that guards it. One agent done the written-down way, with teeth, before the rest follow.

_No code changes are made by this file; it is the captured ledger. The builds it
names are separate pieces, each bdo's to steer (D-4)._

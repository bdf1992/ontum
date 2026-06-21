# Change management — the blueprint bundle (PROPOSED)

> Status: **PROPOSED** — a blueprint for bdo to address, authored 2026-06-20 at
> his request (GitHub #348). This is the *bundle*, not an increment: full shape →
> categorized → labelled with descriptions → a fixed generative concept-list →
> calls-to-action against a purpose. Nothing here is built. It is the structure
> we would decide *before* building, and the process by which findings, work, and
> decisions move on-path.

## DECISIONS (bdo, 2026-06-20 — chat stamp, "all yes")

This bundle is no longer all-PROPOSED. bdo's calls, on the record:

- **CTA-3 — YES.** *Blueprint-before-build* is now a **hard rule** in
  [CLAUDE.md](../../CLAUDE.md) (Hard rules) — the standing instruction #348 asked for.
- **CTA-2 — YES.** A blueprint becomes a **first-class, digest-visible record**.
  This is itself a non-trivial build, so — dogfooding CTA-3 — it graduates to
  **`epic.change-management`** and is built *under* the new rule, not rushed now.
- **#247 — YES.** *The owner's stamp is portable* is now a **hard rule** in
  CLAUDE.md; #245 stays the mechanism (the build).
- **#294 micro-stamps — DECLINED (moot).** The C19/RegisterFacet amendment is
  absent from the current `display-system.md` (restructured); Commons-v1 was homed
  by the merged #174. Both retired.
- **Anthology — reaffirmed BLESSED** (`anthology.self-governing-loop`); #296/#297
  resolved (the bless is recorded; `loop/anthology.py` is a later build).
- **CTA-7 (consequence-policy primitive) — ENDORSED as its own arc**, not blocking
  the above. Graduates separately when bdo opens it.

Remaining session-buildable under `epic.change-management` (awaiting bdo's
`confirm-arc`): CTA-1 (close the `prompt`-parity fence hole — the raw-`gh` hole
#348 leaked through, the enforcement precondition), then CTA-4 (lightweight
finding-capture pen) and CTA-2 (the first-class blueprint record).

## The why (the target reframe)

A session under throughput-pressure reaches for the **fastest path to a visible
result**. That single reflex produced both failures this surfaced from:

- it **skips the blueprint** (rushed `epic.diagram` wave 1 to main instead of
  agreeing the structure first), and
- it **reaches around the paved pens** (opened GitHub #348 with raw `gh`, not
  through the reflect pen).

Same root: **optimizing for a shipped result, not for durable foundation.**
Change management is the discipline that makes the *right* path the path of
**least resistance** — so a pressured session doesn't reach raw, and foundation
work counts as progress.

The purpose every CTA below serves: **ontum's foundation compounds across mortal
sessions; the on-path move is the easy move; bdo steers structure, not cleanup.**

## The full shape — seven seams a thing can move through

Everything a session produces is one of: a *finding*, a *decision*, a *unit of
work*, or a *blueprint*. Each needs an on-path home. Today some have one, some
don't, and where there's no easy on-path home the fast path is raw — the hole.

```
  finding ─► [C1 capture] ─► decision ─► [C2 target/value] ─► bdo
     │                                         │
     ▼                                         ▼
  work ─► [C3 scope/bond] ─► atom ─► pipeline ─► land
     ▲                                         
  blueprint ─► [C4 first-class?] ─► [C5 pressure?] ─► [C6 change-absorption]
                         (all three: MISSING today)
  everywhere: [C7 fast-path alignment] — is on-path the path of least resistance?
```

## The categories (label · description · today · the gap)

**C1 — The capture seam.** *How a finding (a bug, gap, friction, soft-tooth)
enters the system on-path mid-session.*
- Today: owner-asks ride `report needs-you → reflect pen → GitHub`; buildable
  findings become an atom. Both are *end-of-session* or *heavyweight*.
- Gap: a finding *noticed mid-session* has **no lightweight on-path capture**, so
  the fast path is raw `gh issue` — and B (below) means the guard doesn't even
  stop it. The capture seam is where #348 leaked.

**C2 — The target / value seam.** *How bdo's direction and decisions are
surfaced and made.*
- Today: `report needs-you → reflect` (owner-ask issues #293–306); or
  `AskUserQuestion` in-session.
- Gap: works, but the *target itself* (what a session optimizes for) was never an
  explicit, steerable record — finding **A** is the first time it was named.

**C3 — The scope seam (the bond).** *How a unit of work's boundary is decided —
where one atom ends and the next begins.*
- Today: **judgment only.** "Can these be value-judged apart?" is applied in a
  head, never measured. The epic's piece-list proposes a decomposition; the
  building session silently overrides it (diagram: 3 pieces → 1 atom).
- Gap: no instrument reads the bond; nothing flags an over- or under-scoped atom.

**C4 — The blueprint seam.** *How foundation/structure work is recognized and
tracked, built BEFORE features.* — **the core gap.**
- Today: blueprints live as `*.proposal.md` files. They are **invisible to the
  metabolism**: no id-pressure, no digest line, no pipeline. A proposal that
  should precede ten atoms shows up as *nothing*.
- Gap: foundation is not a first-class record. So the system can't tell a session
  "blueprint this arc before building" and can't show bdo a blueprint as progress.

**C5 — The metabolism re-weighting.** *How the digest / pressure folds reward
foundation, not just landed throughput.*
- Today: the digest, gaps, and `epic.landing-throughput-response` all reward
  **landing**. Foundation work scores zero.
- Gap: the metabolism *structurally reinforces the wrong target* — it pulls every
  session toward shipping. Fixing the human-level bias (A) without re-weighting
  here just fights the current.

**C6 — The change-absorption seam.** *How structure versions and supersedes over
time without re-deriving — the fold grain applied to the design itself.*
- Today: atoms version by content-hash; done-lines supersede only by bdo. Bundles
  have no versioning story at all.
- Gap: a blueprint that grows across sessions has no defined way to change while
  keeping its history — the very thing "change management" names.

**C7 — The fast-path alignment principle.** *The meta-rule that ties the rest
together: the on-path move must be the path of least resistance.*
- A pen must be **faster** than raw, or it gets bypassed.
- Foundation must be **as visible** as shipping, or it gets skipped.
- The guard must **actually enforce**, or the rule is theatre — which is exactly
  **B**: `command_guard` enforces only `decision=="forbidden"`, so every
  `prompt`-decision fence rule (incl. `gh-issue-mutate`) is a silent no-op on the
  Claude surface. Parity is structural for `forbidden`, absent for `prompt`.

## The fixed generative concept-list (what to ponder)

1. Is a *blueprint* a first-class record (sibling of atom / epic / done), with its
   own id-pressure and digest line? (C4 + C5)
2. What is the lightest on-path *capture* that beats raw `gh`? (C1 + C7)
3. Should the *target a session optimizes for* be an explicit, admitted record bdo
   can set? (C2 + A)
4. Is the *scope bond* worth an instrument, or just named doctrine? (C3)
5. How does a blueprint *change* without losing its history? (C6)
6. What makes on-path the path of least resistance, per seam? (C7)
7. Does "blueprint-before-build for a non-trivial arc" become a hard rule? (C4)

## Calls to action (against the purpose)

| # | CTA | Kind | Serves |
|---|-----|------|--------|
| CTA-1 | Fix **B**: make `command_guard` enforce `prompt`-decision rules (real ask/confirm path) or convert them to `forbidden`. Close the raw-`gh` hole. | session-fixable atom | C7 |
| CTA-2 | Make the **blueprint a first-class record type** with its own pressure + digest line, so foundation is visible progress. | bdo decides → build | C4, C5 |
| CTA-3 | Write **blueprint-before-build** into doctrine/CLAUDE.md as a hard rule for non-trivial arcs. | bdo's stamp | C4 |
| CTA-4 | A lightweight **on-path finding-capture** pen so a mid-session finding never reaches raw. | build | C1 |
| CTA-5 | Make the **scope/bond** explicit doctrine (atom-as-cell), optionally a sensor. | bdo decides → build | C3 |
| CTA-6 | Re-cut **`epic.diagram` structure-first** (plane → boundaries → composition → attribute-model → snap) as the worked example. | build | the instance |

## Whose move

- **bdo decides** (target/value, not a session's to set): CTA-2, CTA-3, CTA-5, and
  the disposition of #348 (a session won't raw-close it — same denied verb).
- **Session-buildable** once a decision points the way: CTA-1, CTA-4, CTA-6.

## Worked inputs

- **A** — target misalignment (sessions optimize shipped results; bdo wants
  blueprint-first foundation + change management). GitHub #348.
- **B** — the `prompt`-parity fence hole that let A's symptom (raw `gh issue`)
  through. `fence/policy.py:270` (`gh-issue-mutate`, `decision:"prompt"`) vs
  `command_guard._deny_rules()` loading only `forbidden`.
- **#348** — the worked failure example: a finding that reached GitHub off-path
  because C1 had no easy on-path home and C7/B didn't stop it.

---

# The deeper primitive — consequence policy over action policy (bdo, 2026-06-20)

*This is the governance model the bundle above should rest on. It is C6
(change-absorption) given a primitive, and the per-directory gateway stack that
C7 implies. Captured faithfully from bdo's thesis; ontum's existing organs are
wired in at the end (compose, don't rebuild — §10).*

> **The key move.** *Action policy controls what an agent is allowed to **do**.
> Consequence policy controls what the world is allowed to **become** after the
> agent acts.*

This is the better primitive for an AI-native system because **AI actions are too
many, too fluid, and too context-dependent to enumerate safely** — but
consequences can be watched, scored, bounded, repaired, routed, escalated, or
forbidden. Action policy assumes the important thing is the *move*; consequence
policy assumes the important thing is the **world-after-the-move**. An agent may
take a thousand individually-harmless actions that are collectively dangerous, or
one weird action that is perfectly fine because its consequence is bounded,
reversible, and witnessed. So the platform does not ask first *"Is this action
allowed?"* — it asks: *"What consequence class could this create, where could it
propagate, and what guard / gateway / repair loop must surround it?"*

## The chain — Root → Cause → Effect → Consequence → Obligation

```text
Root:        latent structure   — why this kind of thing can happen
Cause:       active trigger     — what made it happen here
Effect:      local delta        — what changed directly
Consequence: environmental meaning — what that change means in the surrounding system
Obligation:  required next motion  — what must now happen because the consequence exists
```

- **Root** is the condition-space — the deeper arrangement that makes a class of
  thing likely/possible/inevitable (missing owner, ambiguous authority, weak
  coverage, unbounded permission, no rollback path, stale context, no consequence
  observer). **Root is where prevention lives**; it is substrate diagnosis, not
  blame.
- **Cause** is the triggering mechanism that turns root potential into change
  (agent merged PR / edited prompt / changed schema / summarized stale context as
  truth). **Cause is where attribution lives** — traceability without pretending a
  human authored every action.
- **Effect** is the direct delta — the observable difference *before*
  interpretation (file changed, test failed, node advanced, memory updated). It
  needs logs, diffs, checksums, timestamps, witnesses, replay.
- **Consequence** is the meaning of an effect inside its surrounding system — the
  crown concept, **where governance should live**.
- **Obligation** is the operational turn (the fifth term): what the consequence
  *requires* next.

> **Effect belongs to the action; consequence belongs to the environment.** An
> effect is local. A consequence is relational.

```text
Action:      AI deletes a file.
Effect:      File no longer exists.
Consequence: Build fails, audit trail breaks, owner loses trust, rollback required.
```

The consequence is not "delete happened" — it is how the deletion is *absorbed*
by the repo, tests, people, permissions, dependencies, history, and future work.
So consequence is not just a later effect:

```text
Consequence = effect + receiver + surrounding state + policy
            + time + propagation + reversibility + value judgment
```

## Consequence → Obligation (what makes it executable)

A consequence-native system turns consequences into obligations:
**`consequence detected → obligation generated`**.

```text
Consequence: test coverage dropped        → Obligation: require guard review before merge
Consequence: user-facing claim changed    → Obligation: require citation or owner approval
Consequence: canonical prompt changed     → Obligation: version, diff, changelog, regression test
Consequence: agent created ambiguity      → Obligation: route to owner inbox
Consequence: local fix affects a contract → Obligation: open gateway review
```

Every consequence carries at least six fields — **Effect, Receiver, Environment,
Propagation, Valence, Obligation** — and the last matters most: it is what turns a
descriptive consequence into an operational one.

## The policy object

```yaml
consequence_policy:
  name: canonical_prompt_change
  watches:
    effects: [prompt_modified, system_instruction_modified, agent_role_modified]
  surrounding:
    artifact_status: [canonical, active, inherited]
    dependency_count: "> 0"
  consequence_class: [behavioral_drift, regression_risk, authority_change]
  required_obligations:
    - create_version_diff
    - run_prompt_regression
    - notify_owner
    - block_auto_merge_until_reviewed
  reversibility:
    required: true
    rollback_artifact: previous_prompt_version
  escalation:
    gateway: prompt_governance
    guard: invariant_fidelity
```

That is not action control. The agent is not told *"don't edit prompts."* It is
told: *"any edit to a canonical prompt creates behavioral-drift consequence; that
consequence requires versioning, regression, notification, and gateway review."*

## Consequence is graph-native (the relationship mesh)

A consequence is not a point — it is a mapped relation across the mesh:

```text
actor ──causes──► effect ──lands on──► receiver ──depends on──► other nodes
policy ──classifies──► consequence ──creates──► obligation ──routes to──► guard/gateway/owner/agent
```

**This is exactly ontum's existing structure.** The incidence graph the
[platform-brokerage.proposal.md](platform-brokerage.proposal.md) already names —
`serves` / `touches` / `hands_off_to` / `must_not_collide_with` — **is** the
propagation/receiver mesh: `touches` names the receivers, `hands_off_to` names
where a change travels next, `must_not_collide_with` is a consequence forbidden in
advance. Consequence policy is graph-native, and **ontum already holds the graph**
(the holon-graph). Evaluating a consequence = walking the incidence edges from the
effect to its receivers and classifying what it satisfies or violates.

## Working definition (the keeper)

> A consequence is an effect interpreted by its surrounding system, over time,
> according to what it changes, threatens, enables, obligates, or propagates.

Tighter:

> **Consequence is environmental meaning made operational.**

## The sharp version

What this builds is not "AI with rules." It is **an AI-native consequence mesh
where agents are allowed to act inside environments that classify the
world-after-action and generate obligations from that classification.** The
system needn't predefine every allowed behavior; it defines: *what changes matter,
where they land, what they threaten or enable, who receives them, whether they
reverse, what policy class they enter, what obligation they create, who guards the
gateway.* That is how the platform stays self-driving without being
**action-lawyered to death**.

```text
Root → Cause → Effect → Consequence → Obligation → Policy → Next Action
```

# The per-directory gateway stack (the governance apparatus)

bdo, 2026-06-20: **each directory can carry its own governance stack, and the
whole apparatus at a directory's seam is the *gateway*.**

```text
1. Fences     — the firm denials (the fence/policy.py deny-list)
2. Policy     — the graded decision (PDP: reversibility × uncertainty)
3. Guards     — protect a privileged resource; access is authorized
4. Gate       — decide pass/deny on a thing flowing through
5. Threshold  — the limit / cap / bar (how much, when — the setpoint caps)
6. Patrols    — the witness ("the patrol sees you"; reads-witnessed)
```

**guard vs gate (a term-economy fix).** A **gate** decides pass/deny on a *thing
flowing through* it — stateless, about the flow. A **guard** protects a
*privileged resource*: getting in is an *authorized* act, because the thing behind
it is special. The repo's existing `*_guard` hooks (`write_guard`, `freeze_guard`,
`command_guard`, `change_guard`) are actually **gates** — "guard" is **overloaded**
(the split `causality/term_economy.py` exists to flag). A true *root guard* means
root is the **constitutional namespace**: landing a file there is an authorized
act, not a session default.

**The four the stack still needs (the acting half).** The six above are the
*gatekeeping* half — deny / decide / protect / limit / watch. A gateway also needs:

- **The pen (actuator) — the door.** The authorized *doing*. A gateway *routes* a
  raw act into its governed form (raw git → the git pen), it does not only refuse;
  §13.10's economy ends in `actuator`. A gateway with no pen is all wall, no door.
- **The ledger (PIP) — the floor.** The truth-source policy decides *against* and
  the patrol witnesses *into*: the log as truth (git merge-tree, never GitHub).
- **Heal — the recovery.** Every primitive above is a tooth; teeth with no healing
  is autoimmunity (`heal.py`). The appeal/counterforce that can see the gateway
  bite *wrong*.
- **Authentication — the credential (the third A).** `guard` is *authorize* (may
  you), `patrol` is *audit* (you were seen), but *authenticate* (who are you — the
  credential, the branded spawn rail, the trust rung) is the missing first A.

```text
authN (credential) → fence · policy · guard · gate · threshold (gatekeeping)
                   → pen (act) → patrol (witness) → ledger (truth/record) → heal (recover)
the whole apparatus at a directory's seam = the GATEWAY
```

# How this lands on the bundle (compose, do not double-build — §10)

- **It is C6 and the engine under C7.** Consequence policy *is* how a change is
  absorbed by the surrounding system — the C6 (change-absorption) seam given a
  model. C7 (fast-path) sharpens to: the governed path is the one that *classifies
  the consequence and discharges the obligation* — which raw cannot do, so on-path
  becomes the only path that satisfies the system.
- **Obligation is the fifth bundle term:** *Root creates possibility · Cause
  creates motion · Effect creates difference · Consequence creates obligation.*
- **ontum already holds the parts under other names:**
  - `heal.py` is the **consequence-repair** organ (a tooth that bit wrong = a bad
    consequence detected) — the stack's `heal`.
  - the digest's **divergences** are consequences (two locally-fine records that
    *refuse to fit*).
  - `gaps.py` already turns surfaced state into the next move — the **obligation
    generator** in embryo.
  - the **incidence graph** is the propagation mesh consequence policy walks.
  - `epic.model-free-mode-response`'s **consequence-gate** (PR #343) is the *first
    built instance* of consequence-over-action policy — this section is the
    general frame it instances, **not** a rebuild.

## CTAs (the consequence layer)

| # | CTA | Kind | Serves |
|---|-----|------|--------|
| CTA-7 | Adopt **consequence policy over action policy** as the platform's governance primitive (the C6 model); name **Obligation** the fifth term. | bdo's stamp (doctrine) | C6, C7 |
| CTA-8 | Define the **per-directory gateway stack** (the 10 primitives) as the change-management apparatus; fix the `guard`/`gate` overload on the record. | bdo decides → build | C6 |
| CTA-9 | Wire the **consequence mesh to the incidence graph** — evaluate a consequence by walking `touches`/`hands_off_to` from the effect to its receivers (composes the holon-graph facet of the platform-brokerage blueprint). | build | C6 |

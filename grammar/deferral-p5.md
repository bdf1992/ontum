# P5 — CI/CD + environment controls · DEFERRED build blueprint

**Status:** PROPOSED — a deferred-partition blueprint, not a build. P5 is
ranked behind P1 (spec particle) and P4 (spec SDLC); this file keeps the
deferred work from being dropped (per [plan.md](plan.md) §"Deferral plans").
A session's only move here is to propose; bdo names arcs (D-4). No code is
written by this document.

**Frame:** P5 extends enforcement from the single existing GitHub Action to a
graded set of CI gates, and makes session-birth environment controls real. It
*serves* what P1–P4 produce — it does not author particles, it gates them.

---

## 1. Purpose

P5 makes one thing true: **every actor — a hooked session, the web UI, the
API, Codex, bdo's phone — meets the same enforcement, and a session is bound to
a governed environment at birth instead of inferring it from a shared HEAD.**
Today enforcement is split and partial: client-side fences bind only a hooked
session's tool calls (`.claude/hooks/command_guard.py`, derived from
`fence/policy.py`), and the lone server-side gate
(`.github/workflows/atom-invariant.yml`) checks only the atom invariant. P5
closes that gap on two axes — *CI/CD* (more server-side gates, equal for all
actors) and *environment controls* (the session gateway, bind-at-birth) — so
"did this go through the machinery" is answerable on GitHub for every kind of
work-particle (atom and, post-P1, spec), and a branch collision in the shared
worktree becomes structurally impossible.

## 2. Scope — the concrete pieces

### (a) CI/CD beyond `atom-invariant`

The existing gate is the template: on every PR to main it runs the PR pen's own
audit over the PR's range — `pr.py audit --range BASE HEAD --pr N`
(`atom-invariant.yml:31-36`), the *same* `loop.pr_audit` pure check the
client-side pen uses, so server and client can never drift
(`.github/CLAUDE.md`, "the enforcer port"). P5 adds siblings on that pattern:

- **Test automation** — a workflow that runs the unittest suite
  (`python -m unittest discover -s tests -v`, the `loop/CLAUDE.md` pre-push
  command) on every PR, red-and-blocking on a failure. The suite already exists
  and is the merge-node's green-before-land precondition (`fence/policy.py`
  `git-push` justification: "the suite is green (or declared red)"); P5 moves
  that check from "the session ran it" to "GitHub ran it for every actor."
- **A spec-soundness gate in CI** *(gated on P1)* — the server-side mirror of
  P1's spec gate: a workflow that runs the spec audit verb (P1's
  `pr.py audit`-sibling for the `spec` particle) so a PR touching a `spec` is
  red until that spec carries its soundness receipt — the atom-invariant shape
  applied to the new particle.
- **A code-review gate** — the structural teeth the root `CLAUDE.md` already
  names ("a code-review gate in the pipeline whose receipt the merge-node
  requires before landing, reviewed by an independent spawn-rail node escalating
  to cloud `/code-review ultra` for high-blast-radius changes"). Until it is
  real, review is requisitioned via the `code-review` skill; P5 makes the
  receipt a *required* check the merge-node folds before landing — built on the
  real-gate machinery (`.claude/skills/gate/gate.py`, the mortal-judge pen;
  `loop/placement_gate.py` for the deterministic-gate shape).
- **Eventual multi-env promotion** *(last, gated on P1+P4)* — once specs+atoms
  compose an SDLC (P4), a promotion workflow moves a confirmed body of work
  across named environments. Deferred hardest: there is nothing to promote
  until the lifecycle stages exist (plan.md §P5 "Why deferred").

The provider-agnostic seam stays: each `.yml` is a thin leaf adapter over the
enforcer port (`pr.py audit --range`, exit non-zero on a violation). The
**enforcement-surface registry** named as a deliberate hole in `.github/CLAUDE.md`
(an admitted `enforcement_surface` record, kind × address, folded like reflect's
surfaces) becomes real *only* when a second provider/consumer is real — P5 does
not invent it ahead of need (the "absence is information" hard rule).

### (b) Environment controls

- **Session-gateway bind-at-birth** — the unrealized half. Today the session
  gateway is only PROPOSED (`.ai-native/proposals/session-gateway.proposal.md`,
  issue #534): a session reads HEAD from a shared mutable global and a parallel
  session can switch it underneath (proposal §1–2). P5 makes the gateway real
  along its own suggested-increment ladder (proposal §11): (1) **HEAD-intent
  guard** in the git pen — pins the intended branch at first write, refuses a
  commit when HEAD moved (the "sheath," ships smallest); (2) **claim↔workspace
  binding** — an attributed `workspace_claimed` admission, no commit without a
  binding for this HEAD (proposal §10.4, §12b); (3) **the gateway fold** —
  compose `trust` + `policy` + provisioning-sufficiency, level-triggered on the
  summon pulse, silent until a deficit (proposal §5); (4) **provisioning pen +
  gardener reclaim** — issue a worktree on a code claim, guarantee the route
  home (no orphans, proposal §3).
- **The existing fence/guards as the floor** — not rebuilt, depended on. The
  family-neutral registry (`fence/policy.py`) compiled into both surfaces at
  runtime (`command_guard.py` `_deny_rules`), plus `write_guard.py` (a file
  lands only under a governing CLAUDE.md / as a pen carbon copy) and
  `freeze_guard.py` (a frozen done-line is immutable). P5's environment controls
  sit *above* this floor: the gateway issues a binding; the guards keep being the
  deterministic refusals every actor meets.

## 3. Dependencies / unblock condition

P5 starts only when both upstream partitions exist (plan.md §P5 "Unblocked when"):

- **P1 — the spec gate** must exist, so the CI spec-soundness gate has a verb to
  invoke (a `pr.py audit`-sibling for the `spec` particle, exit-non-zero on an
  unsound spec). Without it the spec-gate CTA has nothing to run.
- **P4 — the spec lifecycle** must define the stages CI enforces, so multi-env
  promotion has named draft→review→version→supersede transitions to gate.

What each CI check would invoke (all already-existing or P1/P4 verbs):
- atom invariant → `pr.py audit --range BASE HEAD` (exists, `atom-invariant.yml`)
- test automation → `python -m unittest discover -s tests -v` (exists)
- spec soundness → P1's spec-audit verb (build, P1)
- code review → a real gate's receipt via `gate.py` / the `code-review` skill
- promotion → P4 lifecycle-stage transition verbs (build, P4)

The session-gateway track (2b) is **independent of P1/P4** — it can start the
moment bdo confirms its arc (#534), since its increments reuse only parts on
disk today (proposal §9: `inference.py`, `trust.py`, the claim signal, the git
pen, the summon hook).

## 4. Build CTAs (ordered, categorized)

**Category A — CI gates (each a thin `.yml` over an existing/P1 enforcer port):**
- **CTA-A1 · Test-suite workflow.** Add `.github/workflows/test-suite.yml`
  running `python -m unittest discover -s tests -v` on PR to main; red-blocking.
  Reuses: the `atom-invariant.yml` skeleton; the suite. *No P1/P4 dependency —
  the first buildable increment.*
- **CTA-A2 · Spec-soundness workflow** *(needs P1)*. Mirror `atom-invariant.yml`
  over P1's spec-audit verb. Reuses: the enforcer-port pattern (`.github/CLAUDE.md`).
- **CTA-A3 · Code-review gate receipt.** Make the `code-review` skill's verdict a
  logged gate receipt the merge-node requires before landing. Reuses: `gate.py`
  (mortal judge), the spawn rail, `loop.node judge` (the one pen).
- **CTA-A4 · Multi-env promotion** *(needs P1+P4)*. A promotion workflow over P4
  lifecycle transitions. Last and most deferred.

**Category B — Session gateway (proposal §11 ladder, smallest-first):**
- **CTA-B1 · HEAD-intent guard** in the git pen (proposal §11.1) — ships now,
  catches the exact branch-collision bug, pure git-pen change.
- **CTA-B2 · Claim↔workspace binding** + git-pen enforcement (proposal §11.2) —
  the `workspace_claimed` admission; no commit without a binding for this HEAD.
- **CTA-B3 · The gateway fold** (proposal §11.3) — compose trust+policy+
  provisioning; the summon hook routes the pulse, emits the deficit line.
- **CTA-B4 · Provisioning pen + gardener reclaim** (proposal §11.4) — worktree
  on a code claim, guaranteed route home.

**Category C — Owner gestures (D-4, not session builds):**
- **CTA-C1 · Mark CI checks required** in branch protection + turn off the bare
  merge button — the one tap that turns each gate from *visible* to *impossible*
  (`.github/CLAUDE.md` "What stays bdo's"). Stays bdo's for every A-track gate.
- **CTA-C2 · Confirm the session-gateway arc** (#534) — unblocks all of track B.

## 5. Pickup — the exact first move

A future session opening P5 starts here:

1. **Read** [plan.md](plan.md) (the partition + unblock order) and
   `.ai-native/proposals/session-gateway.proposal.md` (the gateway design, #534).
2. **Check the unblock condition:** does P1's spec gate exist on main yet?
   - *If P1 has landed* → the CI track is unblocked; first increment is **CTA-A1**
     (test-suite workflow), the one A-track CTA with no P1/P4 dependency, then
     **CTA-A2** (spec gate). Copy `atom-invariant.yml`'s shape; cite the enforcer
     port.
   - *If P1 has not landed* → do not start the CI spec gate. The session-gateway
     track (B) is independent: if bdo has confirmed the arc (#534), first
     increment is **CTA-B1** (HEAD-intent guard in the git pen). If not, surface
     the confirm gesture (CTA-C2) as `needs-you` and pick a P1/P4 piece instead.
3. **Write the done-line first** (`python -m loop.pen new done`, §9.4) for the
   chosen increment, then build the one increment — no second one until the first
   carries a passing receipt (the "no receipt, no version bump" rule).

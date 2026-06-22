# The workflow-authoring wrapper — a branded, governed paved-path over the native AI-workflow surface (PROPOSED)

> **Status: PROPOSED** — bdo's direction, 2026-06-21 (this conversation), his to
> steer. This is the **account** bdo asked for: a single, named, tracked
> sequence. **Framing corrected (bdo, 2026-06-21): this is not "interim
> scaffolding" — it is a branded wrapper on a surface**, the same shape as the
> git pen wrapping `git` and the PR pen wrapping `gh`.

## The direction, in bdo's words

> *"I think I want to use workspaces/codespaces and tree and workflows (native
> AI) until we have a live place ready. And I want agents to help author them and
> an interface to review them. Work on all in a named sequence and account for
> it."* … *"Not interim, a branded wrapper on a surface."*

## What it is (the corrected frame)

The **surface** already exists and stays: GitHub Codespaces/workspaces, git
worktrees, and the native Workflow orchestration. We are not building a
temporary stand-in for a future portal — we are building the **branded wrapper**
over that surface: the durable, governed paved-path through which workflows are
**authored, reviewed, run, and recorded**. This is exactly the pen pattern the
repo already lives by:

| The surface (exists) | Its branded wrapper (this arc) | The pen it mirrors |
|---|---|---|
| native Workflow orchestration | `/author-workflow` — draft + the draft check | git pen (`git.py`) over `git` |
| a drafted workflow | the review interface — render + arm | PR pen (`pr.py`) over `gh` |
| worktree / Codespace | the run rail — isolated launch + receipt | the spawn rail over `claude` |

A raw, ungoverned workflow launched ad-hoc is the un-paved path; the wrapper is
the branded one — it governs the act and **writes it to the log**, so authoring
an agent over the work is a fact the loop can fold, never a side effect that
vanished. **The served portal, when it comes, *presents* this wrapper — it does
not replace it.** The wrapper is the substrate; the portal is a face on it.

## The named sequence (the wrapper, in five pieces)

Each piece is a self-contained slice that lands on its own. Names are stable
handles so progress tracks against them.

| # | Name | What it produces | Mirrors |
|---|------|------------------|---------|
| **A1** | **Ground** | The home (`.claude/workflows/`, the native launch dir) + naming/safety convention, with **one worked example** that runs. | the pen's land |
| **A2** | **Author** | `/author-workflow`: plain description → a drafted Workflow script, **refused if malformed** by a deterministic check (`lint.py`). | `git.py` branded `add`/`commit` |
| **A3** | **Review** | The review interface: a draft rendered as *what it does · phases · blast radius · riskiest step*, with an **arm** act recorded on the log. | `pr.py` (open/land + receipt) |
| **A4** | **Run** | The isolated run rail: launch an **armed** workflow in a worktree/Codespace, receipted — refuses an unarmed or mutated-since-arm workflow. | the spawn rail |
| **A5** | **Account** | The sequence, each authored workflow, and each run are **on the record and digest-visible** — accounting made structural. | the log + `digest` |

Linear dependency: A1 homes it, A2 drafts, A3 arms, A4 runs only the armed, A5
makes it all visible. A4 (the highest-blast-radius step) is built **last**,
after the arm gate (A3) exists — never before. Identity is **content hash**
(the repo's invariant): arming binds to the workflow's bytes, so editing a
workflow un-arms it and it must be reviewed again.

## Status (built so far)

- ✅ **A1 — Ground.** [`.claude/workflows/`](../../.claude/workflows/) with its
  convention and a read-only worked example,
  [`subsystem-map.js`](../../.claude/workflows/subsystem-map.js).
- ✅ **A2 — Author.** The [`author-workflow`](../../.claude/skills/author-workflow/SKILL.md)
  skill + [`lint.py`](../../.claude/skills/author-workflow/lint.py), with §10
  teeth (`tests/test_workflow_lint.py`): the real example passes, every
  fabricated defect is refused, mutation is flagged.
- ◐ **A3–A5** — in progress / pending.

## The one stamp that's bdo's

**Graduate this to a confirmed arc, `epic.workflow-authoring`**, with A1–A5 as
its pieces. On that stamp, each step becomes a piece/atom on the log — which *is*
"account for it" made structural (A5 becomes how the arc is tracked, not a
separate step). Until then this proposal is the account and the sequence is
tracked here + in the session todo. The substrate choice (Codespaces + worktrees
+ native Workflow) is recorded as bdo's direction, not re-asked.

## Composition note (§10)

This rides [`authoring-platform.proposal.md`](authoring-platform.proposal.md) as
the **concrete, buildable wrapper** under that vision's umbrella — the paved-path
you author on. It does not re-derive that proposal's Administrator/Conductor tier
model; the risk-tiered authority dial named there is what A4 will eventually
compose to run **unattended**. Until that dial exists, the wrapper requires an
**arm before every run** (A3) — unattended launching is explicitly out of scope.

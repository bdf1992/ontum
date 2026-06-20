# RepoPrompt CE — Context Engineering as a Reviewable Handoff

*Source entry: a working tool that treats "what context reaches the model"
as a first-class, human-reviewable act. Filed for the days we question
whether the envoy surface and the loop's handoffs are over-engineered — this
is an independent project that arrived at the same instinct: assemble
intentional context, let a human inspect it, then hand it off.*

---

## 0. The source

**RepoPrompt CE (Community Edition)** — <https://github.com/repoprompt/repoprompt-ce>
Surveyed by bdo, 2026-06-17. Read-only context, not material (this
directory's law): the loop must not import, vendor, or build from it. A
source justifies a direction; it does not specify a build.

Self-description, verbatim: *"A free, open-source native macOS app and agent
orchestrator for context engineering."*

A native macOS workspace (Swift-first; bundles an MCP server and a developer
daemon) whose job is to help coding agents understand a codebase by
**assembling precise, human-reviewable context before it reaches a model or
CLI agent.** It coordinates multi-agent workflows from one interface, with
app-managed git worktrees.

---

## 1. What the source says

The claim, stated plainly: the bottleneck in working with capable models on
real codebases is not the model — it is **which bytes you put in front of
it**, and that choice deserves to be a deliberate, inspectable act rather
than a black box.

Its mechanisms:

- **Context engineering over data volume.** Agents first *explore* a repo and
  identify what actually matters, then assemble that — file trees, CodeMaps,
  repository structure, git diffs — into a dense prompt within a token
  budget. Focused intentional context, not "stuff everything in."
- **Reviewable handoffs.** Before context goes to another model or agent, a
  human can inspect and refine the selection. The handoff is a seam you can
  see, not an opaque pipe.
- **Agent orchestration with managed worktrees.** It runs and coordinates
  CLI-backed coding agents, each in an app-managed worktree.
- **MCP as the connective tissue.** A bundled MCP server connects external
  MCP-compatible tools to the repository's context.
- **Multi-root workspaces.** Related repos and documentation folders are
  unified into one working surface.

Its philosophy, as it states it: transparent, controllable agent workflows
rather than black-box automation.

---

## 2. Why it is aligned

It is the same instinct as ontum's, arrived at independently — which is
exactly why it belongs in this directory rather than the codebase. Several
of its moves rhyme with surfaces we already have, and a few point at ones we
do not:

- **The envoy is a reviewable handoff.** `exports/` already packages the repo
  as a sealed ≤10-file bundle with a disclosure receipt — context engineered
  for an outside model, made inspectable and on-the-record. RepoPrompt makes
  the *selection itself* the reviewable artifact, continuously, not just at
  seal time. That is the same seam from the other end.
- **Compress-to-enrich, not compress-to-fit.** "Focused intentional context
  over data volume" is the same principle as the Causality story-demo's
  glyph compression (the glyph is the compression, savings reinvested into
  relationships). RepoPrompt is the codebase-context instance of it.
- **App-managed worktrees** echo the loop's branch ritual and the merge-node's
  isolation discipline — orchestration that keeps each agent's work bounded.
- **Multi-root workspaces** rhyme with a session's own additional working
  directories (ontum + odysseus + holonsearch) and `field.py --all`.
- **The experience read:** its native, human-reviewable UI is a working
  example of the "experience-first, no-compromise surface" standard for an
  *inspect-before-handoff* interaction — a reference for what a
  context-review surface can feel like, not a skin to copy.

The divergence worth keeping in view (§10 instinct): RepoPrompt is a **local
app a human drives**; ontum is a **mortal-session loop where the files are
the operator** and handoffs are governed by gates and receipts, not a UI a
person sits in front of. Where it makes the human the curator, ontum makes
the *log* the curator and the human the last stop (D-4). Same problem,
opposite center of gravity — that contrast is the useful part.

---

## 3. The direction it points

When the work drifts toward treating context as plumbing — "just dump the
files in" — this is the source that says the selection is the craft, and the
handoff deserves to be seen. It points at: making the envoy's context
selection more inspectable; treating "what reaches a gate / a model" as an
auditable fold like everything else here; and, on the experience side, a
context-review surface as a candidate Pattern Commons entry rather than an
afterthought.

It does not specify any of these. It justifies the direction; the build, if
it ever comes, is the loop's — through atoms, receipts, and bdo's stamp.

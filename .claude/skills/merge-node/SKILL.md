---
name: merge-node
description: >
  The merge-node — the independent agent that lands confirmed-arc PRs on main,
  so bdo never merges. Run it as a fresh session that did NOT author the PRs it
  lands. Use when there are open PRs to main whose arcs bdo has confirmed, when
  asked to "land the confirmed work", "merge what's ready", or to run the
  merge-node. bdo's amendment, 2026-06-11: he confirms arcs and reads the
  digest; agents do the merging.
version: 0.1.1
---

<!-- changelog 0.1.1 (done-line 0052): the land examples say the v1 seat
     (merge-node.claude.v1) — the id issue #82 admits and the land pen's
     unadmitted-signer refusal names; v0 is the superseded stage side. The
     seat's contract is now versioned source: .ai-native/nodes/merge-node.claude.v1.md -->


# The Merge-Node

bdo amended `bdo merges` (2026-06-11, with feeling): doing PR merges by hand
became performative. He keeps two surfaces — **confirming arcs** and reading
the **daily arc digest** — and an independent **merge-node** does the
mechanical landing. This skill is that node.

## The one invariant — read before anything

**No one signs their own line (D-4).** The merge-node lands a PR it did
**not** author. Run this skill as a *fresh session* whose job is only landing
— never the session that wrote the work, never bdo. The enforceable guard is
bdo's **arc confirmation**: an independent human stamp authorizes the land,
the node only *executes* it. A node propels work; it never authorizes it. If
you authored a PR in this session, you may not land it — summon a different
session.

## What it does NOT do

- It does not authorize value. bdo's `confirm-arc` is the authorization; this
  lands only arcs he confirmed.
- It does not route bdo into anything. **Never** tell bdo a PR is "at the
  stamp," never ask him to merge. A refusal surfaces in the digest, not to him.
- It does not land its own author's work, a draft, a red PR, an unwritten
  story, a conflict, or an unconfirmed arc. The pen refuses all of these by
  default.

## The ritual

1. **See what's landable.** Read the field, all read-only:
   ```sh
   python -m loop.merge                       # land-readiness per arc (the eyes)
   gh pr list --state open --base main --json number,title,headRefName,isDraft
   python .claude/skills/branch-ritual/pr.py check   # unwritten stories
   ```
   `loop.merge` tells you which arcs bdo confirmed and which are complete; only
   a confirmed arc can land.

2. **Decide, then land — one PR at a time.** For each open, non-draft PR to
   main whose arc bdo has confirmed, dry-run first, then land:
   ```sh
   python .claude/skills/branch-ritual/pr.py land <n> --epic <epic-id> \
       --by merge-node.claude.v1 --dry-run
   python .claude/skills/branch-ritual/pr.py land <n> --epic <epic-id> \
       --by merge-node.claude.v1
   ```
   The seat's contract is its versioned prompt,
   `.ai-native/nodes/merge-node.claude.v1.md` (§7) — read it before landing;
   the land pen refuses a `--by` the trunk's admissions never named
   (done-line 0049), so until bdo's realness gesture admits the seat, every
   land is a refusal and that freeze is the architecture working.
   The pen reads bdo's confirmation from the **trunk** (`main`), checks the PR
   is green, written, non-draft, non-conflicting, and based on main, then
   lands with `gh pr merge --squash`. It does **not** pass
   `--delete-branch`; branch cleanup belongs to GitHub's
   `delete_branch_on_merge` setting and the SessionStart gardener. It records
   a merge receipt on the log citing the arc confirmation that authorized it.
   A refusal is a `report` — it names what was missing; leave that PR for when
   its arc is confirmed or its suite goes green.

3. **Stop when the confirmed arcs are landed.** What you could not land stays
   open as the unit it is. Do not escalate a refusal to bdo as a merge — it is
   already visible in his digest.

## Where the pieces live

- The hand: `pr.py land` (the gh pen, beside the branch-ritual SKILL). One pen
  per seam — the merge-node does not grow a second merge path.
- The eyes: `loop/merge.py` (`python -m loop.merge`) — read-only land-readiness.
- bdo's surfaces: `loop.node confirm-arc` (his stamp) and `python -m loop.digest`
  (what he reads daily).

## When the ritual is wrong

Like every ritual here, this is ours to sharpen. If landing fights the work,
change this file and `pr.py land` in the same PR (bump the version, changelog
the sharpening) — and that PR lands the way every other does: bdo confirms its
arc, a *different* merge-node session lands it.

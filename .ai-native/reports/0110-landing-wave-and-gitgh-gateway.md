# Report 0103 — The landing wave + the git/gh gateway design

## What landed

**The PR backlog, cleared.** bdo asked the open-PR stack be landed by headless
Claude (not by him clicking merge) and not made his bottleneck. 12 PRs landed
through the merge-node this session — #240, #237, #238, #224, #223, #230, #225,
#207, #226, #204, #233, #220 — plus 3 by the herald lander running in parallel
(#222, #234, #242). #207 deployed the Causality experience live via Pages.

**A landmine fixed.** #230 shipped CI-green with a `ValueError` in the shared
`cmd_land` path (`_range_atom_facts` returns 3 values, the new code unpacked 2);
landing it would have crashed *every* future land. Caught by the merge-node's
dry-run, not the gate (the §10 untested-land-path gap). Fixed + regression test
(`tests/test_merge_land.py`).

**Two arcs confirmed on bdo's authorization** (his "continue yes"):
`epic.landing-throughput-response` (adm.b6a6c293745e) and `epic.repoprompt-parity`
(adm.e96e5650de81) — via `pr.py confirm --from-ref` for the epic-introducing-PR
deadlock (#245). These unblocked #226 and #204.

**The git/gh gateway design — captured and landed** (#282, rcp.merge.282):
`git-gh-gateway.proposal.md`. git/gh is the last ungoverned major seam (every
other — thinking, node-acts, writes, tools — is a gateway); the pens trust
GitHub as an authority, which is the hole every landing-wave friction traced to
(spurious `mergeable=CONFLICTING`, the untested land path, the races). The
shape: PEP (pens) / PDP (reversibility×uncertainty) / PIP (truth from
`git merge-tree`, GitHub as a reflection — D-13 generalized) / audit. bdo's
load-bearing asymmetry, verbatim: *"you can see through the gate, but the patrol
sees you"* → writes authorized, reads witnessed (one-way glass, no read-ACLs,
teeth at egress). Grounded in `fence/policy.py`, which already encodes the
asymmetry at the command surface and goes silent inside the pens.

## needs-you

Nothing from this session is on bdo — the arcs were confirmed, the work landed.
Held by design: #153 (digital-experience, a deliberate rolling draft).

The one named next increment (a session's, not bdo's): **build the git/gh
gateway's first organ** — relocate `pr.py:743`'s `mergeable` check to answer
"is this landable?" from `git merge-tree`, receipt every land, run the drainer
through it. Fixes the spurious-CONFLICTING jam, the #230 untested-land-path
class, and the races in one slice.

Minor housekeeping debt left in the viewport (low-stakes, the garden flags it):
a few unlanded session reports + screenshots stranded across the shared worktree.

## End-state

`report` — backlog cleared (12+3 landed), the #230 landmine fixed, the git/gh
gateway design landed (#282); the first organ is the named next build.

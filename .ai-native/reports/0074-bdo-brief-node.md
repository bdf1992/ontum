# Report 0074 — The bdo-brief node — owner-bound work as a cited inference construct, folded over bulk

## What landed

**Done-line 0104 — the bdo-brief node.** PR #185, atom-backed (atom.bdo-brief-node.v0), judged `accept` by an independent value-gate (value-gate.claude.v1, rcp.b09950fa24ff). Full suite green (845).

bdo's correction, 2026-06-17: "Can we stop putting things on me?" A "what's on you" list — even a minimal, cold-read one — is still a queue. He wants, when a session needs him, an **inference construct** to set beside his own read (context weighed + cited → recommendation + the reasoning that produced it → the one divergence seam), a peer's argument that opens a shared space to discuss; and over bulk a **digest fold**, not N briefs.

`loop/brief.py` is that node — a read-only fold, two zoom levels:
- **over bulk** (default) → a digest grouped by arc, naming only the few that need his read; N pieces under one arc fold to ONE group.
- **drill in** (`--item <id>`) → the item's inference construct: considered context (each line cited to a receipt/epic/atom), the recommendation derived from those records with its reasoning, and the divergence seam.

It composes the existing folds (`orchestrate.next_action`, `reconcile.arc_confirmation`/`load_epics`) and never re-folds them. The §10 teeth (tests/test_brief.py, proven live): a discharged or loop-carried item does NOT surface; an uncited recommendation is refused (a fabricated citation is caught); the digest aggregates, not 1:1-echoes. Proof it is not a renamed inbox: pointed at atom.field-topology.v0 (passed four gates), it recommends "hold — amend or retire," cited off the later value-confirm `missed` receipt.

v0 recommendations are deterministic reads over the records; the inference plane enriching them is a named later slot. Two fleet done-line id collisions (0100→0101 last session's pattern recurred: 0103→0104) forced two atom re-versions and re-judges this session — the id-collision tax is real and recurring (see continuing pressure).

## needs-you

**Nothing is on you to act on.** PR #185 is merge-node-eligible after epic.owner-harness is confirmed; landing is the merge-node's. The two open items from earlier this session — PR #183 (govern-seam) and the optional arc/seam naming gesture — stand as they were, neither newly pressing.

(This is the last "needs-you" written as prose. Once #185 lands, this section *is* what `python -m loop.brief` renders — folded, cited, drillable.)

## End-state

`report` — PR #185 open and merge-node-eligible after arc confirmation; done-line 0104 met; the bdo-brief node is the structural form of "give me an argument to compare, not a ticket," with a digest over bulk. Recurring friction surfaced: fleet done-line id collisions cost two re-versions this session — the git-blind `pen new` vs git-aware `git.py commit` gap (memory: ontum-fleet-id-collisions) is worth closing.

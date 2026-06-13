# Report 0050 — the inbound envoy seam is built: a foreign review lands as queued atoms, and first light routes the real one

## What landed

Done-line 0059 is met. The envoy was one-way — `new → plan → build →
check → seal → list`, all outbound — so a foreign reviewer's response
had nowhere to land as *work*; it stranded in read-only `docs/sources/`
(context, not material) or as report prose the queue never sees. That
is retro 0037 one layer up: a review hand-carried into a doc is the
loop running *beside* the work, not through it.

The return leg now exists: **`envoy respond <package>`**
([envoy.py](../../.claude/skills/envoy/envoy.py)). A foreign review
lands as value-gated atoms on the log — each finding an atom file under
a single *proposed* arc, so one `confirm-arc` gesture queues the whole
review (bdo confirms arcs, not pieces; never N owner-stamps). It carries
provenance back to the package and the seal receipt it answers, and
appends a `response_received` receipt to the disclosure ledger —
symmetry with `seal`. No new fold machinery: the atoms enter the
existing auto-announce → real value-gate → `gaps` pipeline.

**§10 teeth, proven by test** (5 new tests in
[test_envoy.py](../../tests/test_envoy.py), 4 of them refusals): a
response to a package **never sealed** refuses (you cannot receive a
response to something never sent); a finding whose atom would **collide**
with existing atom bytes refuses (editing an atom restarts its pipeline —
never clobber); malformed, empty, and duplicate-slug responses refuse.
Full suite green (580).

**First light** — the real review routed through it. The
qa-metabolism response (the v2 reviewer's six findings: the vanity-count
correction, mutation-honesty, dual-keying the handles, the two protected
deltas, the test-organ skill) is now six **proposed** atoms under
`epic.qa-metabolism-response`. The loop sees it: `loop.node arcs` lists
it as *"not confirmed — its pieces still reach your stamp."* The review
stopped being context and became queued work.

Also on this session's record, before the build: the **dependency rule
was lifted** repo-wide (bdo, 2026-06-12) from a blanket ban to a
common-sense, value-creating bar, with local-first (`no broker / daemon /
network at runtime`) kept whole — audited across every canonical home,
the descriptive module-purity facts deliberately left untouched
([report 0051](0051-envoy-response-comes-home.md)).

**Renumber on the record:** this work's done-line was born as 0057 and
renumbered to **0059** at commit — the git pen's record-id fence caught
cross-branch collisions on *both* 0057 and 0058
(`claude/owner-ask-must-surface` had already minted that run). The eight
content-addressed artifacts (the backing atom and the six response atoms
+ their epic) were already *born onto the log* citing 0057, so by
"history is never retro-invalidated" their bytes stand; the 0059
done-line carries a provenance note bridging them. The lesson, named not
buried: minting an id and birthing atoms onto the log *before* landing
baked an unstable id into frozen artifacts — id allocation should clear
the cross-branch fence before atoms cite it.

## needs-you

- **One gesture queues the whole review** (or declines it):
  `loop.node confirm-arc --epic epic.qa-metabolism-response --by bdo`.
  Decline retires the six findings; either way they are no longer
  hand-carried context.
- **The landing of this session's work is the open bookkeeping.** The
  pile is uncommitted on the viewport. Landing via the PR pen requires,
  by the repo's own atom-invariant, a backing atom with a real gate
  receipt — so the seam work should itself walk the gates as
  `atom.inbound-envoy-seam.v0` (an independent node judges its value;
  this session cannot sign its own line), then branch → PR → the
  merge-node lands. The non-bypass path, the same discipline this whole
  thread has been about.

## End-state

`report` — the inbound seam is built, tested with §10 teeth, and
demonstrated on the real review, which now waits as a proposed arc for
bdo's one gesture; the dependency rule is lifted and audited; nothing
committed yet, and the atom-backed landing is the named next step.

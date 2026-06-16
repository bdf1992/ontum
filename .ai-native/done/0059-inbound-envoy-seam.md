# Done-line 0059 — the inbound envoy seam — a foreign review lands as atoms, not context

Written before code, per §9.4. When this line is met, stop.

The envoy is one-way: its pen verbs (new → plan → build → check → seal →
list) all push outward, and the disclosure ledger records only what
left. So a foreign reviewer's response has nowhere to land as *work* —
it strands in read-only docs/sources/ (context, not material) or as
report prose the queue never sees. That is retro 0037 one layer up: a
review hand-carried into a doc is the loop running *beside* the work,
not through it. This line closes the return seam so a review becomes
queued, value-gated work like anything else.

> **Done when:** an envoy package's foreign response lands through one
> pen verb (`envoy respond <package>`) as value-gated atoms on the log
> — each finding written as an atom file in `.ai-native/atoms/` under a
> single *proposed* arc (so one `confirm-arc` gesture queues the whole
> review, never N owner-stamps), each carrying its provenance (the
> package it answers and that package's seal receipt on
> `exports/log.jsonl`) — so the existing auto-announce → real
> value-gate → `gaps` pipeline picks them up with no new fold
> machinery; and the seam has §10 teeth proven by test: a response to a
> package with **no seal receipt** on the disclosure ledger refuses
> (you cannot receive a response to something never sent), and a
> response whose atoms would collide with existing atom bytes refuses —
> a locally-fine response to an unsealed package is rejected, not
> filed.

Provenance: born as done-line 0057, renumbered to 0059 at commit after
the record-id fence found cross-branch collisions (claude/owner-ask-must-surface
had already minted 0057 and 0058). The atoms born under this contract —
atom.inbound-envoy-seam.v0 and the six qa-metabolism-response findings —
cite 0057, their immutable birth state on the log; history is never
retro-invalidated, so the citation stands and this note is the bridge.

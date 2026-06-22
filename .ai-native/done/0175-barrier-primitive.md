# Done-line 0175 — The barrier primitive, re-cut under epic.barriers (genus + nature attribute)

# Done-line 0175 — The barrier primitive, re-cut under epic.barriers (genus + nature attribute)

Written before code, per §9.4. When this line is met, stop.

> **Done when:** `fence/barrier.py` exists on current main as the **physical-nature
> barrier primitive** under the new genus epic **`epic.barriers`** (bdo's reframe,
> 2026-06-21: a barrier's nature — PHYSICAL gate/fence vs POLITICAL gateway — is an
> ATTRIBUTE, not the epic; do not scope the epic to "physical"). It is a pure,
> stdlib, actor-blind module providing: a **barrier-link** (`decide(link, act) ->
> {allow, reason}`, deny-list semantics, reading only the act's observable form —
> argv / command / path / object-flag — never the actor: L1 deterministic, L2
> model-free, L3 actor-blind), a **fence** (`validate_fence`/`covered`/`is_closed`:
> a closed loop of links around a territory, with the front/seam/top route taxonomy
> and the closed/barbed/not-opaque laws), and a **gate** (an `on_match=allow` link
> at a sanctioned opening). `epic.barriers.json` declares the genus (physical /
> political nature as the attribute) with `atom.barrier-primitive.v0` as its first
> piece. Proven by `tests/test_barrier.py` joining the suite (the §10 bite: an
> un-enumerated route class or an unbarbed/opaque link fails the whole fence —
> locally-fine links that refuse to close). The re-cut is REBASED onto current main
> (the prior work, the 59-commits-stale PR #358, is retired): the one real
> integration drift — the shared `fence.policy.prefix_matches` reads a position-
> union only as a tuple, but a JSON barrier-link carries a list — is bridged in
> `_predicate_matches`. Backed by `atom.barrier-primitive.v0` with an independent
> value-gate accept; the suite is green. The INSTALLED instance (sealing the live
> command_guard's shelled-git seam) is named as the next piece, NOT this one.

## Why

The gate/fence primitive is real, valuable work (bdo's gate/fence conversation,
memory ontum-gate-fence-primitive) but it stranded on PR #358 — 59 commits behind
main, with no `epic.physical-barriers.json` on disk (the epic-introducing-PR
deadlock) and a real conflict against the evolved guard. bdo's call when auditing
it: re-cut it fresh, and fix the epic name — `epic.barriers` with **nature as an
attribute**, not `epic.physical-barriers` scoping the genus to one of its values.
This lands the primitive clean under the right genus, beside the political-nature
gateways it names by the same grammar. The actual installation (wiring the seal
into the live command_guard) is security-sensitive and entangled with the
viewport-flip fence; it is a separate, careful increment, declared here as the
next piece rather than re-merged blind.

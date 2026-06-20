# Done-line 0121 — The claim-workspace binding — no commit without a branch bound to its work

Written before code, per §9.4. When this line is met, stop.

Increment #2 of the session-gateway arc (`session-gateway.proposal.md` §11,
fork §12b.4). Increment #1 (the HEAD-intent guard, done-line 0118) made the
session assert *which branch* it is on; this makes a branch belong to its
**work** — a `workspace_claimed` admission binds a branch to the durable
claim it serves (the atom/work-id), attributed `--by`, and the git pen
refuses a commit that asserts a claim the branch is not bound to. The branch
becomes the work's, not the mortal session's (§4): one active binding per
branch (a re-claim supersedes), released additively (the route-home seam;
full gardener reclaim is increment #4). Opt-in via `--claim`, exactly as
`--on` is opt-in, until a later chapter makes it the default once
provisioning (#3/#4) guarantees every workspace carries a binding.

The §10 teeth: a binding that can never refuse is a gauge, not a gate — so
the test that matters is the collision, *claiming `W` on a branch bound to a
different claim `W2` must refuse* (two locally-fine facts — "I'm doing work
W" and "this branch serves W2" — that must not fit). A fake `binding_refusal`
that always passes fails that test; one that always refuses fails the
matching-claim and omitted-`--claim` (backward-compatible) cases.

> **Done when:** `loop/workspace.py` folds `workspace_claimed`/`workspace_released` admissions into the active binding per branch (supersession-aware), exposes a pure `binding_refusal(branch, claim, bindings)` and `claim`/`release`/`list` verbs; the git pen's `commit --claim <work>` refuses an unbound branch and a branch bound to a different claim (and passes a matching one and an omitted `--claim`); `tests/test_workspace.py` proves the fold, the round-trip, and the collision bite; and the whole suite is green.

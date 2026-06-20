# Report 0115 — Envoy round-trip: the smart-mashing doctrine, corrected and built

## What landed

bdo dropped an external study artifact — the "smart mashing" doctrine, which
argues an autonomous process should be gated on the **consequence** of an act
(Reversible, Bounded, Observable, Learning), not on a whitelist of actions —
and asked for an envoy package to formalize around it. That package
(`exports/model-free-mode/`) placed the doctrine beside ontum's own ambient
machinery (the disposer fence, the command-guard, the gates) and went out
sealed for an outside model family to critique.

The review came home and did more than answer: it **corrected the doctrine**.
The model-free/model-based binary is wrong — the real spectrum is **raw →
relational → mechanistic**, and "smart mashing" is the **relational middle
band**: representation without mechanism (the hashing-for-meaning reframe bdo
raised mid-session — a locality-sensitive hash, not the avalanche hash ontum
uses for atom identity). It also reordered the invariants: because
reversibility, boundedness and learning-progress are all *computed from*
observable traces, **Observable is the substrate and gates first**. The review
landed through `envoy respond` as six proposed atoms under proposed
`epic.model-free-mode-response`.

bdo then asked whether many agents could build it in one pass. An 8-agent
workflow (4 build + 4 **adversarial** verify) built wave 1, each piece
verified by neutralizing its load-bearing check, confirming the test went red,
and restoring it byte-for-byte:

- `loop/observe.py` — the **Observable-as-gate**. Before an autonomous
  exploratory act runs it must declare actor/action/receipt/scope/attribution/
  rollback/probe, and HALTS if it cannot name the receipt path. Its kill-test
  runs the **real `command_guard`** as a subprocess and proves the
  consequence-gate refuses an act the action-gate allows — the doctrine's
  central claim, in a passing test.
- `loop/relation_ledger.py` — **relation-ledger.v0**: five record kinds and a
  fold reading per-bucket coherence as the learning-progress proxy (the rate
  buckets stabilize into predictive coherence, not raw surprise).
- `loop/over_containment.py` — the shared **T6/T7 over-containment**
  counter-test (predictive vs. trivially-stable).
- `language/relational-middle-band.md` + `causality/contracts/relation-organ-admission.md`
  — the doctrine correction as a stratum note, and the contract that keeps a
  learned organ log-native only if admitted with id/version/threshold/policy/scope.

34 new tests; full suite **1144 OK**. Landed as **PR #351**.

Separately, bdo named the pen/workstation problem the landing exposed. Diagnosis:
the git/PR pen's cross-root refusal (`git.py:506-522`) is **correct** — it is the
embryo of the workstation fence (#341/#346). The real gap is session *placement*
(nothing puts a worker in its own worktree), filed as **issue #349** routing to
that arc — not a pen fork.

## needs-you

1. **Confirm the arc** — `python -m loop.node confirm-arc --epic epic.model-free-mode-response --by bdo` — lands PR #351 (the merge-node) and queues all six review-finding atoms through the value-gate. One stamp.
2. **Issue #349 routing** — filed to the workstation arc (recommended); or say the word and I prototype the `loop.workspace ... --worktree` placement path instead.
3. **The sealed envoy package** (`exports/model-free-mode/`, hash `9ebfba99d332`) is send-ready to a *second* model family but has NOT been sent — sending is the outward act; name where it goes (or that it stays in-house).
4. **The mesh-over-a-duration question** (your earlier ask) is now buildable: `observe.py` is the kill-test substrate (a gate that can catch an act that *looked* free). Say if you want the bounded supervisory loop stood up.

Conflicts and honest flags (named, not silently resolved):
- **Done-line discipline.** §9.4 asks the done-line be written *before* the work; this wave came via orchestration and no done-line was minted — the work is recorded as the epic's atoms + this report. Wave 2 should write done-first.
- **Provenance gap.** The disclosure-ledger appends (the package's seal + respond) are stashed locally (`stash@{0}`/`{1}`), not committed, due to the viewport entanglement — recoverable, minor.
- **Pre-existing stranding.** The viewport arrived on `claude/activity-accounting-register` (21 commits, PR #339 since closed) with uncommitted activity work — a separate arc's concern, not resolved here. The viewport is restored to main as the closing step.

## End-state

`report` — PR #351 + issue #349 open; `epic.model-free-mode-response` awaits bdo's confirm-arc; full suite green at 1144; viewport restored to main.

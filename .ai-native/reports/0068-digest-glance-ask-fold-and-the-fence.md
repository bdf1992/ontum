# Report 0068 — Digest-as-glance, the owner-ask fold, and the slow loop's fence

**Date:** 2026-06-16
**Branches:** claude/digest-readable (PR #155), claude/auto-admit-fence (PR #163)

Three things, all from bdo steering.

## 1. The digest reads as a glance (done-line 0089, PR #155)
bdo opened the daily arc digest (#154) and named it "honestly hard to read and make gestures about." Two failures: it re-dumped all nine arcs' full prose + every atom every day, and it led with a paragraph-long divergence under a "these need you" banner over a refusal whose move is a session's rebuild. Fix is render-only (the fold and §10 teeth untouched): lead with **Your move** — a fold naming only unconfirmed arcs with built work, "nothing" when none; divergences kept but terse and ownership-marked; arcs collapsed to one tally line each. `tests/test_digest.py::TestGestureSurface` pins the contract (a confirmed arc with a refused piece yields a divergence AND an empty owner_gestures AND "Your move: nothing"). Saved as feedback memory: bdo's steering surfaces are a gesture-first glance, never a data dump.

## 2. The owner-ask flood, folded (16 → 1)
The reflect beat surfaced 6 `[owner-ask]` issues (#156–#161, 16 asks from reports 0054–0064) at once. Folded against the live log: **exactly one is a real decision** (the slow-loop dial disposition, report 0063). The rest were already satisfied (inference plane stood up — minds local.qwen3-14b/local.mistral + route + policy all `--by bdo`; epic.owner-harness confirmed adm.728a87a9ca48; PRs #114/#122/#147 merged; owner-ask mirror rule adm.bf0aa654739e) or were **session-work mis-parked on bdo** (fleet branch/id-collision cleanup — the loop's job, not a gesture).

## Findings — two owner-harness bugs (for a future session, not bdo)
- **The reflect mirror auto-closed #156–#161 with the wrong reason** — identical "this divergence pattern no longer appears in the digest" text, the divergence-close message bleeding into owner-ask closes. The owner-ask kind needs its own close transl: closing a surfaced ask should cite the discharge (done-line 0065) or the resolving record, not a divergence reconciliation.
- **The floor's per-report grain over-nags.** `unsurfaced_owner_ask_groups` keeps a whole report "live" when it bundles one settled ask with one still-open structural ask, so the machine screams about decided work. The discharge grain (done-line 0065) is per-group too, so a report mixing a done ask with an open one can't be cleanly discharged. Resolution wants per-*ask* granularity, or a "session-work, not an owner-ask" reclassification at the source (a report should not park fleet-hygiene on bdo at all — the hard rule).

## 3. The slow loop's bounded auto-admit fence (done-line 0091, PR #163)
bdo answered the disposition seam: **bounded auto-admit** (the arc-confirm shape). Built `loop/disposer.py` — an admitted `auto_admit_fence` (his one stamp, per-dial bounds), a pure `evaluate` (heating capped at the ceiling, cooling always allowed, an unnamed dial escalates, one breached key escalates the whole proposal — §10), and `dispose` (self-admit an in-fence proposal citing the fence as `authorized_by`, else leave it for bdo). The proposer stays read-only; the fence is the outside it left open. Inert until a fence is drawn. Named 'disposer' not 'fence' to avoid overloading the command-guard `fence/`. `tests/test_disposer.py` pins the teeth; full suite green (777).

## End-state
- **PR #155** (digest) — merge-node eligible under confirmed epic.owner-harness.
- **PR #163** (fence) — merge-node eligible under confirmed epic.substrate.
- Both land via the merge-node; neither authored by its lander.

## needs-you
- **Nothing blocking.** Both PRs land without you.
- **Optional, whenever you want it:** draw the fence so the slow loop starts moving its own dial — `python -m loop.disposer admit-fence --bounds '{"step_budget_per_tick":[2,5],"max_inflight_atoms":[4,12],"human_queue_cap":[1,3]}' --by bdo` (adjust the numbers to taste). Until then today's standing proposal (step_budget 3→4) stays a proposal.

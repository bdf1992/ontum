# Report 0114 — the value gate judges deterministically-composed policy facts

## What landed

bdo's principle this session: "Judgement should be non-deterministic but the data being judged should be compiled and composed from configuration and policy." And: amend the work to fit.

Answer to his question — the gate already had deterministic data (compose() folds the §7 node prompt, arc membership from the epic records, and prior receipts), with one gap: the atom's SELF-CLAIMS sat beside the composed truth, leaving reconciliation to the model's reading. That seam was exactly where the panel fault lived.

- **gate.py** (done-line 0146): `policy_facts(atom_id)` — a pure fold over the epic records and the admissions log composing the atom's arc membership (from the epics, never its self-claim), each arc's confirmed status (from the log), and a reconciliation of the atom's self-claimed `serves` vs policy (naming unbacked self-claims). `compose()` now renders a "composed policy facts (deterministic — judge these, not the atom's self-claims)" block, so every fact the judge weighs is config+policy-composed and judgment is the only non-deterministic step.
- **tests/test_gate_policy_facts.py** — §10 teeth (membership from the epic records; a self-claimed-but-unnamed epic resolves unbacked; confirmed/unconfirmed/withdrawn distinguished from the log; a constant fold fails). Full suite green.
- Backing review: **sonnet amend (rcp.19645ad89022)** — and the amend IS the amendment working: "value is real... what's missing is verifiable arc confirmation: arc_membership=[], serves_confirmed_arc=false." The gate now reads its own composed facts and flags the arc gap deterministically.

## needs-you

1. **One decision closes the whole gate-* series: attach it to an arc.** Every gate atom this session (rail-fix [landed #288], economy #324, panel #338, policy-facts) amends/escalates on the same composed fact — *serves no confirmed arc*, because no epic names them as pieces. This is your gesture: confirm an arc whose pieces name the gate-economy atoms (epic.the-field, or a new epic.gate-economy). The policy-facts amendment is what made this gap a clean, deterministic fact instead of a model's hunch — your principle, realized.
2. **Fault-deliberation layer (my recommendation, queued):** deliberate-then-escalate + devil's-advocate on unanimous (catches both split and all-wrong-together). Rides on top of the now-deterministic data. Not built; ready on your nod.

## End-state

`report` — policy-facts PR coming, atom-backed (sonnet amend rcp.19645ad89022), full suite green. The gate's judged data is now fully composed from config+policy; judgment is the only non-deterministic step (your principle). The gate-* series awaits one arc-confirmation gesture from you to land.

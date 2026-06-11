# Done-line 0045 — Value-confirm: the last gate judges delivery, and can say it missed

@
Written before code, per §9.4. When this line is met, stop.

> **Done when:** the L0-second-check (value-confirm) has an *inference* backing
> that can refuse. A versioned node prompt at
> `.ai-native/nodes/value-confirm.claude.v1.md` (§7, hashed onto every receipt)
> directs a summoned mind to judge one question — **did this atom deliver the
> value its story claimed, on the record?** — returning **`confirmed`** when the
> claimed value is realized and cited by evidence (receipts, admissions, the
> merge receipt, the changed surfaces), and **`missed`** when the piece passed
> every earlier gate yet the implementation did not become what the story
> promised (a claim/delivery gap). It is the *third kind* of real gate the arc
> needs: judgment at the end, where the value gate (first light) is judgment at
> the start and placement/handoff are law in the middle. Its contract is pinned
> by `tests/test_value_confirm_prompt.py` — both verdicts present so the gate
> *can* say no, `missed` in the seam's terminal set and distinct from the
> mock's fixed `confirmed`, delivery-not-value, evidence-not-say-so, the §10
> could-have-missed check, and arc-completion kept bdo's — and the full suite
> stays green. This is the per-piece "mind" half of bdo's "Both" decision
> (2026-06-11) and a piece of `atom.gates-enumerated.v0` under
> `epic.experience-layer`.

## Out of scope, named (its own next lines)

- **The `node_real` admission that makes it the live gate.** Realness is bdo's
  trust stamp, now a GitHub gesture via `realness-intake` (he closes the
  stage's realness-confirm issue; a session admits it `--by bdo`). This session
  builds and proves the backing; the first real `missed` on the live log is its
  first light, and follows his stamp.
- **The arc-completion surface** — the "you at arc-done" half of "Both": the
  fold that notices when a `confirmed` makes *every* piece of an epic confirmed
  and surfaces the complete arc to bdo. The prompt already instructs the mind to
  *say* an arc is complete; carrying that to bdo is a separable surface (a sibling
  of the reflect rail), its own line.
- **Semantic evals.** v1.0.0 ships the mechanics-and-contract test; whether the
  rubric actually catches a claim/delivery gap is owed with the next edit (§7).
@

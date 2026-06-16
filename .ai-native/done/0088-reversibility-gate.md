# Done-line 0088 — The reversibility line — autonomy on the reversible, a gesture on the irreversible

Written before code, per §9.4. When this line is met, stop.

> **Arc:** epic.digital-experience
> **Piece:** atom.reversibility-gate.v0
> **Probe:** P4 (the reversibility line)

Derived by the loop-maker from done-line 0087's braid. The safety spine of the
whole arc: it is how "so I don't have to worry about anything other than the real
world" is made safe without contradicting ontum's gesture-confirm doctrine. The
resolution bdo and the discussion found: cut on **reversibility / blast-radius**.
A reversible, zero-commitment act (pre-stage a surface, render a view, draft) the
system does **autonomously, no gesture**; an irreversible/outward act (send,
delete, purchase, publish) is **gated behind a gesture**. And the gate never
guesses an act safe — an unclassified verb is treated as irreversible. (It
composes with the anima arc's Risk/blast-radius assay when that lands; this v0 is
the verb-keyed classifier in the loop/tags.py grain, §10.)

> **Done when:** `causality/reversibility_gate.py` provides `classify(verb)`
(reversible / irreversible / unknown) and `gate(act, *, gesture=None)` returning a
decision; and `tests/test_reversibility_gate.py` passes under
`python -m unittest`, proving the teeth — (1) a reversible act is allowed with no
gesture, (2) an irreversible/outward act is blocked without a gesture and the
reason is legible, (3) the same irreversible act is allowed when a gesture
authorizes it, and (4) an unknown verb is treated as irreversible (blocked
without a gesture, the reason naming that the gate never guesses an act safe) —
never silently allowed.

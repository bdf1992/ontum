# AIM exemplars — the pinned good, the don't-regress floor, the fix list

> Derived from bdo's play of `aim.honest-witness` (slice 1), 2026-06-18 — *"first
> iteration successful, but not complete."* This is the golden reference: what to
> **amplify**, what must **never regress** (with checkable facts), and what to
> **fix** next. It is the oracle a **CHANGE test** judges a change against
> (amplified / held / regressed). Pin it before iterating, so the diverge-judge
> loop can't silently regress a good surface.

## Exemplars — the pinned good (bdo's words)

- **The word→node tendril.** *"I like the connection from the word to the node."*
  The dotted line binding the phrase-skin word ("cat") to its meaning node. The
  skin↔meaning binding made visible. **Amplify into interaction** (his explicit
  ask — see fix F1).
- **Adaptive canvas scale.** *"I like the scale of the last one, using the canvas
  when needed."* The loop level spreads the 5-gate pipeline across the full canvas;
  each level claims the space its content needs. Keep + extend.
- **Honest provenance** (slice 1's win): real-from-the-log, generated-not-authored.

### Golden facts (checkable — the CHANGE-test oracle)
Foldable from the same sources the surface reads (`phrases.json` + `admissions.jsonl`
+ `loop/reconcile.py`), no browser needed:

| fact | golden value | source |
|---|---|---|
| relation-magenta at `?c=2` | **0** (labels generated via `composeRelation`) | phrases.json relations resolve in RELATION |
| recovery composite at `?c=2` | **1.00** | recovery_scorer over the cat-chain |
| trap ghost present at `?c=2` | **yes** (elided-mediator) | phrases.json `surface_trap` |
| `dirMock` at `?c=4` | **0** (all 5 gates real) | 5 `node_real` admissions resolve their `stage_node` |
| pipeline stages parsed at `?c=4` | **5** | reconcile.py PIPELINE |

Visual golden refs: `.ai-native/shots/aim-honest-c2.png`, `aim-honest-c4b.png`.

## Don't-regress (invariants — never lose)

1. **Honest magenta** (AIM I1/F5): no real thing painted mock, no mock painted real.
   *Checked by:* relation-magenta = 0, `dirMock` = 0.
2. **Phrase-skin + the word→node tendril** present (bdo flagged the skin's loss as a
   regression once).
3. **Framing** — content fits the stage, never clipped.
4. **On-brand look** — cream paper, hand-drawn ink; *no* dark dashboard.
5. **Legible gestures** — "lasso/GATHER," never a garbled label.
6. **Cat-chain correct** — recovery composite = 1.00; the trap mediator holds.

## Fix (bdo's "don't like / missing" — all one gap: interaction ≠ meaning)

The unifying diagnosis: every item below is shallow interaction where AIM wants a
gesture to compile into *meaning* (an intent packet), not a tooltip or a text field.

- **F1 · Word + tendril interactive** (his explicit "please"): touching the word
  should drive its meaning (the node, its facets, its relations), and the line is
  the editable skin↔meaning binding — not inert.
- **F2 · Hover reworked** — *"I don't like the current hover interactions."* The
  facet-unfold-on-hover is not the interaction he wants.
- **F3 · Click reworked** — *"I don't like the current click interactions."*
- **F4 · Lines interactive** — *"I don't have interaction with lines like I might
  expect."* A relation/edge should be selectable/editable (its composition), not dead.
- **F5 · Edit meaning, not the title** — *"the only thing I can actually edit right
  now is the title, which doesn't match requirements at all."* The inspector must
  edit the node's *meaning* (facets/composition), gesture-native — the title is the
  wrong (and only) editable.
- **F6 · Corpus tab** — *"Corpus tab doesn't make any sense."* Remove or redefine
  the `corpus` nav level.

## The CHANGE test (with a node)

The exemplar above is the oracle. A change → re-fold the golden facts → diff →
**a node judges**: *amplified* (an invariant held AND a fix/amplify item moved up),
*held*, or *regressed* (an invariant broke). The diff is deterministic (teeth); the
amplify-vs-cosmetic call is the node's freeform reasoning — AIM's freeform-but-
deterministic gate shape, dogfooded on our own iteration.

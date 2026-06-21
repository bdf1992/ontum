# Done-line 0181 — The autonomy dial, completed: draw-fence gesture + owner's manual + the atom act-fence lacked

Written before code, per §9.4. When this line is met, stop.

> **Done when:** the act-fence (`loop/act_fence.py`, the three-tier ask-forgiveness classifier from done-line 0174) is a **complete, documented, landable** autonomy dial: it gains a **`draw-fence --by bdo` gesture pen** (the owner's one command to authorize a forgiveness scope to self-admit — refusing an invalid fence, never self-drawable by a session because draw-fence is itself a FORBIDDEN owner gesture, D-4), a **recommended starting fence** the read-only witness surfaces so the owner's draw is one copy-paste not a design task, and an **owner's manual** (`docs/culture/the-administrator.md` + the live `python -m loop.act_fence` surface) telling what it does, the three tiers, and the one gesture; it is **backed by an atom serving `epic.owner-harness`** (the atom #450 never had, so it can actually land); the dial **stays inert until bdo draws a fence** (D-4 — the authority to self-admit is his stamp, correctly not a session default); and a §10 test proves drawing the recommended fence **flips a forgiveness act from escalate to admit** (non-vacuous — an inert dial fails it), while the existing 0174 teeth (the tier reads authorization context not verb; forbidden acts stay forbidden) carry forward green.

## Why

Two sessions built the same keystone in parallel: act-fence (#450, done-0174 — the richer 3-tier classifier, but no atom, no manual, no draw pen) and an authority-dial (#452 — a thinner classifier, but a manual and Apple "defaults-set" framing). bdo asked: *"can they be composed or do they clash?"* They clash only at the classifier (one decision, keep the better one) and compose everywhere else. This is the composition: act-fence's classifier (carried, attributed) + the recovered owner's manual + the draw-fence gesture that makes it Apple (one command, not hand-written JSON) + the atom that makes it landable. bdo: *"set the default and give me an owner's manual — this isn't ikea, it's apple."*

## Shape

- **Correction on the record:** act-fence's "inert until bdo draws a fence" is NOT an IKEA flaw — it is correct D-4 (the authority to let acts self-admit is the owner's stamp; a session drawing its own fence is the self-dealing the whole repo forbids). So the Apple fix is NOT a default fence (that would grant self-admit by default); it is the **one-command gesture + the recommended cut + the manual**, the authorization still bdo's.
- **No double-build (§10):** the duplicate classifier (`loop/authority.py`, #452) is dropped; act-fence's is the engine.
- One atom backs the whole `act_fence.py` (classifier + pen); the manual rides as the authored telling.

## Not in scope

- bdo drawing the first fence (his gesture; this only makes it one command and legible).
- The Administrator (the fleet join that runs acts through this cut and shapes the ask-first set into a briefing) — named, this is its keystone, later increment.

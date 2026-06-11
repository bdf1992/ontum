# handoff-gate.det.v1 — the L2 handoff gate (deterministic)

version: 1.0.0 — §7: a patch is wording; a minor adds a check; a major
changes what this gate may decide. The receipt records this file's sha256 as
`prompt_hash`, so every verdict is attributable to the exact law that produced
it — even though no mind reads this file. For a deterministic gate the prompt
*is* the law: this document is the human-readable statement, `loop/handoff_gate.py`
is its executable form, and the two are kept in lockstep (a change to the law
changes this file and bumps the version).

## Role

You are the third real gate and the second of the *law* kind (report 0004 §3;
epic.experience-layer horizon: "real gates — deterministic where the question
is law, inference where it is judgment"). The value gate (first light, done-line
0040) judges *value* — meaning, answered by a mortal mind. The placement gate
(done-line 0041) judges *placement* — a fold over the field. You judge
*readiness to hand off* — whether the atom carries the structural minimum an
implementer needs to begin. That is a question of presence, not of taste: an
atom either declares the three things or it does not. No mind is summoned for
you, and one would only add noise.

## You read

The single atom under judgment:

- `story.text` — the what and the why, in the atom's own words;
- `incidence.touches` — the addresses (files, surfaces, named units) the work
  will occupy;
- `incidence.hands_off_to` — the downstream seam(s) the finished work flows to.

## The law

An atom is **ready to be handed off** when it carries all three of:

1. a **non-empty story** (`story.text` has text) — without it an implementer
   has nothing to build toward;
2. at least one **`incidence.touches`** address — without a surface, placement
   passed vacuously and a spec has nowhere to land;
3. at least one **`incidence.hands_off_to`** seam — without a declared
   downstream, the finished work has nowhere to go.

All three are required because each is something the next stage cannot supply
for the atom: a spec written from a storyless, surface-less, or
downstream-less atom would be invention, not implementation. Any one missing
is a hard `send_back`.

## You return

Exactly one verdict from the seam's terminal set, through the one pen
(`loop.node judge`, D-4 — the law computes the verdict; only the pen writes the
receipt):

- **`send_back`** — at least one of the three requirements is missing. The
  reason names *which* one(s) and what each absence means: a cold reader must
  see *why* it was sent back, not only *that* it was.
- **`ready_for_spec`** — all three are present; the atom can be handed to an
  implementer without guessing.

The verdict is landed by `loop.handoff_gate judge`, which calls the same
`loop.node judge` the inference gate and the CLI use. There is deliberately no
second write path.

## The §10 test

Your verdict must be one missing field away from its opposite. The test that
binds you (`tests/test_handoff_gate.py`): an atom that is locally fine at every
earlier gate — it had value, it placed cleanly — but is **hollow** at handoff
(a story with no surface, or a surface with no downstream) must `send_back`,
while a complete atom must `ready_for_spec` — and a fixed-verdict mock that
always says `ready_for_spec` must *fail* that test. A gate whose answer cannot
be `send_back` is not a gate; a gate whose answer cannot be `ready_for_spec` is
a tripwire, not a readiness check. This one is both, because the law reads the
atom's structure, not a constant.

## You will not

- judge an event you announced (D-2) — the pen refuses; the deterministic
  runner is a distinct node from the announcer, so this never arises;
- write anywhere except through `judge` — the receipt is the only pen (I-2);
- decide *value* (that is the L0 gate's question) or *placement* (the L1
  gate's), or invent a requirement the atom's schema does not carry — absence
  in `incidence` is information, not a gap to fill;
- judge the *substance* of the story (whether the plan is good) — that is
  judgment, reserved for a later inference extension; v1.0.0 decides only the
  *presence* axis (the cheapest real refusal).

## Realness

This backing exists, is tested, and can refuse. Making it the *live* L2 gate is
a `node_real` admission — `handoff-gate.mock.v0 -> handoff-gate.det.v1` — which
is bdo's stamp, not a session's (done-line 0028 scopes arc-confirmation to the
owner-stamp stage, not `node_real`; the prior real gates were admitted by bdo's
authorization). Until he stamps, the loop still judges its own mock here, and
`loop.handoff_gate judge` is refused by the seam — by design. The gesture path
for that stamp is the `realness-intake` skill: bdo closes the stage's
realness-confirm issue with a plain-language comment, and a session admits it
real on his authorization — never forged.

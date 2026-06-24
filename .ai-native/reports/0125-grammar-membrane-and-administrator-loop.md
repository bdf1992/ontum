# Report 0125 — Corpus grammar derived, the membrane reframe, and the launchable Administrator loop

## What landed

All of this is **in the working tree, unlanded** (loose files — not committed,
not PR'd; the viewport was already dirty at session start). Nothing here is a
done-line; this session was blueprint + understanding + tooling, by bdo's steer.

**1. The corpus envoy + raw zips** — `exports/ontum-grammar-derivation/` (sealed,
7 files) + `exports/ontum-corpus.zip` (3.4 MB) + `exports/gallery-corpus.zip`. The
framing to send the corpus out for grammar derivation.

**2. The settled grammar (panel report)** —
`.ai-native/proposals/corpus-derivation-organ.proposal.md`. A 9-agent local panel
(`wf_22d65bda-585`) derived the corpus's grammar; bdo handed a settled cross-model
report that supersedes it. Conclusions, citations re-verified by grep this session:
the working grammar reduces to **FIVE** operations — `APPEND · FOLD · HASH-IDENTITY
· CITE · VERDICT` (`POSTURE` demoted = `FOLD` over `APPEND`ed governance);
`gallery` confirms by role under divergent words; the first object is
**work-ontum.v0** and the **first *meaning* ontum is NOT yet real**; the buildable
v1 is the **consequence throat** (assemble `field.route_audit` + `observe.gate` +
`relation_ledger`, proven by refusal); the cube is a *proposed* fabric lattice, not
the harness skeleton.

**3. The membrane reframe** —
`.ai-native/proposals/generative-basis-membrane.proposal.md` + **`loop/basis.py`**
(built + verified: §10 self-test passes — admits 4 real basis moves, refuses 4
fakes). The five are not the floor: they are the basis *emitted by a membrane*
(the generalized seam) under work-accountability **pressure**. Different pressure →
different basis (B&W/RGB/CMYK/PANTONE). A slot = a decided axis with a refusal-tooth;
the gamut law gates SPLIT/MERGE/ADD/DROP; `POSTURE` is a pressure-relative DROP/ADD,
not a final demotion. The report carries a §4·5 correction (basis-generation sits
*before* the throat).

**4. The launchable Administrator loop** — `.claude/skills/administer/SKILL.md`
(the `/administer` ritual) + **`loop/fleet.py`** (the eyes; v1 with liveness —
caught 2 zombie runs live) + `.ai-native/proposals/administrator-requirements.md`
(R1–R18, real vs missing). Superpowered: oversight fans out to monitor-subagents,
dispatch routes by herald reputation, the fold sees RUNNING vs STALLED.

**5. Two architecture questions settled by test, not assumption** — R17: a
subagent **cannot** launch a Workflow (no tool in its set — proven). R18: but it
**can request one upward**; the Administrator holds the tool + bound + rail and
disposes (the propose-dispose / merge-node shape). The fleet self-extends, governed.

## To continue (the handoff — start here)

**THE REAL NEXT MOVE — CTA-1: make the first *meaning* ontum real.** Everything
above is map + machinery; the actual prize is undone. Mint one `relation_claim`
whose subject is a unit of **meaning** (not a work-atom) + its `consequence_receipt`,
and drive it through the consequence throat (`field.route_audit` → `observe.gate` →
`relation_ledger.validate`/`fold`) for a real `PREDICTIVE`/`TRIVIAL` score. Passes
only if: subject is meaning-bearing; claim cites backing; receipt *observes*
consequence; a ghost subject is refused. This is the smallest honest bridge from
harness to fabric, and it forces the work-vs-meaning seam to resolve in code. **Do
NOT** build NL/generative interfaces over the still-hollow center.

**Smaller real steps available now:**
- *Fit one slot* (basis.py §9 honest edge): bind `CITE` to
  `consequence_graph.resolves`, confirm it rejects an unresolved citation — turns the
  checker into CTA-2's kernel.
- *Pin the new modules:* add `tests/test_basis.py` (assert 4 admits / 4 refuses) +
  `tests/test_fleet.py` (assert STALLED reclassification) — they currently read idle
  in the census because the suite doesn't guard them.
- *Take `/administer` for a live run* over the pending work, harvesting requirements
  R8–R14 (R8 already closed this session).

**Land it:** this session's proposals + `loop/basis.py` + `loop/fleet.py` +
`/administer` are all unlanded. They need branch → PR → independent review →
merge-node, or they stay loose. The membrane/grammar work may want its own arc, or
to ride an existing one — bdo's call (needs-you).

## needs-you

1. **The one suite failure is your in-flight work, not this session's.**
   `test_git_pen.test_local_mutating_git_is_now_watched` fails because
   `.claude/hooks/command_guard.py` is **modified in your working tree** (the
   workstation fence now denies `git checkout -b` on the viewport), which
   contradicts that older test (it expects `checkout -b` to be *watched*, rc 0;
   it now gets *denied*, rc 2). Two locally-fine things refuse to fit — the suite
   did its §10 job. Resolve by updating the test to expect the deny, or narrowing
   the fence. I did not touch it (uncommitted work I didn't author).
2. **Landing decision.** This session's work is all PROPOSED/unlanded. Whether and
   how to land it — and which arc it rides (a new grammar/membrane arc, or an
   existing one) — is yours. Nothing here is at a stamp; it's the next session's
   build (CTA-1) that produces a landable atom.
3. **Two STALLED conductors** (`causality-sing-bakeoff`, `causality-dirstory-bakeoff`)
   have sat idle 3 days — reap candidates (`python -m loop.fleet` shows them).
4. **The dirty viewport** needs recovery at some point (the whiteout utensil
   preserves the pile before cleaning).

## End-state

`report` — Corpus grammar derived (five primaries: APPEND·FOLD·HASH·CITE·VERDICT)
and reframed as a pressure-relative basis cut by a membrane (`loop/basis.py`, §10
verified); the Administrator loop is launchable (`/administer` + `loop/fleet.py` v1)
with R17/R18 settled by test. All work is unlanded in the working tree. The real
next move — CTA-1, the first *meaning* cut — is **not started**; the session built
the map and the machinery around it, deliberately, but the first meaning ontum is
still hollow. QA clean (1409/1410; the lone failure is bdo's in-flight fence change).

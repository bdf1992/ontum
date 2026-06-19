# ISSUES — the feedback channel

*Each review round writes findings here, keyed by family. An agent
iterates against its own open issues (handed back via SendMessage to the
same session). An issue closes when the revised draft passes the RUBRIC
line it failed. This is the loop's backpressure — nothing accepts with
open blocking issues.*

Severity: **block** (fails RUBRIC, cannot enter) · **fix** (real gap) ·
**nit** (polish). Status: **open** · **addressed** · **accepted**.

---

## Format (one entry per finding)

```
### <family-id> · <severity> · <short title>   [status]
Round: N
Finding: what is wrong, against which RUBRIC line.
Asked: the concrete change requested.
```

---

## Round 0 — backlog seeded, no drafts yet

_No issues filed. First drafts land, then review opens this log._

---

## Round 1 — review gate (independent second eyes; reviewer did not author the drafts)

### topo · block · register-strata is verdict-inflated (ai-native unearned)   [open]
Round: 1
Finding: Fails RUBRIC "Verdict (derived, not invented)" + "The refusal (teeth)". register-strata scores register=full, provenance=partial, agent=partial → nominally ai-native. But both the register=full and provenance=partial claims rest on the SAME unbuilt binding ("a node's stratum is derived from its admission state"), which the family itself concedes is unpopulated ("population from real admission state is a later piece — capability present, use-trace pending"). Worse, it is mis-grounded: the canvas `strata{fundamental,derived,learned}` field is the EPISTEMIC-origin axis, NOT the four truth-registers (record/runtime/request/simulation). Mapping "settled RECORD → fundamental stratum" conflates two orthogonal axes (verified: display-system.md C1–C3 strata = fundamental/derived/learned; the four registers appear nowhere in the doc). Strip the two contingent axes and only agent-drivable (the real schema field + inspector) stands → 1 axis → truth-capable, not ai-native.
Asked: Recut register=full → none/partial honestly and re-ground onto the register axis (RUBRIC.md or term_economy verdict classes), OR hold the pattern at truth-capable until a use-trace shows a real admission moving a node pencil→ink. Do not enter as ai-native on an unpopulated, mis-grounded binding.

### register · block · register-badge cites a ghost source for the four registers   [open]
Round: 1
Finding: Fails RUBRIC "New-pattern bar" (grounded exemplar, "never a guessed landmark stated as fact") + the ghost-citation teeth. Exemplar 1 states: "causality:display-system.md — the four registers (RECORD/RUNTIME/SIMULATION; ink vs pencil) are the named axis this badge encodes." Verified against the file: display-system.md does NOT name those four registers. Its named axes are strata (fundamental/derived/learned), anima (strength/tempo), and two EDGE registers (sync/async). The four-register taxonomy lives only in evolution/RUBRIC.md. The anchor resolves but says something else — a citation that points to nothing the way it claims (the term_economy ghost).
Asked: Drop the false display-system.md claim. Re-ground on what actually resolves: RUBRIC.md (which defines the four registers) and/or term_economy.py's verdict classes (which the badge says it carries one-to-one). Keep exemplar 3 (canvas.js SCHEMA) — that one resolves.

### register · block · no canonical four-register schema exists — 9 families re-declare it   [open]
Round: 1
Finding: Fails RUBRIC's anti-"overloaded" intent. Every truth-bearing family (living, topo, spatial, play, instr, hud, edit, register, interface-ai, async) independently enumerates RECORD/RUNTIME/REQUEST/SIMULATION + ink/pencil. There is no single source: RUBRIC.md defines them; causality/display-system.md uses a DIFFERENT model (strata + anima + sync/async edge-registers). So the families are not drifting from a canon — there is no canon, and the one doc they cite for it (display-system.md) does not contain it. Re-declaration with no owner is exactly the overloaded failure the rubric refuses.
Asked: bdo architectural call. Either (a) author the four-register enum as a Commons primitive owned by the register family and have every other pattern cite it, OR (b) reconcile the rubric's 4 registers with display-system.md's strata/anima/edge-register model. Reviewer recommendation: (a) + treat register (commitment: record/runtime/request/simulation) and strata (epistemic: fundamental/derived/learned) as ORTHOGONAL axes a node carries both of — they do not compete for meaning, only for channels (see register · channel-allocation).

### register · fix · register/strata/anima contend for one node's visual channels   [open]
Round: 1
Finding: Raised independently by register (Q1), hud (Q1), topo (register-strata), living. Three axes want the same channels: register (4, ink/pencil) wants hue+weight+line-treatment; strata (3) wants altitude (topo:register-strata) and per display-system.md H4 already owns colour/layer; anima (2) per display-system.md already owns size & motion. topo:register-strata's "register→altitude" collides with strata's natural home in altitude.
Asked: bdo's channel cut. Reviewer recommendation, grounded in display-system.md H4's existing allocation (strata = colour/layer; anima = size & motion): give register the only non-colliding channels left — line-treatment (solid=ink / dashed=pencil) + the discrete register-badge — and deny register both hue (strata's) and size/motion (anima's). Resolves register Q1, hud Q1, and de-conflicts register-badge vs pencil-vs-ink (ambient line-read vs precise badge-read — both ship, different channels).

### async · fix · in-flight/parked may be a fifth register the rubric cannot see   [open]
Round: 1
Finding: async Q3 — the whole family asserts "happening-but-blocked" is a state none of RECORD/RUNTIME/REQUEST/SIMULATION holds. parked-pulse and backpressure-visible score register=full against a taxonomy that arguably cannot represent what makes them honest. If parked is a genuine 5th register, every async pattern is scoring against an incomplete axis; if it is a sub-state of RUNTIME, the scores stand.
Asked: bdo fork tied to the canonical-schema decision. Reviewer recommendation: keep 4 registers; model "parked/in-flight" as a RUNTIME sub-state (active vs blocked-on-X), not a 5th register — avoids taxonomy bloat and keeps the ink/pencil binary the eye relies on. Re-score async patterns' register axis against RUNTIME-with-substate if confirmed.

### register · fix · settle-on-commit mis-cites C4 as an atom lifecycle   [open]
Round: 1
Finding: Fails the grounded-exemplar bar. Exemplar 1: "display-system.md — the C4 lifecycle a proposed atom follows." Verified: C4 = DivergenceComparator (the three-way fundamental/derived/learned compare), not a lifecycle. The pattern's actual grounding (authoring.js validate→instantiate, foundry:04 pulse) is sound; only the C4 anchor is wrong.
Asked: Replace the C4 reference with the real settling source — reconcile.PIPELINE / the append-only log's pencil→ink-on-append (the substrate's actual level-triggered settle), or display-system.md's real lifecycle line if one is cited correctly. Keep the authoring.js + foundry exemplars.

### topo · fix · backing-bound-topology register=full is unjustified   [open]
Round: 1
Finding: Scores register=full, but the pattern's whole content is provenance/ghost (resolve a backing or render hollow) — it does not distinguish RECORD/RUNTIME/REQUEST/SIMULATION at all. The verdict (ai-native) survives on provenance=full + agent=full, so this is axis-inflation, not verdict-inflation, but it overstates coverage.
Asked: Justify which of the four registers it distinguishes, or drop register=full → partial/none. Verdict stays ai-native either way.

### topo · fix · genealogy-trails axis table and verdict disagree   [open]
Round: 1
Finding: RUBRIC "Verdict (derived, not invented)": register=partial + provenance=partial = 2 axes → mechanically ai-native, yet verdict=truth-capable. The family's own prose explains the conservatism honestly ("the path is drawn but not yet resolved to a backing... shaped like provenance without being grounded in it") — i.e. provenance is really none today. The conservatism is correct; the axis table is generous and contradicts it.
Asked: Set provenance=none to match the honest prose and the truth-capable verdict (the inverse of inflation — make the table agree with the call). Do not promote to ai-native on an ungrounded provenance.

### spatial · fix · altitude-breadcrumb axis table and verdict disagree   [open]
Round: 1
Finding: Same shape as genealogy-trails. provenance=partial + agent=partial = 2 axes → mechanically ai-native, but verdict=truth-capable. The evolution prose concedes the crumb is a route to a viewport-state, not yet to a source record — so provenance is shaped-not-grounded.
Asked: Drop the ungrounded axis (provenance → none, and confirm agent=partial is real for a breadcrumb) so the table matches the honest truth-capable verdict.

### interface-ai · fix · virtual-request-node full/full/full rests on analogy   [open]
Round: 1
Finding: Scores full on all three axes, but the grounding for register/provenance is ontum's atom→pen→receipt pipeline (real as a CONCEPT) while the pattern's distinctive claim — a visible request node walking a lifecycle ON THE CANVAS — is, per the family's own Q1, "the least-built of the family." The pipeline grounds the lifecycle idea, not a rendered node.
Asked: Either land/cite a built canvas request-node surface, or honestly note the full/full/full is by analogy and resolve the family's open question (rendered node vs spec-object-in-inspector) before bdo's bless. Not a block — grounding is real — but the strongest claim in the family should not ride solely on analogy.

### play · fix · poke-to-route duplicates register:provenance-trace   [open]
Round: 1
Finding: Deduplication. poke-to-route ("poke any element → its route home: backing record / file:line / log substring") is the same gesture as register:provenance-trace ("click any element → its route home") and hud:provenance-tooltip ("hover → its source"). Three families, one "click/hover/poke → path home" primitive. Most-grounded home wins: register:provenance-trace (the register family IS provenance, grounded in term_economy.py + display-system.md C15). (Note: the brief paired poke-to-route with interface-ai:virtual-request-node — refuted, those are different things; the real dup is the provenance-trace trio.)
Asked: Drop poke-to-route as a standalone pattern OR cite-as-kin: keep it only as the play-gesture surface of register:provenance-trace, not a re-owned primitive.

### hud · fix · provenance-tooltip duplicates register:provenance-trace   [open]
Round: 1
Finding: Deduplication (confirms the brief's suspect). provenance-tooltip = "hover → backing record id / file:line / log substring" = register:provenance-trace's gesture in HUD chrome. hud's own Q2 already asks whether ticker-feed's click-to-source and provenance-tooltip "are one thing seen twice" — they are, and both are register:provenance-trace. register wins (most grounded).
Asked: Cite-as-kin (the HUD-chrome expression of register:provenance-trace) or drop. Do not ship a third independent "route home" pattern.

### play · fix · simulate-before-commit overlaps dry-run-preview + settle-on-commit   [open]
Round: 1
Finding: Deduplication. simulate-before-commit ("every edit runs first as pencil; see propagated consequence before ink on commit") overlaps interface-ai:dry-run-preview ("show what would happen before submit; pencil before ink") and register:settle-on-commit (the pencil→ink-on-append transition). The generic "preview-the-consequence-in-SIMULATION-before-RECORD" primitive is most-grounded in interface-ai:dry-run-preview (reconcile.py --status, digest --json, term_economy project — real read-only folds) and the transition in register:settle-on-commit.
Asked: Narrow simulate-before-commit to its play-specific contribution (propagated consequence rendered on the LIVE GRAPH as a play gesture) and cite dry-run-preview + settle-on-commit as kin; do not re-own the generic pencil-before-ink preview.

### edit · fix · authored-finish re-owns interface-ai's schema-gate mechanism   [open]
Round: 1
Finding: Deduplication (edit's own Q1 concedes it). authored-finish's teeth ("schema-validated BEFORE it renders... refused, exactly as causality:authoring.js refuses a malformed graph-spec") are interface-ai:schema-gate-before-draw's mechanism, which is the most-grounded home (authoring.js#validateSpec + authoring.test.js — the actually-built gate). authored-finish's real, distinct contribution is the EDITORIAL spec (type-role + spacing + register as required fields) — that addition is worth keeping.
Asked: Keep the editorial-finish spec; cite interface-ai:schema-gate-before-draw as the gate it rides. Do not re-own "schema-validate-before-draw."

### instr · fix · provisional-take re-owns register's pencil/ink mechanic   [open]
Round: 1
Finding: Deduplication. provisional-take's core ("machine take lands in SIMULATION/pencil; inked to RECORD only by explicit human keep-gesture") is register:pencil-vs-ink + register:settle-on-commit (the keep-gesture = the commit that settles pencil→ink). register is the canonical home of the register mechanic. provisional-take's distinct contribution — the generative-instrument seam (machine plays in pencil, human keeps) — is real and worth keeping.
Asked: Keep the keep-gesture performance seam; cite register:pencil-vs-ink + settle-on-commit as kin; do not re-derive the register mechanic.

### async · nit · virtual-request-node and parked-pulse are adjacent lifecycle states   [open]
Round: 1
Finding: Not a dup, but unnamed kinship. interface-ai:virtual-request-node (the REQUEST object, pre-submit, draft→valid→submitted) and async:parked-pulse (the RUNTIME object, post-submit, blocked-on-X) are two lifecycle stages of one unit; both ground in real loop folds (reconcile.PIPELINE; loop.summon/node).
Asked: Name the seam — a virtual-request-node becomes a parked-pulse on submit — so the two patterns cite each other as kin rather than reading as overlapping inventions.

### topo · nit · new patterns ground in prose, not a structured exemplars[] field   [open]
Round: 1
Finding: Consistency. backing-bound-topology and register-strata (topo's strongest patterns) carry their grounding (term_economy.py, canvas.js, evidence-edge.schema.json — all verified to resolve) inside the "evolution" prose, with no `exemplars[]` array, unlike every other family's new patterns. The refs are real; the structure is inconsistent.
Asked: Lift the in-prose causality refs into an `exemplars[]` field so topo's patterns are machine-readable like the rest.

### living,spatial,play,instr,hud · nit · families 1–7 new patterns omit explicit use_when   [open]
Round: 1
Finding: RUBRIC "New-pattern bar" requires "a real use_when" for new patterns (named for 8/9/10; spirit applies to all newly authored). The new patterns in living, spatial, play, instr, hud embed use-when inside intent/evolution prose but have no explicit `use_when` field (only edit, register, interface-ai, async carry it).
Asked: Add an explicit `use_when` to each newly authored pattern in families 1–7 for parity with the 8/9/10 bar.

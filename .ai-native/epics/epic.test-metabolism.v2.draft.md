# epic.test-metabolism (v2) — the test-quality pipeline, dual-keyed to its lineage

**Status:** draft arc, awaiting bdo confirm-arc
**Supersedes:** epic.test-metabolism (v1). v1 wrote the arc in repo idiom alone;
v2 keeps every handle and pins each to its standard-practice name, so the skill
this arc delivers inherits solved failure-modes and existing tooling instead of
rediscovering them in retros.

---

## The thesis (read first — it sets the whole frame)

A rose by any other name smells as sweet: the repo's bespoke terms are
legitimate **handles** — each bundles a concept *plus* local design intent that
the generic name omits. The handles stay. They are not decoration and this arc
does not rename anything.

But a handle severed from its lineage costs real money. Retro 0037 (thirteen PRs
behind one receipt) is the canonical CI lesson *"a bypassable gate will be
bypassed; enforcement must be mandatory"* — learned from an incident because the
bespoke vocabulary walled the repo off from where that lesson is already
written. The tax is not the vocabulary; it is the **isolation** the vocabulary
creates.

**This arc's discipline:** every QA handle becomes *dual-keyed* — local name
(design intent) + standard name (inherited failure-modes + free tooling). This
is the repo's own rosetta-creole practice, applied for the first time to its own
QA engineering rather than to language.

This does not shrink the arc. It grounds it. The repeatable skill it delivers is
stronger for standing on fifteen years of others' scar tissue.

---

## The lineage spine (the rosetta — every handle, dual-keyed)

| handle | standard-practice name | what you inherit by pinning to it | local delta the handle legitimately adds |
|---|---|---|---|
| the log is truth; all state is a fold | **event sourcing + CQRS projections** | known failure modes: projection drift, replay cost at scale, event-schema evolution — read instead of rediscovered | torn-tail tolerance + fsync line-atomicity, hand-built correctly |
| atom = sha256 of bytes; edit makes a new atom | **content-addressed storage** (git/Merkle) | dedup, integrity, rename-detection are solved upstream | restart-the-pipeline-on-edit semantics git blobs don't carry |
| mock gate → real gate, admitted on the log | **test double (stub) + capability registry / feature flag w/ audit trail** | stub-replacement hygiene; flag-rollout literature | **delta: see Protected Deltas §A** |
| §10 — locally-fine atoms refuse to fit | **negative / failure-path testing** | testing-101; *and* the Assertion-Roulette warning (below) | the *practice* is standard; the *token count* is a trap (Correction 2) |
| done-line, frozen before work | **acceptance criteria, spec-first, immutable+versioned** | TDD/BDD body of practice on falsifiable criteria | the freeze-and-loud-supersede ritual |
| organs: census / gaps / mock-shame | **observability dashboard + auto-generated backlog + failing-CI nag** | existing DevX tooling; don't hand-fold what's shipped | **delta: see Protected Deltas §B** (mock-shame) |
| the test-organ site, seats, seams | **a test-QA pipeline: linter + LLM-review step + metrics report** | separation-of-concerns; "don't grade your own homework" = D-2 | the composition + non-bypassable enforcement |
| anti-constant assertion `assertNotEqual(verdict, MOCK)` | **one hand-written mutant** | the recognition that one mutant ≠ a mutation score (Correction 1) | a cheap smoke-check, honestly scoped |

---

## Protected deltas (translation proves these EXCEED baseline — name them so reviewers credit them)

**§A — non-bypassable enforcement.** Standard quality gates can be overridden
("if necessary, these policies may be overridden" — verbatim across the CI
literature; GitHub ships override as a setting). The repo's invariant is
structurally un-overridable: an atomless PR refuses, a mock-only receipt
refuses, enforced by a *fold*, not a permission toggle. State it in standard
terms — *"non-bypassable required checks with no admin override, enforced in the
merge fold rather than in repo settings"* — and any reviewer recognizes it as
**stronger than what they ship.** No piece in this arc adds an override, waiver,
or threshold-exception. This delta is protected.

**§B — stub-never-silently-real.** Typical test-double hygiene trusts a naming
convention; a stub left in by accident ships silently. The repo makes mock-vs-
real an auditable runtime admission that *screams every turn until resolved*
(mock-shame, holds 0/5). That is above baseline. The "organ" framing earns its
biology exactly here. Protected.

These two are the answer to "don't downplay this": the repo did real systems
engineering and went past industry practice in two specific, defensible places.
The arc's job is to lift the *tractable* layer (test-quality) while leaving
these untouched.

---

## The three corrections (survive translation; non-negotiable; baked into pieces)

**Correction 1 — make the mutation-testing call honestly; stop laundering the
grep.** The anti-constant check kills *one* mutant in *one* file. Mutation
testing measures the *distribution* of caught faults — different in kind, not
degree. v1 dodged this by calling per-file `needs_instrumentation` verdicts a
"hybrid oracle-gap" — that is the same shared-blind-spot error the arc exists to
fix. The honest fork, forced in piece 2: **either** run a real mutation lane
(`mutmut` / `cosmic-ray` exist for Python; opt-in slow lane, off the 24s path)
and get an actual score, **or** keep the grep as a labelled smoke-check and
*stop describing it as oracle-gap coverage.* No third option.

**Correction 2 — retire the vanity count; keep the practice underneath.** The
`refuse`-token count (370) is a vanity metric in the precise sense coverage% is
discredited: it counts a proxy, not the property. Worse, high assertion density
*without per-assertion messages* is **Assertion Roulette**, an empirically
measured debugging-cost smell. Kill the count. Keep §10's *content* (negative-
path tests where good-looking input is rejected) and require those assertions to
carry **messages** — which converts a possible anti-pattern into a strength.

**Correction 3 — the skill is a pipeline of standard components; its value is
composition + enforcement, not invented parts.** Linter, LLM-review, mutation
lane, metrics report all exist. The skill does not reinvent them; it composes
them in repo idiom and makes the gate non-bypassable. Building from existing
tooling is the point, not a concession.

---

## The site this arc delivers (= the repeatable skill)

**`.claude/skills/test-organ/`** (name bdo's to set). In standard terms: a
**test-QA pipeline** with three stages and a non-bypassable gate. In repo terms:
a site with three context-isolated, prompt-pinned seats and two refusing seams.
D-2 ("no node judges its own writer's work") = *don't grade your own homework* =
separate the build seat from the approval seat. Both framings name the same
constraint; the arc honors it once.

**Seats:**
- **classifier** — pure fold; types each module to an archetype. Standard name:
  a *test categorizer / static pre-pass*. Prevents the naive-heuristic false
  positive (the field's own smell detectors "rely on highly inaccurate rules" —
  this seat is the repo's answer to that, and it must be falsifiable).
- **reviewer** — real (LLM) judging seat. Standard name: an *LLM test-review
  step* (now competitive with classical static detectors zero-shot). Emits
  admit / send_back / needs_instrumentation. Backed by deterministic folds for
  the cheap checks; leans on the model for semantic smell judgment.
- **auditor** — pure fold over the whole tree. Standard name: a *test-suite
  metrics report*. Emits aggregate symptoms a single green run hides.

**Seams (the refusals that make it a pipeline, not a bag of scripts):**
- classifier → reviewer: reviewer refuses to judge an unclassifiable module
  (needs_instrumentation, never admit).
- reviewer → auditor: a tree of all-green admits must still be screamable as
  unhealthy. "A clean ledger is not a healthy system," one stage down.

**Author seat: cut (resolved, do not rebuild).** A seat that emits test-
acceptance-bars judges nothing in front of it, cannot refuse, cannot be admitted
real by the repo's bar — a structural mock. In standard terms: *generating
acceptance criteria is authoring, not review; don't fuse them.* Bar-authoring
lives upstream at the freeze (done-line 0033). A create-facet, if ever wanted,
is a separate site with its own teeth (refuses a hollow done-line) and its own
arc.

---

## The pieces (each independently refusable; build order 1 → (2‖3‖4) → 5 → 6)

### piece 1 — the classifier fold *(standard: static test-categorizer)*
**Bar:** a pure fold types every module in `tests/` to exactly one archetype,
with a **named** "unclassifiable" residual — never a silent bucket.
Provisional archetypes (the build's first job is to falsify their coverage):
pure-fold · seam-on-log · subprocess-hook · prompt-pin · organ · recovery.
**Teeth:** refuse to silently bucket the untypable; a large residual is a
finding about the *typology*, not the tests. Mirror `reflect.py` kind-dispatch
(0030); no flat rubric.
**Opening instrumented step:** dry-run the archetypes against all 49 modules; a
large residual re-scopes the piece before any rubric is written.
**Inherited failure-mode to respect:** static categorizers misclassify on
surface features — this is *why* the reviewer (piece-level seam) must be able to
overrule the classifier, not trust it blindly.

### piece 2 — assertion power *(standard: mutation testing — make the call)*
**Bar — and this piece forces Correction 1.** Pick one, record which, do not
straddle:
- **2a (measured):** stand up an opt-in mutation lane (`mutmut`/`cosmic-ray`),
  off the 24s path, scoped initially to the pure-fold modules (`reconcile`,
  gates' deterministic backings, `digest`). Report a real mutation score. This
  *is* oracle-gap coverage; describe it as such only here.
- **2b (smoke-check):** keep the anti-constant grep as a labelled cheap check —
  "does a gate test kill the fixed-mock mutant?" — and **drop every claim that
  it measures oracle gap.** It measures one mutant in one file. Honest, cheap,
  named for what it is.
**Teeth:** whichever is chosen, the seat emits needs_instrumentation (not admit)
for any archetype it cannot actually evaluate. A check that passes what it
cannot measure is a mock wearing a real receipt.
**Open the build owns:** does the anti-constant pattern generalize past gate
tests? If gate-specific, define each archetype's own discriminating anchor here
— design work, not a skip.

### piece 3 — test smells *(standard: test-smell catalog; contradicts our own §10 count)*
**Bar:** detect the catalogued smells the suite is most exposed to by its own
culture — **Assertion Roulette first** (multi-assert, no message; our refutation-
dense subprocess tests are the prime suspect), plus Empty Test / Redundant
Assertion (the existing tautological check, *renamed to the field's term* so a
foreign reviewer recognizes it). Require per-assertion messages on negative-path
tests (this is Correction 2 made executable).
**Teeth:** the detector must itself be falsifiable — a flagged smell the author
shows is a false positive (the 'semantic coherence' problem) is logged as a
*detector* defect, not enforced. "An unverified symptom is not a finding" is
this piece's first law, and it is also the field's open research frontier — the
repo's discipline here is a genuine edge, not parochial.
**Retire here:** the `refuse`-token count as a reported metric. Keep the
negative-path practice; report *asserted, message-bearing negative-path
coverage* instead of token density.

### piece 4 — the auditor fold *(standard: suite metrics report; promotes the seams file to an organ)*
**Bar:** a pure fold over the whole tree emitting aggregate-only symptoms:
done-line pin coverage (47/49 — **this makes the headline honor-system
convention executable, the arc's centerpiece**), asserted-negative-path coverage
(replacing §10 density), **single-atom monoculture** (every fixture builds one
atom; the shared-log many-atom fold is the least-pinned path — an inherited
event-sourcing risk: projections are only as trustworthy as their multi-stream
replay tests), and the executable-vs-honor-system split itself.
**Teeth:** must scream over a tree of all-green admits. A monocultural healthy
ledger is a symptom, not clean.
**Acceptance criterion for the WHOLE site (this piece carries it):** running the
auditor on the current tree must **reproduce the existing seams findings by
hand** — 47/49 pins, 0 xfail, the reconcile false positive. A reviewer that
cannot re-derive what is already known cannot be admitted real.

### piece 5 — wire to gaps *(standard: auto-generated backlog from CI signal)*
**Bar:** needs_instrumentation verdicts (piece 2) + aggregate symptoms (piece 4)
become gap-kinds in `gaps.py` — unpinned-done-line, missing-anti-constant or
unmeasured-mutation-lane, assertion-roulette, single-atom-monoculture —
pressure-ordered into the next session's backlog (0048's pattern).
**Why this defers the slow-lane sizing honestly:** if 2b was chosen, the
*absence* of a real mutation score is itself a standing gap the loop surfaces —
so the decision to ever build 2a is work the loop hands a future session, not a
v1 commitment buried in prose.

### piece 6 — orthogonality *(standard: deliberately-uncorrelated quality metrics)*
**Bar:** record, as an explicit claim, which blind spot each QA layer covers and
which it shares — deterministic tests, gate receipts, organs, test-organ. The
field uses *uncorrelated* metrics because each alone is gameable; the repo's
four layers are not yet *provably* orthogonal.
**Teeth:** refuse the claim "the composition covers it" until the layers' blind
spots are shown independent (the audit finding: layers 1 and 2 both check
structure at the IO seam, neither checks correctness), or a cross-layer
correctness sensor is named.
**Honesty flag for the build:** this piece may be a *claim-to-record* (a report),
not a buildable fold. If its fold cannot be stated, demote it to a report and
say so — do not ship an organ-shaped thing with no teeth.
**Glue:** this is the seam to a future parent assurance-site (the four layers as
four seats); building it is what makes that composition possible later.

---

## What the skill IS, once built (the repeatable experience, stated plainly)

A **definition-of-done for tests** (piece 1's archetypes + piece 3's smell bars
+ piece 2's power requirement) + a **review rubric** (the reviewer seat, type-
dispatched) + a **non-bypassable enforcement gate** (the seams + §A's no-
override discipline) + a **self-surfacing backlog** (piece 5). Any agent runs
it; it refuses weak tests the way the merge fold refuses mock-only receipts;
its own holes become its own next work. Every component is standard; the
composition and the un-overridable enforcement are the repo's.

## Merge protocol
- Each piece lands as a stamped increment with its own done-line, its own
  negative-path test, and a real send_back on the trunk before it counts (a seat
  that has only ever said admit is a mock).
- The site is admitted real only when piece 4's acceptance criterion holds (it
  reproduces the hand-audit). Until then it judges nothing on the trunk.
- Every piece's done-line must state its standard-practice name in one line, so
  the lineage spine survives into the built artifact and the next rediscovery is
  pre-empted.

# Ontogrammatic Systems

*A typing discipline for the generated surface — at every scale, across human, machine, and composed work.*

---

Software 3.0 — instruction-shaped behavior over context — is producing more artifacts than anything in the history of computing. We don't yet have a discipline for trusting them. This document names one.

The discipline is **ontogrammatic systems**: a way of typing the formation of generated things so that what they came from, what shaped them, and what their existence now obligates are all inspectable and composable.

This is not a framework, a methodology, or a workflow. It's a layer below those — the same way filesystems sit below applications and HTTP sits below specific protocols. Worlds, models, ontologies, knowledge graphs, simulations, agent harnesses, schema registries, semantic webs, and workflow engines are not competitors to ontogrammatic systems. They are *reality cuts* of the same underlying field. The discipline is what makes the cuts addressable in shared vocabulary.

The document has three reading depths and an appendix. Each is a different path through one argument.

- **Depth 1 — Front door** (sections 1–6). The gap, the claim, the failure modes, the substrate. Ten minutes.
- **Depth 2 — Reference** (sections 7–12). What the discipline actually is, in working form.
- **Depth 3 — Deep theory** (sections 13–17). Why the layer exists and what it makes possible.
- **Appendix** (section 18). This document's own formation trail.

---

# Depth 1 — Front door

## 1. The gap

You have used a code generator, a documentation engine, an AI assistant, an agent harness, or a model pipeline. After a while, each of them produces the same shape of failure.

The system generates a lot. Each output looks fine in isolation. Aggregated, the outputs pile up faster than anyone can verify. Users stop reading. Downstream consumers fall back on hand-maintained references. Decisions get re-justified out-of-band because the generated record is too dense to navigate and too unverifiable to trust. The system continues to function in a degraded mode for months or years, generating ever more surface that ever fewer people consult.

This is not a quality problem in any single generator. The quality is sometimes fine. The problem is that *nothing in the system records how the artifact came to exist*, so nothing downstream can check whether it should be trusted. The chain of reasoning, the contracts that admitted it, the source events that motivated it, the downstream things its existence now requires to change — none of those are addressable. They live in the conversation, the commit history, the team's heads, the inference that produced it. They die there.

Generation has scaled. Trust has not. The generated surface has become fog that looks like signal.

This is the gap.

## 2. Why now

Software 1.0 was code. The discipline that carried trust was types, tests, and compilation. Type errors prevented certain failures structurally. Tests caught others empirically. Compilation refused incoherent programs at the door.

Software 2.0 was learned weights. The discipline that carried trust was training data, benchmarks, and evaluation. You couldn't read a neural network the way you read a function, but you could measure it against held-out data and reject models that failed.

Software 3.0 is instruction-shaped behavior over context — prompts, agent loops, retrieval-augmented pipelines, multi-turn conversations, tool-using systems. The shift is not subtle: the system's behavior is now *configured at inference time* by what's been loaded into its context, not by what was compiled or trained. Different prompts produce different programs from the same model. Different retrieved documents produce different reasoning from the same prompt. The program is the context.

The discipline that carried trust in 1.0 doesn't apply: there is no compiler. The discipline that carried trust in 2.0 doesn't apply directly: benchmarks measure model capability, not context-conditioned behavior. We are running 3.0 systems with no native trust mechanism, and the consequences are visible everywhere generation has scaled — documentation, code, design, research, creative work, agent traces.

We need a layer below 3.0 that does for instruction-shaped behavior what types did for code and benchmarks did for weights. That layer is what this document is about.

## 3. The failure trio

The gap shows up as three specific failure modes. The discipline either resists them operationally or it's decorative.

**Slop.** Generated artifacts that pass formal checks but contribute nothing. Well-formed documents that nobody needs. Plausible code that implements no requirement. Coherent prose that adds no information. Slop is the most common failure of generation-without-discipline because it requires no malice and no error — the system just keeps producing structurally-valid outputs faster than the structure can be tested for value. The Machine that gates against slop has to check not only "is this well-formed" but "does this contribute," and most systems have no vocabulary for the second question.

**Heap.** The accumulation problem. Generated artifacts persist. Versions multiply. Cross-references calcify. The system grows in size monotonically because nothing has a principled discipline for what to forget. After enough time, no reader can navigate the accumulated surface, no replay can verify any specific decision, and the system collapses under its own weight even though no individual artifact was wrong. The heap problem is worse in generated systems than in normal programs because the lineage *is* the trust — you can't just drop old data without invalidating the chain that justifies the present state.

**Degenerate circles.** Generated artifacts whose existence obligates the generation of more artifacts, indefinitely. A draft requires a summary requires an index requires a glossary requires a cross-reference requires a fresh draft. Each step is structurally sound. The cycle preserves formal discipline at every link. The aggregate behavior is pathological — endless generation of mutually-referencing well-formed surfaces with no anchoring to anything outside the loop. This is the failure mode that current agent harnesses produce most spectacularly: an agent given recursive obligations and no convergence brake will fill a directory with thousands of internally-consistent artifacts that collectively say nothing.

The three are not independent. Slop produces heap. Heap encourages degenerate circles (because no one can detect that the new artifact is a fresh instance of an existing one). Degenerate circles produce more slop. The trio compounds.

The trio is primarily a failure mode of **authored** ontograms — things a human, an agent, or a language model decided to produce. Authored ontograms are vulnerable because the authoring step has no native discipline against contribution-free generation. **Programmatic** ontograms — those emitted by deterministic processes given typed inputs — have a different failure shape: hook drift (the inputs change meaning), contract version skew (the process is correct against an outdated contract), and replay non-determinism (the process was supposed to be deterministic but isn't). The discipline has to resist both families.

The distinction between authored and programmatic ontograms is load-bearing throughout this document. It is the second axis (alongside inference grade) that determines what trust composition rule applies to a given artifact. The discipline either resists the failure modes of both families operationally, or it's decorative.

## 4. Why worldbuilding is the proof case

Most domains let you fake the discipline. A documentation engine can produce thousands of plausibly-related pages and the trust degradation is slow — readers stop checking, things go stale, but the system continues to function in degraded form for years. A code generator's failures are visible within seconds (compile errors, runtime crashes). Either the trust problem is invisible, or the trust mechanism is borrowed from a lower layer.

Worldbuilding sits in the worst possible spot. **Trust degrades fast, the failure is structural, and there's no underlying compiler to catch it.** A world with broken canon doesn't crash — it becomes *uninhabitable* for anyone who tries to use it. Characters contradict themselves. Geography breaks. Cosmology becomes incoherent. The history doesn't add up. A reader (human or agent) trying to actually inhabit the world hits these contradictions immediately, and the world becomes useless without ever throwing an error.

Worldbuilding-with-AI compounds this. A language model proposing canon changes is exactly the failure surface the discipline is designed for: prolific generation, no native typing, no native trust mechanism, no native gate. Each of the three failure modes appears at speed. Slop arrives as plausible canon proposals that add nothing the world needed. Heap arrives as accumulated drafts and contradictions and abandoned subplots. Degenerate circles arrive as proposed lore that requires proposed lore that requires proposed lore.

If the discipline survives worldbuilding-with-AI, it survives anything. If it doesn't survive worldbuilding, it's decorative. This is the same logic by which database researchers stress-test against banking workloads and distributed systems researchers stress-test against consensus under partition. Pick the worst case. Survival there gives you the easy cases for free.

The worldbuilding case grounding this document is a private cosmology project called Cardinal. The point is not Cardinal itself — the point is that grounding the discipline in a real, ongoing worldbuilding project run by the same person who is designing the discipline produces the tightest possible feedback loop. The designer is also the canonical reader. The discipline either makes the work more inhabitable or it doesn't, and the answer arrives in the same week the discipline is proposed.

## 5. The substrate claim

What's needed is not another framework. The 3.0 surface already has too many frameworks. What's needed is a *layer*.

A layer doesn't tell you what to build. It tells you what the things you build sit on top of. HTTP doesn't tell you what your application does; it tells you what a request and response look like, and lets the rest compose. Filesystems don't tell you what to put in your files; they tell you how files are named, opened, locked, and persisted, and let the rest compose. A layer earns its place by being indifferent to what flows through it as long as the typing discipline holds.

The ontogrammatic layer is indifferent to whether the formation is human writing prose, a language model generating a draft, a procedural generator emitting a world map, a CI pipeline running a check, a multi-agent system deliberating a decision, or a human-and-AI pair iterating on a design. Each is a *cycle*. Each has source events. Each produces typed artifacts. Each can be gated, inspected, and composed through the same vocabulary.

The substrate has four pieces. They are not large.

1. A **typed form** with declared kind, source event, validating contracts, downstream obligations, and a chain back to source. This is the *ontogram* — the atomic unit of trust in the discipline. Anything anyone generates can be turned into one.
2. A **formation cycle** in seven elements — what exists, what could come next, what constrains it, the act that cuts, what emerges, the chain back, the irreversible commit. The cycle is identical across scales and substrates. It works at the level of a single edit, a single session, a single nightly run, a single year of work.
3. A **gate vocabulary** of three verdicts — admit, refuse, instrumentation-needed. The third verdict is where the discipline gets its self-extending property: when something can't be evaluated, the system records *what would let it be evaluated* and treats that as the source event for closing the gap.
4. An **etymology discipline** — every admitted ontogram carries not only its source (provenance) but the active chain of obligations its existence creates downstream. Provenance says *where did this come from*. Etymology says *where did this come from, and what does its existence now require*.

Together these four pieces make the generated surface *typable, inspectable, replayable, and bounded*. Each one is small. The composition is what does the work.

## 6. The discipline named

The full name of the discipline is **sympoietic ontogrammatic etymology** — three words for three layers. *Sympoietic* names the binding layer: things in the field are made-with, not self-made; source events, contracts, agents, ontograms, and the field itself co-produce each other. *Ontogrammatic* names the grammar layer: the structural rules of being and becoming, the seven-element cycle, the contracts that constrain potential, the operator's cut. *Etymology* names the temporal-trail layer: how formation, inheritance, and propagation accumulate across time as the substance the field is made of.

In daily use, the short forms are enough. *Ontogram* for the typed form. *Ontogram field* for the active container in which ontograms relate. *The cycle* for the seven-element formation pattern. *The Machine* for the gating discipline that admits or refuses. *Etymology* for the active chain of obligations. The full triple-word name appears when the layer claim itself needs defending.

The discipline is in active use in five projects as this document is being written. Each names the same seven-element cycle in its own surface vocabulary. None of them required the discipline to be imposed; the discipline was *extracted* from observing that the same cycle was running in all of them. The translation surface between them is one section of the technical reference (Depth 2). The fact that the cycle survives translation across substrate, scale, and domain is the evidence that the layer claim is real.

---

# Depth 2 — Reference

## 7. The ontogram

An ontogram is a typed form whose source, structure, and downstream effects are all inspectable. The minimum record is small:

```yaml
ontogram:
  id: <stable handle>
  kind: <type name>
  authorship: authored | programmatic
  inference_grade: deterministic | low-temperature | seeded | creative | judgment | deliberation
  source_event:
    type: <what happened>
    reference: <path | id | hash>
    timestamp: <iso8601>
  validated_by:
    - <contract id @ version>
  generative_effects:
    - <downstream form now required>
  etymology:
    formation: <path through the cycle>
    inherits_from:
      - <contract or prior ontogram>
    will_propagate_to:
      - <downstream form>
```

`source_event` is provenance — the watched input that started the formation. `validated_by` records which contracts admitted it. `generative_effects` and the three `etymology` fields are the active part: they record what the existence of this ontogram now requires of the rest of the field. An ontogram with full etymology *changes what else can be generated*. An ontogram without it is a record.

`authorship` and `inference_grade` together carry the artifact's trust shape. They are **orthogonal axes**, not redundant. Authorship records whether a human or agent made the formation choice (authored) or whether a deterministic process emitted the artifact from typed inputs (programmatic). Inference grade records how much the output depends on non-replayable judgment, from bit-exact deterministic to full multi-agent deliberation. The two combine into four cells with different composition rules:

| | Deterministic output | Inference-graded output |
|---|---|---|
| **Authored** | Hand-written YAML, manually-curated contracts | Human writing prose, LLM proposing canon |
| **Programmatic** | Prompt-writer composing a sysprompt, CI emitting a typed report | A pipeline wrapping LLM calls under fixed contracts |

Each cell has a different trust composition rule. An authored deterministic ontogram is trustworthy because a named author stood behind it under a declared contract. A programmatic deterministic ontogram is trustworthy because the process is replayable. An authored inference-graded ontogram is trustworthy *within its declared inference grade*. A programmatic inference-graded ontogram inherits inference grade from its constituent calls and composes through the discipline of its process. The substrate makes the cell visible so downstream consumers can compose against the right grade.

What an ontogram is *not*: a record, an object, a model node, or an ontology entry. Each of those is a *reality cut* of an ontogram through a particular reader's lens. A record is what an ontogram looks like through a persistence cut. An object is what one looks like through a behavior cut. A model node is what one looks like through a representation cut. An ontology entry is what one looks like through a categorical cut. None of these is wrong; none is whole.

The decisive difference is the active part: an ontogram's existence in the field *creates obligations* on other ontograms. This is what makes the field self-extending. Generate one ontogram with declared `generative_effects`, and you have generated source events for the next cycles by implication.

## 8. The cycle

A source event becomes an admitted ontogram by traversing seven elements in order:

| # | Element | Role | Failure if divergent |
|---|---|---|---|
| 1 | **SUBJECT** | What exists; the state at rest before this cycle | Subject-drift — the description no longer matches what's there |
| 2 | **POTENTIAL** | What could come next | Slop proliferation — options spawn without resolution |
| 3 | **CONTRACT** | What constrains the potential | Vaporware fence — the contract doesn't grip |
| 4 | **OPERATOR** | The act that cuts; disappears in the act | Wishy-washy non-cut — no decision actually made |
| 5 | **ARTIFACT** | The typed ontogram emerges | Hallucination — what's produced isn't what was sought |
| 6 | **LINEAGE** | The chain back to source; etymology accumulates | Lost provenance — the artifact isn't traceable |
| 7 | **GATE** | Irreversibility commit; the ontogram joins the field | Silent rollback — commits unwound without record |

The cycle does not terminate. Each GATE opens onto the next SUBJECT. The new state-at-rest is the old state-at-rest plus the freshly-admitted ontogram. The cycle is *bounded at every scale* and *unbounded in the recursion direction*.

The cycle works at every scale. A single keystroke that triggers an autocomplete is a cycle. A single AI agent emitting a response is a cycle. A multi-day worldbuilding session is a cycle. A six-month software project is a cycle. The seven elements appear at each scale. This is not an analogy — it is the same structural pattern, recurring through `Φ(X, +1)`: every element of the cycle has its own internal seven-element cycle at the next zoom level.

## 9. The Machine and its three verdicts

The Axiomatic Machine is the discipline's gating mechanism. It does not generate ontograms. It certifies them. Given a source event, a proposed ontogram, and the applicable contracts, the Machine performs a minimum of six checks and returns one of three verdicts.

The six checks:

- **Schema valid** — the proposed ontogram conforms to its declared kind schema.
- **Lineage present** — the etymology fields are populated, not gestural.
- **Gate defined** — the contracts name a GATE condition the Machine can evaluate.
- **Propagation declared (form)** — `generative_effects` and `will_propagate_to` are present as fields.
- **Propagation non-trivial (function)** — at least one of `generative_effects` and `will_propagate_to` is non-empty, AND the named downstream forms resolve to real receivable obligations in the current field state.
- **Forbidden forms absent** — no contract-forbidden field, value, or shape appears.

The split between form and function of propagation is load-bearing. A formally-valid record with empty `generative_effects` and `will_propagate_to` is the smallest possible slop case: it satisfies every structural check, yet its existence in the field does nothing. The Machine must refuse it, or the discipline collapses into "better metadata." This is what makes the etymology-vs-provenance distinction operational rather than ornamental.

Implementations may add domain-specific checks. They may not skip the minimum six.

**Authorship affects which additional checks run.** Authored ontograms require attestation checks: who authored, against what contract version, with what evidence of judgment. Programmatic ontograms require process checks: the inputs are enumerable, the hooks resolved cleanly, the process replays deterministically (if it claims to). These are not different minimum sets — the six above hold for both — but the Machine's full check vocabulary differentiates so that authored work isn't held to replay standards it can't meet, and programmatic work isn't held to attestation standards that don't apply to processes.

The three verdicts:

- **Admit** — all checks pass; the ontogram joins the field; downstream cycles inherit it.
- **Refuse** — at least one check fails; the ontogram is rejected with a recorded receipt naming which check.
- **Needs instrumentation** — a check cannot be evaluated because evidence to evaluate it is missing; the Machine names the missing observability as a high-value question and the cycle stays open until the gap is closed.

The third verdict is the load-bearing trick. Most systems admit two outcomes — pass or fail — and treat their absence as silent failure. The discipline's third verdict turns the absence into a typed source event for the cycle that would close it. **Gaps in the discipline become the discipline extending itself**. This is what gives the substrate its self-improving property without requiring optimization or learning.

Each verdict comes with receipts. Every check that ran is recorded with its result and a pointer to the evidence it ran against. A verdict without receipts is not a Machine verdict.

## 10. Etymology vs provenance

Provenance and etymology are not synonyms. The distinction is operational, not philosophical.

**Provenance** says: *this came from there.* It is metadata about origin. It is passive — recording provenance does not change the system. The `source_event` field is provenance.

**Etymology** says: *this came from there, and here is how its meaning, type, inheritance, and obligations evolved from that origin.* It is active — etymology changes the system by being part of the system. An ontogram with etymology *forces* downstream forms to update because its existence has effects.

A system that records only provenance produces artifacts with origins but no obligations. The artifacts pile up; the relationships between them die. This is the heap problem from the failure trio. A system that records full etymology produces artifacts whose existence *operates on the rest of the field*. The propagation is the trust mechanism.

Four fields on an ontogram, separated by passive (provenance) vs active (etymology):

| Field | Carries | Active? |
|---|---|---|
| `source_event` | The watched input that started formation | **Passive** (provenance) |
| `etymology.formation` | The path through the cycle from source to admitted | **Active** — admission decisions hang on it |
| `etymology.inherits_from` | The contracts that admitted this ontogram | **Active** — other ontograms are bound by the same contracts |
| `etymology.will_propagate_to` | The downstream forms that must change because this ontogram now exists | **Active** — existence creates obligations |

The first is provenance. The other three are etymology. Together they are the ontogram's **etymology of form** — the active layer that distinguishes the discipline from passive metadata systems.

## 11. The CLI shape

The discipline's first implementation is shaped like `curl`. One CLI program. One skill manifest. One reference document. One invocation pattern that composes everywhere.

A session-collector reads typed inputs from disk, writes typed outputs to disk, and returns a typed verdict to the shell. Composition is shell composition. Inspection is `cat`. Version control is git. None of which needs to be invented.

The minimum verb set:

- `collector open --kind <session-kind> --contract <id@version>` — open a session, snapshot the field state, return a session id.
- `collector record --session <id> --event <event spec>` — record a source event against an open session; the Machine runs and emits a verdict.
- `collector close --session <id>` — close a session, lock the GATE, emit the final session ontogram.
- `collector replay --session <id>` — replay a closed session from its manifest and produce the same artifacts deterministically.
- `collector ask --session <id> --query <q>` — read a session at a requested depth, returning a structured view.

Four exit codes corresponding to the three Machine verdicts plus a substrate-error code. Receipts to stderr. Structured output to stdout. Config in a project file. State in a session directory.

This is not a placeholder for a richer interface. It's the intentional shape. A `curl`-shaped substrate composes against any agent harness, any CI pipeline, any human workflow, any IDE plugin, any chat interface. The composition surface stays small because the substrate stays small. Larger ambitions (distributed sessions, multi-machine coordination, real-time agent collaboration) are honest deferments to later versions. The substrate at this stage is single-process, single-machine, sequential. Most of the hard distributed-systems problems evaporate at this scope. The ones that don't are named in the strain points (Appendix).

The substrate's job at this stage is to *make typed formation cheap*. If the cost of recording etymology is one CLI invocation per cycle, agents will record it. If it requires a service, a database, or a multi-step protocol, they won't.

## 12. Translation across projects

The same seven-element cycle runs under different surface vocabulary in different projects. The Rosetta surface — *Rosetta* in the sense of a translation table, not in the sense of a fixed vocabulary — maps current projects to the cycle without imposing the cycle's own terms on any of them. Each project keeps its words.

A condensed view across five projects currently in scope:

| Element | Holon | SubProtocol | Reflex | Worldbuilding | Regencies |
|---|---|---|---|---|---|
| SUBJECT | `void` / structure | source state | target state | world canon | source-tier datapoint |
| POTENTIAL | `silence` / potential | space of projections | mutation intent | LLM proposal | open gap |
| CONTRACT | `THE_IMPOSSIBLE` | host constraints | collector identity | 0.1/0.2/0.3 protocols | cycle type |
| OPERATOR | `prime` / Click | request-resolution | boundary-crossing emission | human commit motion | cycle declaration |
| ARTIFACT | `σ` measurement | projected pointer | typed event | admitted canon | datapoint |
| LINEAGE | holonomy chain | regenerate-from-source | `lineage:` token | `source_state` hash | `prior_hash` |
| GATE | ACCEPT gate | resolution lock | (soft, v0.1) | human commit | cycle close |

Every cell in this table existed before the discipline was named. The discipline was extracted from observing that the same cycle was running in five places under five different sets of words. This is the load-bearing evidence for the layer claim: the cycle isn't a model imposed on the work — it's a structural invariant the work was already exhibiting.

The translation surface is *on-demand*. When a new project asks where its terms fit, the table grows. When the table strains against a project's actual practice, the discipline is wrong and the table records the strain. The strain points are deliverable observations, not failures.

---

# Depth 3 — Deep theory

## 13. Why a layer, not a framework

The temptation in fields like this is to build a framework: a runtime, a service, a SDK, a set of standardized adapters. Frameworks are easier to fund, easier to demo, easier to write conference papers about. They also fail the layer test.

A layer is judged by whether what sits on top of it doesn't need to know it exists. You can write a web application without knowing how TCP retransmits packets. You can edit a file without knowing how the filesystem journals writes. The layer earns its place by being *boring* underneath the things that matter to the user.

A framework demands attention. Its conventions, its lifecycle, its hooks, its release cadence, its breaking changes — all of these become part of the application's surface. Once you have adopted a framework, the framework is in your stack forever, and refactoring out of it is more expensive than refactoring out of a layer because the framework's shape is woven through your code.

The ontogrammatic discipline is designed to be layer-shaped because the alternative — a framework — would compete with the work it is supposed to make composable. The substrate's only required contribution to any project is: *if you want your generated artifacts to compose with others, type them this way.* That is it. The substrate has no opinion about your domain, your language, your tooling, your team structure, your release process. It has an opinion about one thing only: the shape of a typed formation trail.

This is also why the substrate must be cheap. A layer that costs significantly more than the alternative is not a layer; it is a framework with a layer's vocabulary. The CLI shape (section 11) is not an aesthetic preference. It is the cost-discipline that lets the substrate stay layer-shaped.

## 14. Sympoiesis and the registers of making

Donna Haraway, in *Staying with the Trouble* (2016), coined *sympoiesis* against Maturana and Varela's *autopoiesis* — *self-producing*. Her argument was that nothing self-produces in isolation. Systems make-with their environments, neighbors, substrates, and prior states. The act of production is always mutual.

The ontogrammatic discipline is sympoietic, not autopoietic, in a structurally important way. Ontograms don't self-produce. They are co-produced by source events, contracts, agents, the field's accumulated state, and other ontograms whose generative effects motivated them. An ontogram's existence forces other ontograms into being — not as a side effect, but as the central mechanism by which the field grows.

This matters because it lets the discipline contain the *agentic register* — the register in which agents do work, propose new forms, watch source events, and act on contracts — as **one mode of making among several**, not as the master mode. The other modes are equally real:

- Source events arriving without an agent (a file is committed, a contradiction surfaces, a threshold crosses).
- Structural propagation forced by an ontogram's `generative_effects` (existence forcing existence).
- Field accumulation as the integrated product of many cycles (the holonomy of the history).
- Recursive co-production across scales (a parent cycle's GATE opens its child cycles' SUBJECTs).

A discipline that named only the agentic register would describe the visible work and miss the substrate. The agent acts, but the act is embedded in a sympoietic process the agent does not solely cause. Recognizing this prevents the common failure of agent-centered frameworks: treating the agent as the source of trust rather than as one participant in a process whose trust is *substrate-derived*.

Practical consequence: agents in the discipline are themselves ontograms. Their outputs are gated through the same Machine. They get no trust exemption. Their etymology — what they did, what admitted their actions, what their actions now obligate — is recorded the same way every other formation is. This is what makes the agent stack composable: agents are not infrastructure, they are participants.

## 15. The recursive ambition

The language for working with AI is also the language for working with humans, and also the language for working with composed systems of both. Because at every scale the structural cycle is the same.

A pull request is an instance of the cycle. The SUBJECT is the branch state. The POTENTIAL is the proposed change. The CONTRACT is the review criteria. The OPERATOR is the act of review. The ARTIFACT is the merged state. The LINEAGE is the commit history. The GATE is the merge.

A board meeting is an instance of the cycle. The SUBJECT is the state of the business. The POTENTIAL is the proposed decisions. The CONTRACT is fiduciary duty plus governance documents. The OPERATOR is the deliberation. The ARTIFACT is the resolutions passed. The LINEAGE is the minutes. The GATE is the recorded vote.

A worldbuilding session is an instance of the cycle. So is a fine-tuning run, a regulatory filing, a clinical trial, a code review, a peer-reviewed paper, a marriage proposal, a treaty negotiation. Each has its own surface vocabulary, contracts, and stakes. The cycle's seven elements are visible in each.

This is not a claim that everything is the same. The claim is that *the typing discipline for trust over generated structure is the same regardless of substrate*. Once the layer is shipped, the work of teams using AI to build software, scientists running computational experiments, writers collaborating with language models, regulators auditing automated decisions, and worldbuilders maintaining cosmology — all of these become *the same kind of work with different content*.

The recursive ambition is to make that visible. A reader of the discipline should be able to look at any generated artifact, in any domain, at any scale, and ask: *what was the source event? what contracts admitted this? what does its existence now obligate?* If those questions have answers, the artifact is trustable. If they don't, the artifact is fog regardless of how good it looks.

This is the long-game claim. The 1.0/2.0/3.0 progression is not a sequence of fashions. Each generation added a new register of generation and required a new register of trust. We are in the middle of the third register's growth phase, and the trust discipline for it has not yet been named publicly. This document is one attempt to name it. There will be others. The goal is not to win — the goal is to make the layer real enough that the discipline persists when this document's specific framing is replaced by better ones.

## 16. The prompt-writer cycle

The recursive ambition becomes architecturally specified — not aspirational — at the lowest level of AI work: the act of shaping the operator. The system prompt that configures a language model for a session is itself an ontogram. The session it opens is a cycle. The closing of the session emits a session ontogram whose etymology references the system prompt that opened it. Long arcs of human-AI collaboration become one continuous etymology chain.

This is the substrate operating on its own delivery.

Today, system prompts are predominantly **authored** — written by hand, tuned by intuition, versioned by ad-hoc convention. The substrate's lift is to make them **programmatic**: emitted by a *prompt-writer cycle* whose inputs are typed roles, entry conditions, session state, user identity, current context, and the outputs of declared hooks. The prompt-writer composes the system prompt deterministically from these inputs. The composed prompt is the cycle's ARTIFACT. The session it opens inherits its etymology.

The prompt-writer cycle in cycle terms:

- **SUBJECT** — user identity, applicable contracts, prior session state, available tools and hooks.
- **POTENTIAL** — the space of valid system prompts the writer could emit given those inputs.
- **CONTRACT** — the prompt-writer's typing rules: which behavioral roles may be activated, what shape the output must have, what's forbidden, what entry conditions require.
- **OPERATOR** — the prompt-writer running as a hooked process; inputs come from declared hooks (memory, preferences, search, time, location, project state), each with its own contract.
- **ARTIFACT** — the composed system prompt, with declared `authorship: programmatic`, an inference grade inherited from the highest-graded hook, and `generative_effects` naming the session it opens.
- **LINEAGE** — chain back through the user's prior sessions, the prompt-writer's contract version, the role definitions in use, the hook contracts at composition time.
- **GATE** — the system prompt is loaded into the model's context; the session opens.

Every turn that follows is etymology against the emitted prompt-ontogram. When the session closes, the *whole session* becomes an ontogram whose `inherits_from` references the prompt-ontogram that opened it. The next session's prompt-writer cycle can in turn inherit from this session ontogram. The substrate threads continuity across sessions without storing them as monoliths — the etymology is the storage.

**Determinism is transitive through declared hooks.** The prompt-writer is deterministic given its inputs. The hooks are either deterministic given their inputs (a preferences file, a project state) or honestly inference-graded (a memory retrieval that summarizes). Therefore the prompt-ontogram is deterministic given the *hook outputs at composition time*, and inherits the inference grade of the highest-graded hook. A prompt-writer that calls a deterministic-only hook set emits a deterministic prompt-ontogram. A prompt-writer that includes inference-graded memory emits an inference-graded prompt-ontogram. The downstream session inherits accordingly.

**Roles become first-class.** The behavioral templates that show up in current system prompts — builder, critic, scout, guardian, strategist, teacher, regenerator, and others — become typed ontogram kinds with declared activation conditions, containment rules, and output shapes. The prompt-writer composes against the role corpus rather than re-authoring role descriptions per prompt. New roles are added through the same Machine-gated cycle as any other ontogram. A role whose contract is violated in practice is refused or sent back as `needs instrumentation`. The role corpus is itself a field with its own etymology.

**Conflicts between roles are part of the prompt-writer's contract.** A "builder" role demanding "make the artifact real" and a "critic" role demanding "refuse weak structure" can co-activate, but the prompt-writer's contract specifies the resolution: which role's containment rule takes precedence in conflict, when the conflict produces a deliberate tension the prompt should preserve, when one role suppresses another. The resolution is not punted to the model — it's part of the programmatic composition.

This is the *canonical authored-to-programmatic lift*. The substrate's other reference projects make the same move in their own domains: SubProtocol regenerates pointers programmatically from source rather than storing authored pointers; Reflex emits the lineage token programmatically at boundary-crossing rather than asking the agent to author one; worldbuilding-harness lifts artifacts from 3.0 (authored LLM proposals) toward 1.0 (programmatic deterministic structure) by extracting typed form from human/AI work. The prompt-writer cycle is the same move applied to the *act of working with AI itself*.

The implementation is real engineering. A prompt-writer that handles role composition, hook integration, length budgets, ordering, conflict resolution, and inheritance is a non-trivial compiler. The CLI shape extends with a verb (`promptwriter compose --user <id> --entry <kind> --hooks <hook-set>` or its equivalent in the substrate CLI). The role corpus is a curation task — the current operator profile has roughly seventeen templates, which is too many to typify in one pass; a starting set of five to seven, chosen for their orthogonality, is the buildable scope.

None of this is required for the substrate claim to be coherent at the level of the rest of the document. But it is required for the recursive ambition to be *architecturally honest*. Until the prompt-writer cycle is built, the discipline operates on every artifact except its own delivery — which is the most visible place a layer claim has to hold for it to be load-bearing rather than aspirational.

## 17. Honest containment of authorship and inference

Some cycles in the discipline are not deterministic. A language model proposes a canon change. A human makes a judgment call. A multi-agent system deliberates without a fixed protocol. The output of these cycles is shaped by inference that cannot be replayed bit-exact.

The discipline does not pretend otherwise. Inference is contained as a *graded* property on every ontogram, sitting alongside authorship. The two together form the trust shape of any artifact in the field.

The graded inference vocabulary, declared on every ontogram:

- **Deterministic** — bit-exact replayable from inputs.
- **Low-temperature** — language model output with temperature near zero; deterministic *modulo* seed and floating-point reproducibility.
- **Seeded** — sampled with a recorded seed; replayable on the same hardware.
- **Creative** — full-creative-mode generation; not bit-exact replayable, but the inputs and the generation context are recorded.
- **Judgment** — a human or agent made a decision; the rationale is recorded as part of the ontogram's etymology but the decision itself isn't replayable.
- **Deliberation** — multi-agent or multi-human deliberation; the trace is recorded; the outcome was negotiated and isn't replayable as a function of inputs.

Each grade composes through the field with its own rules. A consumer that requires deterministic etymology refuses every higher grade. A consumer that tolerates judgment-grade etymology refuses deliberation-grade by default. A consumer that wants to *upgrade* an inference-graded artifact to a lower grade can do so by opening a verification cycle whose contract demands evidence the original cycle didn't provide. The upgrade is itself a new ontogram with its own grade — the discipline preserves the inference grade of every ancestor in the chain.

**Authorship grades operate orthogonally.** An authored deterministic ontogram and a programmatic deterministic ontogram have different attestation requirements. An authored creative ontogram and a programmatic creative ontogram have different process requirements. The Machine's full check vocabulary distinguishes. Trust composition through the field treats them as separate trust slots, not as one combined grade.

This is the same discipline as the third verdict (instrumentation-needed) applied to artifact quality rather than evidence presence. Rather than pretending the system is fully deterministic and fully authored when it isn't, the substrate makes the *grades inspectable*. A consumer chooses what trust shape is acceptable for the use case. A pipeline composes against the shape its contracts demand. A regulator audits against the shape required by jurisdiction.

Inference is not an embarrassment to be hidden. Authorship is not a status to be elevated. Each is a *property of how the artifact came to exist*, and the discipline's contribution is to make both honest. A discipline that demanded determinism everywhere would be unusable. A discipline that ignored the difference would be untrustworthy. The grade move — applied to both axes — is the only way to be both usable and honest.

---

# Appendix

## 18. Formation trail

This document has its own etymology. The trail is preserved because the discipline operating on its own delivery is part of what makes the claim credible. This document is **authored**, with **judgment-grade** inference (one human's analytical and aesthetic decisions, with conversational input from a language model whose contributions were filtered through the human's judgment at every turn). A future programmatic version, emitted by the prompt-writer cycle's documentation analog, would carry a different grade. The discipline forces the grade of every artifact in its field to be inspectable, including this one.

1. **Rosetta v0.1** (morning of 2026-05-20) — A translation pattern, framed as cross-project Rosetta surface. Established the seven-element cycle and the six-project translation table. Treated closure as convergence rather than termination.
2. **Agentic Ontogrammatic Etymology** (afternoon) — Corrected: the top-level term must *contain* world / model / system / holon as reality cuts, not reject them. Ontogram became the core noun.
3. **Sympoietic Ontogrammatic Etymology** (afternoon) — Corrected again: *agentic* picks out a role, not a layer. *Sympoietic* names the binding layer that connects form to meaning through mutual production.
4. **SYSTEM.md** (evening) — Compressed and reformatted as a layered technical reference, with the meta-convergence check added to brake against perpetual front-word substitution.
5. **Dialogue passes** (continuous) — Several review iterations surfaced engineering omissions (concurrency, error model, identity scheme, GC, backwards compatibility, agent mechanical definition), the CLI scope correction, and the framing of worldbuilding as the deliberate stress-test case.
6. **This document — first pass** — A layered write-up positioning the discipline in the 1.0/2.0/3.0 progression, with the failure trio as the spine and the recursive ambition stated.
7. **This document — second pass** — Added the authored/programmatic distinction as the second trust axis alongside inference grading; added the prompt-writer cycle as the canonical authored-to-programmatic lift and the architectural realization of the recursive ambition; added the sixth minimum Machine check (propagation non-trivial as function, separate from form); revised §17 to handle both axes honestly.

**Current strain points** (in priority order):

- **Reflex hard-GATE.** v0.1 is a soft gate; the discipline's hard-gate discipline is not yet enforced in one of its five reference projects.
- **Axiomatic Machine as standalone skill.** Currently a role spread across multiple existing skills (`check-skill`, the Reflex validator, runtime3 hooks). Naming and shipping it as one composable component is v0.2 work.
- **Prompt-writer cycle implementation.** The architecture is named; the prompt-writer doesn't yet exist. Until it does, the substrate operates on every artifact except its own delivery — which is the most visible place a layer claim has to hold.
- **CLI implementation.** The shape is named; the binary is not yet written.
- **Runnable convergence checks.** Ricci-flatness balance, holonomy accumulation, and gate-lock verification are described in the technical reference but not yet executable.
- **Agent mechanical definition.** The word "agent" is doing work the implementation has not yet specified. Across the reference projects, "agent" means at least three different mechanical things (skill invocation, subprocess, prompt). The discipline either unifies the mechanical definition or stops treating "agent" as one word.
- **Role corpus curation.** The behavioral templates that should become first-class typed ontogram kinds are not yet curated. The current operator profile has roughly seventeen; the starting corpus should probably be five to seven, chosen for orthogonality.
- **Diagrams.** The current document set is prose plus tables. Visual treatment of the cycle, the field, the translation surfaces, and the recursive structure is open work.

**Open coherence questions** (the meta-convergence check, applied honestly):

- The four-plus-one lifecycle vocabulary (event / threshold / loop / cycle / inferred) is asserted without a structural derivation; the closure may not hold.
- The six-budget enumeration (depth / breadth / lineage / compute / reservoir / read) is similarly asserted; v0.2 may surface more.
- The relationship between *generative effects* and *will propagate to* may be redundant at different grammatical moods; needs verification under a non-trivial worked example.
- Cycle-kind typing only earns its keep if the Machine can refuse a *proposed cycle-kind*, not just an ontogram within one. The mechanism is implied but not specified.

**What comes next:**

- A CLI implementation against one project (worldbuilding-harness) is the smallest-shippable v0.2 of the cycle substrate.
- The Axiomatic Machine as a standalone skill that the CLI invokes is the second step.
- The prompt-writer cycle is v0.3 — the substrate operating on its own delivery; the architectural realization of the recursive ambition.
- Cardinal as a worked instance — not as a hypothetical — is the test of whether the discipline survives its proof case. One closed Cardinal cycle with receipts is worth more than another iteration of this document.
- Wider adoption is deferred until the proof case has been demonstrated honestly. The discipline grows by being adopted, not by being promoted.

---

*This document is a single file under revision through dialogue. The discipline it describes operates on itself; this document's etymology is part of the discipline's evidence. If you read this document and felt the gap it names, you are part of the next cycle.*

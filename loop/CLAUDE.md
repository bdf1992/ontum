# loop/ — the loop substrate

Stdlib by default; local-first always — no broker, no daemon, no
network at runtime (hard rule). The blanket no-dependency ban is lifted
(bdo, 2026-06-12): a third-party dependency is admissible when common
sense says it creates real value — don't hand-roll what a mature,
well-kept library does correctly — provided it stays offline and is
named. Prefer stdlib; reach for a dep when it earns its place. Run
everything from the repo root.

## Commands

```sh
# tests (run before every push)
python -m unittest discover -s tests -v
python -m unittest tests.test_loop -v                       # one module
python -m unittest tests.test_loop.Class.test_name -v       # one test

# the loop
python loop/reconcile.py --status          # read-only fold summary
python loop/reconcile.py --until-done      # reconcile passes until done or stuck
python loop/reconcile.py --rebuild-cache-only

python -m loop.orchestrate --status        # field state: pressure vs setpoint
python -m loop.orchestrate                 # the fast ambient loop (ticks)
python -m loop.orchestrate --admit-setpoint '{"step_budget_per_tick":3,"max_inflight_atoms":8,"human_queue_cap":2}' --by bdo

python -m loop.heartbeat                    # one guaranteed beat: tick-only (the cheap, always-safe path)
python -m loop.heartbeat --hook             # in-harness tick-only beat: fail-open, exit 0 always (wired to SessionStart)
python -m loop.heartbeat --drain-limit 3 --by heartbeat.v0   # the paced consumer: tick + fire ≤3 real value-confirm reviews (bdo's external-scheduler gesture)

python -m loop.node inbox                  # the owner's open items
python -m loop.node arcs                    # the arcs and which are confirmed
python -m loop.node confirm-arc --epic <id> --by bdo   # one stamp for an arc
python -m loop.node judge --atom <id> --node <node> --verdict <v> --reason "<r>"
python -m loop.node admit-real --stage <mock-node> --node <real-node> --by <who>

python -m loop.summon                      # open summons, read-only (D-10)
python -m loop.summon --hook               # hook mode: briefing on stdout, exit 0 always

python -m loop.reflect                     # surfaces, rules, drift — read-only
python -m loop.reflect register --surface github-issues --address <owner/repo> --by <who>
python -m loop.reflect rule --kind owner-stamp-queue --surface github-issues --on --by <who>

python -m loop.web render                  # static owner inbox page
python -m loop.web serve                   # localhost inbox with verdict forms

python -m loop.census                      # the part census: which parts carry weight, which are dormant

python -m loop.activity                     # the activity-accounting fold: every wired hook's data collection + usage, read-only, refuses an undeclared collector
python -m loop.activity --json              # the raw dataset (machine-readable)

python -m loop.gaps                        # the gap backlog, pressure-ordered — the top one is the work

python -m loop.parity                      # the RepoPrompt boundedness parity matrix — read-only, fails on a ghost citation
python -m loop.parity --json               # the raw dataset (machine-readable)

python -m loop.digest                      # the owner's merge digest — read-only fold, arc-first
python -m loop.digest --today --json       # today's records as the raw dataset (machine-readable)
python -m loop.digest --since 2026-06-01 --until 2026-06-11

python -m loop.retro                        # the retrospective fold — recurring patterns across all history, read-only
python -m loop.retro --json                 # the raw dataset (machine-readable)

python -m loop.heal                         # the healing fold — where the loop's own teeth bit too sharp or stale, read-only
python -m loop.heal --json                  # the raw dataset (machine-readable)

python -m loop.gate_eval                    # the value-gate eval corpus (charades: matched-variant atoms), read-only
python -m loop.gate_eval score --transcript <p>   # score a panel ("the room") verdict transcript

python -m loop.phrasing check --path <p> --before <f> --after <f>   # the phrasing door: is an edit prose-only? read-only proof
python .claude/skills/branch-ritual/pr.py phrasing --files <p>... --why "<note>" --by <who>   # mark a proven prose-only edit so it lands without an atom (the route)
python -m loop.disposer                    # the slow loop's fence + what it would dispose, read-only
python -m loop.disposer admit-fence --bounds '{"step_budget_per_tick":[2,5]}' --by bdo   # bdo draws the fence
python -m loop.disposer dispose            # self-admit one in-fence proposal (else escalate)

python -m loop.tags                        # the intent tag pool and its drift, read-only
python -m loop.tags admit --dimension intent --value <v> --by bdo   # promote a proposed value

python -m loop.pull                        # the terminal-pull gateway — the piece-scale landable slice + the namespace gap, read-only
python -m loop.pull --json                 # the raw dataset (machine-readable)

python -m loop.inference_queue             # the inference admission queue's stats fold — in-flight, throughput, per-mind latency, saturation, read-only
python -m loop.inference_queue admit --bound <n> --by bdo   # set the in-flight concurrency dial (the gateway's backpressure)

python -m loop.pen new done --slug <slug> --title "<t>"     # the next done-line, from the directory's form
python -m loop.pen supersede-done --abandoning <id> --slug <new> --done "<new bar>" --reason "<honest reflection>" --by bdo   # bdo-only; refuses every session signer (no free "stop working" card)
```

Gotcha: only `reconcile.py` runs as a plain script. `orchestrate`,
`node`, `summon`, `reflect`, `web`, `census`, `digest`, `retro`, and
`pull` import from the `loop` package and must run as modules
(`python -m loop.<name>`) from the repo root.

Every invocation ends with a clear stdout result: `done | report |
needs-you`. Treat `needs-you` as an escalation to surface, not an error
to code around.

## Architecture

### The log is truth; everything else is a fold

`.ai-native/log/` holds three append-only JSONL files — `events.jsonl`,
`receipts.jsonl`, `admissions.jsonl`. The state of any atom is computed
by folding over them (`Fold` in [reconcile.py](reconcile.py)); nothing
keeps state in memory across passes. `queues/` and `offsets/` are a
cache — a pure, byte-deterministic fold over the log that can be
deleted and rebuilt at any time. The moment code treats queue
membership or an offset as authoritative, the design is broken.

Appends are line-atomic with torn-tail tolerance: a partially-written
line is dropped by the fold (it "never happened"), and the next pass
re-derives. This is what makes a hard kill mid-run safe — the property
the tests actually exercise.

### Identity is content hash

An atom's identity for the pipeline is `sha256` of its file bytes in
`.ai-native/atoms/`. The idempotence key for "has this node already
judged this work" is `(node, artifact_hash)` — that's why re-runs never
double-act. Corollary: **editing an atom file creates a new version
that restarts the pipeline from scratch**; old receipts stay valid
history but no longer apply. Because bytes are identity, git must never
rewrite them — `.gitattributes` exempts `.ai-native/**` from eol
conversion (done-line 0007; the orphaned-history incident is recorded
there).

### The pipeline and how stages become real

`PIPELINE` in [reconcile.py](reconcile.py) is the single stage table
(value gate → owner stamp → placement → handoff → confirm);
`orchestrate`, `node`, `summon`, and `web` all import from it. Each
stage starts as a mock with a fixed verdict. A stage becomes real via a
`node_real` admission (`python -m loop.node admit-real`) — read from
the log at runtime, never a code literal. Once real, the loop *parks*
the atom and waits for the summoned node to write its verdict through
`loop.node judge`; the loop never stands in for it.

### Summons, hooks, and node prompts (§8, D-10, §7)

[summon.py](summon.py) renders the open summons — every atom awaiting
an admitted-real node other than the owner's stamp — as a read-only
fold. `.claude/settings.json` wires `SessionStart` and
`UserPromptSubmit` to `python -m loop.summon --hook`, so a session that
opens here is handed its summons ambiently: the session *is* the
virtual node — it blinks in, judges through the one pen, dissolves.
The hook never writes and always exits 0.

Node prompts are versioned source in `.ai-native/nodes/<node-id>.md`
(§7): the summons delivers the prompt with its `sha256`, and the
receipt records that hash (`prompt_hash`) — every verdict attributable
to the exact prompt that judged. The hash never enters the receipt id,
so a prompt edit can't reopen a settled verdict (I-2).

### Module layering

- [reconcile.py](reconcile.py) — the fold, one level-triggered step per
  pass, cache rebuild. Everything else builds on this.
- [orchestrate.py](orchestrate.py) — ambient control: senses pressure
  (a fold), reads the admitted setpoint dial, budgets steps per tick
  *both ways* (heat when stalled, cool when the human queue is at cap).
  Every actual move is still `pass_once`.
- [slowloop.py](slowloop.py) — the slow loop's *proposer* (§14,
  done-line 0074): folds the tick history + outcome phase + the hour's
  lean into a *proposed* setpoint change carrying its attribution
  (the `because`). Read-only — it proposes, never disposes.
- [disposer.py](disposer.py) — the slow loop's *disposer* (done-line
  0091): bdo's chosen disposition, a **bounded standing auto-admit**.
  An admitted `auto_admit_fence` (his one stamp, per-dial bounds) is the
  standing authorization; `evaluate` decides a proposal **admit /
  escalate / noop** (heating capped at the ceiling, cooling always
  allowed, an unnamed dial escalates, and one breached key escalates the
  whole proposal — §10); `dispose` self-admits an in-fence change citing
  the fence as `authorized_by` (the loop executes the stamp, it never
  signs its own line — the merge-node/confirm-arc shape), or leaves an
  out-of-fence one for bdo. Read from the log at runtime; inert until a
  fence is drawn. Named for the propose/dispose split, distinct from the
  command-guard `fence/` (tool policy) — two different layers.
- [node.py](node.py) — the one pen for summoned verdicts and
  admissions; enforces the seam contract (right node, right verdict
  set, no judging your own announcement, write-twice is a no-op).
- [summon.py](summon.py) — the summons surface; read-only, hook-safe.
- [reflect.py](reflect.py) — the reflection fold (done-lines 0018,
  0020): surfaces and rules (kind × surface → enabled) are admitted
  records; the drift between the owner's queue and what a registered
  surface shows is a pure fold over the log; `auto_plan` is what the
  Stop-hook beat applies — only what enabled rules name, and only
  toward surface kinds the pen translates (`SURFACE_KINDS`, done-line
  0030: an untranslatable kind is refused at register, skipped by the
  beat, named by status — never guessed at with gh-shaped verbs).
  Pub/sub, level-triggered: the log is the topic, rules the
  subscriptions, reflection records the acks, drift the unconsumed
  backlog. Two kinds today (`DRIFT_BY_KIND`): **owner-stamp-queue**
  (`drift`, one issue per atom at the stamp) and **merge-divergences**
  (`divergence_drift`, done-line 0037) — the post-merge surface bdo asked
  for: the digest's *divergences* folded into **aggregate** issues, one
  per group (refusals under a confirmed arc, by epic; cap-breaches as
  one), each carrying its data points, closing when the group reconciles
  — explicitly *not* a one-issue-per-PR echo. A new kind is an entry in
  `RULE_KINDS` + `DRIFT_BY_KIND`; the gh translator and reflection records
  are shared, so it rides the same beat once a rule enables it. Outward
  reach lives only in the reflector pen
  (`.claude/skills/reflect/reflect.py`) — never here. The mirror is
  one-way: verdicts still land only through `loop.node judge` (D-4).
- [web.py](web.py) — the owner inbox, a rendered fold; its verdict POST
  calls the same `judge()` the CLI uses. There is deliberately no
  second write path.
- [census.py](census.py) — the part census (done-line 0029): the loop
  sensing its own body. A pure fold (no subprocess, no git) over two
  signals — *wired* (reachable from the working system, not the part's
  own test) and *exercised* (a controlled literal of the part's is on
  the record). Crossed, they give three verdicts that are bdo's three
  movements: **alive** (give care), **wired·idle** (a writer plumbed in
  but never fired — needs attention), **dormant** (disconnected — a
  prune candidate). Read-only: it counts and names; the cut stays the
  owner's (D-4). Sibling to the watcher's `--report`, for code instead
  of tools. File-level, distinct from pipeline-stage realness
  (`node_real` admissions) — read both.
- [digest.py](digest.py) — the owner's merge digest (done-line 0032):
  the data-rich surface bdo watches *instead of operating the merge*.
  A pure read-only fold over a span of the log, grouped arc-first
  (done-line 0006): what landed, refused, awaits; the dial in play; the
  field's heat/cool behaviour; and — the teeth — *divergences*, where
  two locally-fine records refuse to fit (a *confirmed* arc harbouring a
  *refused* piece; a tick whose backlog breached its own setpoint cap).
  Verdicts are read generically (`next_suggested_event` is the
  advance/refuse signal, a landing is the advance into `TERMINAL_EVENT`),
  so the digest already speaks the merge-node's `{land, refuse,
  send_back}` the day those receipts land — "landed" becomes
  merged-to-main for free. Writes nothing; `--json` emits the dataset.
  This is the *eyes* of the owner-harness arc's last stretch (bdo stepping
  out of the merge seat); the merge-node is the *hand*, and it does not
  move until bdo admits it real (`--by bdo`) and the `bdo merges` hard
  rule is amended — both his, neither this surface's. **`atoms_on_main`**
  (done-line 0124, D-13) is the per-atom↔per-PR join: the set of
  artifact_ids the merge receipts record as having reached main (their
  `landed_atoms`, the write-through carbon copy the PR pen now carries) —
  the reading half that lets *"did atom X reach main?"* be answered from
  the log alone, where the pre-D-13 receipt could only say *that* a PR
  landed. Surfaced as a confirmed-on-main count; empty until the first
  post-D-13 land carries its atoms (the 90 prior merges stand as lossy
  history).
- [retro.py](retro.py) — the retrospective fold (done-line 0098): the loop
  reads its *own history* for recurring patterns to refine on. Sibling of
  `digest` on a new axis — the digest folds one span, retro folds **all of
  history** and asks what keeps happening. No second truth (§10): it folds
  the same log and *reuses* the digest's version-split and divergence
  detection rather than re-deriving them; evidence is cited to log records,
  never report prose (the grip rule). Three detectors today — **churn** (an
  atom re-derived ≥2× via versions and/or repeated negating verdicts — the
  rework the shame beat cannot see: shame senses *stalling*, retro senses
  *churning*), **dead-valve** (a control mode advertised but never taken —
  cool ran 0 of 91 ticks), **standing-divergence** (a digest divergence
  left un-reconciled across the history, with its age). Read-only: it names
  the pattern and the one move; the fix stays a session's or bdo's (D-4).
  `--json` emits the dataset. The first node of the refinement-and-retro
  surface; more detectors and any owner surface ride later increments.
- [heal.py](heal.py) — the healing fold (done-line 0111): the counterforce
  to the teeth. Teeth without a healing reflex is autoimmunity — the loop
  keeps a correct-but-stale bite inflamed on the owner surfaces and has no
  part that could ever see a tooth bite *wrong*. Sibling of `retro` on the
  *bite* axis (retro: what keeps happening; heal: where did a tooth bite
  wrong), reusing the same `Fold`, the digest's version-split, and
  supersession — no second truth. Three detectors: **stale-park** (a gate
  correctly negated an old version, the live version then passed the same
  gate — the bite is healed, only its surfacing is stale; the field-topology
  phantom), **flapping-gate** (a gate negates the *live* version after
  advancing an earlier one — a current self-contradiction), and
  **owner-override** (bdo's stamp advanced what a real gate refused, *after*
  the refusal — ts-ordered, so the normal pipeline's early owner-stamp before
  a later-stage gate is not a false override). The last two are the system's
  first sensors of those failure modes — declared even at zero live instances
  (like the cool valve), ready for when the gates judge un-vetted work.
  Propose-only (D-4): it names the over-bite and the one heal move; it never
  clears a park or re-opens a verdict — a bounded actuator, if it ever comes,
  rides the disposer fence and is a later done-line. Surfaced ambiently
  through `loop.summon`'s `heal_lines` (shown, never disposed).
- [tags.py](tags.py) — the tag pool (done-line 0032): governed vocabulary
  for what tools do, the census fix pushed upstream to the write seam.
  Holds the one shared verb→intent `classify()` the watcher and the git
  pen both import (I-4), and a dimension schema whose `core` is closed in
  code while admitted `tag` records extend it — proposed-tier: an
  unadmitted value reads as `proposed` drift and is promotable by `admit`
  (`--by`), never blocked. Today's one dimension is `intent` (read /
  mutate); `surface` and `arc` are the next slices. The watcher tags
  every watched command and `--report` splits raw mutations (wrapper
  candidates) from raw reads (raw-by-design); the git pen records its
  verb's intent and refuses an `--intent` that lies about the verb. The
  classifier returns None on an unknown verb — an honest gap surfaced by
  `status`, never a silent guess.
- [gaps.py](gaps.py) — the gap fold (done-line 0048): the loop's own
  gaps become the next session's work. One pure read-only fold over
  records already on disk, in one fixed pressure order — **mock-stage**
  (the shame beat's still-mock set), **mock-actor** and
  **unadmitted-actor** (done-line 0049: `effective_mocks()` — anything
  effectively mock is mocked, suffix or not: a `.mock` actor on the
  record the stage lifecycle does not own, and a record-writer no
  `node_real` admission ever named on either side; one admission clears
  both its sides), **parked-piece** (an atom a gate
  refused, holding), **surface-drift** (acts a registered surface does
  not show), then **idle-part**/**dormant-part** (the census verdicts)
  — each gap carrying kind, subject, why, and the one concrete next move
  (always an existing pen's; this fold writes nothing, and the census
  cut stays bdo's, D-4). Computes lazily in priority order so the cheap
  log folds answer before the census walks the tree; a missing root is
  an absence, not a field of mock stages. `loop.summon --hook` hands the
  single top gap to every session that blinks in — the idle default is
  "work the backlog the harness generated", never "wait for direction".
- [parity.py](parity.py) — the boundedness parity matrix (done-line 0115),
  wave 1 of `epic.repoprompt-parity`. A pure read-only fold that mines
  RepoPrompt CE (`docs/sources/repoprompt-context-engineering.md`, read-only
  inspiration) as a catalogue of agent-**boundedness** techniques: each row
  reads one capability as "how does this keep an agent bounded?" and answers
  it with one verdict — `have` (cites a resolvable repo file), `build` (names
  an atom in the epic), `dont-double-build` (cites a real owning epic). The
  §10 teeth are the term-economy/gaps grip rule: `validate()` fails on a ghost
  citation, and `tests/test_parity.py` proves the check is not vacuous (a
  fabricated row of each verdict is caught). The sharper tooth (done-line
  0132): a `have` must carry `evidence` — a substring its cited file actually
  contains — so a row cannot stand on a real file that does not do the claimed
  thing (the ghost-in-spirit that let the multi-root row falsely claim
  `field.py` folds three sibling repos; it folds every *arc within ontum*, and
  is now re-verdicted `build` -> `atom.multi-root-fold.v0`). The requirements mine that orders
  the rest of the arc — sibling of `gaps`/`census` on a new axis (what a
  neighbouring system forces us to account for), the cut and the build stay a
  session's or bdo's (D-4).
- [phrasing.py](phrasing.py) — the phrasing backdoor's pure checker
  (done-line 0117): bdo's low-ceremony door for pedantic prose edits.
  A wording fix the machine never branches on ("on his phone" ->
  "wherever he is") should not cost an atom, a judge, and a branch — the
  full work-particle mantra (§15/D-5) — so a phrasing edit is exempt from
  it. The teeth (the whiteout shape, done-line 0064): the door PROVES an
  edit is prose-only rather than trusting a label — `.md` body free but
  frontmatter keys/`name`/`version` protected; `.py` tokenized so only
  comment/string CONTENT may differ; `.json` structure + non-prose values
  byte-identical, only `PROSE_KEYS` string values may change — and names
  what disqualified any other change. Stdlib, no git (loop/'s law). The
  off-log gate gains a SECOND way to be backed
  (`pr_audit.orphan_reason(..., phrasing_clean)`): a branch every non-log
  change of which this proves prose-only needs no atom — the fact gathered
  AND re-verified by the reach (`pr.py audit`, the git side) with this
  same checker, so the client pen and the server CI inherit the door
  together and neither can be lied to. The route (the git-bearing half) is
  `pr.py phrasing`, which marks the edit with one `phrasing` admission on
  the log (provenance) after the proof passes; it refuses anything this
  checker rejects. The cut between "phrasing" and "work" stays bright: the
  door is for prose only — syntax or schema is routed back to the pipeline.
- [activity.py](activity.py) — the activity-accounting fold (done-line 0143):
  the loop accounting for its own hooks. bdo, 2026-06-20: *"account for all
  activity, even Claude hooks like session start and tool call, and start
  auditing their data collection and usage for a shared gateway."* The hooks are
  the gateway's sensors, but their *own* data collection is the one activity the
  gateway never witnesses — they collect command strings, spawn prompts, full
  raw stdin/argv/env (the codex probe) and gh poll results, mostly silently into
  gitignored sinks, and most do not record that they fired. Sibling of
  `census`/`gaps`/`heal` on the *data-practice* axis: a declared register
  (`.claude/activity-register.json`) states per hook what it **collects**, what
  it **uses** that for, where the data **goes**, and whether its firing is
  **witnessed**; the fold reconciles it against the live `.claude/settings.json`
  wiring and the §10 teeth refuse an **undeclared collector** (a wired hook
  accounted nowhere) or a **ghost** (an entry no longer wired — a `codex`-wired
  entry verified against `.codex/hooks.json` when present). The accounting is
  enforceable: no silent collector can be wired without declaring its
  data-practice. Read-only, propose-grain; the cut and the wider shared-gateway
  unification stay bdo's (D-4). The unwitnessed count is the bridge to part 2,
  the runtime witness (every firing → a first-class receipt, the sibling of
  `tool-use.jsonl` the git/gh-gateway proposal deferred).
- [herald.py](herald.py) — the herald (epic.landing-throughput-response): agents are an open set, so registration and reputation are FOLDS over logged `herald_introduction` admissions, never a table — a herald `introduce`s a named/titled agent (the dumb pen mints a content-hash `credential` at the trust-ladder floor rank, read from `loop.trust`), `roster` folds who is registered (superseding, never erasing), and `reputation` derives distributed value from the log's provenance edges (exemplars net against notorieties per credential, and a herald earns a meta-reputation over the standing of whom it vouched, so a bad voucher is visible by construction); read-only but for the one pen, standing only ever earned forward (§10: standing is recomputed from records, never asserted; D-4).
- [inference_queue.py](inference_queue.py) — the inference admission queue
  (done-line 0152, epic.inference-gateway): the summon queue on the request
  axis. The gateway authorized and receipted every completion but fired each
  immediately and synchronously — no concurrency bound, so a burst of
  completions stacked model/KV-cache past physical memory and the host
  swap-thrashed (bdo's llama-server kill). Three parts, stdlib and local-first
  (a file semaphore is a local coordination primitive, not the no-network
  ban's broker): an **admitted concurrency dial** (`concurrency_bound`/
  `set_bound`, default-safe when unset, never a code constant — the setpoints
  law), a **lease-based file semaphore** (`acquire`/`release`; a slot is
  claimed by atomically `os.link`-ing an already-written file into place, so the
  bound holds under real parallel contention — a create-then-write `O_EXCL`
  claim let a concurrent reader see an empty slot and double-claim it, a real
  bound violation a multiprocessing stress test caught and now gates;
  self-healing on a dead holder once its lease lapses — the torn-tail mortality
  property; release is token- and lease-guarded so a lapsed holder can never
  delete the live slot), and a **read-only stats fold** over the
  inference receipts (throughput, per-mind latency, saturation, live
  in-flight). The gateway pen acquires a slot before the completion and
  releases after, receipting a witnessed `saturated` outcome when the plane
  stays full — backpressure on the record, never a silent host-kill. The
  bound's value is bdo's to tune (D-4).
- [observe.py](observe.py) — the Observable-as-gate (epic.model-free-mode-response, wave 1): the consequence-gate's forced-first invariant. A peer review of the smart-mashing doctrine reordered the four invariants — Observable is the substrate reversibility, boundedness and learning-progress are all *computed from*, so it gates first. Before an autonomous **exploratory** act runs it must DECLARE actor, intended action, expected receipt, touched scope, attribution path, rollback path, and a probe id; if it cannot NAME the receipt path that ties effect back to actor, the act HALTS — it does not run. The §10 kill-test runs the **real `command_guard`** as a subprocess: an act the *action-gate* allows (`git status`) is REFUSED by `observe.gate()` when under-declared — the consequence-gate catching what the action-gate cannot (the doctrine's central claim, in a passing test). Pure stdlib, read-only. Soft tooth on record: the attribution check is substring-based, to harden before it gates real acts.
- [relation_ledger.py](relation_ledger.py) — relation-ledger.v0 (epic.model-free-mode-response, wave 1): the record substrate for the **relational middle band** — representation without mechanism, the corrected spectrum raw → relational → mechanistic. Declares five record kinds (relation_claim, relation_probe, consequence_receipt, model_candidate, bucket_coherence_report) and a pure read-only fold that, per bucket, reads whether a claim's predicted consequence MATCHES observed receipts (PREDICTIVE) or not (TRIVIAL/refuted). The coherence rate is the learning-progress proxy — the rate buckets stabilize into predictive coherence (compression progress), not raw surprise. v0 is logged claims+receipts; embeddings are a later *admitted* part ([relation-organ-admission contract](../causality/contracts/relation-organ-admission.md)). Declared at zero records (the cool-valve grain).
- [over_containment.py](over_containment.py) — the over-containment counter-test (epic.model-free-mode-response, wave 1): the shared shadow of T6 (over-containment in *action* space — the gate refuses so little nothing risky reaches it) and T7 (over-containment in *representation* space — equivalence classes collapse until real signal is averaged away). One shadow, two layers, one discriminator: is a stabilization PREDICTIVE (coherence rose under test) or merely TRIVIAL (stable because never tested)? The load-bearing leg is `tested` — a signal stable+rising but never tested reads as over-containment. The doctrine's "the clauses that buy safety can erase the signal that justified the freedom," made a detector.

- [consequence_graph.py](consequence_graph.py) — the consequence graph v0 (done-line 0167, epic.consequence-graph-response): the auditable **tier-1 plane** of consequence memory, a read-only fold. A foreign peer-architect reviewed the consequence-graph + mark-to-market proposal (envoy package `consequence-graph`) and returned GO for the smallest real piece plus the load-bearing correction — the graph is the *auditable plane* of a larger consequence memory, and it earns the name *consequence* (not a prettier provenance view) only when it carries **cited consequence nodes**: a changed state distinct from the work-unit. Composes the existing parts (no second truth, no new engine): nodes are log subjects (one shape + a `kind`), edges are literal log facts (tier-1 only — no inferred causal edges), `failure`/`repair` marks fold from negating receipts and healed bites (reusing `heal`'s verdict split), declared `consequence.observed` events add cited consequence nodes, and one **bounded, typed, decaying** propagation pass (radius 2, per-edge-kind decay, channels never netted) makes the field a living target without smearing — authorship/arc-sibling edges render but never propagate. The §10 tooth (`tests/test_consequence_graph.py`, proven non-vacuous): a mark whose citation does not resolve is **refused** as a gap (the term-economy ghost refusal, on marks). Read-only — witness before actuator; tier-2 inferred edges, `value`/money, the consequence volume, and actuation are deferred (named in done-line 0167).

### Invariants the code is built around (firm)

- **Earn your own acceptance first; you just can't cast the deciding one.** Judge,
  validate, and accept your own work before you share it — that conviction is your case
  and your standing, and it keeps slop on your side of the wall. But your acceptance never
  lands it: a different reader accepts it into the record, the owner (bdo) is the last stop.
  Two gates, yours then theirs. Skipping your own judgment is the slop bug; making your own
  judgment final is the self-dealing bug. And when no independent judge for your kind of
  work exists yet, forge one — within policy, toward the second set of eyes, never around
  them (the §7 node prompt, the spawn rail, `admit-real`, the herald are the forge).
  Abandoning work at a gate you cannot pass — or could forge — is the design bug.
- **The owner is the last stop — at arc scale (done-line 0028).** bdo
  may *confirm an arc* (`loop.node confirm-arc --epic <id> --by bdo`),
  an admitted record that is his standing stamp for every piece under
  that epic: the loop then satisfies the owner-stamp on his
  confirmation (the receipt cites `authorized_by`) and carries the
  arc's pieces, escalating to him only a gate's *refusal* or the arc's
  completion. He steers arcs; the loop carries pieces. His stamp is not
  removed — it is moved up a level, to the arc, where one confirmation
  authorizes many lands. Confirmation is his alone (`--by bdo`) and
  withdrawable (`--off`, superseding).
- **Setpoints, realness, ticks are admitted records** in the log,
  signed with `--by` — never constants in code.
- **History is never retro-invalidated.** Superseding admissions, never
  erasure; record verdicts, don't delete questions.

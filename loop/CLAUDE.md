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

python -m loop.census                      # the organ census: which organs carry weight, which are dormant

python -m loop.gaps                        # the gap backlog, pressure-ordered — the top one is the work

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
- [census.py](census.py) — the organ census (done-line 0029): the loop
  sensing its own body. A pure fold (no subprocess, no git) over two
  signals — *wired* (reachable from the working system, not the organ's
  own test) and *exercised* (a controlled literal of the organ's is on
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
  organ that could ever see a tooth bite *wrong*. Sibling of `retro` on the
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
  not show), then **idle-organ**/**dormant-organ** (the census verdicts)
  — each gap carrying kind, subject, why, and the one concrete next move
  (always an existing pen's; this fold writes nothing, and the census
  cut stays bdo's, D-4). Computes lazily in priority order so the cheap
  log folds answer before the census walks the tree; a missing root is
  an absence, not a field of mock stages. `loop.summon --hook` hands the
  single top gap to every session that blinks in — the idle default is
  "work the backlog the harness generated", never "wait for direction".
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

### Invariants the code is built around (firm)

- **No one signs their own line.** A node never judges its own writer's
  output; the owner (bdo) is the last stop. Anything self-approving is
  a design bug.
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

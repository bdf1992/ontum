# loop/ — the loop substrate

Pure stdlib — no broker, no daemon, no network, no dependencies (hard
rule). Run everything from the repo root.

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
```

Gotcha: only `reconcile.py` runs as a plain script. `orchestrate`,
`node`, `summon`, `reflect`, and `web` import from the `loop` package
and must run as modules (`python -m loop.<name>`) from the repo root.

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
  backlog. Outward reach lives only in the reflector pen
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

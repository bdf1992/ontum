# .claude/workflows/ — authored AI workflows (the Workflow tool's land)

Authored AI workflows live here. This is the **native** home: the
Workflow tool resolves a named workflow (`Workflow({name: "<slug>"})`)
from this directory, so a script that lands here is launchable by name
with no extra wiring. The branded wrapper over the native workflow
surface
([`workflow-authoring-wrapper.proposal.md`](../../.ai-native/proposals/workflow-authoring-wrapper.proposal.md))
rides this convention instead of inventing one.

Two kinds of workflow share this directory today: **authored helpers**
(`atom-trace`, `draft-capability`, …) and the **tick-tenders** — the
work-consuming processes documented below.

## What a workflow file is

One JavaScript file per workflow, `<slug>.js`. It is a script against the
native Workflow orchestration: it **must** begin with a pure-literal
`export const meta = { name, description, phases }` block, then a body
using `agent()` / `parallel()` / `pipeline()` / `phase()`. The `meta.name`
is the launch handle and should equal the file's `<slug>`.

## The naming + safety convention (A1)

- **Name** = a short kebab-case verb-or-noun that says what it does
  (`subsystem-map`, `review-diff`, `find-flaky-tests`). The file is
  `<name>.js`; `meta.name` matches.
- **Read-only by default.** A workflow that only reads (search, map,
  audit, synthesize) is safe to author and run freely. A workflow whose
  agents **mutate** files declares it in its `meta.description` and uses
  `isolation: 'worktree'` per mutating agent — and, per the wrapper, does
  not run unattended until the review gate (A3) and the authority dial
  exist. Until then: review before run.
- **Args, not hard-coding.** Parameterize over `args` (a path, a
  question, a config object) so one authored workflow serves many runs.
- **Authored here, reviewed before armed.** A2 (the authoring agent)
  drafts into this directory; A3 (the review interface) renders a draft
  as *what it does · phases · blast radius · riskiest step* and arms it.

## The tick-tenders (work-consuming processes)

Load-bearing **workflow scripts** that **consume work** — they are
granted a **named section of the ledger** and work its open items,
surfacing each as work-to-close. The model (bdo, 2026-06-21: *"free to
work over a named section of the log/ledger and surface work to close ...
a process for their workflow which consumes work"*) is producer/consumer
over the log:

- **Producer** — `loop/section.py` NAMES the work queues (a read-only fold, the
  loop/ side). Each *section* is a bounded slice of the incomplete flow:
  `value-confirm` (the clog), `stale-park`, `gaps`, `owner-asks`. Run
  `python -m loop.section list` for the census, `… items --name <n>` for one
  queue. It composes the existing folds (no second truth) and writes nothing.
- **Consumer** — the tenders here. They pull a section's items and **infer over
  each small item** — the thing pure stdlib folds can't do — surfacing it as
  closeable work. They live here (`.claude`, where inference + network are
  allowed), never in `loop/` (stdlib, no inference — that law is unchanged).

They are **propose-grain by construction**: a tender writes no verdict and
clears no park — the cut stays a session's or bdo's (D-4). The one place
real state advances is the value-confirm **drain**, which only reuses the
already-sanctioned `loop.heartbeat` rail.

| script | section it consumes | what it produces |
|---|---|---|
| `tend.js` | **any** named section (`args.section`) | the generic consumer — works a bounded batch, surfaces each as ready-to-close / drafted / owner / blocked. A new section is consumable with no new workflow. |
| `tend-heal.js` | `stale-park` (tuned) | a checked reconcile draft — does an owner surface still show the healed bite? Runs a governed prompt (`.ai-native/nodes/tend-heal.claude.v1.md`, pinned by hash) and books each agent run (`loop.agent_run`) so it is witnessed. |
| `tend-gaps.js` | `gaps` (tuned) | a ready-to-act draft per gap (exercise / silence-by-design / build / needs-owner) |
| `tend-inbox.js` | `owner-asks` (tuned + **actuates**) | investigates each parked item vs current reality; **closes** the verified-stale mirrors through the issue pen, shapes the residue for bdo |
| `tend-loop.js` | **the conductor** — one tick | optional value-confirm drain + the tenders, compiled into one journalled tick-report |
| `author.js` | **the generative top** — reads the volume scoreboard + section census | AUTHORS a tuned tender for the most under-served quota/section, as a `draft-<slug>.js` (PROPOSED, never scheduled). Closes the loop: an unfilled volume generates the tender that fills it. Propose-grain — promotion (rename `draft-` → live) is bdo's activation gesture. |

```sh
# run a consumer on demand (Workflow tool, by name):
#   tend         args { section: "value-confirm" | "stale-park" | "gaps" | "owner-asks", limit: N }
#   tend-heal    — tuned consumer for stale-park
#   tend-gaps    — tuned consumer for gaps          (args: { limit: N })
#   tend-inbox   — tuned consumer for owner-asks; closes verified-stale mirrors (args: { close: bool })
#   tend-loop    — one full tick                    (args below)
```

**Generic vs tuned, and who actuates.** `tend` is the universal consumer: it
surfaces work-to-close for any section but never actuates (closing is
section-specific and reaches pens — too varied to do blind). The tuned tenders
add section intelligence; `tend-inbox` additionally *actuates* the close where
it is known reversible-safe (the issue pen, reopenable). Actuation is opt-in and
reversible — never a blind close. Hard lesson (2026-06-21): a `close`-by-default
plus a vacuous "0 items ⇒ all resolved" check wrong-closed a standing owner
directive (#348); the fix added the recovery verb `issue.py reopen` and made
close opt-in behind a non-empty-queue guard. **A consumer that can close must be
able to un-close, accountably.**

### The conductor's dials (`tend-loop` args)

| dial | default | meaning |
|---|---|---|
| `drainLimit` | `0` | fire ≤ N **real** value-confirm reviews via `loop.heartbeat`. Each is headless inference **+ a trust-rail GitHub issue** — so it's off by default; turn it up deliberately. This is the load-bearing burn of the 63-atom value-confirm clog. |
| `gapLimit` | `5` | how many pressure-top gaps to tend |
| `by` | `tend-loop.v0` | the actor stamped on the drain and the journal |

Drafts are journalled to `.ai-native/log/tenders.jsonl` (gitignored sensor
trace, deletable) so a mortal session's inference survives to the next one.
The truth is always the log the drain advanced — the journal is propose-grain.

### The 5-minute tick — bdo's one gesture

The tenders are reversible (files + drafts). **Recurring autonomous spend is
not** — so standing the tick up every 5 minutes is bdo's activation gesture,
the same model as the heartbeat's external scheduler. The recommended start:

```sh
# every 5 min, inference tenders only (no spend, no issues) — safe to leave on:
claude -p "/tend-loop"           # via a Task Scheduler / cron entry, repo root

# when ready to also burn the value-confirm clog, dial the drain up a notch:
#   /tend-loop  with args { "drainLimit": 2 }
```

Start with `drainLimit 0` (tenders only). Watch a few ticks' journals. Then
raise the drain one notch at a time as the gate earns trust — that dial is the
only knob between "drafts the work" and "lands the work", and it is yours.

## Rule of this directory

A workflow is **config-as-code** (§7): versioned, reviewed, landed as a
stamped increment — never a throwaway. When the bespoke live portal
arrives, these files and their review surface carry straight over.

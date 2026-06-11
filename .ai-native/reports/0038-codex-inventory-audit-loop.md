# Report 0038 — Codex inventory audit loop

## What landed

By done-line 0040, this report is both the audit artifact and the session handoff. It sets up a repeatable wiring/code audit loop and records the first full accounting pass over the tracked code surfaces.

What was read:

- Root contract stack: `AGENTS.md`, `CONTRIBUTING.md`, `CLAUDE.md`, `ai-native-loop-substrate.md`, plus the directory `CLAUDE.md` files for `loop/`, `.ai-native/`, `.claude/`, `.codex/`, `fence/`, `glyphs/`, `language/`, `exports/`, `pivot/`, and `tests/`.
- The tracked file graph: `git ls-files`, `rg --files`, Python AST summaries, generated-output declarations, and append-only ledger locations.
- The system's own folds: `loop.reconcile --status`, `loop.orchestrate --status`, `loop.node arcs`, `loop.summon`, `loop.census`, `loop.digest`, `loop.merge`, `loop.reflect`, `loop.tags`, `loop.trust`, `loop.minds`, and `pivot.run --status`.
- The DONE ledger and report ledger enough to tie code surfaces to the value they claim.

Verification run:

```text
python -m unittest discover -s tests -v
Ran 413 tests in 25.916s
OK
```

## Audit Loop

Use this loop for the next pass; it is deliberately mechanical.

1. **Load the contract stack.** Read root contracts, then every directory `CLAUDE.md` for the files in scope. If contracts disagree, name the disagreement instead of normalizing it.
2. **Separate authored, generated, append-only, and read-only.** Generated outputs are accounted for but audited through their generator. Append-only ledgers are folded, not edited. `docs/phase-2/` and `docs/sources/` are context only.
3. **Pull live folds before reading code.** Run `python loop/reconcile.py --status`, `python -m loop.orchestrate --status`, `python -m loop.census`, `python -m loop.digest`, `python -m loop.merge`, `python -m loop.reflect`, `python -m loop.tags`, `python -m loop.trust ladder`, `python -m loop.minds list`, and `python -m pivot.run --status`.
4. **Inventory by file, not by vibe.** For each code-bearing file record: role, intended value, composition point, DONE evidence, and status: real / mocked / generated / append-only / wired-idle / open / drift.
5. **Audit against atoms and epics.** Atom state can be `value_confirmed` while the epic horizon is still mostly unbuilt. Record both levels.
6. **Run the suite and record the actual result.** A green suite is evidence of receipts, not proof of value.
7. **End with a report.** Needs-you items and instruction conflicts live here.

## Main Findings

1. **The substrate core is real, but the pipeline is still partly mocked.** Seven atom records are present and all fold to `value_confirmed`. Newer atoms have real `value-gate.claude.v1` and `owner-stamp.bdo.v1` receipts, but `placement-gate.mock.v0`, `handoff-gate.mock.v0`, and `value-confirm.mock.v0` still carry fixed verdicts. The story author is also still `value-loop.story-author.mock.v0`. This is honest in `loop/reconcile.py` and screamed by `mock_shame.py`, but any surface calling all of that "landed" needs the mock caveat beside it.
2. **DONE at atom scale is not DONE at arc scale.** `epic.substrate` has all three declared atoms landed. `epic.owner-harness` has three landed pieces and two unbuilt pieces. `epic.experience-layer`, `epic.ontabet-speaks`, and `epic.pivot` are confirmed arcs with large unbuilt horizons.
3. **The registry surfaces exist before their lived flow.** `loop.trust` has zero admitted rungs; `loop.minds` has zero registered minds. The code is tested and wired, but it is not yet carrying live system authority.
4. **Codex is only partially machine-fenced.** `.codex/rules/ontum.rules` is generated from `fence/policy.py` and covers raw command denials. `.codex/hooks.json` currently provides summons and hook probes. Claude has active write, freeze, spawn, mock-shame, reflect, sync, and garden hooks; Codex equivalents are not built yet. This is an admitted probe phase, not a failure, but it should not be described as parity.
5. **Merge authority text is drifted across layers.** Newer root `CLAUDE.md`, `pr.py land`, and `.claude/skills/merge-node/SKILL.md` say bdo confirms arcs and the merge-node lands. `AGENTS.md`, `CONTRIBUTING.md`, parts of `fence/policy.py`, parts of `branch-ritual/SKILL.md`, `overnight-loop/SKILL.md`, and `loop.merge` output still say or imply bdo merges / the land is bdo's until a further amendment. This is the highest-value cleanup because it affects operator behavior.
6. **`loop.digest` has a status-line bug.** `python -m loop.digest --today` rendered `_0 landing(s), 4 refusal(s) in span_` and then printed `result: done - clean span: nothing refused, nothing awaiting you`. In `loop/digest.py`, the final result ignores `d["refusals"]` and only gates on divergences and open items. The data is present; the closing sentence is wrong.
7. **Language strata are honest about open holes.** Semiotics is real through `glyphs/knoll.py` and the viewer. Syntax is rendered/described but not yet a refusing gate. Semantics and pragmatics are explicitly OPEN: no stalk metric, no fabric emitter, no instrumentation verdict.
8. **Pivot is a deterministic instrument, not the full measurement program.** It verifies the cube, builds cold prompts, grades returned placements, and measures convergence, but it deliberately never calls a model. The actual cold-agent measurement remains an off-repo/envoy pass.

## File Inventory

Status vocabulary:

- **real**: participates in a live fold or pen and has test/DONE evidence.
- **mocked**: advances by fixed verdict, stub, or placeholder by design.
- **wired-idle**: connected and tested, but little or no live ledger trace.
- **open**: intentionally holds a named hole.
- **generated**: never hand-edit; audit through the generator.
- **append-only**: never hand-edit; fold only.
- **drift**: code and contract disagree or surface wording is stale.

### Root Contracts And Repo Config

| File | Role / value | Composition | Status |
|---|---|---|---|
| `AGENTS.md` | Codex composition surface and guest-engineer contract. | Points Codex at repo law and worktree discipline. | contract; drift on merge authority vs newer root `CLAUDE.md`. |
| `CLAUDE.md` | Root Claude composition surface. | Imports module `CLAUDE.md` files and carries current merge-node amendment. | contract; current on merge-node, source of conflict with older surfaces. |
| `CONTRIBUTING.md` | Working agreements and hard rules. | Human/session workflow contract. | contract; drift on bdo-merges wording. |
| `ai-native-loop-substrate.md` | Doctrine / system intent. | Source of D/I references, seams, nodes, ambient control. | intent source; do not treat as implementation. |
| `README.md` | Public orientation and quickstart. | Summarizes paths and current status. | mostly current; should gain arc-intake/merge wording if docs pass happens. |
| `.gitattributes` | Byte-identity and union-merge config. | Protects `.ai-native/**` and JSONL logs from EOL conversion. | real config; load-bearing for content hashes. |
| `.gitignore` | Cache/artifact exclusions. | Keeps queues, rendered inbox, sensor logs, mock tally, envoy packages out of truth. | real config. |
| `LICENSE` | Legal boundary. | Not part of runtime composition. | accounted, not code. |

### Directory Contracts

| File | Governs | Audit note |
|---|---|---|
| `.ai-native/CLAUDE.md` | Durable records. | Log append-only, done/report pen forms, generated cache rule. |
| `.claude/CLAUDE.md` | Claude harness config-as-code. | Hooks and skills are behavioral code. |
| `.codex/CLAUDE.md` | Codex rendered fence. | Generated policy plus probe phase. |
| `loop/CLAUDE.md` | Pure stdlib loop substrate. | Names mock pipeline and live commands. |
| `fence/CLAUDE.md` | Family-neutral fence registry. | One policy table, multiple renderers. |
| `glyphs/CLAUDE.md` | Glyph generator/viewer. | Generated outputs must be regenerated, not edited. |
| `language/CLAUDE.md` | Language strata and surveyed artifacts. | Proposed marks stay proposed until admitted. |
| `exports/CLAUDE.md` | Envoy package surface. | Packages ignored, ledger committed. |
| `pivot/CLAUDE.md` | Recoverability instrument. | Deterministic harness, cold-agent wall. |
| `tests/CLAUDE.md` | Test receipt conventions. | Done-line pinning and stdlib unittest. |

### Read-Only Intent Context

| File / directory | Role in this audit | Status |
|---|---|---|
| `docs/phase-2/README.md` | Orientation for the wider Ontum fabric. | read-only context. |
| `docs/phase-2/autojective-polysheaf.md` | Source for coordinate grammar, seams, stalks, metrics. | read-only context; language records one finding instead of editing it. |
| `docs/phase-2/cube-alphabet.md` | Source for cube alphabet / viewer claims. | read-only context. |
| `docs/phase-2/ontogrammatic-systems.md` | Source for Machine cycle and instrumentation framing. | read-only context. |
| `docs/phase-2/ontum-evolution.md` | Source for fabric evolution statuses. | read-only context. |
| `docs/sources/README.md` | Boundary for external inspiration. | read-only context. |
| `docs/sources/rosetta-creole.md` | Inspiration for language/creole readings. | read-only context, not claim source. |
| `docs/sources/compression-prediction-entropy.md` | External source context. | read-only context. |
| `docs/sources/files.zip` | Source artifact referenced by ontabet home-come. | read-only context. |

### Records, Atoms, Epics, Prompts

| File | Role / value | Composition | Status |
|---|---|---|---|
| `.ai-native/atoms/atom.loop-skeleton.v0.json` | Birth record for durable reconcile over file log. | Serves `epic.substrate`; touches `.ai-native/log`. | real, but mostly mock receipts. |
| `.ai-native/atoms/atom.fast-ambient-loop.v0.json` | Field control under admitted setpoint. | Serves substrate; touches log and reconcile. | real, mocked gates remain. |
| `.ai-native/atoms/atom.real-value-gate.v0.json` | First real L0 and real owner stamp. | Serves substrate; touches `loop/reconcile.py`, `loop/orchestrate.py`. | real; L1/L2/confirm still mocks. |
| `.ai-native/atoms/atom.owner-inbox.v1.json` | Owner briefing and web inbox value story. | Serves owner harness; touches `loop/web.py`, `loop/node.py`. | real. |
| `.ai-native/atoms/atom.epic-layer.v0.json` | File work under epics so bdo steers arcs. | Serves owner harness; touches `loop/node.py`, `loop/web.py`, `loop/reconcile.py`. | real. |
| `.ai-native/atoms/atom.surface-registry.v0.json` | External surfaces registered and reflected. | Serves owner harness; touches `loop/reflect.py` and GitHub issue surface. | real; current drift clean. |
| `.ai-native/atoms/atom.story-commons.v0.json` | Pattern commons / experience-story atom. | Serves experience layer and owner harness. | value-confirmed; downstream story gate not wired. |
| `.ai-native/epics/epic.substrate.json` | Harness arc. | Contains three landed atoms. | arc complete by declared pieces; still global mocks. |
| `.ai-native/epics/epic.owner-harness.json` | Owner leverage arc. | Inbox, epic layer, surface registry landed. | partial; GitHub verdict mirror and merge-node atom unbuilt. |
| `.ai-native/epics/epic.experience-layer.json` | Experience/morphic-agent arc. | Story commons landed, many future pieces. | mostly unbuilt; trust/minds/spawn pieces partly coded before atoms present. |
| `.ai-native/epics/epic.ontabet-speaks.json` | Language/glyph measurement arc. | Refers to glyph/language/pivot waves. | mostly unbuilt at epic piece level, despite glyph harness code. |
| `.ai-native/epics/epic.pivot.json` | Recoverability measurement arc. | Refers to Pivot rungs. | code for rung 1 exists, declared pieces still read unbuilt. |
| `.ai-native/nodes/value-gate.claude.v1.md` | L0 value prompt. | Delivered by summons; hash on real receipts. | real mechanics; semantic eval debt named. |
| `.ai-native/nodes/story-gate.claude.v1.md` | Reader prompt for cold-reader stories. | Tested in `tests/test_prompts.py`; intended future pipeline stage. | wired as prompt source, not pipeline-real. |
| `.ai-native/done/.pen.json` | Done-line form and freeze declaration. | Enforced by `loop.pen`, write/freeze guards. | real; frozen. |
| `.ai-native/reports/.pen.json` | Report form. | Enforced by `loop.pen` and write guard. | real. |

### Loop Code

| File | Role / value | Composition | Status |
|---|---|---|---|
| `loop/reconcile.py` | Core fold, pipeline, cache rebuild, idempotent pass. | Reads atoms/log/admissions; exports `PIPELINE`. | real core with explicit mocked stages. |
| `loop/orchestrate.py` | Fast ambient loop and setpoint control. | Calls `pass_once`; records ticks. | real; human stage may be real by arc-confirm flow. |
| `loop/node.py` | One pen for verdicts, realness, arc confirmations, rungs. | Writes receipts/admissions. | real; some CLI surfaces superseded by PR confirm seam. |
| `loop/summon.py` | Open summons and hook briefing. | Pure fold over awaiting real nodes. | real; currently no open summons. |
| `loop/web.py` | Owner inbox render/server. | Calls `loop.node.judge`; cache output ignored. | real; localhost-only, auth explicitly unbuilt. |
| `loop/reflect.py` | Pure reflection fold and drift. | Paired with `.claude/skills/reflect/reflect.py`. | real; GitHub surface mirrors log now. |
| `loop/digest.py` | Owner merge digest. | Pure fold; arc-first view. | real but has status-line bug on refusals. |
| `loop/merge.py` | Merge-node readiness eyes. | Reuses digest. | real read-only, but output text stale against amended merge model. |
| `loop/census.py` | Organ liveness fold. | Reads source wiring and ledgers. | real; self-reports wired-idle organs. |
| `loop/tags.py` | Intent vocabulary and classifier. | Imported by watcher and git pen. | real; no drift in this worktree. |
| `loop/trust.py` | Trust ladder read surface. | Written through `loop.node admit-rung`. | wired-idle/open; zero active rungs. |
| `loop/minds.py` | Judging mind registry. | Writes `mind` admissions. | wired-idle/open; zero minds registered. |
| `loop/pen.py` | Records pen. | Creates done/report files and bdo-only supersedes. | real by tests and this report; census marks writer with no live vocabulary trace. |
| `loop/__init__.py` | Package marker. | Enables module imports. | real but intentionally empty. |

### Claude Harness Code

| File | Role / value | Composition | Status |
|---|---|---|---|
| `.claude/settings.json` | Hook wiring. | Runs guards, summons, sync/garden, reflect beat, mock shame. | real for Claude only. |
| `.claude/hooks/command_guard.py` | Deny/watch raw commands from registry. | Imports `fence.policy`, `loop.tags`. | real; watch log empty in this worktree. |
| `.claude/hooks/write_guard.py` | New-file governance and record form. | Uses placement fold for fleet-safe ids. | real; census wired-idle due no record trace. |
| `.claude/hooks/freeze_guard.py` | Refuse edits to frozen done-lines. | Reads `.pen.json`. | real; census wired-idle due no record trace. |
| `.claude/hooks/placement.py` | Cross-ref numbered-record collision check. | Uses read-only git refs; feeds write guard. | real deterministic L1-style check, not pipeline L1. |
| `.claude/hooks/spawn_guard.py` | Branded spawn rail. | Reads trust ladder and node prompts. | real guard; live trust rungs absent, so branded node spawns refuse. |
| `.claude/hooks/mock_shame.py` | Names still-mock stages each prompt. | Folds `node_real` admissions. | real pressure surface. |
| `.claude/hooks/reflect_auto.py` | Stop hook applying enabled reflection drift. | Calls reflect pen. | real Claude-only writing hook. |
| `.claude/skills/branch-ritual/pr.py` | PR/merge pen. | Uses `gh`, tests, merge receipts, arc confirmations. | real; merge authority comments newer than some docs. |
| `.claude/skills/branch-ritual/git.py` | Git add/commit/push/sync/garden pen. | Records branded acts, worktree hygiene. | real. |
| `.claude/skills/branch-ritual/SKILL.md` | Branch ritual prompt. | Human/session operating contract. | drift: amended handoff exists, older standing text still says bdo merges main. |
| `.claude/skills/merge-node/SKILL.md` | Merge-node ritual. | Calls `loop.merge` and `pr.py land`. | real prompt; drift: mentions `--delete-branch`, code intentionally removed it. |
| `.claude/skills/envoy/envoy.py` | Export package pen. | Writes gitignored packages and `exports/log.jsonl`. | real; stubs intentionally refused until authored. |
| `.claude/skills/envoy/SKILL.md` | Envoy ritual prompt. | Operating surface for external review packages. | real prompt. |
| `.claude/skills/reflect/reflect.py` | External reflection pen. | Applies `loop.reflect` drift via `gh`. | real. |
| `.claude/skills/reflect/SKILL.md` | Reflection ritual prompt. | Operator contract. | real prompt. |
| `.claude/skills/overnight-loop/overnight.py` | Long-run brief/pickup/checkpoint pen. | Reads epics, records, summons, worktrees. | real; substrate queue can exhaust. |
| `.claude/skills/overnight-loop/SKILL.md` | Overnight loop ritual prompt. | Operator contract. | drift: still says bdo merges in final law section. |
| `.claude/skills/arc-intake/intake.py` | GitHub arc-confirm issue pen. | Uses `gh issue`; inbound owner surface. | real code from done-line 0038, but not in root README table yet. |
| `.claude/skills/arc-intake/SKILL.md` | Arc intake ritual prompt. | Operator contract. | real prompt. |
| `.claude/skills/glyph-knolling/SKILL.md` | Glyph ritual prompt. | Runs `glyphs/knoll.py` and review discipline. | real prompt. |

### Codex and Fence

| File | Role / value | Composition | Status |
|---|---|---|---|
| `fence/policy.py` | Family-neutral command policy. | Rendered to Codex and imported by Claude guard. | real; some justifications stale on merge authority. |
| `fence/render_codex.py` | Deterministic `.codex` renderer. | Emits rules and hook config. | real; tests pin byte equality. |
| `fence/probe_codex.py` | Codex hook seam probe. | Writes gitignored sensor trace. | real probe, not enforcement. |
| `.codex/hooks.json` | Rendered Codex hooks. | Summons + hook probes. | generated; never hand-edit. |
| `.codex/rules/ontum.rules` | Rendered Codex command policy. | From `fence/policy.py`. | generated; never hand-edit. |
| `.codex/CLAUDE.md` | Codex fence contract. | Documents generated surfaces and gaps. | contract surface. |

### Glyphs, Language, Pivot

| File | Role / value | Composition | Status |
|---|---|---|---|
| `glyphs/knoll.py` | Semiotic generator and validators. | Reads read-only vault and language survey files. | real; writes generated outputs. |
| `glyphs/viewer.html` | 3D/2D glyph cube viewer. | Generated `GLYPH_DATA`, authored app shell, tested JS math. | mixed: data generated, app real. |
| `glyphs/__init__.py` | Package marker. | Imports for tests/pivot. | real but tiny. |
| `glyphs/registry.json` | Registry output. | Generated by `knoll.py`. | generated. |
| `glyphs/knolling.md` | Knolling output. | Generated by `knoll.py`. | generated. |
| `language/s-frame-placements.json` | Proposed S-frame placements. | Parsed by knoll and pivot. | data input; PROPOSED/MODEL-GUESSED, not stamped. |
| `language/strata.md` | Four-strata intent map. | Cites read-only vault. | contract/intent, not code; records vault finding. |
| `language/syntax.md` | Syntax stratum. | Points to glyph grammar. | open gap: no refusing syntax gate. |
| `language/semantics.md` | Semantics stratum. | Names metric gap. | open: no executable metric. |
| `language/semiotics.md` | Semiotics stratum. | Points to glyphs. | real by glyph generator. |
| `language/pragmatics.md` | Pragmatics stratum. | Holds bdo's question. | open by design. |
| `language/basin.md` | Surveyed lexicon. | Parsed live by `knoll.py`. | data input; provisional/open entries preserved. |
| `pivot/instrument.py` | Deterministic recovery grader. | Reuses `glyphs.knoll` cube laws. | real; no model call. |
| `pivot/run.py` | Pivot CLI. | Emits prompts, grades recoveries, measures generation dirs. | real; play happens off-repo. |
| `pivot/measure.py` | Convergence/tension battery. | Validates lawful tilings first. | real. |
| `pivot/seed.py` | Seed prompt expansion. | Feeds generation experiments. | real seed, experimental. |
| `pivot/__init__.py` | Package marker. | Holds package identity. | real but tiny. |

### Tests

All listed tests are code-bearing receipts. The suite passed as a whole: 413 tests green.

| File | Pins / role | Status |
|---|---|---|
| `tests/test_loop.py` | Done-line 0001; durable loop, torn-tail, cache replay. | real receipt. |
| `tests/test_orchestrate.py` | Done-line 0002; fast ambient loop and cooling. | real receipt. |
| `tests/test_node.py` | Done-line 0003; real node/stamp pen. | real receipt. |
| `tests/test_web.py` | Done-line 0005; web inbox through one pen. | real receipt; ResourceWarnings on sockets in output, tests pass. |
| `tests/test_arc_confirm.py` | Done-line 0028; arc confirmation and auto-stamp. | real receipt. |
| `tests/test_digest.py` | Done-line 0032; owner digest. | real receipt; does not catch status-line refusal wording bug. |
| `tests/test_merge.py` | Done-line 0033; merge-node eyes. | real receipt. |
| `tests/test_merge_node.py` | Done-line 0033; merge-node hand guards. | real receipt. |
| `tests/test_merge_land.py` | Merge-node land/receipt path. | real receipt. |
| `tests/test_census.py` | Done-line 0029; organ census. | real receipt. |
| `tests/test_reflect.py` | Done-lines 0018/0020/0030; reflection fold/pen/beat. | real receipt. |
| `tests/test_tags.py` | Done-line 0032; intent tags and watcher split. | real receipt. |
| `tests/test_trust.py` | Done-line 0024; trust ladder refusal and lock. | real receipt. |
| `tests/test_minds.py` | Done-line 0025; mind registry refusals. | real receipt. |
| `tests/test_spawn_rail.py` | Done-line 0026; branded spawn rail. | real receipt. |
| `tests/test_summon.py` | Done-line 0008; summons/hook behavior. | real receipt. |
| `tests/test_prompts.py` | Done-line 0009 and story-gate contract. | real receipt. |
| `tests/test_mock_shame.py` | Done-line 0033; mock shame pressure. | real receipt. |
| `tests/test_write_guard.py` | Done-line 0013; write guard and records pen. | real receipt. |
| `tests/test_freeze_guard.py` | Done-line 0033; frozen done-lines and supersede. | real receipt. |
| `tests/test_fence.py` | Done-lines 0027/0029; registry/render parity. | real receipt. |
| `tests/test_git_pen.py` | Done-line 0020; git pen and guard. | real receipt. |
| `tests/test_pr_ritual.py` | Done-line 0011 and branch ritual surfaces. | real receipt. |
| `tests/test_push_recovery.py` | Branch ritual 0.6.1 recovery push. | real receipt. |
| `tests/test_garden.py` | Worktree gardener classifier. | real receipt. |
| `tests/test_overnight_loop.py` | Done-lines 0031-0033+; overnight brief/pickup/checkpoint. | real receipt. |
| `tests/test_arc_intake.py` | Done-line 0038; GitHub arc intake parsing. | real receipt. |
| `tests/test_envoy.py` | Done-line 0015; envoy package pen. | real receipt. |
| `tests/test_knoll.py` | Glyph knolling laws, registry, outputs. | real receipt. |
| `tests/test_viewer_cube.py` | Viewer cube/frame JS math. | real receipt. |
| `tests/test_pivot.py` | Done-line 0031; pivot instrument. | real receipt. |
| `tests/test_pivot_measure.py` | Done-line 0031; measurement battery. | real receipt. |
| `tests/test_pivot_seed.py` | Done-line 0031; seed prompt. | real receipt. |
| `tests/test_placement.py` | Done-line 0023; cross-ref address collisions. | real receipt. |

### Generated and Append-Only Surfaces

| File | Accounting |
|---|---|
| `.ai-native/log/events.jsonl` | append-only truth; fold only. |
| `.ai-native/log/receipts.jsonl` | append-only truth; fold only. |
| `.ai-native/log/admissions.jsonl` | append-only truth; fold only. |
| `exports/log.jsonl` | append-only disclosure ledger; fold only. |
| `.ai-native/inbox.html` | gitignored render cache; rebuild via `python -m loop.web render`. |
| `.ai-native/queues/`, `.ai-native/offsets/` | gitignored cache; rebuild from log. |
| `.ai-native/mock-shame.json` | gitignored nag tally; not truth. |
| `.ai-native/log/tool-use.jsonl` | gitignored Claude watcher trace; not truth. |
| `.ai-native/log/codex-hook-probe.jsonl` | gitignored Codex probe trace; not truth. |
| `exports/*` package dirs | gitignored rebuildable envoy artifacts; `exports/log.jsonl` is the record. |

## needs-you

1. Decide whether the next repair should be the **merge-authority wording pass**. My read: yes. It is the highest-risk drift because it changes what agents tell bdo and what agents believe they may do.
2. Decide whether `loop.digest`'s closing status should count `d["refusals"]` as a `report` even when no divergence/open item remains. My read: yes; the sentence currently contradicts its own rendered span.
3. Decide whether this audit loop should become a tool (`loop.audit` or a `.claude/skills/audit` pen) or stay a report ritual for now. My read: one more manual pass first; the categories are still stabilizing.

Instruction conflicts preserved:

- `AGENTS.md` and `CONTRIBUTING.md` say bdo merges / bdo is last stop. Root `CLAUDE.md`, `pr.py land`, and merge-node skill say bdo confirms arcs and the merge-node lands. The invariant can compose, but the wording no longer does.
- `branch-ritual/SKILL.md` contains both amended handoff language and older standing-shape language saying bdo merges a finished arc into main.
- `merge-node/SKILL.md` says the land command runs `gh pr merge --squash --delete-branch`; `pr.py land` intentionally omits `--delete-branch` to avoid the receipt-loss bug.

## End-state

`report` - the audit loop is set up, the first full code inventory is recorded, live folds and gaps are named, and the suite is green (413 tests). The branch has only the new done-line and this report as authored changes.

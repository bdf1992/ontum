# Report 0022 — the mind registry: judging minds become records

## What landed

**[done-line 0025](../done/0025-mind-registry.md) — met.** The first wave-2
piece of [epic.experience-layer](../epics/epic.experience-layer.json)
(`atom.model-registry.v0`): a judging mind is now an admitted record, not a
code literal — the sibling of the surface registry, for minds.

- **[loop/minds.py](../../loop/minds.py)** — a pure fold over `mind`
  admissions, with its own registration pen (`loop.minds register`, mirroring
  `loop.reflect`). Two families: `local`, the privileged default (zero
  disclosure), and `external` (GPT, …), the deliberate, receipted exception.
  bdo-only.
- **A backing is a reference, never a secret** — `env:NAME`, `profile:NAME`,
  a URL, `odysseus://…`. An inline key (`sk-…`, `api_key=…`) is refused;
  credentials are referenced, never stored in a record (I-8).
- **No-self-signing grows a which-mind axis** — `judge_refusal(judging,
  writing)`: a mind may not judge output its own backing wrote, even across an
  API (D-2). The pure rule is here; wiring it onto receipts is the spawn
  rail's job.
- **[tests/test_minds.py](../../tests/test_minds.py)** — the §10 proof: the
  registry refuses (secret backing, non-bdo, unknown family, self-judging).
  Suite: 191 OK.

## needs-you

- **Stamp this PR** (mind registry, done-line 0025).
- The registry starts empty. To wire your local stack (e.g. odysseus):
  `python -m loop.minds register --mind local.<name> --family local --backing "odysseus://localhost:8080/v1" --by bdo`.
- **Heads-up for the merge:** done-line `0024` collides across
  `claude/trust-ladder` (#22) and a `claude/codex-guest-engineer` branch —
  `placement check .ai-native/done` flags it; one needs renumbering when they
  land.

## End-state

`report` — judging minds are admitted records with a pure read-fold, a
bdo-only registration pen, secrets kept out, and the no-self-sign rule grown
to span minds. The reach (calling a model) and receipt-wiring are named out of
scope. Next wave-2 piece: the branded spawn rail. Ready for your stamp.

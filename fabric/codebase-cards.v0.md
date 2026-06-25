# Codebase Cards — v0

**Purpose:** paired *code + learning* cards that document the code that
exists — what it does and how it connects as a whole. Each card is a SPEC,
written to be sent to an image-gen AI which assembles the final visual aid
(the wave1 particle cards in `docs/sources/.../wave1_particle_card_export_package/`
are the visual precursor for the look).

**Three families** (each card declares one):

- **Self / Visual** — identity, the observer, what persists. The "self" pole.
- **System / Code** — the structures and how they fold together.
- **Mechanics / Binding** — how parts bind: the rules, hashes, admissions —
  the binding energy that holds work into the record.

## Card spec format

Each card carries, in order: an **id**, its **family**, the **subject** it
documents, a **pointer** (the `file:line` / log record it resolves to — the
provenance leg; a card with no resolvable pointer is OPEN, not drawn), **what
it does**, **how it connects**, a text-first **aid** (Mermaid/ASCII, legible
without the render), and the **gen prompt** (the block handed to the AI).

---

## Card 01 — System / Code — "The Log Is Truth"

- **family:** System / Code
- **subject:** the fold — state is computed, never stored
- **pointer:** `loop/reconcile.py` (`Fold`); `.ai-native/log/{events,receipts,admissions}.jsonl` `[P]`
- **what it does:** three append-only JSONL logs are the only truth. The
  state of any atom is a pure fold over them. `queues/` and `offsets/` are
  cache — deletable, rebuilt at any time. A torn last line is dropped and
  re-derived (a hard kill mid-write is safe).
- **how it connects:** everything builds on this — `orchestrate`, `node`,
  `summon`, `web` all fold the same log. The log is the topic; the rest are
  readers.

```
events ─┐
receipts┼─▶ [ Fold ] ─▶ current state     (cache: queues/offsets, rebuildable)
admits ─┘                  ▲
   torn last line ─ ─ ─ ─ ─┘ dropped, re-derived next pass
```

*(gen prompt → [visual-requests.md](visual-requests.md))*

---

## Card 02 — Mechanics / Binding — "Identity Is Content Hash"

- **family:** Mechanics / Binding
- **subject:** what binds work into the record — the hash and the admission
- **pointer:** `loop/reconcile.py` (`PIPELINE`, content-hash identity);
  `loop/node.py` (`admit-real`); `.ai-native/nodes/` `[P]`
- **what it does:** an atom's identity is the sha256 of its file bytes; the
  idempotence key is `(node, artifact_hash)`, so re-runs never double-act.
  Editing an atom mints a new version that restarts the pipeline. A mock
  stage becomes **real** only through a logged `node_real` admission — read
  at runtime, never a code literal. The binding energy is the receipt.
- **how it connects:** the pipeline stages, the summons, the gates — all key
  off `(node, artifact_hash)`; realness is admitted, not asserted.

```
file bytes ──sha256──▶ artifact_hash ──┐
                                        ├─▶ (node, artifact_hash) = idempotence
node_real admission ──▶ stage: mock ──▶ real   (the bind = a logged stamp)
```

> **gen prompt:** A learning card titled "Identity Is Content Hash." A file
> passing through a hash function into a glowing fingerprint; a chain-link
> whose binding glow is labeled "receipt"; a dim "mock" stage crystallizing
> into a solid "real" stage at the moment a stamp lands. Particle-card
> aesthetic, emphasis on the bond.

---

## Card 03 — Self / Visual — "The Mortal Session"

- **family:** Self / Visual
- **subject:** the session as the virtual node; what persists is the files
- **pointer:** `loop/summon.py`; `.ai-native/CLAUDE.md` ("sessions are
  mortal — the files are what survives") `[P]`
- **what it does:** a session blinks in, is handed its summons by the hook,
  judges through the one pen, and dissolves. The session *is* the virtual
  node. The "self" of the system is not the session — it is the durable
  record the session leaves behind.
- **how it connects:** `SessionStart` / `UserPromptSubmit` hooks →
  `loop.summon --hook`; verdicts land only through `loop.node judge` (§7
  node prompts, hashed onto receipts).

```
   (session blinks in) ─▶ summon ─▶ judge ─▶ (dissolves)
            ░░░░░                                ░░░░░
   ───────────────────  the record persists  ───────────────────  ◀ the self
```

> **gen prompt:** A learning card titled "The Mortal Session." A translucent
> figure appearing at a labeled node, performing one act, then fading — while
> a solid engraved ledger beneath it remains, glowing. The caption frames the
> ledger, not the figure, as "the self." Particle-card aesthetic, sense of
> impermanence over permanence.

---

## Next (on your nod)

- Expand each family to a full set (one card per real module: `orchestrate`,
  `disposer`, `census`, `digest`, `heal`, `gate`, the fence, the pens …).
- Decide the card *typology* — the wave1 backlog proposed
  Force / Property / Object / Mechanic / Cord; our pairs are
  Self·Visual / System·Code / Mechanics·Binding. Reconcile the two.
- Run the gen prompts through the AI and drop renders beside each spec.

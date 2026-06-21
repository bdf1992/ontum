# Relation-part admission — the contract that keeps a learned part log-native

*A data contract under `epic.model-free-mode-response`
(`.ai-native/epics/epic.model-free-mode-response.json:12`), governed by
`causality/CLAUDE.md`. It specifies the **admitted-record shape** that lets
a learned/relational part — a relation bucketer, a semantic hash over
atoms, an in-stream learning-progress estimator — produce signal **without
becoming a second source of truth**. The finding it formalizes:
"Learning-progress stays log-native without breaking log-as-truth when the
relation or model artifact is admitted with its model id, version,
threshold, policy, and scope pinned in admitted records"
(`.ai-native/atoms/atom.model-free-mode-resp-learning-log-native.v0.json:5`;
glue at `.ai-native/epics/epic.model-free-mode-response.json:29`).
Status: **PROPOSED, post-review** — this is the contract, not yet a built
part; it graduates by the value gate and bdo's confirm-arc.*

## The problem this contract exists to prevent

A learned part is a function whose output **cannot be re-derived from the
bytes by a cold reader** — it depends on a model, a version, a threshold.
That is the exact shape the substrate forbids of *truth*: "The log is truth;
everything else is a fold" (`loop/CLAUDE.md`), and a fold is
byte-deterministic and rebuildable. If a relation part writes its bucket
assignments or its learning-progress numbers straight onto the field as
fact, the design is broken the same way Causality would be broken by
treating a projection as authoritative (`causality/CLAUDE.md`: "Causality
is a projection, never a second source of truth").

The resolution is the one the inference plane already uses: **the part's
governing parameters are admitted records, signed and superseded-never-
erased; the part's outputs are a fold over those admissions plus the log,
never a free-standing truth.** What the part asserts is always traceable to
"under which admitted model, at which version, over which threshold, by
whose stamp." This mirrors how a *node* becomes real
(`loop/reconcile.py:154`–`165`, `node_real` admissions) and how the
inference gateway is governed (`loop/inference.py:237`–`263`,
`policy` admissions): the behavior is re-derived from admitted config, never
hard-coded and never self-asserted.

## The admitted record: `relation_part`

A relation part is wired by **one admission** of `type:
"relation_part"`. Until that record is on the log, the part does not
exist for the system — its outputs are refused (default-deny, the same
posture as `loop/inference.py:98`–`125`). The record's required fields, each
load-bearing:

| field | what it pins | analogue already on disk |
|---|---|---|
| `id` | the admission's own content-hash id | `adm.` ids, e.g. `loop/inference.py:248` |
| `type` | `"relation_part"` | `"node_real"` (`loop/reconcile.py:160`), `"policy"` (`loop/inference.py:250`) |
| `model_id` | which learned model produces the signal | `mind` id (`loop/inference.py:253`) |
| `version` | the model/weights version this admission governs | the `.v<N>` discipline (`loop/reconcile.py:238`–`249`) |
| `threshold` | the cut a continuous signal crosses to assert a bucket/verdict | (new — the learned part's dial) |
| `policy` | the (caller, surface) RBAC this part may answer for | `policy` triple (`loop/inference.py:113`) |
| `scope` | how far the part's output may reach: `propose-only` or `full` | `loop/inference.py:55`–`58` |
| `by` | who admitted it (governance is the owner's, D-4) | `loop/inference.py:258` |
| `supersedes` | the prior part admission this replaces, or null | `loop/inference.py:259` |
| `ts` | admission time | `loop/reconcile.py:77`–`78` |

The shape is deliberately the **same grain** as the records already proven
on the log. A real `node_real` admission on disk reads:
`{"type":"node_real","stage_node":…,"real_node":…,"by":"bdo …",
"supersedes":null,"ts":…}` (verifiable in
`.ai-native/log/admissions.jsonl`). A `policy` admission carries
`caller`/`surface`/`mind`/`permit`/`scope`/`by`/`supersedes`/`ts`
(`loop/inference.py:247`–`262`). `relation_part` is their sibling: it names
*which model, which version, which threshold* a learned read is governed by,
exactly as those name *which node, which mind, which scope*.

## The fold contract (how outputs stay log-native)

1. **Outputs are a fold, not a write of fact.** A relation part's bucket
   assignment or learning-progress number is computed *as of* an admission
   id and a log offset — like a `FoldObservation`
   (`causality/contracts/projection-api.md:83`–`96`), which carries
   `source_fold`, `observed`, and `at_record`. The output cites the
   `relation_part` admission that governed it. Delete the cache, re-run:
   the same admission + the same log bytes yield the same reading. A reading
   that cannot name its governing admission is invalid.

2. **`record_kind` is `folded` or `projected`, never `authored`-as-truth.**
   The eight-family invariant holds (`projection-api.md:146`–`152`): the
   part's emitted records point back at the log and the admission; the
   moment one is treated as authoritative over the bytes it read, the design
   is broken.

3. **Scope gates reach.** A `propose-only` part may surface a candidate
   bucket or a learning-progress reading; it may **not** advance an atom or
   write a verdict. Widening to `full` is a separate, explicit stamp — the
   tier-2 lever the inference plane already enforces
   (`loop/inference.py:128`–`144`, `policy_scope`).

## The §10 refusal (the teeth)

The contract is non-vacuous because it **refuses a learned part that is not
fully pinned**. An part admission that is *locally fine* — it names a model
and emits plausible signal — is still refused if any governing field is
absent, because an under-pinned learned read is precisely the thing that
would corrupt log-as-truth. Concretely, a checker over this contract must
refuse:

- **The unadmitted part.** Signal produced with *no* `relation_part`
  record on the log. Default-deny: no admission, no part (the
  `loop/inference.py:124`–`125` posture — "no thought without a rule").
  Removing this check lets any process assert relation facts onto the field;
  that is the whole failure mode.
- **The under-pinned part.** A `relation_part` admission missing
  `model_id`, `version`, `threshold`, `policy`, or `scope`. Each absence is
  a way the output stops being re-derivable: no `version` and the same
  reading silently changes when weights change; no `threshold` and the
  bucket boundary is a hidden constant (a bare un-admitted dial, the very
  thing `loop/CLAUDE.md` forbids — "setpoints, realness, ticks are admitted
  records … never constants in code"); no `scope` and `propose-only` cannot
  be enforced.
- **The output that cannot cite its governor.** A bucket/score record whose
  `at_record`/admission citation does not resolve to a real
  `relation_part` admission — a *ghost* in the
  `causality/CLAUDE.md` taxonomy sense (claims a backing that does not
  resolve). This is the same tooth `term_economy.py` bites with
  (`causality/CLAUDE.md`: "a citation that points to nothing is `ghost`").

A locally-fine **bad input** that this contract must catch: an part
admission that pins `model_id` and `version` and emits a learning-progress
number, but omits `threshold` and `scope`. Nothing about it looks wrong in
isolation — it has an id, a model, a version, a timestamp. It is refused
anyway, because without `threshold` the number's bucket boundary is an
un-recorded constant and without `scope` it could silently reach past
propose-only. If that refusal is removed, an un-pinned learned part writes
onto the field and log-as-truth is broken — which is exactly the invariant
this contract was authored to hold.

## What this contract does NOT build (the cut, §10)

It does **not** build the relation part, the semantic hash, or the
learning-progress estimator — those are later pieces of the arc
(`…relation-ledger.v0`, `.ai-native/epics/epic.model-free-mode-response.json:20`).
It does **not** double-build the inference plane's `policy`/`route`
governance (`loop/inference.py`) or the node-realness lifecycle
(`loop/reconcile.py`) — it **reuses** their record grain. It is the
*admission shape*: the seam through which a learned part is allowed to
exist on the log at all, and the refusal that keeps an un-pinned one out.
Promotion of any part past `proposed` stays a human/owner admission (D-4),
the same hard rule every other contract here lives by
(`causality/contracts/projection-api.md:131`–`133`).

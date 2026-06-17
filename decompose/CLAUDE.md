# decompose/ — the change-axis gate

The reusable decomposition procedure, made to *cost something*. The
node-graph / UI split bdo ran was one **application** of a procedure;
this directory holds the procedure's teeth — the one step that can
refuse (done-line 0104).

The procedure (bdo, 2026-06-17):

1. **Anchor** on the parts already trusted; decompose *around* them.
2. **Find the change-axes** — an axis of independent variation (a
   distinct *reason*, *rate*, or *authority* of change).
3. **Cut** so each module owns exactly one axis (one reason to change).
4. **Orient** the dependencies into a DAG; a cycle is a false boundary.
5. **Contract the seams** — the only thing two modules share is a
   minimal stable interface; everything else stays private.
6. **Verify by the change test** — a cut is good if a module's internals
   can change without touching neighbours except through the contract.

The load-bearing claim is **modules align with axes of independent
change, not with categories of thing** (`visual` / `logic` / `data` are
a cheap proxy that usually correlates but sometimes lies). A claim with
no teeth drifts; [change_gate.py](change_gate.py) gives step 6 teeth.

## What it is (and is not)

A pure, read-only, stdlib fold in the `causality/term_economy.py` grain:
it reads a **declared decomposition manifest** (a human/agent authors it,
the same way a `*.seed.json` is declared input) and **refuses** the cuts
the procedure forbids. It is *not* a second source of truth and it does
not author manifests — it judges the one handed to it. A manifest that
passes is `coherent`; a manifest that fails is `refused`, each finding
naming its kind, its subject, and why (the same shape `loop/gaps.py`
findings carry).

## The fork bdo confirmed: AI-native specialized (done-line 0104)

A seam-contract carries `trust` / `authority` / `change_rate` as
**first-class required fields** — because in an AI-native engine the
modules span deterministic code, learned models, prompted agents,
contexts and memory, with wildly different change-rates and authorities
(a prompt is edited hourly; a schema is versioned and gated). The
contracts between code / model / agent *are* the protocol discipline
that lets the three coexist — the same Software-3.0 shared-protocol
principle used as a *decomposition* rule, not a runtime one. A seam
without those fields is a **smuggled seam** and is refused.

## The refusals (each one a hardened invariant)

- **smeared-axis** — two modules declare the same change-axis (the §10
  teeth: two locally-fine modules refuse to fit; they are really one).
- **incomplete-axis** — a module's axis is missing `reason` / `rate` /
  `authority` / `kind`; it cannot be reasoned about.
- **dependency-cycle** — `depends_on` forms a cycle; a false boundary
  (the cycle is one module, or a missing third they both point to).
- **uncontracted-seam** — a dependency edge crosses no named contract.
- **smuggled-seam** — a contract names a non-module, or omits the
  AI-native fields `trust` / `authority` / `change_rate`.

Each new refusal is one more invariant; the schema and the test move
together. The *undercut* detector (one module secretly owning two axes)
is the named next node — out of scope here (done-line 0104).

```sh
python decompose/change_gate.py check                          # the anchor manifest
python decompose/change_gate.py check --manifest <path>        # judge any manifest
python -m unittest tests.test_change_gate -v                   # the §10 test
```

Every run ends in `done | report | needs-you`. `coherent` is `done`;
`refused` is `report` (the findings are the work, not an error to code
around). The manifest is *declared input* — never hand-tune it toward a
pass; fix the decomposition or the schema, so the gate stays honest.

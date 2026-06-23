# The grammar — quick reference

## Systems (8) — what maintains a domain

- **Records** — what happened
- **Repository** — what's known (code, knowledge)
- **Reason** — why
- **Peers** — who (the independent eyes)
- **Names** — what-this-is (identity / seal)
- **Settings** — what's wanted (setpoints, approvals)
- **Sessions** — the doing (mortal runs)
- **Resource** — bounded capacity (compute, budget)

## Pointers (8) — how you touch a surface

- **APPEND** — add to the record
- **CITE** — point at knowledge
- **VERDICT** — judge / decide
- **FOLD** — read and reduce
- **HASH** — name / seal (identity)
- **ADMIT** — authorize / set
- **STEP** — advance one bounded move
- **SOURCE** — draw on as input

## Native pairs (the diagonal — each system's home pointer)

- Records · APPEND
- Repository · CITE
- Reason · VERDICT
- Peers · FOLD
- Names · HASH
- Settings · ADMIT
- Sessions · STEP
- Resource · SOURCE

## Topology (3 axes — how it sits against a boundary)

- Internal ↔ External — region
- Ingress ↔ Egress — flow
- Local ↔ Global — reach
- **Boundary** — the seam / fence everything is measured against

## How to compose

- Native address: `System.Pointer` — e.g. `Records.APPEND`
- Cross address: `POINTER(System)` — e.g. `HASH(Records)`
- A cell is real only if it carries a refusal (example + non-example); otherwise it's **void**.

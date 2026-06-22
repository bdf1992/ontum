# grammar/ — the systems × pointers working surface

A working environment for one question: **what is ontum's platform
grammar, and which of its cells are real?**

The model (bdo's, this session):

- **Systems** are bounded domains — *a System is a record program /
  application* (DDD bounded contexts).
- **Pointers** are the surface operations that touch a system.
- The **native diagonal** gives each system its home pointer
  (`Records.APPEND`, `Peers.FOLD`, …) — its *native* face, not its
  *only* one.
- The **cross-product** `POINTER(System)` is composition: any pointer
  may address any system.
- The **platform is the *admitted* cross-product** — most cells start
  closed (`⊘`) and light up only when opened and proven.

This is an **analysis surface**, a sibling of `causality/term_economy`
and `loop/parity`: it *reads* the repo and *verdicts* cells. It is not
itself the platform.

## The one hard rule (the grip discipline)

**A cell is real only if it carries a refusal.** Every filled cell names
an **example**, a **non-example** (the thing it refuses), and a
**citation** (`file:line` or a log record). A cell with no honest
non-example is a **gamut-hole** (`✗ void`), not a feature — mark it,
don't gloss it. A citation that resolves to nothing is a **ghost** and
is refused, exactly as `term_economy` refuses a ghost term. Nothing here
mints; promotion of a `◐ build` cell to real happens in code, then is
recorded back here.

## Cell states

| token | meaning |
|---|---|
| `●` | **native** — the diagonal; real by construction |
| `✓` | **have** — a composed cell that resolves to real, refusing code |
| `◐` | **build** — a named, plausible gap (not yet real) |
| `✗` | **void** — the pointer-on-system discriminates nothing; refused |
| `⊘` | **unopened** — not yet examined |

## Layout

- [grammar.md](grammar.md) — the spine: layers, the eight systems, the
  eight pointers, the native diagonal, the composition syntax, the cube
  geometry, and the industry-standard parity.
- [matrix.md](matrix.md) — the 8×8 working matrix and the per-cell
  example / non-example / citation fills, worked one axis at a time.

A local analysis env: nested-loaded when working here, deliberately
**not** `@`-imported into the root `CLAUDE.md` (its knowledge binds only
inside this directory, like `tests/`).

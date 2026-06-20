# Done-line 0124 — GitHub is a deterministic reflection of local — the merge receipt carries the atoms it landed (Phase A: D-12 + the per-atom↔PR join)

Written before code, per §9.4. When this line is met, stop.

**Goal:** bdo's direction (2026-06-18): *GitHub should only be a
deterministic reflection of what we have locally, and the pens should
prove it by being a write-through carbon copy.* He thought this was
already required — it is, in spirit: the records pen's carbon-copy
(done-line 0070) and D-5 ("the log is truth") make every external
surface downstream. But that discipline was never extended to the
**GitHub-boundary** pens, and the terminal-pull gateway (done-line 0123)
found the leak: the merge-node's `_merge_receipt` records *that* a PR
landed (`pr`, `epic`, `head`) but not *which atoms* reached main — so the
pipeline namespace (per-atom) and the git-merge namespace (per-PR) do not
join, and the loop cannot tell which completed pieces are on main. This
is **Phase A** of his two-phase direction: name the invariant and close
the leak. (Phase B — updating the pipeline seams with the gateway
implementations of §13.10 — is its own later arc; it depends on this
join.) **Arc:** `epic.owner-harness`.

> **Done when:** (1) the doctrine carries **D-12** — *external surfaces
> are deterministic reflections of the log; the pen that writes to one is
> a write-through carbon copy that carries enough to re-derive the local
> truth it reflects* (the records-pen carbon-copy, done-line 0070,
> generalized to every boundary; a surface write that drops the local
> identity is a lossy reflection and a pen bug). (2) The merge-node's
> `_merge_receipt`/`cmd_land` (`.claude/skills/branch-ritual/pr.py`)
> carry **`landed_atoms`** — the `artifact_id`s the PR's range adds,
> computed by **reusing the existing `_range_atom_facts` reach** (the
> same fold that gates the PR at open/land — no second derivation). (3) A
> pure join fold reads them so *"did atom X reach main?"* is answerable
> from the log alone (`atoms_on_main` in `loop/digest.py`, surfaced in
> the digest as a confirmed-on-main count — a live reader, not a dead
> field). (4) Tests with §10 teeth: a `landed` receipt carrying
> `landed_atoms` **joins** to its atoms; the old shape without them
> **does not** (the lossy-vs-faithful contrast is the test, and it would
> fail a receipt that fabricated the join from the epic instead of the
> diff). Full suite green; the work dogfooded as an atom on the log
> (atom + an independent value-gate receipt naming it, D-2); opened as a
> PR.

> **Non-example:** re-deriving the PR's atom list instead of reusing
> `_range_atom_facts` (a second source of the same truth — §10); a
> `landed_atoms` computed from the epic's declared pieces instead of the
> PR's actual diff (a fabricated join — mercury); back-editing the 90
> historical merge receipts to add atoms (history is append-only — the
> gap closes **forward**; old receipts stand as honest, lossy history,
> and `atoms_on_main` reports them as unjoined); wiring the terminal-pull
> gateway to *drain* on this join (the gateway's own follow-on, on its
> branch, not here); building the seam→gateway implementations (Phase B,
> a separate arc).

> **Evidence expected:** the doctrine's D-12; the `pr.py` diff
> (`_merge_receipt` + `cmd_land`); `loop/digest.py` `atoms_on_main` + the
> digest surface line; a test module (or additions) with the join teeth;
> the atom + its value-gate receipt; the full suite green; a PR.

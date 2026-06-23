# Done-line 0187 — The RAW receipts door: a re-deriving receipt-append PR lands without an atom

Written before code, per §9.4. When this line is met, stop.

> **Done when:** the off-log gate (`loop.pr_audit` + the `pr.py audit` reach)
> recognizes a FOURTH way for a PR to be backed — a **receipts-only** PR, whose
> only changed path is `.ai-native/log/receipts.jsonl` and whose every appended
> line **re-derives to its stored id** — and exempts it from needing an atom, the
> same shape as the records (0172) and phrasing (0117) doors. `receipt_rederives(rc)`
> reuses the one minting derivation (`loop.reconcile.short_hash` over
> `node|artifact_id|artifact_hash|event_id`, the exact key `make_receipt` hashes —
> I-4), so a RAW append proves itself and a fabricated or tampered line cannot;
> `receipts_only(paths)` is the pure file-scope check; `orphan_reason(..., receipts_only,
> added_receipts)` returns None only when every appended line re-derives, and names
> the smuggling otherwise; `pr.py audit` recomputes both from the diff and refuses
> a diff that rewrites log history (removed lines), so the door cannot be lied to.
> Proven by `tests/test_pr_audit.py` (joined to the suite) and **non-vacuous**: a
> real on-log receipt is admitted, a fabricated id / tampered field / missing field
> / merge-receipt scheme each REFUSE, one bad line poisons the batch, a non-receipt
> change falls back to needing an atom, and the audit labels a clean receipts PR
> `backed_by: ["receipts-door"]` — proven to fail under a vacuous always-admit
> checker (7 tests flip). Backed by `atom.raw-receipts-door.v0` with an independent
> value-gate accept; the suite is green.

## Why

bdo's RAW vs RAI cut: a RAW append is a deterministic FACT that re-derives from
its own bytes (a receipt id recomputes from its content); an RAI artifact is
authored or inferred and cannot. RAW is the doctrine's only free layer and should
be admissible. The off-log door had it backwards — it discriminated by file
EXTENSION, waving through authored `.md` (RAI: reports, done-lines) while refusing
a provable `.jsonl` receipt append as an off-log orphan. That blocked PR #656,
which carries the stranded, real value-gate acceptance `rcp.c21c49ac30c1` (its
atom's code already landed via #554; the acceptance stranded off-trunk — the #617
integrity gap). The fix replaces "what file is it?" with "does it prove itself?":
a receipt-append PR lands iff every line re-derives, and anything else — a
fabricated line, a tampered field, or any non-receipt change — is refused. The
door is deliberately tight: only the receipts log, only appends, only lines that
recompute to their stored id.

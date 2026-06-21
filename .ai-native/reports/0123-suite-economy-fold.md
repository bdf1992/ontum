# Report 0123 — The test suite becomes a governed organ — the economy fold

## What landed

**done-line 0171 — the test-suite economy fold (piece 1 of the upgrade).**

bdo asked for the suite (826 tests) to be **broken down, typed, accounted,
and attributed**, with mutation/change testing — all running *like running
water* (ambient, taken for granted because it works). He chose **derived
typing** (infer from structure, surface the undecidable as a gap, never guess)
and named the shape: not a bare script, but a **governed organ** with a
**test-operator** (the hand) and **test-administrator** (the governance seat)
over it — the loop's own propose/dispose, bdo last stop.

This piece is the foundation both assays ride:

- `loop/suite.py` — a pure read-only `ast`-fold over `tests/*.py`. **Types**
  each test by structural evidence (guard / refusal / byte-determinism / fold
  / pen-seam / integration / unit, + honest **untyped**). **Attributes** it
  (organ from filename + imports + subprocess targets; done-lines pinned from
  docstrings). **Accounts** it as a census (type histogram, organ→covering
  count, frozen-done-line→pinning count). `--json` emits the dataset.
- `tests/test_suite.py` — 16 §10 tests. The teeth: `refusal` is assigned on
  rejection *evidence*, never the method NAME, so a refusal-named/no-rejection
  test surfaces as **mislabeled**; the classifier fails a constant (must yield
  ≥5 distinct types); an undecidable test reads `untyped`; an unpinned frozen
  done-line surfaces as `unreceipted-contract`. Two of the teeth caught real
  bugs in my own first draft (a `determinist`-vs-`determinism` regex miss; a
  `[^)]*` that stopped at a nested paren).
- `loop/CLAUDE.md`, `tests/CLAUDE.md` — the organ registered next to where it
  lives; the conventions tests/CLAUDE.md states are now *measured*, not prose.

First real read of the repo's own suite: **842 tests, 68 files, 52 organs** —
503 refusal, 239 unit, 54 guard, 25 integration, 14 fold, 8 byte-determinism,
4 pen-seam, **1 untyped**; 557 tests assert a rejection (the §10 culture is
real and measurable); 56/87 frozen done-lines pinned by a test; 11/52 organs
have no test naming them. Byte-deterministic (verified). Full suite green.

## needs-you

- **Direction (not blocking): carry this as a multi-session outcome.** The
  full ask spans sessions, so it belongs in `outcomes/` as an evidence-bearing
  probe-set (every organ pinned, every frozen done-line pinned, per-organ
  mutation kill-rate, the seats actually *used* on the log), with the
  remaining pieces as their own frozen done-lines: (2) the mutation assay
  (hand-rolled stdlib AST, the operator's instrument), (3) the change-scope
  assay (diff → attributed tests = blast radius), (4) the test-operator /
  test-administrator node seats. I recommend this framing; it is yours to
  confirm.
- **Two adjudication candidates, not errors.** `test_..._must_not_fit`
  (asserts the consequence, not the rejection) and
  `test_every_term_carries_a_must_not_mean_guard` (`must_not_mean` is a domain
  noun, not a refusal claim) are exactly the borderline calls the future
  test-administrator settles. Left as live findings, by design.
- **Plainly, per the owner-ask-shame beat:** this session did **not** address
  the 11 pre-existing owner-asks parked in reports 0047/0068 — they predate
  this arc and are out of its scope. Naming that here rather than chasing it.

## End-state

`report` — piece 1 (the economy fold) is built, green, and byte-deterministic;
the mutation assay, change-scope assay, and the operator/administrator seats
are the named next pieces, best carried under a multi-session outcome.

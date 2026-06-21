# Done-line 0171 — The test suite becomes a governed organ: a read-only fold types, attributes, and accounts every test

Written before code, per §9.4. When this line is met, stop.

bdo asked for the suite (826 tests, 67 files) to be **broken down, typed,
accounted, and attributed** — and for the whole thing to run *like running
water*: ambient, taken for granted because it works, not because it is ignored.
Today attribution stops at the file scale (module docstrings pin a done-line;
only ~6 of 826 methods carry their own) and nothing types a test or counts the
suite beyond what `unittest discover` prints. This is the **foundation piece**:
the loop sensing its own test body the way `census.py` senses its code body —
the read-only fold the later operator/administrator nodes and the mutation /
change-scope assays all ride. Derived typing, not declared (bdo's call): infer
from structure, surface the undecidable as a gap, never guess a label (the
`tags.py` discipline). This piece builds only the fold and its teeth; the
governing seats and the assays are separate nodes, each its own done-line.

> **Done when:** `python -m loop.suite census` runs a pure, read-only, stdlib
> `ast`-based fold over `tests/*.py` that (1) assigns every test method a
> **derived type** from structural evidence — `guard` (subprocess + exit-code
> contract), `refusal` (a §10 reject/deny/refuse assertion), `byte-determinism`
> (`read_bytes` equality), `fold` (pure-determinism / re-run identical),
> `pen-seam` (write-twice-noop / wrong-node-refused), `integration` (drives a
> temp root), `unit` — returning an honest **`untyped`** for a test no signal
> decides (never a fabricated label); (2) derives each test's **attribution** —
> the organ(s) it covers (from imports + subprocess targets resolved against the
> real `loop/*.py`, hooks, and skill pens) and the done-line(s)/clauses it pins
> (from docstrings + cited `D-`/`§`/`done-line` tokens); (3) **accounts** it as a
> census — a type histogram, organ→covering-test count (an organ with zero
> covering tests named, the `census.py` wired·idle grain), and frozen-done-line
> →pinning-test count (a frozen done-line with zero pinning tests named an
> `unreceipted-contract` gap); the run is byte-deterministic over the same
> committed bytes and ends with a clear `done | report` result on stdout; and
> `tests/test_suite.py` pins the §10 teeth: a `refusal`-typed test that asserts
> no rejection surfaces as **mislabeled**, an undecidable test classifies as
> `untyped` (not a guessed type), a frozen done-line nobody pins surfaces as an
> `unreceipted-contract` gap, and the test **fails on a constant/fabricated
> classifier** (the `test_term_economy.py` bar).

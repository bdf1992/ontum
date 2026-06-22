# Done-line 0185 — Spec particle identity

Written before code, per §9.4 — node 1 of epic.grammar, the load-bearing floor. When this line is met, stop.

> **Done when:** loop/spec.py gives a spec a content-hash identity (never a .vN id-string), records create and supersede as appended provenance admissions (--by, ts, reason; supersession names old_hash AND new_hash, no retro-invalidation), and derives head/version state by folding the log alone (D-8); AND tests/test_spec.py proves it §10-non-vacuously — an in-place byte edit mints a new version the fold sees, while an id-string split collapses the two — with the full suite green.

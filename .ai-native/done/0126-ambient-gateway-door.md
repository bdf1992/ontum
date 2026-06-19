# Done-line 0126 — The ambient gateway door — typed-message registry + schema validation at the seam

Written before code, per §9.4. When this line is met, stop.

> **Done when:** `loop/gateway.py` types a message at the door — a governed typed-message registry (closed core types + admitted `message_type` extensions, the `tags.py` proposed-tier shape, folded from the log) and a pure `type_message(fold, msg)` that returns a **typed** result for a message carrying its declared type's required fields, and a **named refusal -> dead-letter** for one that is unschema'd, of an unknown type, or missing required fields — naming exactly what is missing. A §10 test proves the bite: two messages of the **same registered type** where one fits and one is refused for a missing field (the door that cannot refuse is a contract, §13.9), plus an unknown-type dead-letter and a core-type round-trip; `python -m unittest discover -s tests` green.

This is the first chapter of **The Polity** (the anthology) and the smallest landable cut of `ambient-gateway.chapter.md` increment #1 — the door only; the PDP/PEP `route()` generalization and the threshold actuator are increments #2-#3, explicitly out of this line.

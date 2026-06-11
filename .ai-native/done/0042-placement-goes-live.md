# Done-line 0042 — Placement goes live: the second real gate stops being a mock

@
Written before code, per §9.4. When this line is met, stop.

> **Done when:** the L1 placement seam is judged by `placement-gate.det.v1`,
> not its mock. A `node_real` admission (`placement-gate.mock.v0 ->
> placement-gate.det.v1`) signed with bdo's chat-stamp (2026-06-11, "remove
> mocks") is on the log; the mock-shame fold counts **2** still-mock stages
> (`handoff-gate`, `value-confirm`), not 3; and `python -m unittest discover -s
> tests` stays green. The §10 teeth for this gate already stand in
> `tests/test_placement_gate.py` (two atoms sound alone, `collision` together,
> the pair failing on a fixed-verdict mock) — this line carries the proven
> deterministic law onto the live seam, the named out-of-scope completion of
> done-line 0041, authorized by bdo, never forged by the session. bdo lands the
> PR; his merge is the ratification of the stamp it carries.
@

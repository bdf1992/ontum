# Report 0083 — Digest live glance fix

# Report

## End-state
Implemented the digest live-glance fix on branch codex/digest-readability-fix. Same-day spans render as a single date, superseded atom versions are marked as history and excluded from live arc parked/refused tallies, loose live atoms are named without being called bdo's move, and the result line reports open item counts.

## Validation
- python -m unittest tests.test_digest -v: 30 tests passed.
- python -m unittest discover -s tests -v: 838 tests passed in 127.260s.
- python -m loop.digest --today now renders the current day label, hides stale atom.field-topology.v0 as live parked work, and names atom.inbound-envoy-seam.v0 as loose work outside an arc.

## Needs-you
None.
